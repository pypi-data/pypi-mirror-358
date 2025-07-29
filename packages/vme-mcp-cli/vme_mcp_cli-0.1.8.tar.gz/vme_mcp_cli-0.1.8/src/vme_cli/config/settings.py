"""
Simplified configuration system for VME Textual CLI Client
"""

import os
import platform
import sys
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any

@dataclass
class LLMConfig:
    """LLM provider configuration"""
    anthropic_key: Optional[str] = None
    openai_key: Optional[str] = None
    default_provider: str = "anthropic"
    default_model: str = "claude-3-5-sonnet-20241022"

@dataclass
class MCPServerConfig:
    """Individual MCP server configuration"""
    name: str
    transport: str  # "stdio" or "http"
    path_or_url: str  # Script path for stdio, URL for http
    timeout: int = 30
    auto_connect: bool = True
    enabled: bool = True
    env: Optional[Dict[str, str]] = None  # Environment variables for stdio transport

@dataclass  
class ServerConfig:
    """MCP servers configuration"""
    servers: Dict[str, MCPServerConfig] = field(default_factory=lambda: {
        "vme": MCPServerConfig(
            name="vme",
            transport="stdio", 
            path_or_url="vme-mcp-server",
            auto_connect=True
        )
    })
    default_timeout: int = 30

@dataclass
class AudioConfig:
    """Audio configuration for OpenAI Realtime API"""
    enabled: bool = False
    mode: str = "input_only"  # "full_conversation", "input_only", "transcribe_only"
    use_dedicated_transcription_api: bool = True
    transcription_model: str = "gpt-4o-transcribe"
    sample_rate: int = 24000
    channels: int = 1
    chunk_size: int = 1024
    input_device: Optional[int] = None
    output_device: Optional[int] = None
    model: str = "gpt-4o-realtime-preview-2024-10-01"
    voice: str = "alloy"
    vad_threshold: float = 0.3
    vad_prefix_padding_ms: int = 300
    vad_silence_duration_ms: int = 200
    auto_submit_on_speech_end: bool = True
    show_transcription_in_input: bool = True
    noise_reduction: str = "near_field"
    instructions: str = (
        "You are a helpful assistant for VME infrastructure management. "
        "Keep responses conversational and concise for audio output. "
        "When the user asks about infrastructure, provide brief spoken summaries "
        "while detailed information will be handled separately via text."
    )
    structured_response_prompt: str = (
        "Always respond in this JSON format:\n"
        "{\n"
        '  "content": "Your response with full information, tool results, and explanations"\n'
        "}\n"
    )
    audio_enhancement_prompt: str = (
        "Since audio is enabled, also include a 'tts_text' field with a brief conversational summary (1-2 sentences) suitable for text-to-speech:\n"
        "{\n"
        '  "content": "Your detailed technical response",\n'
        '  "tts_text": "Brief conversational summary that sounds natural when spoken aloud"\n'
        "}\n"
    )

@dataclass
class UIConfig:
    """UI appearance and behavior"""
    theme: str = "github_dark"
    show_thinking_indicator: bool = True
    max_message_history: int = 1000
    audio_visualizer: bool = True
    fft_bars: int = 8

def get_default_config_dir() -> Path:
    """Get the default configuration directory for the current OS"""
    app_name = "vme-cli"
    
    system = platform.system()
    if system == "Windows":
        config_dir = Path(os.environ.get("APPDATA", "")) / app_name
    else:  # Linux, macOS
        config_dir = Path.home() / ".config" / app_name
    
    return config_dir

def get_default_config_file() -> Path:
    """Get the default configuration file path"""
    return get_default_config_dir() / "config.yaml"

