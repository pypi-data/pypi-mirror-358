"""
FastMCP Manager for multiple MCP server connections
Supports both stdio and HTTP transports
"""

import asyncio
import logging
import httpx
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from fastmcp import Client
    from fastmcp.client.transports import PythonStdioTransport, StdioTransport
    from mcp.types import Implementation
except ImportError:
    raise ImportError("FastMCP not installed. Run: pip install fastmcp")

from ..config.settings import MCPServerConfig
from vme_cli._version import __version__
from vme_cli.constants import __app_name__, __command_name__

logger = logging.getLogger(__name__)

# Suppress FastMCP logging to reduce noise
logging.getLogger("fastmcp").setLevel(logging.ERROR)
logging.getLogger("fastmcp.utilities.openapi").setLevel(logging.ERROR)

class VMETool:
    """Simple tool representation"""
    def __init__(self, name: str, description: str, input_schema: Dict[str, Any], server_name: str = ""):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.server_name = server_name

class VMEResource:
    """Simple resource representation"""
    def __init__(self, name: str, description: str, uri: str, server_name: str = ""):
        self.name = name
        self.description = description
        self.uri = uri
        self.server_name = server_name

class MCPServerConnection:
    """Individual MCP server connection"""
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.client: Optional[Client] = None
        self.http_client: Optional[httpx.AsyncClient] = None
        self.tools: List[VMETool] = []
        self.resources: List[VMEResource] = []
        self.is_connected = False
    
    def _get_config_path(self) -> Path:
        """Get OS-appropriate config file path"""
        import platform
        
        if platform.system() == "Windows":
            # Windows: %APPDATA%\vme-cli\config.yaml
            return Path.home() / "AppData" / "Roaming" / "vme-cli" / "config.yaml"
        else:
            # Linux/Mac: ~/.config/vme-cli/config.yaml
            return Path.home() / ".config" / "vme-cli" / "config.yaml"
    
    def _show_server_install_message(self):
        """Show helpful message when server is not found"""
        from rich.console import Console
        from rich.panel import Panel
        
        console = Console()
        config_path = self._get_config_path()
        
        message = f"""[red]❌ MCP server not found![/red]

The server command '[yellow]{self.config.path_or_url}[/yellow]' could not be found.

[bold]To use a local MCP server:[/bold]
  Install the server package:
  [cyan]pip install vme-mcp-server[/cyan]

[bold]To connect to a remote server:[/bold]
  Edit your config file:
  [dim]{config_path}[/dim]
  
  Change the transport and URL:
  [yellow]server:
    servers:
      vme:
        transport: http
        path_or_url: http://your-server:8080[/yellow]

[bold]Or use the config command:[/bold]
  [cyan]{__command_name__} config --server-transport http --server-url http://your-server:8080[/cyan]
"""
        
        console.print(Panel(message, title="Server Not Found", border_style="red"))
    
    async def connect(self) -> bool:
        """Connect to the MCP server"""
        try:
            if self.config.transport == "stdio":
                return await self._connect_stdio()
            elif self.config.transport == "http":
                return await self._connect_http()
            else:
                logger.error(f"Unsupported transport: {self.config.transport}")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to server {self.config.name}: {e}")
            return False
    
    async def _connect_stdio(self) -> bool:
        """Connect via stdio transport"""
        import platform
        import sys
        import subprocess
        
        # Check if path_or_url is a command or a file path
        path_or_url = self.config.path_or_url
        is_command = not ('/' in path_or_url or '\\' in path_or_url or path_or_url.endswith('.py'))
        
        if is_command:
            # It's a command like "vme-mcp-server", check if it exists
            try:
                result = subprocess.run([path_or_url, "--help"], capture_output=True, text=True)
                if result.returncode != 0:
                    raise FileNotFoundError()
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Show helpful error message
                self._show_server_install_message()
                return False
            
            logger.info(f"Connecting to {self.config.name} via stdio command: {path_or_url}")
        else:
            # It's a file path
            script_path = Path(path_or_url).resolve()
            
            if not script_path.exists():
                logger.error(f"Server script not found: {script_path}")
                self._show_server_install_message()
                return False
            
            logger.info(f"Connecting to {self.config.name} via stdio: {script_path}")
        
        # Temporarily suppress logging during connection
        original_level = logging.getLogger().level
        logging.getLogger().setLevel(logging.CRITICAL)
        
        try:
            client_info = Implementation(
                name=__app_name__,
                version=__version__
            )
            
            async def suppress_logs(log_params):
                """Suppress server log messages"""
                pass
            
            # Store debug info for later display
            self._debug_env_info = None
            
            # Create transport with environment variables if provided
            if self.config.env:
                # Prepare debug info about env vars
                env_debug = []
                for key, value in self.config.env.items():
                    if key.endswith('_TOKEN') or key.endswith('_KEY'):
                        # Mask sensitive values
                        masked_value = value[:8] + '...' if len(value) > 8 else '***'
                        env_debug.append(f"{key}={masked_value}")
                    else:
                        env_debug.append(f"{key}={value}")
                
                self._debug_env_info = f"Using environment variables: {', '.join(env_debug)}"
                
                # Create transport based on whether it's a command or script
                if is_command:
                    # For commands, use StdioTransport which accepts any executable
                    import shutil
                    command_path = shutil.which(path_or_url)
                    if command_path:
                        # StdioTransport expects command and args separately
                        transport = StdioTransport(
                            command=command_path,
                            args=[],
                            env=self.config.env
                        )
                    else:
                        raise FileNotFoundError(f"Command '{path_or_url}' not found in PATH")
                else:
                    # For scripts, handle Windows vs Unix
                    if platform.system() == "Windows":
                        # Use sys.executable to get the Python interpreter path
                        transport = PythonStdioTransport(
                            command=[sys.executable, str(script_path)],
                            env=self.config.env
                        )
                    else:
                        transport = PythonStdioTransport(
                            script_path=str(script_path),
                            env=self.config.env
                        )
                self.client = Client(
                    transport,
                    client_info=client_info,
                    log_handler=suppress_logs
                )
            else:
                # Use simple string path for backward compatibility
                self._debug_env_info = "Using server default configuration (no custom env vars)"
                self.client = Client(
                    str(script_path),
                    client_info=client_info,
                    log_handler=suppress_logs
                )
            
            await asyncio.wait_for(
                self.client.__aenter__(), 
                timeout=self.config.timeout
            )
            
            await self._discover_tools()
            await self._discover_resources()
            self.is_connected = True
            logger.info(f"Connected to {self.config.name} - {len(self.tools)} tools, {len(self.resources)} resources available")
            return True
            
        finally:
            logging.getLogger().setLevel(original_level)
    
    async def _connect_http(self) -> bool:
        """Connect via HTTP transport"""
        logger.info(f"Connecting to {self.config.name} via HTTP: {self.config.path_or_url}")
        
        self.http_client = httpx.AsyncClient(
            base_url=self.config.path_or_url,
            timeout=self.config.timeout
        )
        
        # Test connection by trying to list tools and resources
        try:
            # Get tools
            response = await self.http_client.post("/mcp/tools/list", json={})
            response.raise_for_status()
            tools_data = response.json()
            await self._process_tools_data(tools_data)
            
            # Get resources  
            try:
                response = await self.http_client.post("/mcp/resources/list", json={})
                response.raise_for_status()
                resources_data = response.json()
                await self._process_resources_data(resources_data)
            except Exception as e:
                logger.debug(f"No resources endpoint or error for {self.config.name}: {e}")
                self.resources = []
            
            self.is_connected = True
            logger.info(f"Connected to {self.config.name} - {len(self.tools)} tools, {len(self.resources)} resources available")
            return True
            
        except Exception as e:
            logger.error(f"HTTP connection failed for {self.config.name}: {e}")
            if self.http_client:
                await self.http_client.aclose()
                self.http_client = None
            return False
    
    async def _discover_tools(self):
        """Discover tools for stdio connection"""
        if not self.client:
            return
        
        try:
            tools_data = await self.client.list_tools()
            await self._process_tools_data(tools_data)
        except Exception as e:
            logger.error(f"Failed to discover tools for {self.config.name}: {e}")
            self.tools = []
    
    async def _discover_resources(self):
        """Discover resources for stdio connection"""
        if not self.client:
            return
        
        try:
            resources_data = await self.client.list_resources()
            await self._process_resources_data(resources_data)
        except Exception as e:
            logger.debug(f"No resources available or error for {self.config.name}: {e}")
            self.resources = []
    
    async def _process_tools_data(self, tools_data):
        """Process tools data from either stdio or HTTP"""
        self.tools = []
        
        # Handle different response formats
        if isinstance(tools_data, dict) and 'tools' in tools_data:
            tools_list = tools_data['tools']
        else:
            tools_list = tools_data
        
        for tool_data in tools_list:
            # Handle both object and dict formats
            if hasattr(tool_data, 'name'):
                name = tool_data.name
                description = tool_data.description or "No description"
                input_schema = getattr(tool_data, 'input_schema', None) or getattr(tool_data, 'inputSchema', {})
            else:
                name = tool_data.get('name', '')
                description = tool_data.get('description', 'No description')
                input_schema = tool_data.get('input_schema', tool_data.get('inputSchema', {}))
            
            tool = VMETool(
                name=name,
                description=description,
                input_schema=input_schema or {},
                server_name=self.config.name
            )
            self.tools.append(tool)
        
        logger.debug(f"Processed {len(self.tools)} tools for {self.config.name}")
        
        # Debug: Check for DELETE tools
        delete_tools = [t for t in self.tools if 'delete' in t.name.lower() and 'instance' in t.name.lower()]
        if delete_tools:
            logger.info(f"🔍 Found {len(delete_tools)} DELETE instance tools in {self.config.name}:")
            for tool in delete_tools:
                logger.info(f"   - {tool.name}")
    
    async def _process_resources_data(self, resources_data):
        """Process resources data from either stdio or HTTP"""
        self.resources = []
        
        # Handle different response formats
        if isinstance(resources_data, dict) and 'resources' in resources_data:
            resources_list = resources_data['resources']
        else:
            resources_list = resources_data
        
        for resource_data in resources_list:
            # Handle both object and dict formats
            if hasattr(resource_data, 'name'):
                name = resource_data.name
                description = resource_data.description or "No description"
                uri = getattr(resource_data, 'uri', '')
            else:
                name = resource_data.get('name', '')
                description = resource_data.get('description', 'No description')
                uri = resource_data.get('uri', '')
            
            resource = VMEResource(
                name=name,
                description=description,
                uri=uri,
                server_name=self.config.name
            )
            self.resources.append(resource)
        
        logger.debug(f"Processed {len(self.resources)} resources for {self.config.name}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on this server"""
        if not self.is_connected:
            raise Exception(f"Not connected to server {self.config.name}")
        
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if not tool:
            raise Exception(f"Tool '{tool_name}' not found on server {self.config.name}")
        
        try:
            logger.debug(f"Calling tool {tool_name} with args: {arguments}")
            
            if self.config.transport == "stdio" and self.client:
                result = await self.client.call_tool(tool_name, arguments)
            elif self.config.transport == "http" and self.http_client:
                response = await self.http_client.post(
                    "/mcp/tools/call",
                    json={"name": tool_name, "arguments": arguments}
                )
                response.raise_for_status()
                result = response.json()
            else:
                raise Exception(f"No valid client for {self.config.transport} transport")
            
            logger.debug(f"Tool {tool_name} result from {self.config.name}: {str(result)[:200]}...")
            return result
            
        except Exception as e:
            logger.error(f"Tool call failed: {tool_name} on {self.config.name}")
            logger.error(f"Server: {self.config.name}, Transport: {self.config.transport}")
            logger.error(f"Error details: {type(e).__name__}: {str(e)}")
            if hasattr(e, '__cause__') and e.__cause__:
                logger.error(f"Caused by: {type(e.__cause__).__name__}: {str(e.__cause__)}")
            raise Exception(f"Tool call failed: {e}")
    
    def get_debug_env_info(self) -> Optional[str]:
        """Get debug information about environment variables used"""
        return getattr(self, '_debug_env_info', None)
    
    async def refresh_tools(self) -> bool:
        """Refresh the tool list from the server (for stdio connections that cache tools)"""
        if not self.is_connected:
            return False
            
        if self.config.transport == "stdio":
            # Re-discover tools for stdio connection
            old_count = len(self.tools)
            await self._discover_tools()
            new_count = len(self.tools)
            logger.info(f"Refreshed tools for {self.config.name}: {old_count} -> {new_count} tools")
            return True
        elif self.config.transport == "http":
            # HTTP already gets fresh tool list on each call
            return True
        
        return False
    
    async def disconnect(self):
        """Disconnect from the server"""
        self.is_connected = False
        
        if self.client:
            try:
                await self.client.__aexit__(None, None, None)
            except Exception as e:
                logger.warning(f"Error disconnecting stdio client for {self.config.name}: {e}")
            finally:
                self.client = None
        
        if self.http_client:
            try:
                await self.http_client.aclose()
            except Exception as e:
                logger.warning(f"Error disconnecting HTTP client for {self.config.name}: {e}")
            finally:
                self.http_client = None
        
        self.tools.clear()
        self.resources.clear()

class MCPManager:
    """Manages multiple MCP server connections"""
    
    def __init__(self, server_configs: Dict[str, MCPServerConfig]):
        self.server_configs = server_configs
        self.servers: Dict[str, MCPServerConnection] = {}
        self.all_tools: List[VMETool] = []
        self.all_resources: List[VMEResource] = []
        
    async def connect(self) -> bool:
        """Connect to all configured MCP servers"""
        logger.info(f"Connecting to {len(self.server_configs)} MCP servers...")
        
        connected_count = 0
        for name, config in self.server_configs.items():
            if not config.enabled or not config.auto_connect:
                logger.info(f"Skipping server {name} (disabled or auto_connect=False)")
                continue
            
            server = MCPServerConnection(config)
            self.servers[name] = server
            
            try:
                if await server.connect():
                    connected_count += 1
                    logger.info(f"✅ Connected to {name}")
                else:
                    logger.warning(f"❌ Failed to connect to {name}")
            except Exception as e:
                logger.error(f"❌ Error connecting to {name}: {e}")
        
        # Rebuild aggregated tools list
        self._rebuild_tools_list()
        
        success = connected_count > 0
        if success:
            auto_connect_servers = len([c for c in self.server_configs.values() if c.enabled and c.auto_connect])
            logger.info(f"Connected to {connected_count}/{auto_connect_servers} servers - {len(self.all_tools)} tools, {len(self.all_resources)} resources")
        else:
            logger.error("Failed to connect to any MCP servers")
        
        return success
    
    async def disconnect(self):
        """Disconnect from all MCP servers"""
        logger.info("Disconnecting from all MCP servers...")
        
        for name, server in self.servers.items():
            try:
                await server.disconnect()
                logger.info(f"✅ Disconnected from {name}")
            except Exception as e:
                logger.warning(f"❌ Error disconnecting from {name}: {e}")
        
        self.servers.clear()
        self.all_tools.clear()
        self.all_resources.clear()
    
    def _rebuild_tools_list(self):
        """Rebuild the aggregated tools and resources lists from all connected servers"""
        self.all_tools.clear()
        self.all_resources.clear()
        
        for server in self.servers.values():
            if server.is_connected:
                self.all_tools.extend(server.tools)
                self.all_resources.extend(server.resources)
        
        logger.debug(f"Rebuilt lists: {len(self.all_tools)} tools, {len(self.all_resources)} resources")
    
    async def refresh_all_tools(self) -> bool:
        """Refresh tool lists for all stdio connections"""
        refreshed_count = 0
        
        for server_name, server in self.servers.items():
            if server.is_connected and server.config.transport == "stdio":
                try:
                    if await server.refresh_tools():
                        refreshed_count += 1
                        logger.info(f"Refreshed tools for {server_name}")
                except Exception as e:
                    logger.error(f"Failed to refresh tools for {server_name}: {e}")
        
        # Rebuild aggregated list
        self._rebuild_tools_list()
        
        if refreshed_count > 0:
            logger.info(f"Refreshed {refreshed_count} servers - now {len(self.all_tools)} total tools available")
            
            # Debug: Check for DELETE tools after refresh
            delete_tools = [t for t in self.all_tools if 'delete' in t.name.lower() and 'instance' in t.name.lower()]
            if delete_tools:
                logger.info(f"🔍 After refresh, found {len(delete_tools)} DELETE instance tools:")
                for tool in delete_tools:
                    logger.info(f"   - {tool.name}: {tool.description[:100]}...")
        
        return refreshed_count > 0
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on the appropriate MCP server"""
        # Find the tool and determine which server it belongs to
        target_tool = None
        target_server = None
        
        for server in self.servers.values():
            if server.is_connected:
                tool = next((t for t in server.tools if t.name == tool_name), None)
                if tool:
                    target_tool = tool
                    target_server = server
                    break
        
        if not target_tool or not target_server:
            raise Exception(f"Tool '{tool_name}' not found on any connected server")
        
        logger.debug(f"Calling tool {tool_name} on server {target_server.config.name}")
        result = await target_server.call_tool(tool_name, arguments)
        
        # Check if this is a discovery tool that adds new tools
        if tool_name.startswith("discover_"):
            # Result can be a dict, list of TextContent, or other format
            result_text = ""
            
            if isinstance(result, dict) and "content" in result:
                # Dict format
                result_text = str(result.get("content", [{}])[0].get("text", ""))
            elif isinstance(result, list) and len(result) > 0:
                # List of TextContent objects
                result_text = str(result[0]) if hasattr(result[0], '__dict__') else str(result)
            else:
                # Fallback to string representation
                result_text = str(result)
            
            if "Tool count increased" in result_text:
                # Progressive discovery added new tools, refresh for stdio connections
                logger.info("Discovery tool activated new tools, refreshing tool lists...")
                await self.refresh_all_tools()
        
        return result
    
    def get_tools(self) -> List[VMETool]:
        """Get list of all available tools from all servers"""
        return self.all_tools.copy()
    
    def get_tool_by_name(self, name: str) -> Optional[VMETool]:
        """Get a specific tool by name from any server"""
        return next((t for t in self.all_tools if t.name == name), None)
    
    def get_tools_by_server(self, server_name: str) -> List[VMETool]:
        """Get tools from a specific server"""
        server = self.servers.get(server_name)
        if server and server.is_connected:
            return server.tools.copy()
        return []
    
    def get_resources(self) -> List[VMEResource]:
        """Get list of all available resources from all servers"""
        return self.all_resources.copy()
    
    def get_resource_by_name(self, name: str) -> Optional[VMEResource]:
        """Get a specific resource by name from any server"""
        return next((r for r in self.all_resources if r.name == name), None)
    
    def get_resources_by_server(self, server_name: str) -> List[VMEResource]:
        """Get resources from a specific server"""
        server = self.servers.get(server_name)
        if server and server.is_connected:
            return server.resources.copy()
        return []
    
    def get_connected_servers(self) -> List[str]:
        """Get list of connected server names"""
        return [name for name, server in self.servers.items() if server.is_connected]
    
    def has_discovery_tools(self) -> bool:
        """Check if any server has discovery tools available"""
        discovery_keywords = ['discover', 'capabilities', 'list']
        return any(
            any(keyword in tool.name.lower() for keyword in discovery_keywords)
            for tool in self.all_tools
        )
    
    async def connect_server(self, server_name: str) -> bool:
        """Manually connect to a specific server"""
        if server_name not in self.server_configs:
            logger.error(f"Server {server_name} not found in configuration")
            return False
        
        config = self.server_configs[server_name]
        if server_name in self.servers:
            # Disconnect existing connection first
            await self.servers[server_name].disconnect()
        
        server = MCPServerConnection(config)
        self.servers[server_name] = server
        
        try:
            success = await server.connect()
            if success:
                self._rebuild_tools_list()
                logger.info(f"✅ Manually connected to {server_name}")
            else:
                logger.warning(f"❌ Failed to manually connect to {server_name}")
            return success
        except Exception as e:
            logger.error(f"❌ Error manually connecting to {server_name}: {e}")
            return False
    
    async def disconnect_server(self, server_name: str) -> bool:
        """Manually disconnect from a specific server"""
        if server_name not in self.servers:
            logger.warning(f"Server {server_name} not connected")
            return False
        
        try:
            await self.servers[server_name].disconnect()
            del self.servers[server_name]
            self._rebuild_tools_list()
            logger.info(f"✅ Manually disconnected from {server_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Error manually disconnecting from {server_name}: {e}")
            return False