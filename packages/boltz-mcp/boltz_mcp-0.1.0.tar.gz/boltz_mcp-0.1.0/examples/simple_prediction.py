#!/usr/bin/env python3
"""
Simple example demonstrating how to use the Boltz MCP server for protein structure prediction.

This example shows:
1. How to set up a basic prediction request
2. How to predict a single protein structure
3. How to predict a protein complex
4. How to predict protein-ligand affinity
5. How to check server status with GPU detection
"""

import asyncio
import json
from pathlib import Path
from boltz_mcp.server import create_mcp_app, PredictionRequest, SequenceInput, AffinityPredictionRequest


async def example_single_protein():
    """Example: Predict structure of a single protein with auto-detected accelerator."""
    print("=== Single Protein Prediction Example ===")
    
    # Create MCP app
    app = create_mcp_app()
    
    # Example protein sequence (a short peptide for demo)
    sequence = "MKFLVLLFNILCLFPVLAADNHGVGPQGASLFRLAKEGDPSVQGIVSNTGKILFRVVDAHKNDNHKIITNTEGSKGGKDSILGKNIELP"
    
    # Create sequence input
    seq_input = SequenceInput(sequences={"protein1": sequence})
    
    # Predict structure (accelerator will be auto-detected)
    result = app.predict_from_sequences(
        sequences=seq_input,
        output_dir="./predictions/single_protein",
        model="boltz2"
    )
    
    print(f"Prediction successful: {result.success}")
    print(f"Output directory: {result.output_dir}")
    print(f"Generated files: {len(result.output_files)}")
    if result.success:
        for file_path in result.output_files[:3]:  # Show first 3 files
            print(f"  - {file_path}")
    else:
        print(f"Error details: {result.stderr[:200] if result.stderr else 'No stderr'}")
    
    return result


async def example_protein_complex():
    """Example: Predict structure of a protein complex."""
    print("\n=== Protein Complex Prediction Example ===")
    
    app = create_mcp_app()
    
    # Example sequences for a complex
    sequences = {
        "chain_A": "MKFLVLLFNILCLFPVLAADNHGVGPQGASLFRLAKEGDPSVQGIVSNTGKILFRVVDAHKNDNHKIITNTEGSKGGKDSILGKNIELP",
        "chain_B": "ARNDCEQGHILKMFPSTWYV"
    }
    
    # Create prediction request (accelerator auto-detected)
    request = PredictionRequest(
        input_data={"sequences": sequences},
        output_dir="./predictions/complex",
        model="boltz2",
        devices=1,
        # accelerator=None,  # Will auto-detect GPU if available
        recycling_steps=2,  # Reduced for faster demo
        sampling_steps=50,   # Reduced for faster demo
        diffusion_samples=1,
        output_format="mmcif"
    )
    
    # Predict structure
    result = app.predict_structure(request)
    
    print(f"Prediction successful: {result.success}")
    print(f"Output directory: {result.output_dir}")
    print(f"Generated files: {len(result.output_files)}")
    if result.success:
        for file_path in result.output_files[:3]:  # Show first 3 files
            print(f"  - {file_path}")
    else:
        print(f"Error details: {result.stderr[:200] if result.stderr else 'No stderr'}")
    
    return result


async def example_protein_ligand_affinity():
    """Example: Predict protein-ligand binding affinity."""
    print("\n=== Protein-Ligand Affinity Prediction Example ===")
    
    app = create_mcp_app()
    
    # Example protein sequence and ligand SMILES
    protein_sequence = "MKFLVLLFNILCLFPVLAADNHGVGPQGASLFRLAKEGDPSVQGIVSNTGKILFRVVDAHKNDNHKIITNTEGSKGGKDSILGKNIELP"
    ligand_smiles = "N[C@@H](Cc1ccc(O)cc1)C(=O)O"  # Tyrosine
    
    # Simple affinity prediction with auto-detected accelerator
    result = app.predict_binding_affinity(
        protein_sequence=protein_sequence,
        ligand_smiles=ligand_smiles,
        output_dir="./predictions/affinity"
    )
    
    print(f"Affinity prediction successful: {result.success}")
    print(f"Output directory: {result.output_dir}")
    print(f"Generated files: {len(result.output_files)}")
    if result.success:
        for file_path in result.output_files[:3]:  # Show first 3 files
            print(f"  - {file_path}")
    else:
        print(f"Error details: {result.stderr[:200] if result.stderr else 'No stderr'}")
    
    return result


async def example_check_status():
    """Example: Check Boltz installation status with GPU detection."""
    print("\n=== Status Check with GPU Detection ===")
    
    app = create_mcp_app()
    
    # Check status
    status = app.check_status()
    
    print(f"Boltz installed: {status['boltz_installed']}")
    print(f"Cache directory: {status['cache_directory']}")
    print(f"Cache exists: {status['cache_exists']}")
    print(f"Torch available: {status['torch_available']}")
    print(f"GPU available: {status['gpu_available']}")
    if status['gpu_available']:
        print(f"GPU count: {status.get('gpu_count', 'N/A')}")
        print(f"GPU name: {status.get('gpu_name', 'N/A')}")
    print(f"Detected accelerator: {status['detected_accelerator']}")
    print(f"Message: {status['message']}")
    
    return status


async def example_get_examples():
    """Example: Get configuration examples."""
    print("\n=== Configuration Examples ===")
    
    app = create_mcp_app()
    
    # Get examples
    examples = app.get_examples()
    
    print("Available example configurations:")
    for name, example in examples.items():
        print(f"\n{name}:")
        print(f"  Description: {example['description']}")
        if 'config' in example:
            config_preview = str(example['config'])
            if len(config_preview) > 100:
                config_preview = config_preview[:100] + "..."
            print(f"  Config: {config_preview}")


async def main():
    """Run all examples."""
    print("Boltz MCP Server Examples")
    print("=" * 40)
    
    # Check status first
    status = await example_check_status()
    
    if not status['boltz_installed']:
        print("\nWarning: Boltz is not installed. The prediction examples will fail.")
        print("Install Boltz with: pip install boltz")
        print("Continuing with other examples...")
    
    # Show configuration examples
    await example_get_examples()
    
    # If Boltz is installed, try predictions
    if status['boltz_installed']:
        print("\n" + "=" * 40)
        print("Running prediction examples...")
        
        # Run single protein example
        await example_single_protein()
        
        # Run complex example
        await example_protein_complex()
        
        # Run affinity example
        await example_protein_ligand_affinity()
    else:
        print("\nSkipping prediction examples due to missing Boltz installation.")
    
    print("\n" + "=" * 40)
    print("Examples completed!")


if __name__ == "__main__":
    asyncio.run(main()) 