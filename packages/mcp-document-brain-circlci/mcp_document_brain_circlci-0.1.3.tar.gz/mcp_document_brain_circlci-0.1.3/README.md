# MCP Document Reader

An MCP server that can extract text from document files.

## Installation

```bash
pip install mcp-document-brain
```

## Usage

### With Claude Desktop

1. Install the package: `pip install mcp-document-brain`
2. Run: `mcp install mcp-document-brain`
3. Restart Claude Desktop

### With Cursor

Add the following to your `~/.cursor/mcp.json` file:

```json
{
    "mcpServers": {
        "document-reader-mcp": {
            "command": "mcp-document-brain"
        }
    }
}
```

## Features

- Extract text from PDF files
- Extract text from DOCX files
- Access documents from your Recent folder

## Development

1. Clone the repository
2. Install development dependencies: `uv add --dev -e .`
3. Run tests: `pytest`
```