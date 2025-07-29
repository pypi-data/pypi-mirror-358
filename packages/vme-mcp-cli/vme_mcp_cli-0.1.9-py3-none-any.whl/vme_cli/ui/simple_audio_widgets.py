"""
Simple audio widgets for VME Textual CLI Client
Clean, visible microphone indicators without complex audio dependencies
"""

import asyncio
import math
from typing import Optional
from enum import Enum

from textual.widget import Widget
from textual.reactive import reactive
from textual.containers import Horizontal
from rich.text import Text
from rich.panel import Panel
from rich.align import Align

class AudioState(Enum):
    OFF = "off"
    CONNECTING = "connecting"
    LISTENING = "listening"
    TRANSCRIBING = "transcribing"  # Added to match audio manager
    SPEAKING = "speaking"
    ERROR = "error"

class MicrophoneWidget(Widget):
    """Simple, visible microphone status widget"""
    
    DEFAULT_CSS = """
    MicrophoneWidget {
        width: 20;
        height: 4;
        margin: 0 1;
    }
    """
    
    state = reactive(AudioState.OFF)
    level = reactive(0.0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.animation_frame = 0
        self.animation_timer = None
    
    def render(self) -> Panel:
        """Render the microphone widget"""
        
        # Get state-specific styling
        if self.state == AudioState.OFF:
            icon = "🔇"
            status = "MICROPHONE OFF"
            border_color = "dim white"
            text_color = "dim white"
        elif self.state == AudioState.CONNECTING:
            icon = "⏳"
            status = "CONNECTING..."
            border_color = "yellow"
            text_color = "yellow"
        elif self.state == AudioState.LISTENING:
            icon = "🎤" 
            status = "LISTENING"
            border_color = "blue"
            text_color = "bright_blue"
        elif self.state == AudioState.TRANSCRIBING:
            icon = "📝"
            status = "TRANSCRIBING"
            border_color = "yellow"
            text_color = "bright_yellow"
        elif self.state == AudioState.SPEAKING:
            icon = "🗣️"
            status = "SPEAKING"
            border_color = "green"
            text_color = "bright_green"
        else:  # ERROR
            icon = "❌"
            status = "ERROR"
            border_color = "red"
            text_color = "bright_red"
        
        # Create level visualization
        level_bars = self._create_level_bars()
        
        # Build content
        content = Text()
        content.append(f"{icon} {status}\n", style=f"bold {text_color}")
        content.append(level_bars, style=text_color)
        
        return Panel(
            Align.center(content, vertical="middle"),
            border_style=border_color,
            title="AUDIO STATUS",
            title_align="center"
        )
    
    def _create_level_bars(self) -> str:
        """Create audio level visualization bars"""
        if self.state in [AudioState.OFF, AudioState.ERROR]:
            return "[▪▪▪▪▪▪▪▪▪▪]"
        
        # Create animated level bars
        filled_bars = int(self.level * 10)
        
        # Add pulsing effect for listening
        if self.state == AudioState.LISTENING:
            pulse = 0.3 + 0.7 * (0.5 + 0.5 * math.sin(self.animation_frame * 0.5))
            filled_bars = max(1, int(pulse * 3))
        
        bars = "█" * filled_bars + "▪" * (10 - filled_bars)
        return f"[{bars}]"
    
    def set_state(self, state: AudioState, level: float = 0.0):
        """Update widget state and level"""
        self.state = state
        self.level = max(0.0, min(1.0, level))
        
        # Force refresh for threading
        self.refresh()
        
        # Start/stop animation based on state
        if state in [AudioState.LISTENING, AudioState.CONNECTING]:
            self._start_animation()
        else:
            self._stop_animation()
    
    def _start_animation(self):
        """Start animation timer"""
        if self.animation_timer is None:
            self.animation_timer = self.set_interval(0.2, self._animate_frame)
    
    def _stop_animation(self):
        """Stop animation timer"""
        if self.animation_timer:
            self.animation_timer.stop()
            self.animation_timer = None
        self.animation_frame = 0
    
    def _animate_frame(self):
        """Animate one frame"""
        self.animation_frame += 1
        self.refresh()

class AudioStatusPanel(Widget):
    """Complete audio status panel"""
    
    DEFAULT_CSS = """
    AudioStatusPanel {
        height: 6;
        dock: bottom;
        background: #161b22;
        border-top: solid #30363d;
        padding: 1;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mic_widget = MicrophoneWidget()
        self.connection_status = "Disconnected"
        self.api_status = "Not Connected"
    
    def compose(self):
        """Compose the audio status panel"""
        with Horizontal():
            yield self.mic_widget
            yield ConnectionStatusWidget()

class ConnectionStatusWidget(Widget):
    """Simple connection status display"""
    
    DEFAULT_CSS = """
    ConnectionStatusWidget {
        width: 1fr;
        margin: 0 1;
    }
    """
    
    connection_state = reactive("disconnected")
    api_state = reactive("disconnected")
    
    def render(self) -> Panel:
        """Render connection status"""
        
        # Connection status
        if self.connection_state == "connected":
            conn_icon = "🔗"
            conn_text = "REALTIME API CONNECTED"
            conn_color = "green"
        elif self.connection_state == "connecting":
            conn_icon = "⏳"
            conn_text = "CONNECTING TO REALTIME API"
            conn_color = "yellow"
        else:
            conn_icon = "❌"
            conn_text = "REALTIME API OFFLINE"
            conn_color = "red"
        
        # Build content
        content = Text()
        content.append(f"{conn_icon} {conn_text}\n", style=f"bold {conn_color}")
        content.append("OpenAI Realtime API Status\n", style="dim white")
        content.append("Audio streaming for voice chat", style="dim white")
        
        return Panel(
            content,
            border_style=conn_color,
            title="CONNECTION",
            title_align="center"
        )
    
    def set_connection_state(self, state: str):
        """Update connection state"""
        self.connection_state = state

class SimpleAudioBar(Widget):
    """Minimal audio status bar for header"""
    
    DEFAULT_CSS = """
    SimpleAudioBar {
        height: 1;
        dock: top;
        background: #21262d;
        padding: 0 2;
    }
    """
    
    audio_state = reactive(AudioState.OFF)
    connection_state = reactive("disconnected")
    
    def render(self) -> Text:
        """Render simple status line"""
        
        # Audio status
        if self.audio_state == AudioState.LISTENING:
            audio_status = "🎤 LISTENING"
            audio_color = "blue"
        elif self.audio_state == AudioState.TRANSCRIBING:
            audio_status = "📝 TRANSCRIBING"
            audio_color = "yellow"
        elif self.audio_state == AudioState.SPEAKING:
            audio_status = "🗣️ SPEAKING"
            audio_color = "green"
        elif self.audio_state == AudioState.CONNECTING:
            audio_status = "⏳ CONNECTING"
            audio_color = "yellow"
        elif self.audio_state == AudioState.ERROR:
            audio_status = "❌ ERROR"
            audio_color = "red"
        else:
            audio_status = "🔇 MUTED"
            audio_color = "dim white"
        
        # Connection status
        if self.connection_state == "connected":
            conn_status = "🔗 REALTIME"
            conn_color = "green"
        else:
            conn_status = "❌ OFFLINE"
            conn_color = "red"
        
        # Combine
        status_line = Text()
        status_line.append(audio_status, style=f"bold {audio_color}")
        status_line.append(" │ ", style="dim white")
        status_line.append(conn_status, style=f"bold {conn_color}")
        
        return status_line
    
    def update_audio_state(self, state: AudioState):
        """Update audio state"""
        self.audio_state = state
        self.refresh()
    
    def update_connection_state(self, state: str):
        """Update connection state"""
        self.connection_state = state
        self.refresh()