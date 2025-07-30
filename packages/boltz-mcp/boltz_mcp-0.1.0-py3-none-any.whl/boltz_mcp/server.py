#!/usr/bin/env python3
"""Boltz MCP Server - Protein structure prediction interface using Boltz-2 model."""

import asyncio
import os
import tempfile
import yaml
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Literal
from contextlib import asynccontextmanager
import subprocess
import shutil

from fastmcp import FastMCP
from pydantic import BaseModel, Field
from eliot import start_action
import requests
from tqdm import tqdm
import typer

# Import torch for GPU detection
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# Import Boltz components from installed package
try:
    from boltz.main import get_cache_path
    BOLTZ_AVAILABLE = True
except ImportError:
    BOLTZ_AVAILABLE = False
    
    def get_cache_path():
        return "~/.boltz"

# Configuration using environment variables (os.getenv is the appropriate way to access env vars)
DEFAULT_HOST = os.getenv("MCP_HOST", "0.0.0.0")
DEFAULT_PORT = int(os.getenv("MCP_PORT", "3002"))
DEFAULT_TRANSPORT = os.getenv("MCP_TRANSPORT", "streamable-http")

class PredictionRequest(BaseModel):
    """Request for protein structure prediction."""
    input_data: Dict[str, Any] = Field(description="Input configuration for Boltz prediction")
    output_dir: Optional[str] = Field(default=None, description="Output directory path")
    model: Literal["boltz1", "boltz2"] = Field(default="boltz2", description="Model to use")
    devices: int = Field(default=1, description="Number of devices to use")
    accelerator: Optional[Literal["gpu", "cpu", "tpu"]] = Field(default=None, description="Accelerator type (auto-detected if None)")
    recycling_steps: int = Field(default=3, description="Number of recycling steps")
    sampling_steps: int = Field(default=200, description="Number of sampling steps")
    diffusion_samples: int = Field(default=1, description="Number of diffusion samples")
    output_format: Literal["pdb", "mmcif"] = Field(default="mmcif", description="Output format")
    override: bool = Field(default=False, description="Override existing predictions")
    use_msa_server: bool = Field(default=True, description="Use MSA server")
    
class PredictionResult(BaseModel):
    """Result from a Boltz prediction."""
    success: bool = Field(description="Whether prediction was successful")
    output_files: List[str] = Field(description="List of generated output files")
    output_dir: str = Field(description="Output directory path")
    command: str = Field(description="The command that was executed")
    stdout: Optional[str] = Field(description="Standard output from the command")
    stderr: Optional[str] = Field(description="Standard error from the command")

class SequenceInput(BaseModel):
    """Input for sequence-based prediction."""
    sequences: Dict[str, str] = Field(description="Dictionary of sequence_id: sequence")
    sequence_type: Literal["protein", "dna", "rna"] = Field(default="protein", description="Type of sequences")

class AffinityPredictionRequest(BaseModel):
    """Request for protein-ligand affinity prediction."""
    protein_sequence: str = Field(description="Protein sequence in single letter amino acid code")
    ligand_smiles: str = Field(description="Ligand structure as SMILES string")
    output_dir: Optional[str] = Field(default=None, description="Output directory path")
    devices: int = Field(default=1, description="Number of devices to use")
    accelerator: Optional[Literal["gpu", "cpu", "tpu"]] = Field(default=None, description="Accelerator type (auto-detected if None)")
    recycling_steps: int = Field(default=3, description="Number of recycling steps")
    sampling_steps: int = Field(default=200, description="Number of sampling steps for structure")
    diffusion_samples: int = Field(default=1, description="Number of diffusion samples for structure")
    sampling_steps_affinity: int = Field(default=200, description="Number of sampling steps for affinity")
    diffusion_samples_affinity: int = Field(default=5, description="Number of diffusion samples for affinity")
    output_format: Literal["pdb", "mmcif"] = Field(default="mmcif", description="Output format")
    override: bool = Field(default=False, description="Override existing predictions")
    use_msa_server: bool = Field(default=True, description="Use MSA server")
    affinity_mw_correction: bool = Field(default=False, description="Use molecular weight correction for affinity")

