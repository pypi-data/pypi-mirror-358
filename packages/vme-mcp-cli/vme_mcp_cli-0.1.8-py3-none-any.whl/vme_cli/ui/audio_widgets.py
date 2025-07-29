"""
Audio UI widgets for VME Textual CLI Client
Sophisticated microphone indicators and audio visualizations
"""

import asyncio
import math
from typing import Optional, List
from enum import Enum

from textual.widget import Widget
from textual.reactive import reactive
from textual.renderables.gradient import LinearGradient
from rich.console import Console, ConsoleOptions, RenderResult
from rich.text import Text
from rich.align import Align
from rich.panel import Panel
from rich.bar import Bar
from rich import box

class MicState(Enum):
    INACTIVE = "inactive"
    LISTENING = "listening" 
    SPEAKING = "speaking"
    ERROR = "error"

class MicrophoneIndicator(Widget):
    """Sophisticated microphone activity indicator with pulsing effect"""
    
    DEFAULT_CSS = """
    MicrophoneIndicator {
        width: 6;
        height: 3;
        margin: 0 1;
    }
    """
    
    state = reactive(MicState.INACTIVE)
    audio_level = reactive(0.0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pulse_frame = 0
        self.pulse_timer = None
        
    def render(self) -> Panel:
        """Render the microphone indicator"""
        
        # Get colors based on state
        if self.state == MicState.INACTIVE:
            primary_color = "#404040"
            secondary_color = "#2a2a2a"
            border_color = "#303030"
            status_text = "OFF"
        elif self.state == MicState.LISTENING:
            # Pulsing blue for listening
            intensity = 0.5 + 0.5 * math.sin(self.pulse_frame * 0.3)
            primary_color = f"rgb({int(64 * intensity)},{int(164 * intensity)},{int(255 * intensity)})"
            secondary_color = f"rgb({int(32 * intensity)},{int(82 * intensity)},{int(128 * intensity)})"
            border_color = "#40a4ff"
            status_text = "LIVE"
        elif self.state == MicState.SPEAKING:
            # Animated green for speaking
            intensity = 0.3 + 0.7 * self.audio_level
            primary_color = f"rgb({int(63 * intensity)},{int(185 * intensity)},{int(80 * intensity)})"
            secondary_color = f"rgb({int(31 * intensity)},{int(92 * intensity)},{int(40 * intensity)})"
            border_color = "#3fb950"
            status_text = "TALK"
        else:  # ERROR
            primary_color = "#f85149"
            secondary_color = "#8b1538"
            border_color = "#f85149"
            status_text = "ERR"
        
        # Create microphone visual representation
        mic_visual = self._create_mic_visual(primary_color, secondary_color)
        
        # Activity level indicator
        level_bar = self._create_level_indicator()
        
        # Combine elements
        content = Text.assemble(
            (mic_visual, ""),
            ("\n", ""),
            (f"[{status_text}]", f"bold {primary_color}"),
            ("\n", ""),
            (level_bar, "")
        )
        
        return Panel(
            Align.center(content, vertical="middle"),
            border_style=border_color,
            box=box.ROUNDED,
            padding=(0, 1),
            title="MIC" if self.state != MicState.INACTIVE else None,
            title_align="center"
        )
    
    def _create_mic_visual(self, primary_color: str, secondary_color: str) -> str:
        """Create ASCII art microphone representation"""
        if self.state == MicState.INACTIVE:
            return "╔═══╗\n║   ║\n╚═╤═╝\n  │  \n ═╧═ "
        else:
            # Animated microphone with sound waves
            wave_intensity = int(self.audio_level * 3)
            waves = ""
            if wave_intensity >= 1:
                waves += ")"
            if wave_intensity >= 2:
                waves += "))"
            if wave_intensity >= 3:
                waves += ")))"
            
            return f"╔═══╗{waves}\n║●●●║\n╚═╤═╝\n  │  \n ═╧═ "
    
    def _create_level_indicator(self) -> str:
        """Create audio level indicator bar"""
        if self.state in [MicState.INACTIVE, MicState.ERROR]:
            return "▪▪▪▪▪"
        
        # Create level bar with Unicode blocks
        level_blocks = int(self.audio_level * 5)
        full_blocks = "█" * level_blocks
        empty_blocks = "▪" * (5 - level_blocks)
        
        if self.state == MicState.LISTENING:
            color = "#40a4ff"
        else:  # SPEAKING
            color = "#3fb950"
        
        return f"[{color}]{full_blocks}[/]{empty_blocks}"
    
    def set_state(self, state: MicState):
        """Update microphone state"""
        self.state = state
        
        if state == MicState.LISTENING:
            self._start_pulse_animation()
        else:
            self._stop_pulse_animation()
    
    def set_audio_level(self, level: float):
        """Update audio level (0.0 to 1.0)"""
        self.audio_level = max(0.0, min(1.0, level))
    
    def _start_pulse_animation(self):
        """Start pulsing animation for listening state"""
        if self.pulse_timer is None:
            self.pulse_timer = self.set_interval(0.1, self._animate_pulse)
    
    def _stop_pulse_animation(self):
        """Stop pulsing animation"""
        if self.pulse_timer:
            self.pulse_timer.stop()
            self.pulse_timer = None
        self.pulse_frame = 0
    
    def _animate_pulse(self):
        """Animate one frame of the pulse effect"""
        self.pulse_frame += 1
        self.refresh()

class AudioStatusBar(Widget):
    """Combined audio status bar with microphone and connection info"""
    
    DEFAULT_CSS = """
    AudioStatusBar {
        height: 1;
        dock: top;
        background: #161b22;
        border-bottom: solid #30363d;
        padding: 0 1;
    }
    """
    
    connection_state = reactive("disconnected")
    is_recording = reactive(False)
    is_speaking = reactive(False)
    audio_level = reactive(0.0)
    
    def render(self) -> Text:
        """Render the audio status bar"""
        
        # Connection status
        if self.connection_state == "connected":
            conn_status = Text("🔗 REALTIME", style="bold #3fb950")
        elif self.connection_state == "connecting":
            conn_status = Text("⏳ CONNECTING", style="bold #f9826c")
        else:
            conn_status = Text("❌ OFFLINE", style="bold #7d8590")
        
        # Recording status
        if self.is_recording:
            if self.is_speaking:
                rec_status = Text("🎙️ SPEAKING", style="bold #3fb950")
            else:
                rec_status = Text("🎙️ LISTENING", style="bold #40a4ff")
        else:
            rec_status = Text("🎙️ MUTED", style="bold #7d8590")
        
        # Audio level visualization
        level_blocks = int(self.audio_level * 10)
        level_vis = "█" * level_blocks + "▪" * (10 - level_blocks)
        
        if self.audio_level > 0.7:
            level_color = "#f85149"  # Red for high
        elif self.audio_level > 0.3:
            level_color = "#f9826c"  # Orange for medium
        else:
            level_color = "#3fb950"  # Green for low
        
        level_text = Text(f"[{level_vis}]", style=level_color)
        
        # Combine all elements
        status_line = Text()
        status_line.append_text(conn_status)
        status_line.append("  │  ")
        status_line.append_text(rec_status)
        status_line.append("  │  ")
        status_line.append_text(level_text)
        
        return status_line
    
    def update_connection(self, state: str):
        """Update connection state"""
        self.connection_state = state
    
    def update_recording(self, is_recording: bool, is_speaking: bool = False):
        """Update recording state"""
        self.is_recording = is_recording
        self.is_speaking = is_speaking
    
    def update_audio_level(self, level: float):
        """Update audio level"""
        self.audio_level = max(0.0, min(1.0, level))

class ConnectionIndicator(Widget):
    """Minimalist connection status indicator"""
    
    DEFAULT_CSS = """
    ConnectionIndicator {
        width: 3;
        height: 1;
        margin: 0 1;
    }
    """
    
    state = reactive("disconnected")
    
    def render(self) -> Text:
        """Render connection indicator"""
        if self.state == "connected":
            return Text("●", style="bold #3fb950")  # Green dot
        elif self.state == "connecting":
            return Text("◐", style="bold #f9826c")  # Half circle (animated)
        elif self.state == "error":
            return Text("●", style="bold #f85149")  # Red dot
        else:
            return Text("○", style="bold #7d8590")  # Empty circle
    
    def set_state(self, state: str):
        """Update connection state"""
        self.state = state

class AudioControlPanel(Widget):
    """Complete audio control panel with mic, status, and controls"""
    
    DEFAULT_CSS = """
    AudioControlPanel {
        height: 5;
        dock: bottom;
        background: #161b22;
        border-top: solid #30363d;
        padding: 1;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mic_indicator = MicrophoneIndicator()
        self.connection_indicator = ConnectionIndicator()
        
    def compose(self):
        """Compose the audio control panel"""
        from textual.containers import Horizontal, Vertical
        
        with Horizontal():
            yield self.mic_indicator
            with Vertical():
                yield self.connection_indicator
                yield AudioStatusBar()
    
    def update_mic_state(self, state: MicState, audio_level: float = 0.0):
        """Update microphone state and level"""
        self.mic_indicator.set_state(state)
        self.mic_indicator.set_audio_level(audio_level)
    
    def update_connection_state(self, state: str):
        """Update connection state"""
        self.connection_indicator.set_state(state)