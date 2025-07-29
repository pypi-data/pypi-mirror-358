# VME MCP CLI

Rich terminal chat interface for VME infrastructure management with voice support.

## Installation

```bash
# Basic installation
pip install vme-mcp-cli

# With audio support for voice commands
pip install "vme-mcp-cli[audio]"
```

## MCP Server Setup

The VME MCP CLI requires an MCP server to communicate with your VME/Morpheus infrastructure.

### Option 1: Local Server (Recommended for development)

```bash
# Install the server package from source
git clone https://github.com/frippe75/vme-fastmcp-server-v2.git
cd vme-fastmcp-server-v2
pip install -e packages/vme-mcp-server

# The server will be started automatically by the CLI
```

### Option 2: Remote Server

If you have a remote MCP server running, configure it in your config file:

```yaml
server:
  servers:
    vme:
      transport: http
      path_or_url: http://your-server:8080
```

## Quick Start

```bash
# 1. Create default configuration
vme-mcp-cli config

# 2. Set your API credentials
export VME_API_BASE_URL=https://your-vme.com/api
export VME_API_TOKEN=your-token
export ANTHROPIC_API_KEY=your-anthropic-key
export OPENAI_API_KEY=your-openai-key  # Optional: for voice features

# 3. Start the chat interface
vme-mcp-cli

# Or with debug output
vme-mcp-cli --debug-level 3
```

## Configuration

Config file location:
- Linux/Mac: `~/.config/vme-cli/config.yaml`
- Windows: `%APPDATA%\vme-cli\config.yaml`

### Default Configuration

```yaml
llm:
  anthropic_key: ${ANTHROPIC_API_KEY}
  default_provider: anthropic
  default_model: claude-3-5-sonnet-20241022

server:
  servers:
    vme:
      name: "vme"
      transport: "stdio"
      command: "vme-mcp-server"  # Requires server package installed
      env:
        VME_API_BASE_URL: ${VME_API_BASE_URL}
        VME_API_TOKEN: ${VME_API_TOKEN}
        VME_LAZY_LOADING: "true"  # Fast startup with on-demand tool loading

audio:
  enabled: false
  voice: "alloy"  # OpenAI voice options: alloy, echo, fable, onyx, nova, shimmer

ui:
  theme: github_dark
  show_thinking_indicator: true
```

### Environment Variables

The CLI supports environment variable substitution in the config file:

```bash
# Required
VME_API_BASE_URL=https://your-vme.com/api
VME_API_TOKEN=your-api-token
ANTHROPIC_API_KEY=your-anthropic-key

# Optional
OPENAI_API_KEY=your-openai-key  # For voice features
VME_LAZY_LOADING=true           # Control server startup behavior
VME_PRELOAD_GROUPS=compute      # Preload specific tool groups
```

## Features

- 🎨 **Rich Terminal Interface** - GitHub-inspired dark theme with syntax highlighting
- 💬 **Natural Language Processing** - Chat with your infrastructure using plain English
- 🎙️ **Voice Commands** - Speak to manage VMs (requires OpenAI API key)
- 🔧 **Progressive Tool Discovery** - Start with 18 tools, unlock 500+ on demand
- 📊 **Real-time Status** - Visual indicators for thinking, speaking, and operations
- 🔒 **Secure Credentials** - Environment variables and encrypted config support
- ⚡ **Lazy Loading** - 70% faster startup with on-demand tool creation
- 🤖 **Multi-LLM Support** - Works with Anthropic Claude and OpenAI GPT

## Usage Examples

### Basic Commands
```
> What tools are available?
> Show me the appliance settings
> Get current license information
```

### VM Management
```
> List all VMs
> Create a VM called web-server-01
> Show me VMs in zone tc-lab
> Delete VM with ID 123
```

### Progressive Discovery
```
> Discover compute infrastructure    # Unlocks 40+ VM tools
> Discover networking capabilities   # Unlocks network tools
> Discover storage capabilities      # Unlocks storage tools
```

### Advanced Operations
```
> Create a Ubuntu 22.04 VM with 4 CPUs and 8GB RAM
> Show me all available instance types
> What virtual images are available?
> Help me create a web server with specific requirements
```

## Requirements

- Python 3.10+
- Anthropic API key (for Claude LLM)
- VME/Morpheus API credentials (URL and token)
- OpenAI API key (optional, for voice features)
- PortAudio (optional, for microphone support)

## Audio Setup (Optional)

For voice command support:

**Ubuntu/Debian:**
```bash
sudo apt-get install portaudio19-dev
pip install "vme-mcp-cli[audio]"
```

**Fedora/RHEL:**
```bash
sudo dnf install portaudio-devel
pip install "vme-mcp-cli[audio]"
```

**macOS:**
```bash
brew install portaudio
pip install "vme-mcp-cli[audio]"
```

## Troubleshooting

### "MCP server not found" Error

If you see this error, install the server package:
```bash
git clone https://github.com/frippe75/vme-fastmcp-server-v2.git
cd vme-fastmcp-server-v2
pip install -e packages/vme-mcp-server
```

### Audio Not Working

1. Ensure PortAudio is installed (see Audio Setup above)
2. Set your OpenAI API key: `export OPENAI_API_KEY=your-key`
3. Enable audio in config: `audio.enabled: true`
4. Check microphone permissions

## Links

- [GitHub Repository](https://github.com/frippe75/vme-fastmcp-server-v2)
- [Contributing Guide](https://github.com/frippe75/vme-fastmcp-server-v2/blob/master/CONTRIBUTING.md)
- [VME Infrastructure Guide](https://github.com/frippe75/vme-fastmcp-server-v2/blob/master/docs/vme-infrastructure-guide.md)
- [Report Issues](https://github.com/frippe75/vme-fastmcp-server-v2/issues)

## License

Private repository - Internal use only.