def detect_accelerator() -> Literal["gpu", "cpu", "tpu"]:
    """Detect the best available accelerator."""
    if TORCH_AVAILABLE and torch.cuda.is_available():
        return "gpu"
    # TODO: Add TPU detection when needed
    return "cpu"

class BoltzManager:
    """Manages Boltz model operations and predictions using the Python API."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path(get_cache_path()).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def check_boltz_installation(self) -> bool:
        """Check if Boltz is installed and accessible."""
        return BOLTZ_AVAILABLE
    
    def create_config_file(self, data: Dict[str, Any], temp_dir: Path) -> Path:
        """Create a YAML configuration file from input data."""
        config_path = temp_dir / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        return config_path
    
    def create_fasta_file(self, sequences: Dict[str, str], temp_dir: Path) -> Path:
        """Create a FASTA file from sequences in the format Boltz expects."""
        fasta_path = temp_dir / "input.fasta"
        
        # Convert sequence IDs to single letters (A, B, C, etc.) as Boltz expects
        chain_letters = [chr(65 + i) for i in range(len(sequences))]  # A, B, C, ...
        
        with open(fasta_path, 'w') as f:
            for i, (seq_id, sequence) in enumerate(sequences.items()):
                chain_id = chain_letters[i]
                # Boltz expects format: >CHAIN_ID|ENTITY_TYPE
                # When using --use_msa_server, we don't specify MSA path
                f.write(f">{chain_id}|protein\n{sequence}\n")
        return fasta_path
    
    def create_affinity_config(self, protein_sequence: str, ligand_smiles: str, temp_dir: Path) -> Path:
        """Create a YAML configuration file for affinity prediction."""
        config_data = {
            "version": 1,
            "sequences": [
                {
                    "protein": {
                        "id": "A",
                        "sequence": protein_sequence
                    }
                },
                {
                    "ligand": {
                        "id": "B", 
                        "smiles": ligand_smiles
                    }
                }
            ],
            "properties": [
                {
                    "affinity": {
                        "binder": "B"
                    }
                }
            ]
        }
        
        config_path = temp_dir / "affinity_config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        return config_path
    
    def run_prediction(self, request: PredictionRequest) -> PredictionResult:
        """Run Boltz prediction using subprocess."""
        with start_action(action_type="run_boltz_prediction", model=request.model) as action:
            # Auto-detect accelerator if not specified
            accelerator = request.accelerator or detect_accelerator()
            action.add_success_fields(accelerator_detected=accelerator)
            
            # Create temporary directory for input files
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Determine output directory
                if request.output_dir:
                    output_dir = Path(request.output_dir)
                    output_dir.mkdir(parents=True, exist_ok=True)
                else:
                    output_dir = temp_path / "outputs"
                    output_dir.mkdir(exist_ok=True)
                
                # Create input file based on input_data
                if "sequences" in request.input_data:
                    input_file = self.create_fasta_file(request.input_data["sequences"], temp_path)
                elif "config" in request.input_data:
                    input_file = self.create_config_file(request.input_data["config"], temp_path)
                else:
                    # Assume input_data is the config itself
                    input_file = self.create_config_file(request.input_data, temp_path)
                
                # Build command to run boltz using the installed package
                cmd = [
                    "boltz", "predict", str(input_file),
                    "--out_dir", str(output_dir),
                    "--model", request.model,
                    "--devices", str(request.devices),
                    "--accelerator", accelerator,
                    "--recycling_steps", str(request.recycling_steps),
                    "--sampling_steps", str(request.sampling_steps),
                    "--diffusion_samples", str(request.diffusion_samples),
                    "--output_format", request.output_format,
                    "--cache", str(self.cache_dir),
                    "--num_workers", "1"
                ]
                
                # Add conditional flags
                if "sequences" in request.input_data or request.use_msa_server:
                    cmd.append("--use_msa_server")
                
                if accelerator == "cpu":
                    cmd.append("--no_kernels")
                
                if request.override:
                    cmd.append("--override")
                
                # Execute command using the installed package
                action.add_success_fields(command=" ".join(cmd))
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=3600,  # 1 hour timeout
                )
                
                # Find the actual output directory (Boltz creates a subdirectory)
                actual_output_dir = output_dir
                for item in output_dir.iterdir():
                    if item.is_dir() and item.name.startswith("boltz_results_"):
                        actual_output_dir = item
                        break
                
                # Collect output files
                output_files = []
                if actual_output_dir.exists():
                    for file_path in actual_output_dir.rglob("*"):
                        if file_path.is_file():
                            output_files.append(str(file_path))
                
                prediction_result = PredictionResult(
                    success=result.returncode == 0,
                    output_files=output_files,
                    output_dir=str(actual_output_dir),
                    command=" ".join(cmd),
                    stdout=result.stdout,
                    stderr=result.stderr
                )
                
                action.add_success_fields(
                    success=prediction_result.success,
                    output_files_count=len(output_files),
                    return_code=result.returncode
                )
                
                return prediction_result
    
    def run_affinity_prediction(self, request: AffinityPredictionRequest) -> PredictionResult:
        """Run Boltz affinity prediction using subprocess."""
        with start_action(action_type="run_boltz_affinity_prediction") as action:
            # Auto-detect accelerator if not specified
            accelerator = request.accelerator or detect_accelerator()
            action.add_success_fields(accelerator_detected=accelerator)
            
            # Create temporary directory for input files
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Determine output directory
                if request.output_dir:
                    output_dir = Path(request.output_dir)
                    output_dir.mkdir(parents=True, exist_ok=True)
                else:
                    output_dir = temp_path / "outputs"
                    output_dir.mkdir(exist_ok=True)
                
                # Create affinity configuration file
                config_file = self.create_affinity_config(
                    request.protein_sequence, 
                    request.ligand_smiles, 
                    temp_path
                )
                
                # Build command to run boltz using the installed package
                cmd = [
                    "boltz", "predict", str(config_file),
                    "--out_dir", str(output_dir),
                    "--model", "boltz2",  # Always use boltz2 for affinity
                    "--devices", str(request.devices),
                    "--accelerator", accelerator,
                    "--recycling_steps", str(request.recycling_steps),
                    "--sampling_steps", str(request.sampling_steps),
                    "--diffusion_samples", str(request.diffusion_samples),
                    "--sampling_steps_affinity", str(request.sampling_steps_affinity),
                    "--diffusion_samples_affinity", str(request.diffusion_samples_affinity),
                    "--output_format", request.output_format,
                    "--cache", str(self.cache_dir),
                    "--num_workers", "1"
                ]
                
                # Add conditional flags
                if request.use_msa_server:
                    cmd.append("--use_msa_server")
                
                if accelerator == "cpu":
                    cmd.append("--no_kernels")
                
                if request.override:
                    cmd.append("--override")
                
                if request.affinity_mw_correction:
                    cmd.append("--affinity_mw_correction")
                
                # Execute command using the installed package
                action.add_success_fields(command=" ".join(cmd))
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=3600,  # 1 hour timeout
                )
                
                # Find the actual output directory (Boltz creates a subdirectory)
                actual_output_dir = output_dir
                for item in output_dir.iterdir():
                    if item.is_dir() and item.name.startswith("boltz_results_"):
                        actual_output_dir = item
                        break
                
                # Collect output files
                output_files = []
                if actual_output_dir.exists():
                    for file_path in actual_output_dir.rglob("*"):
                        if file_path.is_file():
                            output_files.append(str(file_path))
                
                prediction_result = PredictionResult(
                    success=result.returncode == 0,
                    output_files=output_files,
                    output_dir=str(actual_output_dir),
                    command=" ".join(cmd),
                    stdout=result.stdout,
                    stderr=result.stderr
                )
                
                action.add_success_fields(
                    success=prediction_result.success,
                    output_files_count=len(output_files),
                    return_code=result.returncode
                )
                
                return prediction_result

class BoltzMCP(FastMCP):
    """Boltz MCP Server with protein structure prediction tools."""
    
    def __init__(
        self, 
        name: str = "Boltz MCP Server",
        cache_dir: Optional[Path] = None,
        **kwargs
    ):
        """Initialize the BoltzMCP server."""
        # Remove debug from kwargs if present to avoid passing it to parent
        debug = kwargs.pop('debug', False)
        
        super().__init__(name=name, **kwargs)
        self.manager = BoltzManager(cache_dir=cache_dir)
        self._register_boltz_tools()
        self._register_boltz_resources()
    
    def _register_boltz_tools(self):
        """Register Boltz-specific tools."""
        self.tool(
            name="boltz_predict_structure",
            description="Predict protein structure using Boltz-2 model from input configuration or sequences"
        )(self.predict_structure)
        
        self.tool(
            name="boltz_predict_from_sequences", 
            description="Predict protein structure from amino acid sequences using Boltz-2"
        )(self.predict_from_sequences)
        
        self.tool(
            name="boltz_predict_affinity",
            description="Predict protein-ligand binding affinity using Boltz-2 affinity model"
        )(self.predict_affinity)
        
        self.tool(
            name="boltz_predict_binding_affinity",
            description="Simple protein-ligand binding affinity prediction from sequence and SMILES"
        )(self.predict_binding_affinity)
        
        self.tool(
            name="boltz_check_status",
            description="Check if Boltz is properly installed and accessible"
        )(self.check_status)
        
        self.tool(
            name="boltz_get_examples",
            description="Get example configurations for different types of Boltz predictions"
        )(self.get_examples)
    
    def _register_boltz_resources(self):
        """Register Boltz-specific resources."""
        
        @self.resource("resource://boltz-usage-guide")
        def get_usage_guide() -> str:
            """
            Get comprehensive usage guide for Boltz-2 protein structure prediction.
            
            This resource contains detailed information about:
            - Input formats and requirements
            - Configuration options
            - Output formats
            - Examples of common prediction tasks
            
            Returns:
                The complete usage guide text
            """
            return """
