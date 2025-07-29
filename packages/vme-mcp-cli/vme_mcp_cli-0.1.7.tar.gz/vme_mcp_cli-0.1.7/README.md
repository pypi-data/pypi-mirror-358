# VME MCP CLI

Rich terminal chat interface for VME infrastructure management with voice support.

## Installation

### From PyPI (Coming Soon)

```bash
# Basic installation
pip install vme-mcp-cli

# With audio support
pip install "vme-mcp-cli[audio]"
```

### From Source (Current Method)

```bash
# Clone the repository
git clone https://github.com/frippe75/vme-fastmcp-server-v2.git
cd vme-fastmcp-server-v2

# Install with uv
uv pip install -e packages/vme-mcp-cli

# Or with pip
pip install -e packages/vme-mcp-cli
```

### Server Package

The `vme-mcp-server` package is not yet available on PyPI. For local server usage, install from source:

```bash
uv pip install -e packages/vme-mcp-server
```

## Quick Start

```bash
# First time setup - create config
vme-mcp-cli config

# Set your API credentials
export VME_API_BASE_URL=https://your-vme.com
export VME_API_TOKEN=your-token
export ANTHROPIC_API_KEY=your-anthropic-key

# Start the chat interface
vme-mcp-cli
```

## Configuration

Config file location:
- Linux/Mac: `~/.config/vme-cli/config.yaml`
- Windows: `%APPDATA%\vme-cli\config.yaml`

### Using a Remote Server

Edit your config to use HTTP transport:

```yaml
server:
  servers:
    vme:
      transport: http
      path_or_url: http://your-server:8080
```

Or use the config command:
```bash
vme-mcp-cli config --server-transport http --server-url http://your-server:8080
```

## Features

- 🎨 Rich terminal interface with GitHub-inspired theme
- 💬 Natural language infrastructure management
- 🎙️ Voice commands and responses (optional)
- 🔧 Progressive tool discovery
- 📊 Real-time operation status
- 🔒 Secure credential handling

## Usage Examples

```
# In the chat interface:
> What tools are available?
> List all VMs
> Create a VM called web-server-01
> Show me the appliance settings
```

## Requirements

- Python 3.10+
- Anthropic API key (for Claude)
- OpenAI API key (for voice features)
- VME/Morpheus API credentials