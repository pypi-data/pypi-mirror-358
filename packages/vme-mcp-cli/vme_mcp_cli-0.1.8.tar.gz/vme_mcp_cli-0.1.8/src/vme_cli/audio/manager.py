"""
OpenAI Realtime API Audio Manager
Handles WebSocket connection, audio streaming, and real-time conversation
"""

import asyncio
import json
import logging
import os
import base64
import time
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

import websockets
import sounddevice as sd
import numpy as np
from websockets.exceptions import ConnectionClosed, WebSocketException

logger = logging.getLogger(__name__)

class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

@dataclass
class RealtimeAudioConfig:
    sample_rate: int = 24000
    channels: int = 1
    chunk_size: int = 1024
    dtype: str = "int16"  # sounddevice format
    input_device: Optional[int] = None
    output_device: Optional[int] = None
    model: str = "gpt-4o-realtime-preview-2024-10-01"
    voice: str = "alloy"
    vad_threshold: float = 0.5
    vad_prefix_padding_ms: int = 300
    vad_silence_duration_ms: int = 200
    instructions: str = (
        "You are a helpful assistant for VME infrastructure management. "
        "Keep responses conversational and concise for audio output. "
        "When the user asks about infrastructure, provide brief spoken summaries "
        "while detailed information will be handled separately via text."
    )