# Boltz-2 MCP Usage Guide

## Overview
Boltz-2 is a state-of-the-art protein structure prediction model that can predict:
- Single protein structures
- Protein complexes
- Protein-ligand interactions
- Cyclic peptides
- Custom MSA handling

## Input Formats

### 1. Sequence-based Input
Provide amino acid sequences directly:
```python
{
    "sequences": {
        "protein_A": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
        "protein_B": "ARNDCEQGHILKMFPSTWYV"
    }
}
```

### 2. Configuration-based Input
Use YAML-style configuration:
```python
{
    "sequences": ["protein1.fasta"],
    "job_name": "my_prediction",
    "pdb_id": "1ABC",  # Optional template
    "msa": ["custom.a3m"],  # Custom MSA
    "ligands": ["ligand.sdf"]  # Ligands
}
```

### 3. Affinity Prediction Input
For protein-ligand binding affinity:
```python
{
    "protein_sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
    "ligand_smiles": "N[C@@H](Cc1ccc(O)cc1)C(=O)O"
}
```

This will create a YAML configuration like:
```yaml
version: 1
sequences:
  - protein:
      id: A
      sequence: MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG
  - ligand:
      id: B
      smiles: 'N[C@@H](Cc1ccc(O)cc1)C(=O)O'
properties:
  - affinity:
      binder: B
```

