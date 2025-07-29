#!/usr/bin/env python3
"""
VME Textual CLI Client - Main Entry Point
"""

import asyncio
import sys
import os
from pathlib import Path

# Load .env file first
def load_dotenv_file():
    """Load environment variables from .env file"""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    if line.startswith('export '):
                        line = line[7:]
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")

load_dotenv_file()

import click
from .ui.app import VMEChatApp
from .config.settings import ClientConfig

@click.command()
@click.option('--config', '-c', help='Config file path (default: auto-detect OS config location)')
@click.option('--anthropic-key', envvar='ANTHROPIC_API_KEY', help='Anthropic API key')
@click.option('--openai-key', envvar='OPENAI_API_KEY', help='OpenAI API key')
@click.option('--server-path', help='Path to VME server script')
@click.option('--debug', is_flag=True, help='Enable debug mode (same as --debug-level 1)')
@click.option('--debug-level', type=int, default=0, help='Debug level: 0=off, 1=basic, 2=detailed, 3=verbose')
def main(config, anthropic_key, openai_key, server_path, debug, debug_level):
    """VME Infrastructure Chat Client
    
    On first run, this tool will guide you through setting up your API keys.
    
    \b
    Required Environment Variables:
      ANTHROPIC_API_KEY    Your Anthropic Claude API key
      OPENAI_API_KEY       Your OpenAI GPT API key
      
    You need at least one of these API keys to use the client.
    
    \b
    Configuration:
      Linux/macOS: ~/.config/vme-cli/config.yaml
      Windows:     %APPDATA%\\vme-cli\\config.yaml
      
    On first run, the configuration file will be created automatically.
    """
    
    try:
        # Set debug level (--debug flag sets level 1)
        final_debug_level = max(debug_level, 1 if debug else 0)
        
        client_config = ClientConfig(
            config_file=config,
            anthropic_key=anthropic_key,
            openai_key=openai_key,
            server_path=server_path,
            debug=final_debug_level > 0,
            debug_level=final_debug_level
        )
        
        app = VMEChatApp(client_config)
        app.run()
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    main()