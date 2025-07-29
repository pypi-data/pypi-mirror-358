"""
Simplified OpenAI Realtime API Audio Manager using sounddevice
Focus on WebSocket connection and basic audio streaming
"""

import asyncio
import json
import logging
import os
import base64
from typing import Optional, Callable, Dict, Any
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
class SimpleAudioConfig:
    sample_rate: int = 24000
    channels: int = 1
    dtype: str = "int16"
    input_device: Optional[int] = None
    output_device: Optional[int] = None
    model: str = "gpt-4o-realtime-preview-2024-10-01"
    voice: str = "alloy"
    instructions: str = (
        "You are a helpful assistant for VME infrastructure management. "
        "Keep responses conversational and concise for audio output."
    )

class SimpleRealtimeAudioManager:
    """Simplified OpenAI Realtime API manager"""
    
    def __init__(self, api_key: str, config: SimpleAudioConfig = None):
        self.api_key = api_key
        self.config = config or SimpleAudioConfig()
        
        # Connection state
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.connection_state = ConnectionState.DISCONNECTED
        
        # Audio state
        self.is_recording = False
        self.is_speaking = False
        self.audio_level = 0.0
        
        # Event callbacks
        self.on_transcription: Optional[Callable[[str], None]] = None
        self.on_audio_response: Optional[Callable[[bytes], None]] = None
        self.on_connection_changed: Optional[Callable[[ConnectionState], None]] = None
        self.on_audio_level: Optional[Callable[[float], None]] = None
        
        # Control
        self._stop_event = asyncio.Event()
        self._tasks = []
    
    async def initialize(self):
        """Initialize audio system"""
        try:
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
            
            # Start background task for WebSocket handling
            self._tasks.append(
                asyncio.create_task(self._websocket_listener())
            )
            
            self._set_connection_state(ConnectionState.CONNECTED)
            logger.info("Connected to OpenAI Realtime API")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Realtime API: {e}")
            self._set_connection_state(ConnectionState.ERROR)
            return False
    
    async def disconnect(self):
        """Disconnect from Realtime API"""
        self._stop_event.set()
        
        # Cancel background tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()
        
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        
        # Stop audio recording
        if self.is_recording:
            await self.stop_recording()
        
        # Close WebSocket
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket: {e}")
            self.websocket = None
        
        self._set_connection_state(ConnectionState.DISCONNECTED)
        logger.info("Disconnected from Realtime API")
    
    async def start_recording(self):
        """Start audio recording (simplified)"""
        if self.is_recording or not self.websocket:
            return False
        
        try:
            self.is_recording = True
            logger.info("Started audio recording")
            
            # For now, just simulate audio input
            # Real implementation would use sounddevice input stream
            self._tasks.append(
                asyncio.create_task(self._simulate_audio_input())
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return False
    
    async def stop_recording(self):
        """Stop audio recording"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        logger.info("Stopped audio recording")
    
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
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 200
                },
                "tools": [],
                "tool_choice": "auto"
            }
        }
        
        await self.websocket.send(json.dumps(session_config))
    
    async def _websocket_listener(self):
        """Listen for WebSocket messages"""
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
                    if self.on_audio_response:
                        await self._safe_callback(self.on_audio_response, audio_data)
            
            elif event_type == "response.audio.done":
                # Audio response completed
                logger.debug("Audio response completed")
                self.is_speaking = False
            
            elif event_type == "response.audio.started":
                # Audio response started
                self.is_speaking = True
            
            elif event_type == "error":
                # Handle API errors
                error = event.get("error", {})
                logger.error(f"Realtime API error: {error}")
            
            else:
                logger.debug(f"Unhandled event type: {event_type}")
                
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
    
    async def _simulate_audio_input(self):
        """Simulate audio input for testing"""
        while self.is_recording and not self._stop_event.is_set():
            # Simulate varying audio levels
            import random
            level = random.uniform(0.1, 0.9)
            self.audio_level = level
            
            if self.on_audio_level:
                await self._safe_callback(self.on_audio_level, level)
            
            await asyncio.sleep(0.1)
    
    def _set_connection_state(self, state: ConnectionState):
        """Update connection state and notify callback"""
        self.connection_state = state
        if self.on_connection_changed:
            asyncio.create_task(self._safe_callback(self.on_connection_changed, state))
    
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