## Prediction Types

### Single Protein
- Input: Single amino acid sequence
- Output: 3D structure in PDB/mmCIF format

### Protein Complex
- Input: Multiple sequences
- Output: Complex structure with interfaces

### Protein-Ligand Structure
- Input: Protein sequence + ligand structure
- Output: Bound complex structure

### Protein-Ligand Affinity
- Input: Protein sequence + ligand SMILES
- Output: Binding affinity prediction + structure

## Parameters

### Core Parameters
- `model`: "boltz1" or "boltz2" (default: "boltz2")
- `devices`: Number of GPU devices (default: 1)
- `accelerator`: "gpu", "cpu", or "tpu" (default: auto-detected, usually "gpu" if available)

### Sampling Parameters
- `recycling_steps`: Number of recycling iterations (default: 3)
- `sampling_steps`: Diffusion sampling steps (default: 200)
- `diffusion_samples`: Number of samples to generate (default: 1)

### Output Parameters
- `output_format`: "pdb" or "mmcif" (default: "mmcif")
- `output_dir`: Where to save results

## Examples

See the `boltz_get_examples` tool for specific configuration examples.
"""
    
    def predict_structure(self, request: PredictionRequest) -> PredictionResult:
        """
        Predict protein structure using Boltz-2 model.
        
        Args:
            request: Prediction configuration including input data and parameters
            
        Returns:
            PredictionResult with success status and output file paths
        """
        with start_action(action_type="predict_structure", model=request.model) as action:
            return self.manager.run_prediction(request)
    
    def predict_from_sequences(self, sequences: SequenceInput, output_dir: Optional[str] = None, model: Literal["boltz1", "boltz2"] = "boltz2") -> PredictionResult:
        """
        Predict protein structure from amino acid sequences.
        
        Args:
            sequences: Input sequences with IDs
            output_dir: Where to save results (optional)
            model: Model to use ("boltz1" or "boltz2")
            
        Returns:
            PredictionResult with success status and output file paths
        """
        request = PredictionRequest(
            input_data={"sequences": sequences.sequences},
            output_dir=output_dir,
            model=model
        )
        return self.predict_structure(request)
    
    def predict_affinity(self, request: AffinityPredictionRequest) -> PredictionResult:
        """
        Predict protein-ligand binding affinity using Boltz-2 affinity model.
        
        Args:
            request: Affinity prediction configuration including protein sequence and ligand SMILES
            
        Returns:
            PredictionResult with success status and output file paths including affinity predictions
        """
        with start_action(action_type="predict_affinity") as action:
            return self.manager.run_affinity_prediction(request)
    
    def predict_binding_affinity(
        self, 
        protein_sequence: str, 
        ligand_smiles: str, 
        output_dir: Optional[str] = None,
        accelerator: Optional[Literal["gpu", "cpu", "tpu"]] = None
    ) -> PredictionResult:
        """
        Simple protein-ligand binding affinity prediction.
        
        Args:
            protein_sequence: Protein sequence in single letter amino acid code
            ligand_smiles: Ligand structure as SMILES string
            output_dir: Where to save results (optional)
            accelerator: Accelerator type to use
            
        Returns:
            PredictionResult with success status and output file paths including affinity predictions
        """
        request = AffinityPredictionRequest(
            protein_sequence=protein_sequence,
            ligand_smiles=ligand_smiles,
            output_dir=output_dir,
            accelerator=accelerator
        )
        return self.predict_affinity(request)
    
    def check_status(self) -> Dict[str, Any]:
        """
        Check if Boltz is properly installed and accessible.
        
        Returns:
            Status information including installation status, cache directory, and GPU availability
        """
        with start_action(action_type="check_boltz_status") as action:
            is_installed = self.manager.check_boltz_installation()
            detected_accelerator = detect_accelerator()
            
            status = {
                "boltz_installed": is_installed,
                "cache_directory": str(self.manager.cache_dir),
                "cache_exists": self.manager.cache_dir.exists(),
                "torch_available": TORCH_AVAILABLE,
                "gpu_available": TORCH_AVAILABLE and torch.cuda.is_available() if TORCH_AVAILABLE else False,
                "detected_accelerator": detected_accelerator
            }
            
            if TORCH_AVAILABLE and torch.cuda.is_available():
                status["gpu_count"] = torch.cuda.device_count()
                status["gpu_name"] = torch.cuda.get_device_name(0) if torch.cuda.device_count() > 0 else None
            
            if is_installed:
                status["message"] = f"Boltz is properly installed and accessible. Default accelerator: {detected_accelerator}"
            else:
                status["message"] = "Boltz is not installed or not accessible. Please install using: pip install boltz"
            
            action.add_success_fields(**status)
            return status
    
    def get_examples(self) -> Dict[str, Any]:
        """
        Get example configurations for different types of Boltz predictions.
        
        Returns:
            Dictionary of example configurations for various prediction scenarios
        """
        return {
            "single_protein": {
                "description": "Predict structure of a single protein",
                "config": {
                    "sequences": {
                        "protein1": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
                    }
                }
            },
            "protein_complex": {
                "description": "Predict structure of a protein complex",
                "config": {
                    "sequences": {
                        "chain_A": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
                        "chain_B": "ARNDCEQGHILKMFPSTWYV"
                    }
                }
            },
            "with_template": {
                "description": "Use existing structure as template",
                "config": {
                    "sequences": ["protein.fasta"],
                    "job_name": "templated_prediction",
                    "pdb_id": "1ABC"
                }
            },
            "custom_msa": {
                "description": "Use custom multiple sequence alignment",
                "config": {
                    "sequences": ["protein.fasta"],
                    "job_name": "custom_msa_prediction",
                    "msa": ["custom_alignment.a3m"]
                }
            },
            "protein_ligand": {
                "description": "Predict protein-ligand complex",
                "config": {
                    "sequences": ["protein.fasta"],
                    "job_name": "protein_ligand",
                    "ligands": ["ligand.sdf"]
                }
            },
            "cyclic_peptide": {
                "description": "Predict cyclic peptide structure",
                "config": {
                    "sequences": ["peptide.fasta"],
                    "job_name": "cyclic_peptide",
                    "is_cyclic": True
                }
            },
            "protein_ligand_affinity": {
                "description": "Predict protein-ligand binding affinity",
                "config": {
                    "protein_sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
                    "ligand_smiles": "N[C@@H](Cc1ccc(O)cc1)C(=O)O"
                },
                "yaml_format": {
                    "version": 1,
                    "sequences": [
                        {
                            "protein": {
                                "id": "A",
                                "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
                            }
                        },
                        {
                            "ligand": {
                                "id": "B",
                                "smiles": "N[C@@H](Cc1ccc(O)cc1)C(=O)O"
                            }
                        }
                    ],
                    "properties": [
                        {
                            "affinity": {
                                "binder": "B"
                            }
                        }
                    ]
                }
            }
        }

def create_mcp_app(cache_dir: Optional[Path] = None) -> BoltzMCP:
    """Helper to create the MCP app."""
    app = BoltzMCP(cache_dir=cache_dir)
    return app

cli = typer.Typer(
    name="boltz-mcp",
    help="""Boltz MCP Server for protein structure and affinity prediction.

