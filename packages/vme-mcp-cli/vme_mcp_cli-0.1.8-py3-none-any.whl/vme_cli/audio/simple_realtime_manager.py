"""
Simple OpenAI Realtime API Audio Manager - Based on Working Code
Clean, simple, and actually works!
"""

import asyncio
import websockets
import json
try:
    import sounddevice as sd
    import soundfile as sf
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
import base64
import logging
import os
import ssl
import threading
from typing import Optional, Callable
from enum import Enum

logger = logging.getLogger(__name__)

class AudioState(Enum):
    OFF = "off"
    LISTENING = "listening"
    SPEAKING = "speaking"
    ERROR = "error"

class SimpleRealtimeAudioManager:
    """Simple audio manager based on proven working code"""
    
    def __init__(self, openai_api_key: str = None):
        # WebSocket Configuration
        self.url = "wss://api.openai.com/v1/realtime"
        self.model = "gpt-4o-realtime-preview-2024-10-01"
        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.ws = None
        
        # SSL Configuration (skip cert verification like working code)
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
        # Audio setup
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.chunk_size = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 24000  # OpenAI expects 24kHz
        self.is_recording = False
        self.audio_buffer = b''
        
        # State
        self.is_connected = False
        self.current_state = AudioState.OFF
        self.audio_level = 0.0
        self.is_playing_response = False  # Flag to prevent feedback
        
        # VAD Configuration - More responsive settings
        self.VAD_config = {
            "type": "server_vad",
            "threshold": 0.3,  # More sensitive
            "prefix_padding_ms": 300,
            "silence_duration_ms": 200  # Respond faster after silence
        }
        
        # Session Configuration
        self.session_config = {
            "modalities": ["audio", "text"],
            "instructions": "You are a helpful assistant for VME infrastructure management.",
            "voice": "alloy",
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "turn_detection": self.VAD_config,
            "input_audio_transcription": {
                "model": "whisper-1"
            },
            "temperature": 0.6
        }
        
        # Callbacks
        self.on_audio_level: Optional[Callable[[float], None]] = None
        self.on_transcription: Optional[Callable[[str], None]] = None
        self.on_assistant_text: Optional[Callable[[str], None]] = None
        self.on_state_change: Optional[Callable[[AudioState], None]] = None
        
        # Background tasks
        self.receive_task = None
        self.audio_task = None
    
    async def initialize(self):
        """Initialize PyAudio"""
        try:
            logger.info("🎙️  Initializing PyAudio...")
            
            # Get device info
            device_count = self.p.get_device_count()
            logger.info(f"🎙️  Found {device_count} audio devices")
            
            # Get default input device
            default_input = self.p.get_default_input_device_info()
            logger.info(f"🎙️  Default input: {default_input['name']}")
            
            # Test audio stream
            test_stream = self.p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            test_stream.close()
            
            logger.info("✅ Audio initialization successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Audio initialization failed: {e}")
            return False
    
    async def connect(self):
        """Connect to OpenAI Realtime API"""
        if not self.api_key:
            logger.error("❌ No OpenAI API key provided")
            return False
        
        try:
            logger.info(f"🔗 Connecting to {self.url}")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            self.ws = await websockets.connect(
                f"{self.url}?model={self.model}",
                extra_headers=headers,
                ssl=self.ssl_context
            )
            
            self.is_connected = True
            logger.info("✅ Connected to OpenAI Realtime API")
            
            # Configure session
            await self._send_event({
                "type": "session.update",
                "session": self.session_config
            })
            
            logger.info("✅ Session configured")
            
            # Start receiving events
            self.receive_task = asyncio.create_task(self._receive_events())
            
            # Don't send initial response.create - wait for user input
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            self.is_connected = False
            return False
    
    async def start_recording(self):
        """Start recording audio"""
        if self.is_recording:
            return True
        
        try:
            logger.info("🎙️  Starting audio recording...")
            
            self.stream = self.p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            self.is_recording = True
            self._set_state(AudioState.LISTENING)
            
            # Start continuous audio streaming
            self.audio_task = asyncio.create_task(self._stream_audio())
            
            logger.info("✅ Recording started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start recording: {e}")
            self._set_state(AudioState.ERROR)
            return False
    
    async def stop_recording(self):
        """Stop recording audio"""
        if not self.is_recording:
            return
        
        logger.info("🔇 Stopping recording...")
        self.is_recording = False
        
        if self.audio_task:
            self.audio_task.cancel()
            try:
                await self.audio_task
            except asyncio.CancelledError:
                pass
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        self._set_state(AudioState.OFF)
        logger.info("✅ Recording stopped")
    
    def _reset_playback_flag_after_delay(self, duration):
        """Reset playback flag after estimated playback duration"""
        def reset_flag():
            import time
            time.sleep(duration + 1.0)  # Add 1 second buffer
            self.is_playing_response = False
            logger.info("🎙️  Ready to receive input again")
        
        import threading
        reset_thread = threading.Thread(target=reset_flag)
        reset_thread.daemon = True
        reset_thread.start()
    
    async def _stream_audio(self):
        """Continuously stream audio to OpenAI"""
        try:
            while self.is_recording and self.is_connected:
                if self.stream:
                    # Read audio chunk
                    chunk = self.stream.read(self.chunk_size, exception_on_overflow=False)
                    
                    # Calculate audio level for UI
                    import numpy as np
                    audio_array = np.frombuffer(chunk, dtype=np.int16)
                    rms = np.sqrt(np.mean(audio_array.astype(np.float32)**2))
                    self.audio_level = min(rms / 10000.0, 1.0)
                    
                    # Update audio level callback
                    if self.on_audio_level:
                        self.on_audio_level(self.audio_level)
                    
                    # Send to OpenAI (only if not playing response audio)
                    if not self.is_playing_response:
                        base64_chunk = base64.b64encode(chunk).decode('utf-8')
                        await self._send_event({
                            "type": "input_audio_buffer.append",
                            "audio": base64_chunk
                        })
                    
                    await asyncio.sleep(0.01)  # Small delay
                
        except Exception as e:
            logger.error(f"❌ Audio streaming error: {e}")
            self._set_state(AudioState.ERROR)
    
    async def _send_event(self, event):
        """Send event to WebSocket"""
        if self.ws and self.is_connected:
            try:
                await self.ws.send(json.dumps(event))
                logger.debug(f"📤 Sent event: {event['type']}")
            except Exception as e:
                logger.error(f"❌ Failed to send event: {e}")
    
    async def _receive_events(self):
        """Receive events from OpenAI"""
        try:
            async for message in self.ws:
                event = json.loads(message)
                await self._handle_event(event)
        except websockets.ConnectionClosed:
            logger.info("🔌 WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"❌ Event receiving error: {e}")
            self.is_connected = False
    
    async def _handle_event(self, event):
        """Handle incoming events from OpenAI"""
        event_type = event.get("type")
        logger.debug(f"📥 Received: {event_type}")
        
        if event_type == "error":
            logger.error(f"OpenAI error: {event['error']['message']}")
            self._set_state(AudioState.ERROR)
            
        elif event_type == "response.text.delta":
            # Assistant text response (incremental)
            text_delta = event.get("delta", "")
            if self.on_assistant_text:
                self.on_assistant_text(text_delta)
                
        elif event_type == "response.audio.delta":
            # Assistant audio response
            audio_data = base64.b64decode(event["delta"])
            self.audio_buffer += audio_data
            logger.debug("📥 Audio delta received")
            
        elif event_type == "response.audio.done":
            # Play assistant audio response
            if self.audio_buffer:
                # Set flag to prevent audio sending during playback
                self.is_playing_response = True
                self._play_audio(self.audio_buffer)
                self.audio_buffer = b''
                
        elif event_type == "input_audio_buffer.speech_started":
            logger.info("🗣️  Speech started (VAD)")
            self._set_state(AudioState.SPEAKING)
            
        elif event_type == "input_audio_buffer.speech_stopped":
            logger.info("🔇 Speech stopped (VAD)")
            self._set_state(AudioState.LISTENING)
            # Trigger response generation to get transcription and response
            await self._send_event({"type": "response.create"})
            
        elif event_type == "conversation.item.input_audio_transcription.completed":
            # User speech transcription
            transcript = event.get("transcript", "")
            logger.info(f"📝 Transcription: {transcript}")
            if self.on_transcription:
                self.on_transcription(transcript)
                
        elif event_type == "response.done":
            logger.debug("✅ Response completed")
    
    def _play_audio(self, audio_data):
        """Play audio response in background thread"""
        def play():
            try:
                stream = self.p.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.rate,
                    output=True
                )
                stream.write(audio_data)
                stream.stop_stream()
                stream.close()
                logger.info("🔊 Audio played")
            except Exception as e:
                logger.error(f"❌ Audio playback error: {e}")
        
        # Calculate playback duration and reset flag afterwards
        duration = len(audio_data) / (self.rate * 2)  # 2 bytes per sample
        self._reset_playback_flag_after_delay(duration)
        
        # Play in background thread
        playback_thread = threading.Thread(target=play)
        playback_thread.daemon = True
        playback_thread.start()
    
    def _set_state(self, new_state: AudioState):
        """Update audio state and notify callback"""
        if self.current_state != new_state:
            self.current_state = new_state
            if self.on_state_change:
                self.on_state_change(new_state)
    
    async def disconnect(self):
        """Cleanup and disconnect"""
        logger.info("🔌 Disconnecting...")
        
        await self.stop_recording()
        
        if self.receive_task:
            self.receive_task.cancel()
            try:
                await self.receive_task
            except asyncio.CancelledError:
                pass
        
        if self.ws:
            await self.ws.close()
            self.is_connected = False
        
        if self.p:
            self.p.terminate()
        
        logger.info("✅ Disconnected")
    
    @property
    def state(self) -> AudioState:
        """Get current audio state"""
        return self.current_state