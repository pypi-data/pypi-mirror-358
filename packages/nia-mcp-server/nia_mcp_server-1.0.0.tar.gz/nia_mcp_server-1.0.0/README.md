# NIA MCP Server

The NIA MCP Server enables AI assistants like Claude to search and understand your indexed codebases through the Model Context Protocol (MCP).

## Quick Start

### 1. Get your NIA API Key

Sign up and get your API key at [https://trynia.ai/api-keys](https://trynia.ai/api-keys)

### 2. Install via pip

```bash
pip install nia-mcp-server
```

### 3. Configure with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "nia": {
      "command": "nia-mcp-server",
      "env": {
        "NIA_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### 4. Restart Claude Desktop

That's it! You can now ask Claude to index and search codebases.

## Usage Examples

### Index a repository
```
Claude, please index https://github.com/facebook/react
```

### Index documentation
```
Index the documentation at https://docs.python.org
```

### Search across everything
```
How does async/await work? Search both my code and documentation.
```

### Search only repositories
```
Find the authentication logic in my repositories
```

### Search only documentation
```
What are the best practices for error handling according to the docs?
```

### List your resources
```
Show me all my indexed repositories and documentation
```

## Available Tools

### Repository Management
- **`index_repository`** - Index a GitHub repository
- **`list_repositories`** - List all indexed repositories
- **`check_repository_status`** - Check repository indexing progress
- **`delete_repository`** - Remove an indexed repository

### Documentation Management
- **`index_documentation`** - Index documentation or any website
- **`list_documentation`** - List all indexed documentation sources
- **`check_documentation_status`** - Check documentation indexing progress
- **`delete_documentation`** - Remove indexed documentation

### Unified Search
- **`search_codebase`** - Search across repositories and/or documentation
  - `search_mode`: "repositories", "sources", or "unified" (default)
  - Automatically searches all indexed content if not specified

## Other MCP Clients

### Continue.dev

Add to your `~/.continue/config.json`:

```json
{
  "models": [...],
  "mcpServers": [
    {
      "name": "nia",
      "command": "nia-mcp-server",
      "env": {
        "NIA_API_KEY": "your-api-key-here"
      }
    }
  ]
}
```

### VS Code Cline

Add to your Cline settings:

```json
{
  "mcpServers": {
    "nia": {
      "command": "nia-mcp-server",
      "env": {
        "NIA_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Environment Variables

- `NIA_API_KEY` (required) - Your NIA API key
- `NIA_API_URL` (optional) - API endpoint (defaults to https://api.trynia.ai)

## Pricing

NIA offers simple, transparent pricing:

- **Free Tier**: Limited usage, public repos only
- **Pro**: Unlimited API calls, private repos, advanced features

See [https://trynia.ai/pricing](https://trynia.ai/pricing) for details.

## Features

- 🔍 **Unified Search** - Search across code AND documentation seamlessly
- 📚 **Documentation Indexing** - Index any website or documentation
- 🚀 **Fast Indexing** - Index repositories and websites quickly
- 🔒 **Private Repos** - Support for private repositories (Pro)
- 📊 **Smart Understanding** - AI-powered code and content comprehension
- 🌐 **Works Everywhere** - Any MCP-compatible client

## Troubleshooting

### "No API key provided"
Make sure `NIA_API_KEY` is set in your MCP client configuration.

### "Invalid API key"
Check your API key at [https://trynia.ai/api-keys](https://trynia.ai/api-keys)

### "Rate limit exceeded"
You've hit your monthly limit. Upgrade at [https://trynia.ai/billing](https://trynia.ai/billing)

### Repository not indexing
Large repositories can take a few minutes. Use `check_repository_status` to monitor progress.

## Support

- Documentation: [https://docs.trynia.ai](https://docs.trynia.ai)
- Discord: [https://discord.gg/trynia](https://discord.gg/trynia)
- Email: support@trynia.ai

## License

MIT License - see LICENSE file for details.