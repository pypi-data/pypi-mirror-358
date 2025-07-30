# Drug-Protein Affinity Prediction Example

This example demonstrates how to predict binding affinity between drugs (in SMILES format) and proteins using the Boltz-2 model through the MCP server.

## Overview

The Boltz-2 model can predict both:
1. **3D structure** of protein-ligand complexes
2. **Binding affinity** between proteins and small molecules
3. **Confidence scores** for the predictions

## Examples Included

### 1. Basic Affinity Prediction
- Simple drug-protein binding prediction
- Uses acetazolamide (glaucoma drug) with carbonic anhydrase II
- Demonstrates the `predict_binding_affinity()` method

### 2. Virtual Drug Screening
- Screen multiple drug candidates against a single target
- Uses thrombin (blood clotting protein) with anticoagulant drugs
- Compares: Warfarin, Dabigatran, Rivaroxaban, and Aspirin

### 3. Advanced Configuration
- Full control over prediction parameters
- HIV protease with Ritonavir (HIV drug)
- Uses `AffinityPredictionRequest` for detailed settings

### 4. Configuration-Based Approach
- YAML-style configuration similar to Boltz examples
- Insulin receptor with glucose analog
- Uses the general `predict_structure()` method

## Real Drug Examples Used

| Drug | Target Protein | Condition | SMILES |
|------|----------------|-----------|---------|
| Acetazolamide | Carbonic Anhydrase II | Glaucoma | `CC(=O)Nc1nnc(s1)S(=O)(=O)N` |
| Warfarin | Thrombin | Blood clots | `CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O` |
| Ritonavir | HIV Protease | HIV | Complex molecule |
| Glucose analog | Insulin Receptor | Diabetes | `OCC1OC(O)C(O)C(O)C1O` |

## Prerequisites

1. **Install Boltz**: `pip install boltz`
2. **Install MCP server**: Already included in this project
3. **GPU recommended** (but CPU works too, just slower)
4. **Internet connection** for first-time model download (~2GB)

## Running the Examples

```bash
# Run all examples
cd examples
python drug_protein_affinity_example.py

# Or use uv (recommended)
uv run examples/drug_protein_affinity_example.py
```

## Output Files

Each prediction generates:
- **Structure files**: `.mmcif` or `.pdb` format with 3D coordinates
- **Affinity predictions**: Binding energy estimates
- **Confidence scores**: Reliability metrics
- **Log files**: Detailed prediction information

Example output structure:
```
predictions/
├── drug_affinity/acetazolamide/
│   ├── boltz_results_*/
│   │   ├── prediction_*.mmcif
│   │   ├── affinity_*.json
│   │   └── confidence_*.json
├── drug_screening/warfarin/
├── advanced_affinity/hiv_protease_ritonavir/
└── config_affinity/insulin_glucose/
```

## Understanding Results

### Binding Affinity
- Measured in **kcal/mol** or **pKd/pIC50** units
- Lower values = stronger binding
- Typical range: -15 to +5 kcal/mol

### Confidence Scores
- Range: 0-100
- Higher = more reliable prediction
- Consider results with confidence >70 as reliable

### Structure Quality
- Look for reasonable protein-ligand contacts
- Check for proper binding pose geometry
- Validate against known crystal structures if available

## Tips for Best Results

1. **Protein sequences**: Use canonical sequences from UniProt
2. **SMILES strings**: Validate with chemical databases (ChEMBL, PubChem)
3. **GPU memory**: Reduce `sampling_steps` if you get memory errors
4. **Multiple runs**: Use `diffusion_samples_affinity=5` for better statistics
5. **Comparison**: Always compare with known experimental data when available

## Troubleshooting

### Common Issues
- **Model download**: First run downloads ~2GB (automatic)
- **GPU memory**: Reduce `sampling_steps` or use CPU
- **Invalid SMILES**: Validate molecule structure first
- **Long sequences**: May need more GPU memory or longer runtime

### Performance Notes
- **GPU**: ~5-15 minutes per prediction
- **CPU**: ~30-60 minutes per prediction  
- **Memory**: 4-8GB GPU recommended, 16GB+ RAM for CPU

## Using with Claude MCP

This example can also be used through Claude with the MCP interface:

```python
# Through MCP tools
mcp_boltz_predict_binding_affinity(
    protein_sequence="YOUR_PROTEIN_SEQUENCE",
    ligand_smiles="YOUR_SMILES_STRING"
)
```

## Further Reading

- [Boltz-2 Paper](https://arxiv.org/abs/2411.14494)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [SMILES Format Guide](https://daylight.com/dayhtml/doc/theory/theory.smiles.html)
- [UniProt Database](https://www.uniprot.org/) 