@dataclass
class ClientConfig:
    """Main client configuration"""
    llm: LLMConfig = field(default_factory=LLMConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    debug: bool = False
    debug_level: int = 0
    
    def __init__(self, config_file: str = None, **kwargs):
        # Initialize with defaults
        self.llm = LLMConfig()
        self.server = ServerConfig()
        self.audio = AudioConfig()
        self.ui = UIConfig()
        self.debug = kwargs.get('debug', False)
        self.debug_level = kwargs.get('debug_level', 0)
        
        # Override with CLI args
        if kwargs.get('anthropic_key'):
            self.llm.anthropic_key = kwargs['anthropic_key']
        if kwargs.get('openai_key'):
            self.llm.openai_key = kwargs['openai_key']
        if kwargs.get('server_path'):
            # Convert old CLI arg to new multi-server format
            self.server.servers["default"] = MCPServerConfig(
                name="default",
                transport="stdio",
                path_or_url=kwargs['server_path'],
                auto_connect=True,
                enabled=True
            )
            
        # Load config file if provided, or auto-detect default
        if config_file:
            self._load_config_file(config_file)
        else:
            # Auto-detect default config file
            default_config_file = get_default_config_file()
            if default_config_file.exists():
                self._load_config_file(str(default_config_file))
        
        # Validate configuration
        self._validate()
    
    def _load_config_file(self, config_file: str):
        """Load configuration from YAML file"""
        config_path = Path(config_file)
        
        if not config_path.exists():
            # Config file doesn't exist - use built-in defaults
            return
        
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f) or {}
            
            # Load LLM config
            if 'llm' in config_data:
                llm_data = config_data['llm']
                if 'anthropic_key' in llm_data:
                    self.llm.anthropic_key = self._resolve_env_var(llm_data['anthropic_key'])
                if 'openai_key' in llm_data:
                    self.llm.openai_key = self._resolve_env_var(llm_data['openai_key'])
                if 'default_provider' in llm_data:
                    self.llm.default_provider = llm_data['default_provider']
                if 'default_model' in llm_data:
                    self.llm.default_model = llm_data['default_model']
            
            # Load server config
            if 'server' in config_data:
                server_data = config_data['server']
                
                # Handle new multi-server format
                if 'servers' in server_data:
                    self.server.servers = {}
                    for server_name, server_config in server_data['servers'].items():
                        # Process env vars if present
                        env_dict = None
                        if 'env' in server_config:
                            env_dict = {}
                            for key, value in server_config['env'].items():
                                env_dict[key] = self._resolve_env_var(value)
                        
                        self.server.servers[server_name] = MCPServerConfig(
                            name=server_config.get('name', server_name),
                            transport=server_config.get('transport', 'stdio'),
                            path_or_url=server_config.get('path_or_url', ''),
                            timeout=server_config.get('timeout', 30),
                            auto_connect=server_config.get('auto_connect', True),
                            enabled=server_config.get('enabled', True),
                            env=env_dict
                        )
                    if 'default_timeout' in server_data:
                        self.server.default_timeout = server_data['default_timeout']
                
                # Handle old single server format for backward compatibility
                elif 'script_path' in server_data:
                    self.server.servers = {
                        "legacy": MCPServerConfig(
                            name="legacy",
                            transport="stdio",
                            path_or_url=server_data['script_path'],
                            timeout=server_data.get('timeout', 30),
                            auto_connect=server_data.get('auto_connect', True),
                            enabled=True
                        )
                    }
            
            # Load audio config
            if 'audio' in config_data:
                audio_data = config_data['audio']
                if 'enabled' in audio_data:
                    self.audio.enabled = audio_data['enabled']
                if 'sample_rate' in audio_data:
                    self.audio.sample_rate = audio_data['sample_rate']
                if 'channels' in audio_data:
                    self.audio.channels = audio_data['channels']
                if 'chunk_size' in audio_data:
                    self.audio.chunk_size = audio_data['chunk_size']
                if 'input_device' in audio_data:
                    self.audio.input_device = audio_data['input_device']
                if 'output_device' in audio_data:
                    self.audio.output_device = audio_data['output_device']
                if 'model' in audio_data:
                    self.audio.model = audio_data['model']
                if 'voice' in audio_data:
                    self.audio.voice = audio_data['voice']
                if 'vad_threshold' in audio_data:
                    self.audio.vad_threshold = audio_data['vad_threshold']
                if 'vad_prefix_padding_ms' in audio_data:
                    self.audio.vad_prefix_padding_ms = audio_data['vad_prefix_padding_ms']
                if 'vad_silence_duration_ms' in audio_data:
                    self.audio.vad_silence_duration_ms = audio_data['vad_silence_duration_ms']
                if 'instructions' in audio_data:
                    self.audio.instructions = audio_data['instructions']
                if 'mode' in audio_data:
                    self.audio.mode = audio_data['mode']
                if 'use_dedicated_transcription_api' in audio_data:
                    self.audio.use_dedicated_transcription_api = audio_data['use_dedicated_transcription_api']
                if 'transcription_model' in audio_data:
                    self.audio.transcription_model = audio_data['transcription_model']
                if 'auto_submit_on_speech_end' in audio_data:
                    self.audio.auto_submit_on_speech_end = audio_data['auto_submit_on_speech_end']
                if 'show_transcription_in_input' in audio_data:
                    self.audio.show_transcription_in_input = audio_data['show_transcription_in_input']
                if 'noise_reduction' in audio_data:
                    self.audio.noise_reduction = audio_data['noise_reduction']
                if 'structured_response_prompt' in audio_data:
                    self.audio.structured_response_prompt = audio_data['structured_response_prompt']
                if 'audio_enhancement_prompt' in audio_data:
                    self.audio.audio_enhancement_prompt = audio_data['audio_enhancement_prompt']
            
            # Load UI config
            if 'ui' in config_data:
                ui_data = config_data['ui']
                if 'theme' in ui_data:
                    self.ui.theme = ui_data['theme']
                if 'show_thinking_indicator' in ui_data:
                    self.ui.show_thinking_indicator = ui_data['show_thinking_indicator']
                if 'max_message_history' in ui_data:
                    self.ui.max_message_history = ui_data['max_message_history']
                if 'audio_visualizer' in ui_data:
                    self.ui.audio_visualizer = ui_data['audio_visualizer']
                if 'fft_bars' in ui_data:
                    self.ui.fft_bars = ui_data['fft_bars']
                    
        except Exception as e:
            raise Exception(f"Failed to load config file '{config_file}': {e}")
    
    def _create_default_config(self, config_path: Path):
        """Create a default configuration file"""
        default_config = {
            'llm': {
                'anthropic_key': '${ANTHROPIC_API_KEY}',
                'openai_key': '${OPENAI_API_KEY}',
                'default_provider': 'anthropic',
                'default_model': 'claude-3-5-sonnet-20241022'
            },
            'server': {
                'servers': {
                    'vme': {
                        'name': 'vme',
                        'transport': 'stdio',
                        'path_or_url': 'src/servers/progressive_discovery_server.py',
                        'timeout': 30,
                        'auto_connect': True,
                        'enabled': True,
                        'env': {
                            'VME_API_BASE_URL': '${VME_API_BASE_URL}',
                            'VME_API_TOKEN': '${VME_API_TOKEN}'
                        }
                    }
                },
                'default_timeout': 30
            },
            'audio': {
                'enabled': True,  # Keep audio enabled by default
                'mode': 'input_only',
                'use_dedicated_transcription_api': True,
                'transcription_model': 'gpt-4o-transcribe',
                'sample_rate': 24000,
                'channels': 1,
                'chunk_size': 1024,
                'input_device': None,
                'output_device': None,
                'model': 'gpt-4o-realtime-preview-2024-10-01',
                'voice': 'echo',
                'vad_threshold': 0.6,
                'vad_prefix_padding_ms': 300,
                'vad_silence_duration_ms': 600,
                'auto_submit_on_speech_end': True,
                'show_transcription_in_input': True,
                'noise_reduction': 'near_field',
                'instructions': (
                    'You are a helpful assistant for VME infrastructure management. '
                    'Keep responses conversational and concise for audio output. '
                    'When the user asks about infrastructure, provide brief spoken summaries '
                    'while detailed information will be handled separately via text.'
                ),
                'structured_response_prompt': (
                    'Always respond in this JSON format:\n'
                    '{\n'
                    '  "content": "Your response with full information, tool results, and explanations"\n'
                    '}\n'
                ),
                'audio_enhancement_prompt': (
                    'Since audio is enabled, also include a \'tts_text\' field with a brief conversational summary (1-2 sentences) suitable for text-to-speech:\n'
                    '{\n'
                    '  "content": "Your detailed technical response",\n'
                    '  "tts_text": "Brief conversational summary that sounds natural when spoken aloud"\n'
                    '}\n'
                )
            },
            'ui': {
                'theme': 'github_dark',
                'show_thinking_indicator': True,
                'max_message_history': 1000,
                'audio_visualizer': True,
                'fft_bars': 8
            }
        }
        
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False, indent=2)
        except Exception as e:
            raise Exception(f"Failed to create default config: {e}")
    
    def _resolve_env_var(self, value: str) -> str:
        """Resolve environment variables in config values"""
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            env_name = value[2:-1]
            return os.getenv(env_name, '')
        return value
    
    def _run_onboarding(self, config_path: Path):
        """Run interactive onboarding for first-time users"""
        print("🚀 Welcome to VME CLI!")
        print("Let's set up your configuration.\n")
        
        # Check for environment variables first
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        
        if anthropic_key or openai_key:
            print("✅ Found API keys in environment variables:")
            if anthropic_key:
                print("  - ANTHROPIC_API_KEY")
                self.llm.anthropic_key = anthropic_key
            if openai_key:
                print("  - OPENAI_API_KEY")
                self.llm.openai_key = openai_key
            print()
        else:
            print("No API keys found in environment variables.")
            print("You'll need at least one API key to use VME CLI.\n")
            
            # Interactive prompting
            while not self.llm.anthropic_key and not self.llm.openai_key:
                print("Available providers:")
                print("  1. Anthropic Claude (recommended)")
                print("  2. OpenAI GPT")
                print("  3. Skip (set environment variables later)")
                
                try:
                    choice = input("\nWhich provider would you like to configure? (1-3): ").strip()
                    
                    if choice == "1":
                        key = input("Enter your Anthropic API key: ").strip()
                        if key:
                            self.llm.anthropic_key = key
                            self.llm.default_provider = "anthropic"
                            print("✅ Anthropic API key configured")
                        
                    elif choice == "2":
                        key = input("Enter your OpenAI API key: ").strip()
                        if key:
                            self.llm.openai_key = key
                            self.llm.default_provider = "openai"
                            print("✅ OpenAI API key configured")
                        
                    elif choice == "3":
                        print("\n⚠️  Skipping API key setup.")
                        print("You can set these environment variables later:")
                        print("  export ANTHROPIC_API_KEY='your-key-here'")
                        print("  export OPENAI_API_KEY='your-key-here'")
                        break
                        
                    else:
                        print("Invalid choice. Please enter 1, 2, or 3.")
                        
                except KeyboardInterrupt:
                    print("\n\nSetup cancelled.")
                    sys.exit(1)
        
        # Create config file
        self._create_config_file(config_path)
        print(f"📝 Configuration saved to: {config_path}")
        print("\n🎉 Setup complete! You can now use VME CLI.")
        
    def _create_config_file(self, config_path: Path):
        """Create configuration file with current settings"""
        config_data = {
            'llm': {
                'anthropic_key': self.llm.anthropic_key or '${ANTHROPIC_API_KEY}',
                'openai_key': self.llm.openai_key or '${OPENAI_API_KEY}',
                'default_provider': self.llm.default_provider,
                'default_model': self.llm.default_model
            },
            'server': {
                'servers': {
                    name: dict(
                        name=server.name,
                        transport=server.transport,
                        path_or_url=server.path_or_url,
                        timeout=server.timeout,
                        auto_connect=server.auto_connect,
                        enabled=server.enabled,
                        **({'env': server.env} if server.env else {})
                    )
                    for name, server in self.server.servers.items()
                },
                'default_timeout': self.server.default_timeout
            },
            'audio': {
                'enabled': self.audio.enabled,
                'mode': self.audio.mode,
                'use_dedicated_transcription_api': self.audio.use_dedicated_transcription_api,
                'transcription_model': self.audio.transcription_model,
                'sample_rate': self.audio.sample_rate,
                'channels': self.audio.channels,
                'chunk_size': self.audio.chunk_size,
                'input_device': self.audio.input_device,
                'output_device': self.audio.output_device,
                'model': self.audio.model,
                'voice': self.audio.voice,
                'vad_threshold': self.audio.vad_threshold,
                'vad_prefix_padding_ms': self.audio.vad_prefix_padding_ms,
                'vad_silence_duration_ms': self.audio.vad_silence_duration_ms,
                'auto_submit_on_speech_end': self.audio.auto_submit_on_speech_end,
                'show_transcription_in_input': self.audio.show_transcription_in_input,
                'noise_reduction': self.audio.noise_reduction,
                'instructions': self.audio.instructions,
                'structured_response_prompt': self.audio.structured_response_prompt,
                'audio_enhancement_prompt': self.audio.audio_enhancement_prompt
            },
            'ui': {
                'theme': self.ui.theme,
                'show_thinking_indicator': self.ui.show_thinking_indicator,
                'max_message_history': self.ui.max_message_history
            }
        }
        
        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write config file
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)

    def _validate(self):
        """Validate the configuration"""
        if not self.llm.anthropic_key and not self.llm.openai_key:
            # Try to get from environment
            self.llm.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            self.llm.openai_key = os.getenv('OPENAI_API_KEY')
        
        if not self.llm.anthropic_key and not self.llm.openai_key:
            print("\n❌ No API keys found!")
            print("Please set one of these environment variables:")
            print("  export ANTHROPIC_API_KEY='your-anthropic-key'")
            print("  export OPENAI_API_KEY='your-openai-key'")
            from vme_cli.constants import __command_name__
            print("\nOr copy the default config and edit it:")
            print(f"  {__command_name__} config")
            print("  # Then edit ~/.config/vme-cli/config.yaml")
            raise Exception("At least one LLM API key is required")
        
        if self.llm.default_provider == 'anthropic' and not self.llm.anthropic_key:
            if self.llm.openai_key:
                self.llm.default_provider = 'openai'
            else:
                raise Exception("Anthropic API key required for default provider")
        
        if self.llm.default_provider == 'openai' and not self.llm.openai_key:
            if self.llm.anthropic_key:
                self.llm.default_provider = 'anthropic'
            else:
                raise Exception("OpenAI API key required for default provider")
        
        # Validate server configurations
        if not self.server.servers:
            raise Exception("At least one MCP server must be configured")
        
        for server_name, server_config in self.server.servers.items():
            if server_config.transport == "stdio":
                if not server_config.path_or_url:
                    raise Exception(f"Server {server_name}: path_or_url is required for stdio transport")
                if not Path(server_config.path_or_url).exists():
                    raise Exception(f"Server {server_name}: script not found: {server_config.path_or_url}")
            elif server_config.transport == "http":
                if not server_config.path_or_url:
                    raise Exception(f"Server {server_name}: path_or_url (URL) is required for HTTP transport")
                if not server_config.path_or_url.startswith(('http://', 'https://')):
                    raise Exception(f"Server {server_name}: HTTP transport requires URL starting with http:// or https://")
            else:
                raise Exception(f"Server {server_name}: unsupported transport '{server_config.transport}'. Use 'stdio' or 'http'")