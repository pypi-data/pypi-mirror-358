# amcp - automcp.ai SDK

[![PyPI version](https://badge.fury.io/py/amcp.svg)](https://badge.fury.io/py/amcp)
[![Python Versions](https://img.shields.io/pypi/pyversions/amcp.svg)](https://pypi.org/project/amcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Python SDK for [automcp.ai](https://automcp.ai) - Generate Model Context Protocol servers intelligently

## 🚧 Development Status

**This package is currently a placeholder.** The full SDK implementation is under active development.

For now, please visit [automcp.ai](https://automcp.ai) for more information.

## Installation

```bash
pip install amcp
```

## What is automcp.ai?

automcp.ai is a tool that automatically generates MCP (Model Context Protocol) servers from OpenAPI specifications. It enables Large Language Models to interact with APIs through a standardized protocol, selecting only the most relevant endpoints based on your use cases.

## Planned Features

- **Programmatic Server Generation**: Generate MCP servers from Python code
- **Smart Endpoint Selection**: Automatically select relevant endpoints based on use cases
- **Authentication Support**: Handle various authentication methods

## Example (Coming Soon)

```python
import amcp

# Generate an MCP server from an OpenAPI spec
amcp.generate_server(
    openapi_spec="path/to/openapi.yaml",
    output_dir="./my-mcp-server",
    use_cases=[
        "Search for repositories",
        "Create and manage issues",
        "Review pull requests"
    ]
)
```

## Links

- [automcp.ai Website](https://automcp.ai)
- [Documentation](https://github.com/automcp-ai/amcp/docs)
- [Issue Tracker](https://github.com/automcp-ai/amcp/issues)

## License

MIT License - see [LICENSE](LICENSE) file for details.
