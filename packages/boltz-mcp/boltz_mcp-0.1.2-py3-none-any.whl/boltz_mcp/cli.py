#!/usr/bin/env python3
"""
CLI for Boltz affinity predictions with optimized defaults.

This provides a simple command-line interface for drug-protein affinity prediction
with GPU acceleration and MSA server enabled by default.
"""

import typer
from pathlib import Path
from typing import Optional
from eliot import start_action
from enum import Enum
from pycomfort.logging import to_nice_stdout

from boltz_mcp.server import create_mcp_app, AffinityPredictionRequest


class Accelerator(str, Enum):
    gpu = "gpu"
    cpu = "cpu" 
    tpu = "tpu"


class OutputFormat(str, Enum):
    pdb = "pdb"
    mmcif = "mmcif"


def predict_affinity(
    protein_sequence: str = typer.Argument(..., help="Protein sequence in single letter amino acid code"),
    ligand_smiles: str = typer.Argument(..., help="Ligand structure as SMILES string"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Output directory path"),
    accelerator: Accelerator = typer.Option(Accelerator.gpu, "--accelerator", "-a", help="Accelerator type"),
    devices: int = typer.Option(1, "--devices", "-d", help="Number of devices to use"),
    recycling_steps: int = typer.Option(3, "--recycling-steps", "-r", help="Number of recycling steps"),
    sampling_steps: int = typer.Option(200, "--sampling-steps", "-s", help="Number of sampling steps for structure"),
    diffusion_samples: int = typer.Option(1, "--diffusion-samples", help="Number of diffusion samples for structure"),
    sampling_steps_affinity: int = typer.Option(200, "--sampling-steps-affinity", help="Number of sampling steps for affinity"),
    diffusion_samples_affinity: int = typer.Option(5, "--diffusion-samples-affinity", help="Number of diffusion samples for affinity"),
    output_format: OutputFormat = typer.Option(OutputFormat.mmcif, "--format", "-f", help="Output format"),
    override: bool = typer.Option(False, "--override", help="Override existing predictions"),
    use_msa_server: bool = typer.Option(True, "--msa-server/--no-msa-server", help="Use MSA server (default: True)"),
    affinity_mw_correction: bool = typer.Option(False, "--mw-correction", help="Use molecular weight correction for affinity"),
    no_kernels: bool = typer.Option(True, "--no-kernels/--use-kernels", help="Disable optimized kernels (fixes Triton GPU issues)"),
    cache_dir: Optional[Path] = typer.Option(None, "--cache-dir", help="Cache directory for Boltz models"),
) -> None:
    """
    Predict protein-ligand binding affinity using Boltz-2.
    
    This command predicts both the 3D structure of the protein-ligand complex
    and the binding affinity between them.
    
    Example:
        boltz-affinity "MKFLVLLFNILCLFPVLA" "CC(=O)Oc1ccccc1C(=O)O" -o results/
    """
    with start_action(action_type="cli_predict_affinity", 
                     protein_length=len(protein_sequence),
                     ligand_smiles=ligand_smiles,
                     accelerator=accelerator.value,
                     output_dir=str(output_dir) if output_dir else "./predictions/affinity",
                     use_msa_server=use_msa_server) as action:
        
        # Create MCP app
        app = create_mcp_app(cache_dir=cache_dir)
        
        # Set default output directory if not provided
        if output_dir is None:
            output_dir = Path("./predictions/affinity")
        
        # Create affinity prediction request
        request = AffinityPredictionRequest(
            protein_sequence=protein_sequence,
            ligand_smiles=ligand_smiles,
            output_dir=str(output_dir),
            devices=devices,
            accelerator=accelerator.value,
            recycling_steps=recycling_steps,
            sampling_steps=sampling_steps,
            diffusion_samples=diffusion_samples,
            sampling_steps_affinity=sampling_steps_affinity,
            diffusion_samples_affinity=diffusion_samples_affinity,
            output_format=output_format.value,
            override=override,
            use_msa_server=use_msa_server,
            affinity_mw_correction=affinity_mw_correction,
            no_kernels=no_kernels
        )
        
        # Run prediction
        result = app.predict_affinity(request)
        
        if result.success:
            action.log(
                message_type="prediction_completed",
                success=True,
                output_dir=result.output_dir,
                num_files=len(result.output_files),
                output_files=result.output_files[:5]  # Log first 5 files
            )
        else:
            action.log(
                message_type="prediction_failed",
                success=False,
                error_full=result.stderr if result.stderr else "No stderr",
                stdout_full=result.stdout if result.stdout else "No stdout", 
                command=result.command,
                return_code=getattr(result, 'returncode', 'Unknown')
            )
            raise typer.Exit(1)


def quick_demo() -> None:
    """
    Run a quick demo affinity prediction with insulin and aspirin.
    
    This uses a small protein (insulin A chain) and aspirin to demonstrate
    the affinity prediction functionality quickly.
    """
    print("🔬 Quick Affinity Prediction Demo")
    print("=" * 40)
    
    # Small protein and simple drug for fast demo
    protein_seq = "GIVEQCCTSICSLYQLENYCN"  # Insulin A chain
    drug_smiles = "CC(=O)Oc1ccccc1C(=O)O"  # Aspirin
    
    predict_affinity(
        protein_sequence=protein_seq,
        ligand_smiles=drug_smiles,
        output_dir=Path("./predictions/demo"),
        sampling_steps=100,  # Reduced for speed
        sampling_steps_affinity=100,  # Reduced for speed
        diffusion_samples_affinity=3  # Reduced for speed
    )


def main():
    """Main CLI application."""
    to_nice_stdout()
    
    app = typer.Typer(
        name="boltz-affinity",
        help="Boltz protein-ligand affinity prediction CLI",
        no_args_is_help=True
    )
    
    app.command("predict", help="Predict protein-ligand binding affinity")(predict_affinity)
    app.command("demo", help="Run quick demo with insulin and aspirin")(quick_demo)
    
    app()


if __name__ == "__main__":
    main() 