This CLI provides multiple ways to run the server (http, sse, stdio).
""",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="markdown"
)

@cli.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    cache_dir: Optional[Path] = typer.Option(None, help="Cache directory for Boltz models"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode for MCP")
) -> None:
    """Boltz MCP Server - defaults to stdio transport if no command specified."""
    if ctx.invoked_subcommand is None:
        # Default to stdio transport
        app = create_mcp_app(cache_dir=cache_dir)
        app.run(transport="stdio")

@cli.command("http")
def cli_app(
    host: str = typer.Option(DEFAULT_HOST, help="Host to bind to"),
    port: int = typer.Option(DEFAULT_PORT, help="Port to bind to"),
    cache_dir: Optional[Path] = typer.Option(None, help="Cache directory for Boltz models"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode for MCP")
) -> None:
    """Start HTTP server."""
    app = create_mcp_app(cache_dir=cache_dir)
    app.run(transport="streamable-http", host=host, port=port)

@cli.command("stdio")
def cli_app_stdio(
    cache_dir: Optional[Path] = typer.Option(None, help="Cache directory for Boltz models"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode for MCP")
) -> None:
    """Start stdio transport (default)."""
    app = create_mcp_app(cache_dir=cache_dir)
    app.run(transport="stdio")

@cli.command("sse")
def cli_app_sse(
    host: str = typer.Option(DEFAULT_HOST, help="Host to bind to"),
    port: int = typer.Option(DEFAULT_PORT, help="Port to bind to"),
    cache_dir: Optional[Path] = typer.Option(None, help="Cache directory for Boltz models"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode for MCP")
) -> None:
    """Start SSE transport."""
    app = create_mcp_app(cache_dir=cache_dir)
    app.run(transport="sse", host=host, port=port)

if __name__ == "__main__":
    cli()

# Standalone entry point functions for script entries
def cli_app_standalone():
    """Standalone HTTP server entry point."""
    app = create_mcp_app()
    app.run(transport="streamable-http", host=DEFAULT_HOST, port=DEFAULT_PORT)

def cli_app_stdio_standalone():
    """Standalone stdio server entry point."""
    app = create_mcp_app()
    app.run(transport="stdio")

def cli_app_sse_standalone():
    """Standalone SSE server entry point."""
    app = create_mcp_app()
    app.run(transport="sse", host=DEFAULT_HOST, port=DEFAULT_PORT)