# boltz-mcp

MCP (Model Context Protocol) server for Boltz-2 protein structure prediction model.

## Overview

This MCP server provides tools for protein structure prediction using the state-of-the-art Boltz-2 model. It enables you to:

- Predict single protein structures from amino acid sequences
- Predict protein complexes and multimers
- Predict protein-ligand interactions
- Use custom multiple sequence alignments (MSAs)
- Handle cyclic peptides
- Configure various prediction parameters

## Features

### Tools Available

1. **`boltz_predict_structure`** - Main prediction tool with full configuration options
2. **`boltz_predict_from_sequences`** - Simple sequence-to-structure prediction
3. **`boltz_check_status`** - Check Boltz installation status
4. **`boltz_get_examples`** - Get example configurations for different prediction types

### Resources Available

- **`resource://boltz-usage-guide`** - Comprehensive usage guide and documentation

## Installation

### Prerequisites

#### System Dependencies

Before installing the Python packages, you need to install system dependencies required for building scientific Python packages:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y cmake build-essential gfortran
```

**CentOS/RHEL/Fedora:**
```bash
# For CentOS/RHEL
sudo yum install cmake gcc-gfortran gcc-c++ make
# For Fedora
sudo dnf install cmake gcc-gfortran gcc-c++ make
```

**macOS:**
```bash
# Install Xcode Command Line Tools if not already installed
xcode-select --install
# Install gfortran (via Homebrew)
brew install gcc cmake
```

**Note:** These system dependencies are required because some Python packages (like SciPy) need to be compiled from source when using uv, and they require:
- `cmake`: For building dm-tree and other native extensions
- `gfortran`: For building SciPy from source
- `build-essential`/`gcc-c++`: For general C/C++ compilation

#### Python Dependencies

1. Install the Boltz-2 model:
   ```bash
   pip install boltz
   ```

2. Install this MCP server:
   ```bash
   cd boltz-mcp
   uv pip install -e .
   ```

### GPU Requirements

Boltz-2 works best with GPU acceleration. Ensure you have:
- CUDA-compatible GPU
- PyTorch with CUDA support
- Sufficient GPU memory (8GB+ recommended)

## Usage

### Running with uvx

You do not have to copy anything, just use uvx and it will install and run the MCP.
Note: the download can take a lot because of evil CUDA dependencies.

```bash
uvx --python 3.12 boltz-mcp stdio
```


### Running the Server localy

Clone the repo and run with uv
```bash
gh repo clone longevity-genie/boltz-mcp
cd boltz-mcp
# or
uv run boltz-mcp
```


### Inspecting the Boltz MCP Server

<details>
<summary>Using MCP Inspector to explore server capabilities</summary>

If you want to inspect the methods provided by the MCP server, use npx (you may need to install nodejs and npm):

For STDIO mode:
```bash
npx @modelcontextprotocol/inspector --config mcp-config-local.json --server boltz-mcp
```

For local stdio mode:
```bash
npx @modelcontextprotocol/inspector --config mcp-config-local.json --server boltz-mcp
```

You can also run the inspector manually and configure it through the interface:
```bash
npx @modelcontextprotocol/inspector
```

After that you can explore the tools and resources with MCP Inspector at http://127.0.0.1:6274 (note, if you run inspector several times it can change port, also use the url that includes proxy token when possible)

</details>

*Note: Using the MCP Inspector is optional. Most MCP clients (like Cursor, Windsurf, Claude Desktop, etc.) will automatically display the available tools from this server once configured. However, the Inspector can be useful for detailed testing and exploration.*

*If you choose to use the Inspector via `npx`, ensure you have Node.js and npm installed. Using [nvm](https://github.com/nvm-sh/nvm) (Node Version Manager) is recommended for managing Node.js versions.*

### Example Usage

#### Simple Protein Structure Prediction

```python
# Using the boltz_predict_from_sequences tool
{
    "sequences": {
        "sequences": {
            "protein1": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
        }
    },
    "output_dir": "./predictions",
    "model": "boltz2"
}
```

#### Protein Complex Prediction

```python
# Using the boltz_predict_structure tool
{
    "input_data": {
        "sequences": {
            "chain_A": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
            "chain_B": "ARNDCEQGHILKMFPSTWYV"
        }
    },
    "model": "boltz2",
    "devices": 1,
    "accelerator": "gpu",
    "sampling_steps": 200,
    "diffusion_samples": 1,
    "output_format": "mmcif"
}
```

#### Advanced Configuration

```python
{
    "input_data": {
        "sequences": ["protein.fasta"],
        "job_name": "my_prediction",
        "pdb_id": "1ABC",  # Template structure
        "msa": ["custom.a3m"],  # Custom MSA
        "ligands": ["ligand.sdf"]  # Ligands
    },
    "model": "boltz2",
    "devices": 2,
    "recycling_steps": 5,
    "sampling_steps": 300,
    "use_msa_server": true,
    "override": false
}
```

## Input Formats

### Sequences
- Amino acid sequences as strings
- FASTA files (specify file paths)
- Multiple sequences for complexes

### Configuration Files
- YAML format configurations
- Support for MSA files (.a3m format)
- Ligand files (.sdf format)
- Template PDB structures

## Output

The server returns:
- Success status
- List of generated output files
- Output directory path
- Command executed
- Standard output/error from Boltz

Output files include:
- Predicted structures (.pdb or .mmcif)
- Confidence scores
- Error estimates (PAE, PDE)

## Parameters

### Core Parameters
- `model`: "boltz1" or "boltz2" (default: "boltz2")
- `devices`: Number of GPU devices (default: 1)
- `accelerator`: "gpu", "cpu", or "tpu" (default: "gpu")

### Sampling Parameters
- `recycling_steps`: Number of recycling iterations (default: 3)
- `sampling_steps`: Diffusion sampling steps (default: 200)
- `diffusion_samples`: Number of samples to generate (default: 1)

### Output Parameters
- `output_format`: "pdb" or "mmcif" (default: "mmcif")
- `output_dir`: Where to save results

### Advanced Options
- `use_msa_server`: Use online MSA generation
- `override`: Override existing predictions
- `step_scale`: Control sampling temperature

## Error Handling

The server handles various error conditions:
- Missing Boltz installation
- Invalid input sequences
- GPU memory issues
- Timeout for long predictions (1 hour limit)

Check the `boltz_check_status` tool to verify installation.

## Known Issues

### Dependency Version Conflicts

The Boltz-2 developers have unfortunately pinned minor versions of several critical libraries in their dependency specifications, which can lead to significant compatibility issues:

- **Python 3.13 Incompatibility**: The strict version pinning prevents Boltz-2 from working with Python 3.13, forcing users to downgrade to older Python versions
- **Excessive CUDA Downloads**: The pinned versions often trigger unnecessary downloads of large CUDA-related packages and dependencies, even when compatible versions are already installed
- **Environment Conflicts**: The rigid dependency constraints can conflict with other packages in your environment, making it difficult to use Boltz-2 alongside other scientific computing tools

**Workarounds**:
- Use Python 3.11 or 3.12 instead of 3.13
- Consider using isolated environments (conda, venv, or uv) to minimize conflicts
- Be prepared for potentially long installation times due to CUDA package downloads

These issues stem from upstream dependency management decisions in the Boltz-2 package and are beyond the scope of this MCP server.

## Development

### Project Structure
```
boltz-mcp/
├── src/
│   └── boltz_mcp/
│       ├── __init__.py
│       └── server.py
├── pyproject.toml
└── README.md
```

### Dependencies
- fastmcp: MCP server framework
- pydantic: Data validation
- eliot: Structured logging
- PyTorch: Deep learning framework
- RDKit: Chemical informatics
- Other scientific computing libraries

## License

This project follows the same license as the original Boltz-2 model.

## Contributing

Contributions are welcome! Please submit issues and pull requests on the project repository.

## Support

For issues related to:
- Boltz-2 model: Check the official Boltz-2 documentation
- MCP protocol: Check the MCP specification
- This server: Submit issues to this repository
