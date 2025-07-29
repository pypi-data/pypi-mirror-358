"""
VME Chat Application - Simplified Textual Interface
Clean chat interface with GitHub dark theme
"""

import asyncio
import logging
import time
from typing import List, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Input, Header, Footer
from textual.reactive import reactive
from textual.message import Message
from rich.text import Text
from rich.markdown import Markdown

from vme_cli.config.settings import ClientConfig
from vme_cli.mcp.manager import MCPManager
from vme_cli.llm.manager import LLMManager
from vme_cli.ui.simple_audio_widgets import SimpleAudioBar, MicrophoneWidget, AudioState
from vme_cli.audio.factory import create_audio_manager
from vme_cli.session_logs.session_logger import SessionLogger, ToolStatus

logger = logging.getLogger(__name__)

class ChatArea(Vertical):
    """Scrollable chat area for conversation"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.thinking_widget = None
        self.thinking_frame = 0
        self.thinking_timer = None
        
    def add_user_message(self, text: str):
        """Add a user message to the chat"""
        # Add some spacing
        self.mount(Static(Text(" ")))
        
        # Create user message
        styled = Text()
        styled.append("❯ ", style="bold #58a6ff")
        styled.append("You: ", style="bold #58a6ff") 
        styled.append(text, style="#f0f6fc")
        self.mount(Static(styled))
        self.scroll_end()
    
    def add_assistant_message(self, text: str):
        """Add an assistant message to the chat"""
        # Add some spacing (preserving the empty line spacing fix)
        self.mount(Static(Text("")))
        
        try:
            # Try to render as markdown
            markdown = Markdown(
                text,
                code_theme="monokai",
                hyperlinks=True
            )
            
            # Add AI prefix
            prefix = Text()
            prefix.append("AI: ", style="bold #3fb950")
            
            self.mount(Static(prefix))
            self.mount(Static(markdown))
            
        except Exception:
            # Fallback to plain text
            styled = Text()
            styled.append("AI: ", style="bold #3fb950")
            styled.append(text, style="#f0f6fc")
            self.mount(Static(styled))
        
        self.scroll_end()
    
    def add_system_message(self, text: str):
        """Add a system message to the chat"""
        # No spacing for tool messages
        styled = Text(text, style="#7d8590")
        self.mount(Static(styled))
        self.scroll_end()
        
        # Log to session logger if parent app has one
        try:
            app = self.app
            if hasattr(app, 'session_logger'):
                app.session_logger.log_error(text, error_type="system_debug")
        except:
            pass
    
    def add_error_message(self, text: str):
        """Add an error message to the chat"""
        styled = Text()
        styled.append("✕ Error: ", style="bold #f85149")
        styled.append(text, style="#f85149")
        self.mount(Static(styled))
        self.scroll_end()
    
    def add_thinking_indicator(self):
        """Add animated thinking indicator"""
        # Add some spacing
        self.mount(Static(Text(" ")))
        
        thinking_text = Text()
        thinking_text.append("AI: ", style="bold #3fb950")
        thinking_text.append("⠋ ", style="bold #58a6ff")
        thinking_text.append("thinking...", style="dim #7d8590")
        
        self.thinking_widget = Static(thinking_text)
        self.mount(self.thinking_widget)
        self.scroll_end()
        
        # Start animation using app timer
        self.thinking_frame = 0
        self.thinking_timer = self.app.set_interval(0.08, self._animate_thinking_frame)
    
    def _animate_thinking_frame(self):
        """Animate one frame of the thinking indicator"""
        if not self.thinking_widget or not self.thinking_widget.parent:
            if self.thinking_timer:
                self.thinking_timer.stop()
            return
            
        # Braille spinner frames
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        
        thinking_text = Text()
        thinking_text.append("AI: ", style="bold #3fb950")
        thinking_text.append(f"{frames[self.thinking_frame]} ", style="bold #58a6ff")
        thinking_text.append("thinking...", style="dim #7d8590")
        
        self.thinking_widget.update(thinking_text)
        self.thinking_frame = (self.thinking_frame + 1) % len(frames)
    
    def remove_thinking_indicator(self):
        """Remove the thinking indicator"""
        if self.thinking_timer:
            self.thinking_timer.stop()
            self.thinking_timer = None
        if self.thinking_widget and self.thinking_widget.parent:
            self.thinking_widget.remove()
        if hasattr(self, 'thinking_spacer') and self.thinking_spacer and self.thinking_spacer.parent:
            self.thinking_spacer.remove()
        self.thinking_widget = None
        self.thinking_spacer = None

class VMEChatApp(App):
    """Main VME Chat Application"""
    
    # Reactive audio state - PROPER Textual pattern!
    audio_state = reactive("listening")
    
    class AudioStateChanged(Message):
        """Message for audio state changes from background threads"""
        def __init__(self, state) -> None:
            self.state = state
            super().__init__()
    
    # GitHub-inspired dark theme
    CSS = """
    Screen {
        background: #0d1117;
    }
    
    #header-container {
        background: #484f58;
        height: 1;
        dock: top;
        padding: 0 2;
    }
    
    #header-left {
        width: 1fr;
        background: transparent;
        padding: 0 1;
    }
    
    .audio-indicator {
        color: #f0f6fc;
        text-align: left;
        background: transparent;
    }
    
    #header-center {
        width: 1fr;  
        color: #f0f6fc;
        text-align: center;
        background: transparent;
    }
    
    #header-right {
        width: 1fr;
        color: #f79000;
        text-align: right;
        background: transparent;
    }
    
    .hidden {
        display: none;
    }
    
    ChatArea {
        background: #161b22;
        padding: 0 2;
        height: 1fr;
        overflow-y: auto;
        scrollbar-size: 1 1;
        scrollbar-background: #0d1117;
        scrollbar-color: #30363d;
    }
    
    #input-container {
        background: #161b22;
        padding: 0 2;
        height: 3;
        dock: bottom;
    }
    
    SimpleAudioBar {
        dock: top;
        height: 1;
        background: #21262d;
        border-bottom: solid #30363d;
        padding: 0 2;
    }
    
    #audio-panel {
        background: #161b22;
        border-top: solid #30363d;
        padding: 1;
        height: 6;
    }
    
    Input {
        color: white;
        background: transparent;
        border: solid #30363d;
        padding: 0;
        margin: 0;
    }
    
    Input:focus {
        border: solid #58a6ff;
        background: transparent;
    }
    
    Static {
        background: #161b22;
    }
    
    Header {
        background: #21262d;
        color: #f0f6fc;
    }
    
    Footer {
        background: #21262d;
        color: #7d8590;
    }
    """
    
    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+q", "quit", "Quit"),
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
    ]
    
    def __init__(self, config: ClientConfig):
        super().__init__()
        self.config = config
        self.mcp_manager = MCPManager(config.server.servers)
        self.llm_manager = LLMManager(config.llm)
        self.audio_manager = create_audio_manager(config.audio, config) if config.audio.enabled else None
        logger.info(f"🎧 Audio manager created: {self.audio_manager is not None}")
        self.conversation_history = []
        self.is_initialized = False
        
        # Initialize session logger
        self.session_logger = SessionLogger()
        self.session_logger.set_session_config(
            audio_enabled=config.audio.enabled,
            audio_mode=config.audio.mode if config.audio.enabled else "disabled",
            llm_provider=config.llm.default_provider
        )
    
    def compose(self) -> ComposeResult:
        """Compose the UI"""
        logger.info(f"🎧 Composing UI - audio manager exists: {self.audio_manager is not None}")
        # Audio status bar (always show if audio enabled)
        if self.audio_manager:
            logger.info("🎧 Adding SimpleAudioBar to UI")
            yield SimpleAudioBar(id="audio-status-bar")
        
        # Three-part header: left (audio) | center (title) | right (tools/resources)
        with Horizontal(id="header-container"):
            with Container(id="header-left"):
                yield Static("🔴 Listening", id="audio-status", classes="audio-indicator")
            yield Static("VME Infrastructure Chat", id="header-center") 
            yield Static("Servers: 0 | Tools: 0 | Resources: 0", id="header-right")
        
        with Container(id="main-container"):
            yield ChatArea(id="chat-area")
            
            # Keep audio functionality but hidden (for now)
            if self.audio_manager:
                logger.info("🎧 Adding MicrophoneWidget (hidden for functionality)")
                with Container(id="audio-panel", classes="hidden"):
                    with Horizontal():
                        yield MicrophoneWidget(id="mic-widget")
            
            with Container(id="input-container"):
                placeholder = "Type or speak your message..." if self.audio_manager else "Type your message..."
                yield Input(placeholder=placeholder, id="chat-input")
        
        yield Footer()
    
    def _get_config_file_path(self) -> str:
        """Get the config file path for display"""
        from vme_cli.config.settings import get_default_config_file
        return str(get_default_config_file())
    
    async def on_mount(self):
        """Initialize the application"""
        # Update title
        self.title = "VME Infrastructure Chat"
        
        # Initialize audio status using reactive property
        if self.audio_manager:
            self.audio_state = "listening"
        else:
            self.audio_state = "off"
        
        # Get chat area
        chat_area = self.query_one("#chat-area", ChatArea)
        
        # Show welcome message
        chat_area.add_system_message("🚀 VME Infrastructure Chat Client")
        
        # Show config file location
        config_path = self._get_config_file_path()
        chat_area.add_system_message(f"📁 Config: {config_path}")
        
        chat_area.add_system_message("Connecting to VME server...")
        
        # Initialize components
        await self._initialize_managers(chat_area)
        
        # Initialize audio if available
        if self.audio_manager:
            # Show debug audio config if debug mode
            if self.config.debug_level >= 1:
                chat_area.add_system_message(f"🔧 Audio Debug: mode={self.audio_manager.mode}, transcription_api={getattr(self.audio_manager.config, 'use_dedicated_transcription_api', False)}")
                chat_area.add_system_message(f"🔧 Audio Debug: model={self.audio_manager.config.transcription_model}, auto_submit={self.audio_manager.config.auto_submit_on_speech_end}")
            await self._initialize_audio_widgets()
            
            # Connect to audio state changes
            self._setup_audio_state_monitoring()
        
        # Focus input
        chat_input = self.query_one("#chat-input", Input)
        self.set_focus(chat_input)
        
        # Audio state is managed through message system - no polling needed
    
    async def _initialize_managers(self, chat_area: ChatArea):
        """Initialize MCP and LLM managers"""
        try:
            # Initialize LLM manager
            await self.llm_manager.initialize()
            chat_area.add_system_message(f"✅ LLM initialized: {self.llm_manager.get_current_provider()}")
            
            # Connect to MCP servers
            success = await self.mcp_manager.connect()
            if success:
                tools_count = len(self.mcp_manager.get_tools())
                connected_servers = self.mcp_manager.get_connected_servers()
                
                # Show connection status for each server
                for server_name in connected_servers:
                    server_tools = len(self.mcp_manager.get_tools_by_server(server_name))
                    server_resources = len(self.mcp_manager.get_resources_by_server(server_name))
                    chat_area.add_system_message(f"✅ Connected to {server_name}: {server_tools} tools, {server_resources} resources")
                    
                    # Show debug info about environment variables if debug mode
                    if self.config.debug_level >= 1:
                        server_connection = self.mcp_manager.servers.get(server_name)
                        if server_connection:
                            debug_info = server_connection.get_debug_env_info()
                            if debug_info:
                                chat_area.add_system_message(f"🔧 {server_name}: {debug_info}")
                
                # Update header counts
                resources_count = len(self.mcp_manager.get_resources())
                self._update_header_counts(len(connected_servers), tools_count, resources_count)
                
                # Show discovery hint if available
                if self.mcp_manager.has_discovery_tools():
                    chat_area.add_system_message("💡 Try asking: 'What infrastructure is available?'")
                
            else:
                chat_area.add_error_message("Failed to connect to any MCP servers")
                return
            
            self.is_initialized = True
            chat_area.add_system_message("")
            chat_area.add_system_message("Ready! Type your message below.")
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            chat_area.add_error_message(f"Initialization failed: {e}")
    
    def _update_header_counts(self, servers: int, tools: int, resources: int):
        """Update the header with current server, tool and resource counts"""
        try:
            header_right = self.query_one("#header-right", Static)
            header_right.update(f"Servers: {servers} | Tools: {tools} | Resources: {resources}")
        except Exception as e:
            logger.warning(f"Failed to update header counts: {e}")
    
    def watch_audio_state(self) -> None:
        try:
            # Use your chat area/system log for output
            chat_area = self.query_one("#chat-area", expect_none=True)
            debug_message = f"WATCH_AUDIO_STATE: audio_state is now '{self.audio_state}'"
            if chat_area:
                chat_area.add_system_message(debug_message)
            else:
                print(debug_message)
    
            widget = self.query_one("#audio-status", expect_none=True)
            widget_message = f"WIDGET: {widget!r}"
            if chat_area:
                chat_area.add_system_message(widget_message)
            else:
                print(widget_message)
    
            display_text = {
                "listening": "🔴 Listening",
                "connecting": "⏳ Connecting",
                "transcribing": "🟡 Transcribing",
                "speaking": "🔵 Speaking",
                "error": "❌ Error",
                "off": "🔇 Off"
            }.get(self.audio_state, f"⚪ {self.audio_state}")
    
            if widget is not None:
                widget.update(display_text)  # If you want to test: Text(display_text, style="bold on yellow")
                widget.refresh()  # Try to force repaint if stuck
                if chat_area:
                    chat_area.add_system_message(f"Updated widget with: {display_text}")
            else:
                err = "Widget #audio-status NOT FOUND!!"
                if chat_area:
                    chat_area.add_system_message(err)
                else:
                    print(err)
    
        except Exception as e:
            error_msg = f"Error in watch_audio_state: {e}"
            if chat_area:
                chat_area.add_system_message(error_msg)
            else:
                print(error_msg)

    def watch_audio_state(self) -> None:
        """Watch reactive audio state and update UI"""
        try:
            logger.info(f"🔊 WATCH: audio_state changed to '{self.audio_state}'")
            
            # Map states to icons
            if self.audio_state == "listening":
                display_text = "🔴 Listening"
            elif self.audio_state == "connecting":
                display_text = "⏳ Connecting"
            elif self.audio_state == "transcribing":
                display_text = "🟡 Transcribing"
            elif self.audio_state == "speaking":
                display_text = "🔵 Speaking"
            elif self.audio_state == "error":
                display_text = "❌ Error"
            elif self.audio_state == "off":
                display_text = "🔇 Off"
            else:
                display_text = f"⚪ {self.audio_state}"
            
            # Update header status
            try:
                self.query_one("#audio-status").update(display_text)
                logger.info(f"🔊 WATCH: Successfully updated #audio-status to '{display_text}'")
            except Exception as e:
                logger.error(f"🔊 WATCH: Failed to update #audio-status: {e}")
            
            # Also update the audio widgets if available
            if self.audio_manager:
                # Map string back to AudioState enum for widgets
                state_to_enum = {
                    "off": AudioState.OFF,
                    "connecting": AudioState.CONNECTING,
                    "listening": AudioState.LISTENING, 
                    "transcribing": AudioState.TRANSCRIBING,
                    "speaking": AudioState.SPEAKING,
                    "error": AudioState.ERROR
                }
                audio_state_enum = state_to_enum.get(self.audio_state, AudioState.LISTENING)
                
                try:
                    # Update status bar
                    status_bar = self.query_one("#audio-status-bar", SimpleAudioBar)
                    status_bar.update_audio_state(audio_state_enum)
                    logger.info(f"🔊 WATCH: Updated status bar")
                except Exception as e:
                    logger.error(f"🔊 WATCH: Failed to update status bar: {e}")
                
                try:
                    # Update mic widget  
                    mic_widget = self.query_one("#mic-widget", MicrophoneWidget)
                    mic_widget.set_state(audio_state_enum, getattr(self.audio_manager, 'audio_level', 0.0))
                    logger.info(f"🔊 WATCH: Updated mic widget")
                except Exception as e:
                    logger.error(f"🔊 WATCH: Failed to update mic widget: {e}")
            
        except Exception as e:
            logger.error(f"🔊 WATCH: Error in watch_audio_state: {e}")
    
    def _setup_audio_state_monitoring(self):
        """Setup monitoring of audio manager state changes"""
        try:
            # The callback is already set in _initialize_audio_widgets
            # This method is kept for compatibility but does nothing
            logger.info("✅ Audio state monitoring already setup in _initialize_audio_widgets")
            
        except Exception as e:
            logger.warning(f"Could not setup audio state monitoring: {e}")
    
    def _force_test_state_change(self):
        """FORCE TEST - cycle through states to test UI updates"""
        test_states = ["ready", "transcribing", "speaking", "ready"]
        if not hasattr(self, '_test_state_index'):
            self._test_state_index = 0
        
        state = test_states[self._test_state_index]
        logger.info(f"🧪 FORCE TEST: Setting UI to {state}")
        
        # Show in chat so you can see it
        try:
            chat_area = self.query_one("#chat-area", ChatArea)
            chat_area.add_system_message(f"🧪 FORCE TEST: Setting UI to {state}")
        except:
            pass
        
        self.audio_state = state
        
        self._test_state_index = (self._test_state_index + 1) % len(test_states)
    
    
    
    
    def on_input_submitted(self, event):
        """Handle user input submission"""
        if event.input.id == "chat-input" and event.value.strip():
            message = event.value.strip()
            event.input.value = ""  # Clear input
            
            if self.is_initialized:
                self.handle_message(message)
            else:
                chat_area = self.query_one("#chat-area", ChatArea)
                chat_area.add_error_message("System not ready yet, please wait...")
    
    def handle_message(self, message: str):
        """Handle user message"""
        chat_area = self.query_one("#chat-area", ChatArea)
        
        # Add user message
        chat_area.add_user_message(message)
        
        # Log user message
        if hasattr(self, 'session_logger'):
            self.session_logger.log_user_message(message)
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Show thinking indicator
        chat_area.add_thinking_indicator()
        
        # Process message asynchronously using Textual's run_worker
        self.run_worker(self._process_message(message, chat_area), exclusive=False)
    
    async def _process_message(self, message: str, chat_area: ChatArea):
        """Process user message with LLM and tools"""
        try:
            # Get available tools
            tools = self.mcp_manager.get_tools()
            
            # Log available tools for debugging DELETE issue
            if self.config.debug_level >= 1:
                delete_tools = [t for t in tools if 'delete' in t.name.lower() and 'instance' in t.name.lower()]
                if delete_tools:
                    chat_area.add_system_message(f"🔍 Found {len(delete_tools)} DELETE instance tools:")
                    for tool in delete_tools:
                        chat_area.add_system_message(f"   - {tool.name}")
                else:
                    chat_area.add_system_message("🔍 No DELETE instance tools found in tool list")
            
            # Convert to LLM format
            llm_tools = []
            for tool in tools:
                llm_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema
                })
            
            # Use JSON when audio is enabled, regardless of tools
            messages = self.conversation_history.copy()
            audio_enabled = self.audio_manager and self.audio_manager.mode == "input_only"
            use_json = audio_enabled
            
            if self.config.debug_level >= 2:
                chat_area.add_system_message(f"🔧 DEBUG: audio_manager={bool(self.audio_manager)}, mode={getattr(self.audio_manager, 'mode', 'None') if self.audio_manager else 'N/A'}")
                chat_area.add_system_message(f"🔧 DEBUG: audio_enabled={audio_enabled}, llm_tools={bool(llm_tools)}, use_json={use_json}")
            
            # Add TTS instruction when audio is enabled
            if audio_enabled:
                tts_instruction = """