class RealtimeAudioManager:
    """Manages OpenAI Realtime API connection and audio streaming"""
    
    def __init__(self, api_key: str, config: RealtimeAudioConfig = None):
        self.api_key = api_key
        self.config = config or RealtimeAudioConfig()
        
        # Connection state
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.connection_state = ConnectionState.DISCONNECTED
        
        # Audio components
        self.input_stream = None
        self.output_stream = None
        
        # Audio buffers
        self.audio_buffer = bytearray()
        self.playback_buffer = asyncio.Queue()
        
        # Event callbacks
        self.on_transcription: Optional[Callable[[str], None]] = None
        self.on_audio_response: Optional[Callable[[bytes], None]] = None
        self.on_connection_changed: Optional[Callable[[ConnectionState], None]] = None
        self.on_audio_level: Optional[Callable[[float], None]] = None
        self.on_conversation_item: Optional[Callable[[Dict], None]] = None
        
        # Control flags
        self.is_recording = False
        self.is_speaking = False
        self._stop_event = asyncio.Event()
        
        # Background tasks
        self._tasks: List[asyncio.Task] = []
    
    async def initialize(self):
        """Initialize audio system"""
        try:
            # Check if sounddevice works
            devices = sd.query_devices()
            logger.info(f"Audio system initialized with {len(devices)} devices")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize audio: {e}")
            return False
    
    async def connect(self):
        """Connect to OpenAI Realtime API"""
        if self.connection_state in [ConnectionState.CONNECTING, ConnectionState.CONNECTED]:
            return True
            
        try:
            self._set_connection_state(ConnectionState.CONNECTING)
            
            # WebSocket URL and headers
            url = f"wss://api.openai.com/v1/realtime?model={self.config.model}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            # Connect to WebSocket
            self.websocket = await websockets.connect(
                url,
                extra_headers=headers,
                ping_interval=20,
                ping_timeout=10
            )
            
            # Send session configuration
            await self._configure_session()
            
            # Start background tasks
            self._start_background_tasks()
            
            self._set_connection_state(ConnectionState.CONNECTED)
            logger.info("Connected to OpenAI Realtime API")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Realtime API: {e}")
            self._set_connection_state(ConnectionState.ERROR)
            return False
    
    async def disconnect(self):
        """Disconnect from Realtime API and cleanup"""
        self._stop_event.set()
        
        # Cancel background tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()
        
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        
        # Close audio streams
        if self.input_stream:
            self.input_stream.stop()
            self.input_stream.close()
            self.input_stream = None
            
        if self.output_stream:
            self.output_stream.stop()
            self.output_stream.close()
            self.output_stream = None
        
        # Close WebSocket
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket: {e}")
            self.websocket = None
        
        # Cleanup audio
        if self.audio:
            self.audio.terminate()
            self.audio = None
        
        self._set_connection_state(ConnectionState.DISCONNECTED)
        logger.info("Disconnected from Realtime API")
    
    async def start_recording(self):
        """Start recording audio from microphone"""
        if self.is_recording or not self.websocket:
            return False
            
        try:
            # Open input stream
            self.input_stream = self.audio.open(
                format=self.config.format,
                channels=self.config.channels,
                rate=self.config.sample_rate,
                input=True,
                input_device_index=self.config.input_device,
                frames_per_buffer=self.config.chunk_size,
                stream_callback=self._audio_input_callback
            )
            
            self.input_stream.start_stream()
            self.is_recording = True
            
            logger.info("Started audio recording")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return False
    
    async def stop_recording(self):
        """Stop recording audio"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
            self.input_stream = None
            
        logger.info("Stopped audio recording")
    
    def _audio_input_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio input stream"""
        if not self.is_recording or not self.websocket:
            return (None, pyaudio.paContinue)
        
        try:
            # Convert to numpy array for processing
            audio_data = np.frombuffer(in_data, dtype=np.int16)
            
            # Calculate audio level for visualization
            if self.on_audio_level:
                level = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
                normalized_level = min(level / 32768.0, 1.0)
                asyncio.create_task(self._notify_audio_level(normalized_level))
            
            # Add to buffer for streaming
            self.audio_buffer.extend(in_data)
            
            # Send audio chunks when buffer is large enough
            if len(self.audio_buffer) >= self.config.chunk_size * 2:
                chunk = bytes(self.audio_buffer[:self.config.chunk_size * 2])
                self.audio_buffer = self.audio_buffer[self.config.chunk_size * 2:]
                
                # Send to WebSocket (non-blocking)
                asyncio.create_task(self._send_audio_chunk(chunk))
                
        except Exception as e:
            logger.error(f"Audio input callback error: {e}")
        
        return (None, pyaudio.paContinue)
    
    async def _send_audio_chunk(self, audio_data: bytes):
        """Send audio chunk to Realtime API"""
        if not self.websocket:
            return
            
        try:
            # Encode audio as base64
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Create input audio buffer append event
            event = {
                "type": "input_audio_buffer.append",
                "audio": audio_b64
            }
            
            await self.websocket.send(json.dumps(event))
            
        except Exception as e:
            logger.error(f"Failed to send audio chunk: {e}")
    
    async def _configure_session(self):
        """Configure the Realtime API session"""
        session_config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": self.config.instructions,
                "voice": self.config.voice,
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": self.config.vad_threshold,
                    "prefix_padding_ms": self.config.vad_prefix_padding_ms,
                    "silence_duration_ms": self.config.vad_silence_duration_ms
                },
                "tools": [],
                "tool_choice": "auto"
            }
        }
        
        await self.websocket.send(json.dumps(session_config))
    
    def _start_background_tasks(self):
        """Start background tasks for WebSocket handling"""
        self._tasks = [
            asyncio.create_task(self._websocket_listener()),
            asyncio.create_task(self._audio_playback_handler())
        ]
    
    async def _websocket_listener(self):
        """Listen for WebSocket messages from Realtime API"""
        try:
            while not self._stop_event.is_set() and self.websocket:
                try:
                    message = await asyncio.wait_for(
                        self.websocket.recv(), timeout=1.0
                    )
                    await self._handle_websocket_message(message)
                    
                except asyncio.TimeoutError:
                    continue
                except ConnectionClosed:
                    logger.warning("WebSocket connection closed")
                    break
                    
        except Exception as e:
            logger.error(f"WebSocket listener error: {e}")
        finally:
            self._set_connection_state(ConnectionState.ERROR)
    
    async def _handle_websocket_message(self, message: str):
        """Handle incoming WebSocket message"""
        try:
            event = json.loads(message)
            event_type = event.get("type")
            
            if event_type == "conversation.item.input_audio_transcription.completed":
                # Handle transcription
                transcript = event.get("transcript", "")
                if transcript and self.on_transcription:
                    await self._safe_callback(self.on_transcription, transcript)
            
            elif event_type == "response.audio.delta":
                # Handle audio response chunk
                audio_b64 = event.get("delta", "")
                if audio_b64:
                    audio_data = base64.b64decode(audio_b64)
                    await self.playback_buffer.put(audio_data)
            
            elif event_type == "conversation.item.created":
                # Handle conversation item
                item = event.get("item", {})
                if self.on_conversation_item:
                    await self._safe_callback(self.on_conversation_item, item)
            
            elif event_type == "response.audio.done":
                # Audio response completed
                logger.debug("Audio response completed")
            
            elif event_type == "error":
                # Handle API errors
                error = event.get("error", {})
                logger.error(f"Realtime API error: {error}")
            
            else:
                logger.debug(f"Unhandled event type: {event_type}")
                
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
    
    async def _audio_playback_handler(self):
        """Handle audio playback from response buffer"""
        try:
            # Initialize output stream when first audio arrives
            output_stream = None
            
            while not self._stop_event.is_set():
                try:
                    # Wait for audio data
                    audio_data = await asyncio.wait_for(
                        self.playback_buffer.get(), timeout=1.0
                    )
                    
                    # Initialize output stream if needed
                    if not output_stream and self.audio:
                        output_stream = self.audio.open(
                            format=self.config.format,
                            channels=self.config.channels,
                            rate=self.config.sample_rate,
                            output=True,
                            output_device_index=self.config.output_device
                        )
                        self.is_speaking = True
                    
                    # Play audio
                    if output_stream:
                        output_stream.write(audio_data)
                        
                except asyncio.TimeoutError:
                    # No audio data, check if we should close stream
                    if output_stream and self.playback_buffer.empty():
                        output_stream.stop_stream()
                        output_stream.close()
                        output_stream = None
                        self.is_speaking = False
                    continue
                    
        except Exception as e:
            logger.error(f"Audio playback error: {e}")
        finally:
            if output_stream:
                output_stream.stop_stream()
                output_stream.close()
            self.is_speaking = False
    
    async def send_text_message(self, text: str):
        """Send a text message to the conversation"""
        if not self.websocket:
            return False
            
        try:
            event = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": text
                        }
                    ]
                }
            }
            
            await self.websocket.send(json.dumps(event))
            
            # Trigger response
            response_event = {
                "type": "response.create",
                "response": {
                    "modalities": ["text", "audio"]
                }
            }
            
            await self.websocket.send(json.dumps(response_event))
            return True
            
        except Exception as e:
            logger.error(f"Failed to send text message: {e}")
            return False
    
    def _set_connection_state(self, state: ConnectionState):
        """Update connection state and notify callback"""
        self.connection_state = state
        if self.on_connection_changed:
            asyncio.create_task(self._safe_callback(self.on_connection_changed, state))
    
    async def _notify_audio_level(self, level: float):
        """Notify audio level callback"""
        if self.on_audio_level:
            await self._safe_callback(self.on_audio_level, level)
    
    async def _safe_callback(self, callback: Callable, *args):
        """Safely execute callback without blocking"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception as e:
            logger.error(f"Callback error: {e}")
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to Realtime API"""
        return self.connection_state == ConnectionState.CONNECTED
    
    @property
    def audio_levels_available(self) -> bool:
        """Check if audio level monitoring is active"""
        return self.is_recording and self.on_audio_level is not None