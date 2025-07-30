#!/usr/bin/env python3
"""
Drug-Protein Affinity Prediction Example using Boltz MCP Server

This example demonstrates how to predict binding affinity between drugs (in SMILES format) 
and proteins using the Boltz-2 model through the MCP server.

Examples include:
1. Basic affinity prediction with a known drug and protein
2. Multiple drug candidates against a single protein target
3. Using the advanced configuration method
4. Real-world examples with FDA-approved drugs

The Boltz-2 model can predict both the 3D structure of the protein-ligand complex
and the binding affinity between them.
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Tuple
from boltz_mcp.server import (
    create_mcp_app, 
    PredictionRequest, 
    AffinityPredictionRequest
)


async def example_basic_drug_protein_affinity():
    """
    Example 1: Basic affinity prediction between a drug and protein.
    
    Uses the simplified predict_binding_affinity method for quick predictions.
    """
    print("=== Basic Drug-Protein Affinity Prediction ===")
    
    # Create MCP app
    app = create_mcp_app()
    
    # Example protein: Human carbonic anhydrase II (truncated for demo)
    # This is a well-studied drug target for glaucoma and other conditions
    protein_sequence = """
    MSHHWGYGKHNGPEHWHKDFPIAKGERQSPVDIDTHTAKYDPSLKPLSVSYDQATSLRILNN
    GHAFNVEFDDSQDKAVLKGGPLDGTYRLIQFHFHWGSLDGQGSEHTVDKKKYAAELHLVHWN
    TKYGDFGKAVQQPDGLAVLGIFLKVGSAKPGLQKVVDVLDSIKTKGKSADFTNFDPRGLLPE
    SLDYWTYPGSLTTPPLLECVTWIVLKEPISVSSEQVLKFRKLNFNGEGEPEELMVDNWRPAQ
    PLKNRQIKASFK
    """
    
    # Example drug: Acetazolamide (a carbonic anhydrase inhibitor)
    # SMILES representation of acetazolamide
    drug_smiles = "CC(=O)Nc1nnc(s1)S(=O)(=O)N"
    
    print(f"Protein length: {len(protein_sequence.replace(' ', '').replace('\n', ''))} residues")
    print(f"Drug SMILES: {drug_smiles}")
    print("Predicting binding affinity...")
    
    # Predict binding affinity using the simple method
    result = app.predict_binding_affinity(
        protein_sequence=protein_sequence.replace(' ', '').replace('\n', ''),
        ligand_smiles=drug_smiles,
        output_dir="./predictions/drug_affinity/acetazolamide"
    )
    
    print(f"Prediction successful: {result.success}")
    print(f"Output directory: {result.output_dir}")
    print(f"Generated files: {len(result.output_files)}")
    
    if result.success:
        print("Generated files:")
        for file_path in result.output_files:
            print(f"  - {file_path}")
    else:
        print(f"Error: {result.stderr[:300] if result.stderr else 'No error details'}")
    
    return result


async def example_multiple_drug_screening():
    """
    Example 2: Screen multiple drug candidates against a single protein target.
    
    This simulates a virtual drug screening scenario where you have multiple
    candidate molecules and want to predict their binding affinities.
    """
    print("\n=== Virtual Drug Screening Example ===")
    
    app = create_mcp_app()
    
    # Target protein: Human thrombin (coagulation factor IIa) - important for anticoagulants
    thrombin_sequence = """
    TFGSGEADCGLRPLFEKKSLEDKTERELLESYIDGRIVEGSDAEIGMSPWQVMLFRKSPQELL
    CGASLISDRWVLTAAHCLLYPPWDKNFTENDLLVRIGKHSRTRYERNIEKISMLEKIYIHPR
    YNWRENLDRDIALMKLKKPVAFSDYIHPVCLPDRETAASLLQAGYKGRVTGWGNLKETWTANV
    GKGQPSVLQVVNLPIVERPVCKDSTRIRITDNMFCAGYKPDEGKRGDACEGDSGGPFVMKSP
    FNNRWYQMGIVSWGEGCDRDGKYGFYTHVFRLKKWIQKVIDQFGE
    """
    
    # Drug candidates with their names and SMILES
    drug_candidates = [
        ("Warfarin", "CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O"),
        ("Dabigatran", "CCN(CC)CCCCNc1nc(N)c2nc(cnc2n1)c1ccc(cc1)C(=O)NC1CCCCC1"),
        ("Rivaroxaban", "Clc1ccc(cc1)c1oc(=O)c(C(=O)NC2CCC(=O)N2)c1c1cccnc1"),
        ("Aspirin", "CC(=O)Oc1ccccc1C(=O)O"),
    ]
    
    print(f"Screening {len(drug_candidates)} drug candidates against thrombin")
    print(f"Target protein length: {len(thrombin_sequence.replace(' ', '').replace('\n', ''))} residues")
    
    results = []
    
    for drug_name, drug_smiles in drug_candidates:
        print(f"\nTesting {drug_name}...")
        print(f"SMILES: {drug_smiles}")
        
        # Predict affinity for each drug
        result = app.predict_binding_affinity(
            protein_sequence=thrombin_sequence.replace(' ', '').replace('\n', ''),
            ligand_smiles=drug_smiles,
            output_dir=f"./predictions/drug_screening/{drug_name.lower()}"
        )
        
        results.append((drug_name, result))
        
        if result.success:
            print(f"✓ {drug_name}: Prediction completed")
        else:
            print(f"✗ {drug_name}: Prediction failed")
    
    # Summary of results
    print(f"\n=== Screening Results Summary ===")
    successful_predictions = sum(1 for _, result in results if result.success)
    print(f"Successful predictions: {successful_predictions}/{len(drug_candidates)}")
    
    for drug_name, result in results:
        if result.success:
            print(f"✓ {drug_name}: Files in {result.output_dir}")
        else:
            print(f"✗ {drug_name}: Failed")
    
    return results


async def example_advanced_affinity_config():
    """
    Example 3: Advanced affinity prediction using detailed configuration.
    
    This shows how to use the full AffinityPredictionRequest for more control
    over the prediction parameters.
    """
    print("\n=== Advanced Affinity Configuration Example ===")
    
    app = create_mcp_app()
    
    # Example: HIV protease with a protease inhibitor
    hiv_protease_sequence = """
    PQITLWQRPLVTIKIGGQLKEALLDTGADDTVLEEMSLPGRWKPKMIGGIGGFIKVRQYDQIL
    IEICGHKAIGTVLVGPTPVNIIGRNLLTQIGCTLNF
    """
    
    # Ritonavir - HIV protease inhibitor
    ritonavir_smiles = "CC(C)c1nc(cs1)CN(C)C(=O)NC(C(C)C)C(=O)NC(Cc1ccccc1)C(O)CC(CC(CC(=O)NC(C)(C)C)N(C)S(=O)(=O)c1ccc(N)cc1)c1ccccc1"
    
    print("Using advanced configuration for HIV protease - Ritonavir binding...")
    print(f"Protein length: {len(hiv_protease_sequence.replace(' ', '').replace('\n', ''))} residues")
    
    # Create advanced request with custom parameters
    advanced_request = AffinityPredictionRequest(
        protein_sequence=hiv_protease_sequence.replace(' ', '').replace('\n', ''),
        ligand_smiles=ritonavir_smiles,
        output_dir="./predictions/advanced_affinity/hiv_protease_ritonavir",
        devices=1,
        accelerator=None,  # Auto-detect
        recycling_steps=3,
        sampling_steps=200,  # Full sampling for better accuracy
        diffusion_samples=1,
        sampling_steps_affinity=200,  # Full affinity sampling
        diffusion_samples_affinity=5,  # Multiple affinity samples
        output_format="mmcif",
        override=True,  # Override existing results
        use_msa_server=True,
        affinity_mw_correction=True  # Use molecular weight correction
    )
    
    # Run advanced prediction
    result = app.predict_affinity(advanced_request)
    
    print(f"Advanced prediction successful: {result.success}")
    print(f"Output directory: {result.output_dir}")
    
    if result.success:
        print(f"Generated {len(result.output_files)} files:")
        for file_path in result.output_files:
            print(f"  - {file_path}")
        
        # The results should include:
        # - Protein-ligand complex structure
        # - Affinity prediction values
        # - Confidence scores
        print("\nLook for files containing:")
        print("  - Complex structure (.mmcif or .pdb)")
        print("  - Affinity predictions (.json or .txt)")
        print("  - Confidence scores")
    else:
        print(f"Error: {result.stderr[:300] if result.stderr else 'No error details'}")
    
    return result


async def example_config_based_affinity():
    """
    Example 4: Using YAML-style configuration for affinity prediction.
    
    This shows how to use the general predict_structure method with
    affinity-specific configuration similar to the Boltz examples.
    """
    print("\n=== Configuration-Based Affinity Prediction ===")
    
    app = create_mcp_app()
    
    # Example: Insulin receptor with a small molecule agonist
    insulin_receptor_sequence = """
    MATGGRRGAAAAPLLVAVAALLLGAAGHLYPGEVCPGMDIRNNLTRLHELENCSVIEGHLQIL
    LMFKTRPEDFRDLSFPKLIMITDYLLLFRVYGLESLKDLFPNLTVIRGSRLFFNYALVIFEM
    VHLKELGLYNLMNITRGSVRIEKNNELCYLATIDWSRILDSVEDNYIVLNKDDNEECGDICPG
    TKKPQFQYDHTFKDVREQAPKADEYEPYLFRLDKDIQEVDTDVDVDVPEDYEVQSTLGDVGN
    FSVLFRRRK
    """
    
    # A simple glucose analog
    glucose_analog_smiles = "OCC1OC(O)C(O)C(O)C1O"
    
    print("Using configuration-based approach...")
    
    # Create affinity configuration similar to boltz examples
    affinity_config = {
        "version": 1,
        "sequences": [
            {
                "protein": {
                    "id": "A",
                    "sequence": insulin_receptor_sequence.replace(' ', '').replace('\n', '')
                }
            },
            {
                "ligand": {
                    "id": "B",
                    "smiles": glucose_analog_smiles
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
    
    # Create prediction request
    config_request = PredictionRequest(
        input_data=affinity_config,
        output_dir="./predictions/config_affinity/insulin_glucose",
        model="boltz2",
        devices=1,
        recycling_steps=2,  # Reduced for faster demo
        sampling_steps=100,  # Reduced for faster demo
        diffusion_samples=1,
        output_format="mmcif"
    )
    
    # Run prediction
    result = app.predict_structure(config_request)
    
    print(f"Config-based prediction successful: {result.success}")
    
    if result.success:
        print(f"Output directory: {result.output_dir}")
        print(f"Generated {len(result.output_files)} files")
        print("Configuration used:")
        print(json.dumps(affinity_config, indent=2))
    else:
        print(f"Error: {result.stderr[:300] if result.stderr else 'No error details'}")
    
    return result


async def check_system_status():
    """Check if the system is ready for affinity predictions."""
    print("=== System Status Check ===")
    
    app = create_mcp_app()
    status = app.check_status()
    
    print(f"Boltz installed: {status['boltz_installed']}")
    print(f"Torch available: {status['torch_available']}")
    print(f"GPU available: {status['gpu_available']}")
    print(f"Detected accelerator: {status['detected_accelerator']}")
    
    if status['gpu_available']:
        print(f"GPU count: {status.get('gpu_count', 'N/A')}")
        print(f"GPU name: {status.get('gpu_name', 'N/A')}")
    
    if not status['boltz_installed']:
        print("\n⚠️  Warning: Boltz is not installed!")
        print("Install with: pip install boltz")
        return False
    
    print("✅ System ready for affinity predictions!")
    return True


async def main():
    """Run all drug-protein affinity prediction examples."""
    print("Drug-Protein Affinity Prediction Examples")
    print("Using Boltz-2 Model via MCP Server")
    print("=" * 50)
    
    # Check system status first
    system_ready = await check_system_status()
    
    if not system_ready:
        print("\nSkipping prediction examples due to missing dependencies.")
        return
    
    print("\n" + "=" * 50)
    print("Running affinity prediction examples...\n")
    
    try:
        # Example 1: Basic affinity prediction
        await example_basic_drug_protein_affinity()
        
        # Example 2: Multiple drug screening
        await example_multiple_drug_screening()
        
        # Example 3: Advanced configuration
        await example_advanced_affinity_config()
        
        # Example 4: Config-based approach
        await example_config_based_affinity()
        
    except Exception as e:
        print(f"\nError during prediction: {e}")
        print("This might be due to:")
        print("1. Boltz model not downloaded (runs automatically on first use)")
        print("2. Insufficient GPU memory")
        print("3. Network issues when downloading models")
        print("4. Invalid protein sequence or SMILES string")
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("\nGenerated predictions are saved in the './predictions/' directory")
    print("Each prediction includes:")
    print("  - 3D structure of protein-ligand complex")
    print("  - Binding affinity prediction")
    print("  - Confidence scores")
    print("  - Log files with detailed information")


if __name__ == "__main__":
    asyncio.run(main()) 