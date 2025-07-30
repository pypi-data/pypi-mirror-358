PLSDB MCP Server

Model Context Protocol server for interacting with the PLSDB (Plasmid Database) API.
This server provides tools to search, filter, and retrieve plasmid data from PLSDB.

## Installation

### From PyPI (Recommended)

```bash
pip install plsdb-mcp
```

### From Source

```bash
git clone <repository-url>
cd PLSDBmcp
pip install -e .
```

## Usage

### Command Line

After installation, you can run the MCP server using:

```bash
plsdb-mcp
```

### MCP Configuration

Add this to your MCP configuration file:

```json
{
  "mcpServers": {
    "plsdb": {
      "command": "plsdb-mcp",
      "args": []
    }
  }
}
```

## Available Tools

The PLSDB MCP server provides the following tools:

### Plasmid Information
- **get_plasmid_summary**: Get plasmid summary information for a given NUCCORE_ACC

### FASTA Downloads
- **start_fasta_download**: Start preparing FASTA download for multiple plasmid accessions
- **get_fasta_download**: Get results from FASTA download job

### Sequence Search
- **start_sequence_search**: Start sequence search in PLSDB using various search methods
- **get_sequence_search_results**: Get results from sequence search job

### Filtering
- **filter_plasmids_by_nuccore**: Filter PLSDB plasmids based on nuccore attributes
- **filter_plasmids_by_biosample**: Filter PLSDB plasmids based on biosample attributes
- **filter_plasmids_by_taxonomy**: Filter PLSDB plasmids based on taxonomy attributes

## API Endpoints

The server connects to the PLSDB API at: `https://ccb-microbe.cs.uni-saarland.de/plsdb2025/api`

## Requirements

- Python 3.8 or higher
- mcp >= 1.0.0
- aiohttp >= 3.8.0

## Development

### Setup Development Environment

```bash
git clone <repository-url>
cd PLSDBmcp
pip install -e ".[dev]"
```

### Running Tests

```bash
python -m pytest
```

### Building Package

```bash
python -m build
```

## Claude integration

inlcude following in your Claude app:
```json
{
  "mcpServers": {
    "plsdb": {
      "command": "plsdb-mcp",
      "env": {}
    }
  }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions, please open an issue on the GitHub repository.
