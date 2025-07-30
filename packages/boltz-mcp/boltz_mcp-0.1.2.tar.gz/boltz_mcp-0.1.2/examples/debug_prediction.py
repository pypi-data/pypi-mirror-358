#!/usr/bin/env python3
"""
Debug script to see what's happening with Boltz predictions.

This script provides detailed debugging information including:
- Server status and GPU detection
- Command execution details
- Complete stdout/stderr output
- File system inspection
"""

import asyncio
import json
from pathlib import Path
from boltz_mcp.server import create_mcp_app, PredictionRequest, SequenceInput, detect_accelerator


async def debug_status():
    """Debug server status and GPU detection."""
    print("=== Debug Server Status ===")
    
    app = create_mcp_app()
    status = app.check_status()
    
    print("Server Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print(f"\nDirect accelerator detection: {detect_accelerator()}")
    
    return status


async def debug_prediction():
    """Debug a single protein prediction to see what's happening."""
    print("\n=== Debug Single Protein Prediction ===")
    
    # Create MCP app
    app = create_mcp_app()
    
    # Simple protein sequence
    sequence = "MKFLVLLFNILCLFPVLAADNHGVGPQGASLFRLAKEGDPSVQGIVSNTGKILFRVVDAHKNDNHKIITNTEGSKGGKDSILGKNIELP"
    
    # Create sequence input
    seq_input = SequenceInput(sequences={"protein1": sequence})
    
    print(f"Input sequence length: {len(sequence)}")
    print(f"Sequence preview: {sequence[:50]}...")
    
    # Predict structure with debug output (accelerator auto-detected)
    result = app.predict_from_sequences(
        sequences=seq_input,
        output_dir="./predictions/debug",
        model="boltz2"
    )
    
    print("\n=== Prediction Results ===")
    print(f"Success: {result.success}")
    print(f"Command executed: {result.command}")
    print(f"Output directory: {result.output_dir}")
    print(f"Generated files count: {len(result.output_files)}")
    
    if result.output_files:
        print("\n=== Output Files ===")
        for i, file_path in enumerate(result.output_files):
            file_size = Path(file_path).stat().st_size if Path(file_path).exists() else 0
            print(f"  {i+1}. {file_path} ({file_size} bytes)")
            if i >= 9:  # Show max 10 files
                remaining = len(result.output_files) - 10
                if remaining > 0:
                    print(f"  ... and {remaining} more files")
                break
    
    # Check what's actually in the output directory
    output_path = Path(result.output_dir)
    if output_path.exists():
        print(f"\n=== Directory Structure: {output_path} ===")
        all_items = list(output_path.rglob("*"))
        dirs = [item for item in all_items if item.is_dir()]
        files = [item for item in all_items if item.is_file()]
        
        print(f"Directories ({len(dirs)}):")
        for directory in sorted(dirs)[:5]:  # Show max 5 dirs
            print(f"  📁 {directory.relative_to(output_path)}")
        if len(dirs) > 5:
            print(f"  ... and {len(dirs) - 5} more directories")
        
        print(f"\nFiles ({len(files)}):")
        for file_item in sorted(files)[:10]:  # Show max 10 files
            rel_path = file_item.relative_to(output_path)
            size = file_item.stat().st_size
            print(f"  📄 {rel_path} ({size} bytes)")
        if len(files) > 10:
            print(f"  ... and {len(files) - 10} more files")
    else:
        print(f"\n❌ Output directory does not exist: {output_path}")
    
    print(f"\n=== STDOUT ({len(result.stdout)} chars) ===")
    if result.stdout:
        lines = result.stdout.split('\n')
        if len(lines) > 20:
            print('\n'.join(lines[:10]))
            print(f"... ({len(lines) - 20} lines omitted) ...")
            print('\n'.join(lines[-10:]))
        else:
            print(result.stdout)
    else:
        print("(No stdout output)")
    
    print(f"\n=== STDERR ({len(result.stderr)} chars) ===")
    if result.stderr:
        lines = result.stderr.split('\n')
        if len(lines) > 20:
            print('\n'.join(lines[:10]))
            print(f"... ({len(lines) - 20} lines omitted) ...")
            print('\n'.join(lines[-10:]))
        else:
            print(result.stderr)
    else:
        print("(No stderr output)")
    
    return result


async def debug_affinity_prediction():
    """Debug protein-ligand affinity prediction."""
    print("\n=== Debug Affinity Prediction ===")
    
    app = create_mcp_app()
    
    # Simple example
    protein_sequence = "MKFLVLLFNILCLFPVLAADNHGVGPQGASLFRLAKEGDPSVQGIVSNTGKILFRVVDAHKNDNHKIITNTEGSKGGKDSILGKNIELP"
    ligand_smiles = "N[C@@H](Cc1ccc(O)cc1)C(=O)O"  # Tyrosine
    
    print(f"Protein sequence length: {len(protein_sequence)}")
    print(f"Ligand SMILES: {ligand_smiles}")
    
    # Quick affinity prediction test
    result = app.predict_binding_affinity(
        protein_sequence=protein_sequence,
        ligand_smiles=ligand_smiles,
        output_dir="./predictions/debug_affinity"
    )
    
    print(f"\nAffinity prediction success: {result.success}")
    print(f"Command: {result.command}")
    print(f"Output files: {len(result.output_files)}")
    
    if not result.success:
        print(f"Error preview: {result.stderr[:300] if result.stderr else 'No stderr'}...")
    
    return result


async def main():
    """Run all debug examples."""
    print("Boltz MCP Debug Script")
    print("=" * 50)
    
    # Debug status
    status = await debug_status()
    
    if not status['boltz_installed']:
        print("\n❌ Boltz is not installed. Install with: pip install boltz")
        return
    
    # Debug structure prediction
    struct_result = await debug_prediction()
    
    # Debug affinity prediction
    affinity_result = await debug_affinity_prediction()
    
    print("\n" + "=" * 50)
    print("Debug completed!")
    print(f"Structure prediction success: {struct_result.success}")
    print(f"Affinity prediction success: {affinity_result.success}")


if __name__ == "__main__":
    asyncio.run(main()) 