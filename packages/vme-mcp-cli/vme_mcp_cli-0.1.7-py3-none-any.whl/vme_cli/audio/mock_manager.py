"""
Mock Audio Manager for VME Textual CLI Client
Provides OpenAI Realtime API WebSocket connection without local audio dependencies
Focus on text-to-speech integration and UI demonstration
"""

import asyncio
import json
import logging
import os
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum

import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

logger = logging.getLogger(__name__)

class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

@dataclass
class MockAudioConfig:
    model: str = "gpt-4o-realtime-preview-2024-10-01"
    voice: str = "alloy"
    instructions: str = (
        "You are a helpful assistant for VME infrastructure management. "
        "Keep responses conversational and concise for audio output. "
        "When the user asks about infrastructure, provide brief spoken summaries "
        "while detailed information will be handled separately via text."
    )

class MockRealtimeAudioManager:
    """Mock OpenAI Realtime API manager for testing without audio hardware"""
    
    def __init__(self, api_key: str, config: MockAudioConfig = None):
        self.api_key = api_key
        self.config = config or MockAudioConfig()
        
        # Connection state
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.connection_state = ConnectionState.DISCONNECTED
        
        # Mock audio state
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
        self._simulation_task = None
    
    async def initialize(self):
        """Initialize mock audio system"""
        logger.info("Mock audio system initialized (no hardware required)")
        return True
    
    async def connect(self):
        """Connect to OpenAI Realtime API"""
        if self.connection_state in [ConnectionState.CONNECTING, ConnectionState.CONNECTED]:
            return True
            
        try:
            self._set_connection_state(ConnectionState.CONNECTING)
            
            # For now, simulate successful connection
            # TODO: Fix websockets version compatibility
            logger.info("Simulating OpenAI Realtime API connection...")
            
            # Mock successful connection
            self.websocket = "mock_websocket"
            
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
        
        # Stop simulation
        if self._simulation_task and not self._simulation_task.done():
            self._simulation_task.cancel()
        
        # Stop recording
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
        """Start mock audio recording"""
        if self.is_recording or not self.websocket:
            return False
        
        try:
            self.is_recording = True
            logger.info("Started mock audio recording")
            
            # Start audio level simulation
            self._simulation_task = asyncio.create_task(self._simulate_audio_input())
            
            return True
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return False
    
    async def stop_recording(self):
        """Stop mock audio recording"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        if self._simulation_task and not self._simulation_task.done():
            self._simulation_task.cancel()
        
        logger.info("Stopped mock audio recording")
    
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
        """Configure the Realtime API session (mock)"""
        logger.info("Mock session configured")
        # No actual WebSocket send needed
    
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
            
            logger.debug(f"Received event: {event_type}")
            
            if event_type == "conversation.item.input_audio_transcription.completed":
                # Handle transcription
                transcript = event.get("transcript", "")
                if transcript and self.on_transcription:
                    await self._safe_callback(self.on_transcription, transcript)
            
            elif event_type == "response.audio.delta":
                # Handle audio response chunk (mock)
                self.is_speaking = True
                if self.on_audio_response:
                    # Mock audio data
                    await self._safe_callback(self.on_audio_response, b"mock_audio_data")
            
            elif event_type == "response.audio.done":
                # Audio response completed
                logger.debug("Audio response completed")
                self.is_speaking = False
            
            elif event_type == "response.audio.started":
                # Audio response started
                self.is_speaking = True
            
            elif event_type == "response.text.delta":
                # Handle text response (for text-based fallback)
                text_delta = event.get("delta", "")
                logger.debug(f"Text delta: {text_delta}")
            
            elif event_type == "error":
                # Handle API errors
                error = event.get("error", {})
                logger.error(f"Realtime API error: {error}")
            
            else:
                logger.debug(f"Unhandled event type: {event_type}")
                
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
    
    async def _simulate_audio_input(self):
        """Simulate audio input levels for testing"""
        import random
        
        while self.is_recording and not self._stop_event.is_set():
            # Simulate varying audio levels
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
    
    def get_connection_state_string(self) -> str:
        """Get connection state as string"""
        return self.connection_state.value