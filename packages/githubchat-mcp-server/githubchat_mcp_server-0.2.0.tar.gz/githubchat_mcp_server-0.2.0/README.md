# GitHubChat MCP Server

Model Context Protocol (MCP) server for GitHub Chat.

## Installation

```bash
pip install githubchat-mcp-server
```

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

## Tools

### githubchat_completion

Main tool that accepts query and GitHub URL parameters.

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

Supported GitHub URL formats:
- Repository URLs (e.g., `https://github.com/username/repo`)
- File URLs (e.g., `https://github.com/username/repo/blob/main/file.md`)
- Branch URLs (e.g., `https://github.com/username/repo/tree/feat/branch`)
- Wiki URLs (e.g., `https://github.com/username/repo/wiki`)

## License

All rights reserved, [Bluera Inc.](https://bluera.ai).
