# GitHubChat MCP Server

Model Context Protocol (MCP) server for GitHub Chat.

## Get Started

### I have an MCP Client (eg. Cursor, Claude, Cline)

Run in terminal: 
```sh
pip install githubchat-mcp-server && githubchat-mcp-server
```

Add `githubchat` server to your client's MCP configuration, commonly:

```py
{
    "mcpServers": {
        "githubchat": {
            "url": "http://localhost:4651/githubchat-mcp"
        }
    }
}
```

> Refer to your MCP client's documentation for supported configuration specifications.

### I don't have an MCP Client

> Looking to get an existing one? See [Awesome MCP Client](https://github.com/punkpeye/awesome-mcp-clients)

Example request using FastMCP client:

```python
import asyncio
from fastmcp import Client
import json

async def main():
    # Connect to the MCP server
    async with Client("http://localhost:4651/githubchat-mcp") as client:
        # Request completion
        print("\nRequesting completion...\n\n")
        result = await client.call_tool("githubchat_completion", {
            "query": "your query",
            "url": "https://github.com/username/repo"
        })
        print(json.dumps(json.loads(result[0].text), indent=2))

if __name__ == "__main__":
    asyncio.run(main())
```

## Documentation

### Install

```bash
pip install githubchat-mcp-server
```

### Run 
After installation, you can run the server in two ways:

1. Using the command-line script:
```bash
# Default port (4651)
githubchat-mcp-server

# Custom port
githubchat-mcp-server --port 3000
```

2. Using Python directly:
```bash
# Default port (4651)
python -m githubchat_mcp_server

# Custom port
python -m githubchat_mcp_server --port 3000
```

The server will run on localhost using streamable-http transport.

### Available Tools

#### githubchat_completion

Main tool that accepts query and GitHub URL parameters.

Supported GitHub URL formats:
- Repository URLs (e.g., `https://github.com/username/repo`)
- File URLs (e.g., `https://github.com/username/repo/blob/main/file.md`)
- Branch URLs (e.g., `https://github.com/username/repo/tree/feat/branch`)
- Wiki URLs (e.g., `https://github.com/username/repo/wiki`)

## License

All rights reserved, [Bluera Inc.](https://bluera.ai).
