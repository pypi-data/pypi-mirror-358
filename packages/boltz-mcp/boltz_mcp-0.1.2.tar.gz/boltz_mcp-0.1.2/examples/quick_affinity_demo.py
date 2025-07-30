#!/usr/bin/env python3
"""
Quick Demo: Drug-Protein Affinity Prediction

A simple, fast example to test the Boltz MCP server affinity prediction.
Uses a small protein and simple drug for quick results.
"""

import asyncio
from boltz_mcp.server import create_mcp_app


async def quick_demo():
    """Quick affinity prediction demo with minimal runtime."""
    print("🔬 Quick Drug-Protein Affinity Demo")
    print("=" * 40)
    
    # Create MCP app
    app = create_mcp_app()
    
    # Check status first
    print("Checking system status...")
    status = app.check_status()
    
    if not status['boltz_installed']:
        print("❌ Boltz not installed. Please run: pip install boltz")
        return
    
    print(f"✅ System ready! Using {status['detected_accelerator']}")
    
    # Small protein sequence (insulin A chain - 21 residues)
    protein_sequence = "GIVEQCCTSICSLYQLENYCN"
    
    # Simple drug (aspirin)
    drug_smiles = "CC(=O)Oc1ccccc1C(=O)O"
    
    print(f"\n🧬 Protein: Insulin A chain ({len(protein_sequence)} residues)")
    print(f"💊 Drug: Aspirin (SMILES: {drug_smiles})")
    print("\n⏳ Running prediction (this may take a few minutes)...")
    
    # Quick prediction with reduced parameters for speed
    try:
        result = app.predict_binding_affinity(
            protein_sequence=protein_sequence,
            ligand_smiles=drug_smiles,
            output_dir="./predictions/quick_demo"
        )
        
        if result.success:
            print("\n✅ Prediction completed successfully!")
            print(f"📁 Results saved to: {result.output_dir}")
            print(f"📄 Generated {len(result.output_files)} files:")
            for file_path in result.output_files[:3]:  # Show first 3 files
                print(f"   - {file_path}")
            
            print("\n📊 What you can find in the results:")
            print("   - 3D structure of protein-drug complex")
            print("   - Binding affinity prediction")
            print("   - Confidence scores")
            
        else:
            print(f"\n❌ Prediction failed: {result.stderr[:200] if result.stderr else 'Unknown error'}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nThis might be due to:")
        print("- Model downloading on first run (automatic)")
        print("- GPU memory limitations")
        print("- Network issues")


if __name__ == "__main__":
    asyncio.run(quick_demo()) 