ADDITIONAL INSTRUCTION: When responding, please include at the very end a section like this:

---TTS---
[Super casual, natural response like you're talking to a friend - use contractions, informal language. NEVER mention technical function names or tool names - convert them to natural language.]
---END TTS---

Examples: "Yep, found 3 VMs" or "All good here" or "Got it" or "Looks solid" or "Everything's running fine" or "Found what you need" or "Checking your virtual machines" or "Looking at your infrastructure". 

CRITICAL: Instead of saying technical names like "vme_compute_listInstances", say natural things like "checking your VMs" or "looking at your virtual machines" or "getting your instance list". Keep it short, natural, and conversational - like texting a friend."""
                
                if self.config.debug_level >= 2:
                    chat_area.add_system_message("🔧 Audio enabled - appending TTS instruction")
                
                # Find existing system message and append TTS instruction
                for msg in messages:
                    if msg.get("role") == "system":
                        msg["content"] += tts_instruction
                        break
                else:
                    # No system message found, create one
                    system_msg = {
                        "role": "system", 
                        "content": tts_instruction.strip()
                    }
                    messages.insert(0, system_msg)
            else:
                if self.config.debug_level >= 2:
                    chat_area.add_system_message("🔧 Audio disabled - normal response only")
            
            response = await self.llm_manager.chat(
                messages=messages,
                tools=llm_tools if llm_tools else None,
                force_json=False  # Never force JSON - handle audio post-processing
            )
            
            if self.config.debug_level >= 2:
                chat_area.add_system_message(f"🔧 LLM response type: {type(response.get('content', ''))}")
                chat_area.add_system_message(f"🔧 LLM response preview: {str(response.get('content', ''))[:100]}...")
            
            # Remove thinking indicator
            chat_area.remove_thinking_indicator()
            
            # Handle response
            if response.get("tool_calls"):
                # Handle tool calls
                await self._handle_tool_calls(response, chat_area)
            else:
                # Direct response
                content = response.get("content", "No response from LLM")
                self._display_response(content, chat_area)
                self.conversation_history.append({"role": "assistant", "content": content})
                
        except Exception as e:
            logger.error(f"Message processing failed: {e}")
            chat_area.remove_thinking_indicator()
            chat_area.add_error_message(f"Processing failed: {e}")
    
    async def _handle_tool_calls(self, response, chat_area: ChatArea):
        """Handle tool calls from LLM"""
        try:
            # Add assistant message with tool calls
            assistant_content = response.get("content", "")
            if assistant_content:
                # Clean content for display (remove TTS section)
                display_content = self._remove_tts_section(assistant_content)
                chat_area.add_assistant_message(display_content)
                
                # Log assistant message
                if hasattr(self, 'session_logger'):
                    self.session_logger.log_assistant_message(
                        content=display_content,
                        response_time_ms=0,  # TODO: Track actual response time
                        tts_enabled=False
                    )
                
                # Generate TTS for assistant content if audio enabled
                audio_enabled = self.audio_manager and self.audio_manager.mode == "input_only"
                if audio_enabled:
                    if self.config.debug_level >= 2:
                        chat_area.add_system_message("TTS: Generating TTS from tool call assistant content")
                    
                    # Extract TTS section from assistant content
                    tts_text = self._extract_tts_section(assistant_content)
                    
                    self._send_audio_response(tts_text, chat_area)
            
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_content,
                "tool_calls": response["tool_calls"]
            })
            
            # Execute tool calls in parallel
            async def execute_tool_call(tool_call):
                tool_name = tool_call.get("name")
                arguments = tool_call.get("arguments", {})
                tool_id = tool_call.get("id")
                
                try:
                    chat_area.add_system_message(f"🔧 Calling tool: {tool_name}")
                    
                    # Log tool call start
                    if hasattr(self, 'session_logger'):
                        self.session_logger.log_error(f"🔧 Calling tool: {tool_name}", error_type="tool_call")
                    
                    start_time = time.time()
                    result = await self.mcp_manager.call_tool(tool_name, arguments)
                    execution_time = (time.time() - start_time) * 1000
                    
                    # Display result in chat area
                    result_str = str(result)
                    if len(result_str) > 500:
                        chat_area.add_system_message(f"✅ Tool result ({len(result_str)} chars): {result_str[:500]}...")
                    else:
                        chat_area.add_system_message(f"✅ Tool result: {result_str}")
                    
                    # Log tool call result
                    if hasattr(self, 'session_logger'):
                        self.session_logger.log_tool_call_result(
                            tool_call_id=tool_id,
                            tool_name=tool_name,
                            status=ToolStatus.SUCCESS,
                            result=result_str
                        )
                        self.session_logger.log_error(
                            f"✅ Tool completed: {tool_name} ({execution_time:.0f}ms)", 
                            error_type="tool_result"
                        )
                    
                    return {
                        "role": "tool",
                        "content": result_str,
                        "tool_call_id": tool_id
                    }
                except Exception as e:
                    error_msg = f"Tool call failed: {e}"
                    chat_area.add_error_message(error_msg)
                    
                    # Add debug info for tool call failures
                    if self.config.debug_level >= 1:
                        chat_area.add_system_message(f"🔧 Tool call debug:")
                        chat_area.add_system_message(f"   Tool: {tool_name}")
                        chat_area.add_system_message(f"   Arguments: {arguments}")
                        chat_area.add_system_message(f"   Error type: {type(e).__name__}")
                        chat_area.add_system_message(f"   Error: {str(e)}")
                    
                    # Log tool call failure
                    if hasattr(self, 'session_logger'):
                        self.session_logger.log_tool_call_result(
                            tool_call_id=tool_id,
                            tool_name=tool_name,
                            status=ToolStatus.FAILED,
                            error_message=str(e)
                        )
                        self.session_logger.log_error(
                            f"❌ Tool failed: {tool_name} - {str(e)}", 
                            error_type="tool_error"
                        )
                    
                    return {
                        "role": "tool",
                        "content": error_msg,
                        "tool_call_id": tool_id
                    }
            
            # Execute all tool calls in parallel
            if response["tool_calls"]:
                chat_area.add_system_message(f"🚀 Executing {len(response['tool_calls'])} tool calls in parallel...")
                tool_results = await asyncio.gather(*[execute_tool_call(call) for call in response["tool_calls"]])
                
                # Add all results to conversation history in order
                for result in tool_results:
                    self.conversation_history.append(result)
            
            # Get final response from LLM
            chat_area.add_thinking_indicator()
            final_response = await self.llm_manager.chat(
                messages=self.conversation_history
            )
            
            chat_area.remove_thinking_indicator()
            
            if final_response.get("content"):
                final_content = final_response["content"]
                # Clean content for display (remove TTS section)
                display_content = self._remove_tts_section(final_content)
                chat_area.add_assistant_message(display_content)
                
                # Log final assistant response
                if hasattr(self, 'session_logger'):
                    self.session_logger.log_assistant_message(
                        content=display_content,
                        response_time_ms=0,  # TODO: Track actual response time
                        tts_enabled=False
                    )
                
                # Generate TTS for final response if audio enabled
                audio_enabled = self.audio_manager and self.audio_manager.mode == "input_only"
                if audio_enabled:
                    if self.config.debug_level >= 2:
                        chat_area.add_system_message("TTS: Generating TTS from final tool response")
                    
                    # Extract TTS section from final content
                    tts_text = self._extract_tts_section(final_content)
                    
                    self._send_audio_response(tts_text, chat_area)
                
                self.conversation_history.append({
                    "role": "assistant", 
                    "content": final_content
                })
            
        except Exception as e:
            logger.error(f"Tool call handling failed: {e}")
            chat_area.remove_thinking_indicator()
            chat_area.add_error_message(f"Tool execution failed: {e}")
    
    async def action_quit(self):
        """Clean up and quit"""
        try:
            logger.info("Shutting down VME client...")
            
            # Finalize session log
            if hasattr(self, 'session_logger'):
                log_file = self.session_logger.finalize_session()
                logger.info(f"Session log saved to: {log_file}")
            
            # Disconnect managers
            if hasattr(self, 'mcp_manager') and self.mcp_manager:
                await self.mcp_manager.disconnect()
            
            if hasattr(self, 'audio_manager') and self.audio_manager:
                await self.audio_manager.disconnect()
                
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        finally:
            self.exit()
    
    async def _initialize_audio_widgets(self):
        """Initialize audio widgets and connect to Realtime API"""
        logger.info("🎧 Initializing audio widgets...")
        try:
            # Initialize audio manager
            logger.info("🎧 Initializing audio manager...")
            await self.audio_manager.initialize()
            
            # Get widgets
            try:
                logger.info("🎧 Finding audio widgets...")
                status_bar = self.query_one("#audio-status-bar", SimpleAudioBar)
                mic_widget = self.query_one("#mic-widget", MicrophoneWidget)
                logger.info("🎧 Found both audio widgets successfully")
                
                # Set up callbacks for flexible audio manager
                self.audio_manager.on_audio_level = self._on_audio_level_changed
                self.audio_manager.on_transcription = self._on_transcription_received
                self.audio_manager.on_transcription_partial = self._on_transcription_partial
                self.audio_manager.on_assistant_text = self._on_assistant_text_received
                self.audio_manager.on_state_change = self._on_audio_state_changed
                self.audio_manager.on_speech_end_submit = self._on_speech_end_submit
                self.audio_manager.on_debug_message = self._on_debug_message
                
                # DEBUG: Verify all callbacks are properly set
                logger.info(f"🔥 CALLBACKS SET:")
                logger.info(f"  - on_state_change: {self.audio_manager.on_state_change is not None}")
                logger.info(f"  - on_audio_level: {self.audio_manager.on_audio_level is not None}")
                logger.info(f"  - on_transcription: {self.audio_manager.on_transcription is not None}")
                logger.info(f"  - on_speech_end_submit: {self.audio_manager.on_speech_end_submit is not None}")
                logger.info(f"  - on_debug_message: {self.audio_manager.on_debug_message is not None}")
                
                # Test immediate state change to verify callback works
                logger.info("🔥 TESTING: Triggering immediate state change to verify callback...")
                self._on_audio_state_changed(AudioState.LISTENING)
                logger.info("🔥 TESTING: Test state change completed")
                
                # Try to connect
                logger.info("🎧 Connecting audio manager...")
                connected = await self.audio_manager.connect()
                if connected:
                    logger.info("🎧 Audio connected successfully")
                    status_bar.update_connection_state("connected")
                    status_bar.update_audio_state(AudioState.LISTENING)
                    mic_widget.set_state(AudioState.LISTENING, 0.0)
                    
                    if self.config.debug_level >= 1:
                        chat_area = self.query_one("#chat-area", ChatArea)
                        chat_area.add_system_message(f"🔧 WebSocket connected to: {self.audio_manager.url}")
                    
                    # Start recording simulation
                    await self.audio_manager.start_recording()
                else:
                    logger.error("🎧 Audio connection failed")
                    status_bar.update_connection_state("error")
                    status_bar.update_audio_state(AudioState.ERROR)
                    mic_widget.set_state(AudioState.ERROR, 0.0)
                    
                    if self.config.debug_level >= 1:
                        chat_area = self.query_one("#chat-area", ChatArea)
                        chat_area.add_error_message("🔧 WebSocket connection FAILED")
                    
            except Exception as e:
                logger.error(f"❌ Failed to find audio widgets: {e}")
                logger.exception("Widget query exception:")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize audio: {e}")
            logger.exception("Audio initialization exception:")
    
    async def _on_audio_level_changed(self, level):
        """Handle audio level changes"""
        try:
            mic_widget = self.query_one("#mic-widget", MicrophoneWidget)
            mic_widget.set_state(self.audio_manager.state, level)
            
            status_bar = self.query_one("#audio-status-bar", SimpleAudioBar)
            status_bar.update_audio_state(self.audio_manager.state)
        except Exception as e:
            logger.error(f"Failed to update audio level: {e}")
    
    async def _on_transcription_received(self, text):
        """Handle final user speech transcription"""
        try:
            logger.info(f"📝 Final transcription: {text}")
            # In input_only mode, this gets auto-submitted via on_speech_end_submit
        except Exception as e:
            logger.error(f"Failed to handle transcription: {e}")
    
    def _on_transcription_partial(self, text_delta):
        """Handle partial transcription (live typing effect)"""
        try:
            logger.info(f"📝 Partial transcription delta: '{text_delta}'")
            if hasattr(self.audio_manager.config, 'show_transcription_in_input') and self.audio_manager.config.show_transcription_in_input:
                # Update input field with live transcription
                input_widget = self.query_one("#chat-input", Input)
                input_widget.value = text_delta
                logger.info(f"📝 Updated input field with: '{text_delta}'")
        except Exception as e:
            logger.error(f"Failed to handle partial transcription: {e}")
    
    async def _on_speech_end_submit(self, text):
        """Handle auto-submit when speech ends (input_only mode)"""
        try:
            logger.info(f"🗣️  Auto-submitting: {text}")
            
            chat_area = self.query_one("#chat-area", ChatArea)
            
            if self.config.debug_level >= 1:
                chat_area.add_system_message(f"🔄 Sending to Claude: {text}")
            
            # Clear input field
            input_widget = self.query_one("#chat-input", Input)
            input_widget.value = ""
            
            # Send to Claude via existing message handling (this will add the user message)
            self.handle_message(text)
            
        except Exception as e:
            logger.error(f"Failed to handle speech end submit: {e}")
    
    async def _on_assistant_text_received(self, text_delta):
        """Handle assistant text response (full_conversation mode only)"""
        try:
            # For now, just log it - could accumulate and display later
            logger.debug(f"🤖 Assistant: {text_delta}")
        except Exception as e:
            logger.error(f"Failed to handle assistant text: {e}")
    
    def _on_audio_state_changed(self, new_state):
        """EXACT same fix as working test - use create_task"""
        try:
            logger.info(f"🔥 CALLBACK RECEIVED: {new_state}")
            
            # Map AudioState enum to string for reactive property
            state_mapping = {
                AudioState.OFF: "off",
                AudioState.LISTENING: "listening", 
                AudioState.TRANSCRIBING: "transcribing",
                AudioState.SPEAKING: "speaking",
                AudioState.ERROR: "error"
            }
            
            state_str = state_mapping.get(new_state, "listening")
            
            # EXACT same fix as working test - schedule after UI is ready
            async def update_state():
                self.audio_state = state_str
                logger.info(f"🔥 REACTIVE STATE SET: {state_str}")
            
            import asyncio
            asyncio.create_task(update_state())
            
        except Exception as e:
            logger.error(f"Failed to set audio state: {e}")
    
    
    def on_vme_chat_app_audio_state_changed(self, message: AudioStateChanged) -> None:
        """Handle audio state change messages from background threads"""
        try:
            logger.info(f"🔊 MESSAGE HANDLER: Received audio state change to {message.state}")
            
            # Map AudioState enum to string for reactive property
            state_mapping = {
                AudioState.OFF: "off",
                AudioState.CONNECTING: "connecting",
                AudioState.LISTENING: "listening", 
                AudioState.TRANSCRIBING: "transcribing",
                AudioState.SPEAKING: "speaking",
                AudioState.ERROR: "error"
            }
            
            state_str = state_mapping.get(message.state, "listening")
            
            # Update reactive property (this will trigger watch_audio_state)
            self.audio_state = state_str
            logger.info(f"🔊 Set reactive audio_state to: {state_str}")
            
            # Debug to chat if enabled
            if self.config.debug_level >= 1:
                chat_area = self.query_one("#chat-area", ChatArea)
                chat_area.add_system_message(f"🔊 Audio state: {message.state.value} → {state_str}")
            
        except Exception as e:
            logger.error(f"Failed to handle audio state change message: {e}")
    
    def on_audio_state_changed(self, message: AudioStateChanged) -> None:
        """Alternative handler name - redirect to main handler"""
        self.on_vme_chat_app_audio_state_changed(message)
    
    
    def _on_debug_message(self, message):
        """Handle debug messages from audio manager"""
        try:
            # Determine debug level based on message content
            level = 1  # Default level
            if "🎵 Audio:" in message or "RMS:" in message:
                level = 3  # High frequency audio messages
            elif "DELTA:" in message or "📥" in message:
                level = 3  # Verbose transcription events
            elif "COMPLETED:" in message or "TRIGGERED" in message:
                level = 2  # Important events
            
            if self.config.debug_level >= level:
                chat_area = self.query_one("#chat-area", ChatArea)
                chat_area.add_system_message(message)
        except Exception as e:
            logger.error(f"Failed to handle debug message: {e}")
    
    def _display_response(self, content, chat_area):
        """Display response content and generate TTS if audio enabled"""
        audio_enabled = self.audio_manager and self.audio_manager.mode == "input_only"
        
        if self.config.debug_level >= 2:
            chat_area.add_system_message(f"🔍 Displaying normal response, audio_enabled={audio_enabled}")
        
        try:
            # Clean content for display (remove TTS section) and display
            display_content = self._remove_tts_section(content)
            chat_area.add_assistant_message(display_content)
            
            # Log assistant response
            if hasattr(self, 'session_logger'):
                response_time = 0  # TODO: Track actual response time
                self.session_logger.log_assistant_message(
                    content=display_content,
                    response_time_ms=response_time,
                    tts_enabled=audio_enabled
                )
            
            # Generate TTS summary if audio is enabled
            if self.config.debug_level >= 2:
                chat_area.add_system_message(f"TTS: DEBUG - audio_enabled={audio_enabled}, audio_manager={bool(self.audio_manager)}")
                if self.audio_manager:
                    chat_area.add_system_message(f"TTS: DEBUG - audio_manager.mode={getattr(self.audio_manager, 'mode', 'None')}")
            
            if audio_enabled:
                if self.config.debug_level >= 2:
                    chat_area.add_system_message("TTS: Generating audio summary from response")
                
                # Extract TTS section
                tts_text = self._extract_tts_section(content)
                
                self._send_audio_response(tts_text, chat_area)
            else:
                # Force TTS test regardless of audio settings
                if self.config.debug_level >= 2:
                    chat_area.add_system_message("TTS: FORCED TEST - audio disabled but showing TTS anyway")
                    test_tts = content[:50] + "..." if len(content) > 50 else content
                    chat_area.add_system_message(f"TTS: {test_tts}")
            
        except Exception as e:
            logger.error(f"Error displaying response: {e}")
            # Fallback to regular display
            chat_area.add_assistant_message(content)
    
    def _attempt_json_repair(self, content, chat_area):
        """Attempt to repair malformed JSON responses"""
        try:
            # Common repair attempts for truncated JSON
            content = content.strip()
            
            # If it starts with { but doesn't end with }, try to close it
            if content.startswith('{') and not content.endswith('}'):
                if self.config.debug_level >= 2:
                    chat_area.add_system_message("🔧 Attempting JSON repair...")
                
                # Find the last complete quote
                if content.count('"') % 2 == 1:
                    # Odd number of quotes, add closing quote
                    content += '"'
                    if self.config.debug_level >= 2:
                        chat_area.add_system_message("🔧 Added missing closing quote")
                
                # Add closing brace
                content += '}'
                if self.config.debug_level >= 2:
                    chat_area.add_system_message(f"🔧 Added closing brace. Result: ...{content[-50:]}")
                
                return content
                
        except Exception as e:
            if self.config.debug_level >= 2:
                chat_area.add_system_message(f"🔧 JSON repair failed: {e}")
        
        return None
    
    def _remove_tts_section(self, content):
        """Remove TTS section from content for clean display"""
        import re
        
        # Remove the TTS section completely
        tts_pattern = r'---TTS---.*?---END TTS---'
        cleaned_content = re.sub(tts_pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Clean up any extra whitespace
        cleaned_content = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_content)  # Multiple newlines to double
        cleaned_content = cleaned_content.strip()
        
        return cleaned_content
    
    def _extract_tts_section(self, content):
        """Extract TTS section from LLM response"""
        import re
        
        # Look for TTS section in the content
        tts_pattern = r'---TTS---(.*?)---END TTS---'
        match = re.search(tts_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            tts_text = match.group(1).strip()
            if self.config.debug_level >= 2:
                # Will be shown when this returns to the calling function
                pass
            return tts_text
        else:
            # Fallback: create simple summary from first sentence
            sentences = content.split('. ')
            fallback_text = sentences[0]
            if not fallback_text.endswith('.'):
                fallback_text += '.'
            
            if len(fallback_text) > 150:
                fallback_text = fallback_text[:150] + "..."
            
            return fallback_text
    
    def _send_audio_response(self, audio_text, chat_area):
        """Send text to audio manager for text-to-speech"""
        try:
            if self.audio_manager and hasattr(self.audio_manager, 'send_text_for_speech'):
                # If audio manager supports TTS
                if self.config.debug_level >= 2:
                    chat_area.add_system_message(f"TTS: Sending to OpenAI TTS API: {audio_text}")
                
                # TRIGGER SPEAKING STATE - same fix as listening/transcribing
                async def set_speaking_state():
                    self.audio_state = "speaking"
                    logger.info(f"🔥 TTS STARTED - Set state to speaking")
                
                import asyncio
                asyncio.create_task(set_speaking_state())
                
                # Use asyncio to call the async TTS method
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're already in an async context, schedule it
                    asyncio.create_task(self.audio_manager.send_text_for_speech(audio_text))
                else:
                    # Run in the event loop
                    loop.run_until_complete(self.audio_manager.send_text_for_speech(audio_text))
                    
            else:
                # Show what would go to TTS as debug level 2 message in chat
                if self.config.debug_level >= 2:
                    chat_area.add_system_message(f"TTS: {audio_text}")
                # Also log for debugging
                logger.info(f"🔊 Audio response: {audio_text}")
        except Exception as e:
            if self.config.debug_level >= 2:
                chat_area.add_system_message(f"TTS: ERROR - {e}")
            logger.error(f"Failed to send audio response: {e}")
