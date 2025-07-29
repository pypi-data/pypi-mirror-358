"""
REAL Audio Manager - Actually accesses microphone hardware
Uses PyAudio for real microphone capture
"""

import asyncio
import logging
import subprocess
import threading
import time
import os
import json
import base64
import numpy as np
from typing import Optional, Callable
from enum import Enum
from scipy import signal

try:
    import sounddevice as sd
    import soundfile as sf
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    logging.warning("Audio libraries not available - falling back to mock audio")

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logging.warning("websockets not available")

logger = logging.getLogger(__name__)

class AudioState(Enum):
    OFF = "off"
    LISTENING = "listening"
    SPEAKING = "speaking"
    ERROR = "error"

class RealAudioManager:
    """REAL audio manager that actually accesses microphone"""
    
    def __init__(self, openai_api_key: str = None):
        self.is_recording = False
        self.is_speaking = False
        self.audio_level = 0.0
        self.recording_thread = None
        self._stop_recording = threading.Event()
        
        # PyAudio setup - FIXED for this system
        self.audio = None
        self.stream = None
        self.sample_rate = 44100  # Use system's native rate (converted to 24kHz for OpenAI)
        self.chunk_size = 1024
        self.channels = 1
        
        # WebSocket setup
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.websocket = None
        self.ws_connected = False
        self.packets_sent = 0
        self.packets_received = 0
        self.main_loop = None  # Store main event loop
        
        # Callbacks
        self.on_audio_level: Optional[Callable[[float], None]] = None
        self.on_transcription: Optional[Callable[[str], None]] = None
        self.on_audio_data: Optional[Callable[[bytes], None]] = None
        
    async def initialize(self):
        """Check if we can access microphone using PyAudio"""
        try:
            if not PYAUDIO_AVAILABLE:
                logger.error("❌ PyAudio not available - install with: uv add pyaudio")
                return False
            
            logger.info("🎙️  Initializing PyAudio...")
            self.audio = pyaudio.PyAudio()
            
            # Get device info
            device_count = self.audio.get_device_count()
            logger.info(f"🎙️  Found {device_count} audio devices")
            
            # Find default input device
            default_input = self.audio.get_default_input_device_info()
            logger.info(f"🎙️  Default input device: {default_input['name']}")
            logger.info(f"🎙️  Max input channels: {default_input['maxInputChannels']}")
            logger.info(f"🎙️  Default sample rate: {default_input['defaultSampleRate']}")
            
            # Test if we can create a stream
            try:
                test_stream = self.audio.open(
                    format=pyaudio.paInt16,
                    channels=self.channels,
                    rate=self.sample_rate,
                    input=True,
                    frames_per_buffer=self.chunk_size,
                    stream_callback=None
                )
                test_stream.close()
                logger.info("✅ Audio input test successful")
                return True
                
            except Exception as e:
                logger.error(f"❌ Audio input test failed: {e}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Audio initialization failed: {e}")
            return False
    
    async def connect(self):
        """Connect to OpenAI Realtime API via WebSocket"""
        logger.info("🎧 RealAudioManager connecting to OpenAI Realtime API...")
        
        # Store main event loop for thread communication
        self.main_loop = asyncio.get_event_loop()
        logger.info(f"🔄 Stored main event loop: {self.main_loop}")
        
        if not self.openai_api_key:
            logger.error("❌ OPENAI_API_KEY not provided")
            return False
        
        if not WEBSOCKETS_AVAILABLE:
            logger.error("❌ websockets library not available")
            return False
        
        try:
            url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            logger.info(f"🔗 Connecting to {url}")
            logger.info(f"📤 WSS PACKET ATTEMPT #1: Connection headers")
            
            self.websocket = await websockets.connect(url, additional_headers=headers)
            self.ws_connected = True
            
            logger.info("✅ WebSocket connected to OpenAI Realtime API")
            
            # Send session configuration
            session_config = {
                "type": "session.update",
                "session": {
                    "model": "gpt-4o-realtime-preview-2024-10-01",
                    "modalities": ["text", "audio"],
                    "instructions": "You are a helpful assistant for VME infrastructure management.",
                    "voice": "alloy",
                    "input_audio_format": "pcm16",
                    "output_audio_format": "pcm16",
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 200
                    }
                }
            }
            
            await self._send_ws_message(session_config, "SESSION_CONFIG")
            
            # Start listening for responses
            asyncio.create_task(self._ws_listener())
            
            return True
            
        except Exception as e:
            logger.error(f"❌ WebSocket connection failed: {e}")
            self.ws_connected = False
            return False
    
    async def _send_ws_message(self, message: dict, msg_type: str = "UNKNOWN"):
        """Send WebSocket message with explicit logging"""
        if not self.websocket or not self.ws_connected:
            logger.error(f"❌ WSS PACKET FAILED: No connection for {msg_type}")
            return False
        
        try:
            self.packets_sent += 1
            json_msg = json.dumps(message)
            
            logger.info(f"📤 WSS PACKET #{self.packets_sent}: {msg_type}")
            logger.info(f"📤 WSS SIZE: {len(json_msg)} bytes")
            logger.info(f"📤 WSS DATA: {json_msg[:200]}...")
            
            await self.websocket.send(json_msg)
            logger.info(f"✅ WSS PACKET #{self.packets_sent} SENT SUCCESSFULLY")
            return True
            
        except Exception as e:
            logger.error(f"❌ WSS PACKET #{self.packets_sent} FAILED: {e}")
            return False
    
    async def _ws_listener(self):
        """Listen for WebSocket messages"""
        try:
            async for message in self.websocket:
                self.packets_received += 1
                logger.info(f"📥 WSS RECEIVED #{self.packets_received}: {len(message)} bytes")
                
                try:
                    data = json.loads(message)
                    msg_type = data.get('type', 'unknown')
                    logger.info(f"📥 WSS MESSAGE TYPE: {msg_type}")
                    
                    if msg_type == "session.created":
                        logger.info("✅ OpenAI Realtime session created")
                    elif msg_type == "input_audio_buffer.speech_started":
                        logger.info("🗣️  OpenAI detected speech start")
                    elif msg_type == "input_audio_buffer.speech_stopped":
                        logger.info("🔇 OpenAI detected speech stop")
                    elif msg_type == "conversation.item.input_audio_transcription.completed":
                        transcript = data.get('transcript', '')
                        logger.info(f"📝 TRANSCRIPTION: {transcript}")
                        if self.on_transcription:
                            self.on_transcription(transcript)
                    
                except json.JSONDecodeError:
                    logger.info(f"📥 WSS NON-JSON: {message[:100]}...")
                    
        except Exception as e:
            logger.error(f"❌ WebSocket listener error: {e}")
            self.ws_connected = False
    
    async def start_recording(self):
        """Start REAL microphone recording using PyAudio"""
        if self.is_recording:
            return True
            
        try:
            if not self.audio:
                logger.error("❌ Audio not initialized")
                return False
                
            logger.info("🎙️  Opening PyAudio stream...")
            
            # Open audio stream with CORRECT device settings
            default_input = self.audio.get_default_input_device_info()
            
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=default_input['index'],  # Use correct device
                frames_per_buffer=self.chunk_size,
                stream_callback=None
            )
            
            self.is_recording = True
            self._stop_recording.clear()
            
            # Start recording thread
            self.recording_thread = threading.Thread(
                target=self._recording_worker, 
                daemon=True
            )
            self.recording_thread.start()
            
            logger.info("🎙️  REAL microphone recording started!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start recording: {e}")
            self.is_recording = False
            return False
    
    async def stop_recording(self):
        """Stop recording"""
        if not self.is_recording:
            return
            
        logger.info("🔇 Stopping microphone recording...")
        self.is_recording = False
        self._stop_recording.set()
        
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=2)
            
        # Close audio stream
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
    
    def _recording_worker(self):
        """Worker thread that captures REAL audio data"""
        logger.info("🎙️  Recording worker started - capturing REAL audio data")
        
        chunk_count = 0
        total_volume_logged = 0
        
        try:
            while not self._stop_recording.is_set() and self.stream:
                try:
                    # Read audio data from microphone - FAIL if no real mic data
                    if not self.stream or not self.stream.is_active():
                        logger.error("❌ Audio stream not active - stopping recording")
                        break
                        
                    audio_data = self.stream.read(self.chunk_size, exception_on_overflow=True)
                    chunk_count += 1
                    
                    # Convert to numpy array for analysis
                    audio_array = np.frombuffer(audio_data, dtype=np.int16)
                    
                    # VERIFY we're getting real audio data, not silence/zeros
                    if len(set(audio_array[:100])) < 3:  # Too many identical values = fake data
                        if chunk_count % 50 == 0:  # Log every 50 chunks
                            logger.warning(f"⚠️  Possible fake audio data - only {len(set(audio_array[:100]))} unique values in sample")
                            logger.warning(f"⚠️  Sample data: {list(audio_array[:10])}")
                    
                    # Check if all values are the same (dead giveaway of fake audio)
                    if len(set(audio_array)) == 1:
                        logger.error(f"❌ FAKE AUDIO DETECTED - all values are {audio_array[0]}")
                        logger.error("❌ Microphone is not providing real data - stopping")
                        break
                    
                    # Calculate RMS (root mean square) for audio level  
                    rms = np.sqrt(np.mean(audio_array.astype(np.float32)**2))
                    normalized_level = min(rms / 10000.0, 1.0)  # Normalize to 0-1
                    
                    # Resample from 44.1kHz to 24kHz for OpenAI
                    if self.sample_rate != 24000:
                        # Convert to float for resampling
                        audio_float = audio_array.astype(np.float32) / 32768.0
                        # Resample to 24kHz  
                        resampled = signal.resample(audio_float, int(len(audio_float) * 24000 / self.sample_rate))
                        # Convert back to int16
                        audio_for_openai = (resampled * 32767).astype(np.int16)
                        openai_audio_data = audio_for_openai.tobytes()
                    else:
                        openai_audio_data = audio_data
                    
                    # Log audio data periodically
                    if chunk_count % 50 == 0:  # Every ~5 seconds at 10fps
                        logger.info(f"🎙️  AUDIO DATA: chunk {chunk_count}, "
                                   f"bytes: {len(audio_data)}, "
                                   f"samples: {len(audio_array)}, "
                                   f"rms: {rms:.1f}, "
                                   f"level: {normalized_level:.3f}")
                        
                        if normalized_level > 0.1:
                            logger.info(f"🗣️  SOUND DETECTED! Level: {normalized_level:.3f}")
                        
                    self.audio_level = normalized_level
                    
                    # Notify level callback
                    if self.on_audio_level:
                        try:
                            if self.main_loop:
                                asyncio.run_coroutine_threadsafe(
                                    self._safe_callback(self.on_audio_level, normalized_level),
                                    self.main_loop
                                )
                        except Exception as e:
                            logger.debug(f"Audio level callback error: {e}")
                    
                    # Only send REAL audio data (not silence/fake data)
                    if normalized_level > 0.001:  # Only send if there's actual audio activity
                        # Send audio data to OpenAI Realtime API
                        if self.ws_connected and self.websocket:
                            try:
                                # Convert resampled audio to base64 for WebSocket
                                audio_b64 = base64.b64encode(openai_audio_data).decode('utf-8')
                                
                                audio_message = {
                                    "type": "input_audio_buffer.append",
                                    "audio": audio_b64
                                }
                                
                                # Send audio chunk to OpenAI (async call from thread)
                                if self.main_loop:
                                    asyncio.run_coroutine_threadsafe(
                                        self._send_ws_message(audio_message, f"AUDIO_CHUNK_{chunk_count}"),
                                        self.main_loop
                                    )
                                else:
                                    logger.error(f"❌ No main event loop - audio chunk {chunk_count} not sent")
                                
                            except Exception as e:
                                logger.error(f"❌ Failed to send audio chunk {chunk_count}: {e}")
                        else:
                            logger.debug(f"🔇 No WebSocket connection - audio chunk {chunk_count} not sent")
                    else:
                        # Skip sending silent/fake audio
                        if chunk_count % 100 == 0:  # Log every 100 silent chunks
                            logger.debug(f"🔇 Skipping silent audio chunk {chunk_count} (level: {normalized_level:.6f})")
                    
                    # Notify raw audio data callback
                    if self.on_audio_data:
                        try:
                            # Call directly since it's from background thread
                            self.on_audio_data(audio_data)
                        except Exception as e:
                            logger.debug(f"Audio data callback error: {e}")
                    
                    # Small delay to control update rate
                    time.sleep(0.01)  # 100fps audio processing
                    
                except Exception as e:
                    logger.error(f"❌ Error reading audio data: {e}")
                    time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"❌ Recording worker error: {e}")
        
        logger.info(f"🔇 Recording worker stopped - processed {chunk_count} audio chunks")
    
    
    async def _safe_callback(self, callback: Callable, *args):
        """Safely execute callback"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception as e:
            logger.error(f"Callback error: {e}")
    
    async def disconnect(self):
        """Cleanup PyAudio and WebSocket resources"""
        await self.stop_recording()
        
        # Close WebSocket connection
        if self.websocket:
            try:
                logger.info(f"🔌 Closing WebSocket (sent {self.packets_sent}, received {self.packets_received} packets)")
                await self.websocket.close()
                self.ws_connected = False
                self.websocket = None
            except Exception as e:
                logger.error(f"Error closing WebSocket: {e}")
        
        if self.audio:
            self.audio.terminate()
            self.audio = None
            logger.info("🔇 PyAudio terminated")
    
    @property
    def is_connected(self) -> bool:
        """Always connected for real audio"""
        return True