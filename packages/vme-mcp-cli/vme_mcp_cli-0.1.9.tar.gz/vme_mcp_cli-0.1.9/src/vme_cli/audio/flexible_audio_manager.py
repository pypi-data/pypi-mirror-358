"""
Flexible Audio Manager - Supports multiple audio modes
- full_conversation: Complete OpenAI conversation with audio responses
- input_only: Voice input → transcription → Claude (no audio responses)  
- transcribe_only: Live transcription display only (no auto-submit)
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

from vme_cli.config.settings import AudioConfig

logger = logging.getLogger(__name__)

# Import AudioState from UI widgets to ensure consistency
try:
    from vme_cli.ui.simple_audio_widgets import AudioState
except ImportError:
    # Fallback definition if import fails
    class AudioState(Enum):
        OFF = "off"
        CONNECTING = "connecting"
        LISTENING = "listening"
        TRANSCRIBING = "transcribing"
        SPEAKING = "speaking"
        ERROR = "error"

class FlexibleAudioManager:
    """Audio manager that supports multiple modes based on config"""
    
    def __init__(self, audio_config: AudioConfig, openai_api_key: str = None):
        if not AUDIO_AVAILABLE:
            raise RuntimeError("Audio libraries (sounddevice/soundfile) not available")
        
        self.config = audio_config
        self.mode = audio_config.mode
        
        # WebSocket Configuration
        self.url = "wss://api.openai.com/v1/realtime"
        self.model = audio_config.model
        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.ws = None
        
        # SSL Configuration
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
        # Audio setup
        self.stream = None
        self.chunk_size = audio_config.chunk_size
        self.channels = audio_config.channels
        self.rate = audio_config.sample_rate
        self.is_recording = False
        self.audio_buffer = b''
        
        # State
        self.is_connected = False
        self.current_state = AudioState.OFF
        self.audio_level = 0.0
        self.is_playing_response = False
        self.current_transcription = ""
        self.accumulated_transcription = ""
        self.pending_item_ids = set()  # Track committed audio items
        
        # VAD Configuration
        self.VAD_config = {
            "type": "server_vad",
            "threshold": audio_config.vad_threshold,
            "prefix_padding_ms": audio_config.vad_prefix_padding_ms,
            "silence_duration_ms": audio_config.vad_silence_duration_ms
        }
        
        # Session Configuration based on mode
        self._configure_session()
        
        # Callbacks
        self.on_audio_level: Optional[Callable[[float], None]] = None
        self.on_transcription: Optional[Callable[[str], None]] = None
        self.on_transcription_partial: Optional[Callable[[str], None]] = None
        self.on_assistant_text: Optional[Callable[[str], None]] = None
        self.on_state_change: Optional[Callable[[AudioState], None]] = None
        self.on_speech_end_submit: Optional[Callable[[str], None]] = None
        self.on_debug_message: Optional[Callable[[str], None]] = None
        
        # Background tasks
        self.receive_task = None
        self.audio_task = None
        
        logger.info(f"🎧 Audio manager initialized in '{self.mode}' mode")
    
    def _configure_session(self):
        """Configure session based on audio mode"""
        if self.mode == "full_conversation":
            # Full OpenAI conversation with audio responses
            self.session_config = {
                "model": self.model,
                "modalities": ["audio", "text"],
                "instructions": self.config.instructions,
                "voice": self.config.voice,
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "turn_detection": self.VAD_config,
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "temperature": 0.6
            }
            self.is_transcription_session = False
            
        elif self.mode in ["input_only", "transcribe_only"]:
            # Use dedicated transcription session API
            if self.config.use_dedicated_transcription_api:
                self.session_config = {
                    "model": "gpt-4o-realtime-preview-2024-10-01",
                    "modalities": ["text"],
                    "input_audio_format": "pcm16",
                    "input_audio_transcription": {
                        "model": "gpt-4o-transcribe",
                        "language": "en"
                    },
                    "turn_detection": self.VAD_config
                }
                self.is_transcription_session = False
            else:
                # Fall back to regular session with transcription
                self.session_config = {
                    "model": self.model,
                    "modalities": ["text"],
                    "input_audio_format": "pcm16",
                    "input_audio_transcription": {
                        "model": "whisper-1"
                    },
                    "turn_detection": self.VAD_config,
                    "temperature": 0.6
                }
                self.is_transcription_session = False
    
    async def initialize(self):
        """Initialize sounddevice audio"""
        try:
            logger.info("🎙️  Initializing sounddevice...")
            
            # Get device info
            devices = sd.query_devices()
            logger.info(f"🎙️  Found {len(devices)} audio devices")
            
            # Get default input device
            default_input = sd.query_devices(kind='input')
            logger.info(f"🎙️  Default input: {default_input['name']}")
            
            # Test audio stream
            test_stream = sd.InputStream(
                channels=self.channels,
                samplerate=self.rate,
                blocksize=self.chunk_size,
                dtype='int16'
            )
            test_stream.start()
            test_stream.stop()
            test_stream.close()
            
            logger.info(f"✅ Audio initialization successful (mode: {self.mode})")
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
            logger.info(f"🔗 Connecting to {self.url} (mode: {self.mode})")
            
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
            
            # Configure session based on type
            if self.is_transcription_session:
                await self._send_event({
                    "type": "session.update",
                    "session": self.session_config
                })
            else:
                await self._send_event({
                    "type": "session.update", 
                    "session": self.session_config
                })
            
            logger.info(f"✅ Session configured for {self.mode} mode")
            
            # Start receiving events
            self.receive_task = asyncio.create_task(self._receive_events())
            
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
            logger.info(f"🎙️  Starting audio recording (mode: {self.mode})...")
            
            self.stream = sd.InputStream(
                channels=self.channels,
                samplerate=self.rate,
                blocksize=self.chunk_size,
                dtype='int16'
            )
            self.stream.start()
            
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
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        self._set_state(AudioState.OFF)
        logger.info("✅ Recording stopped")
    
    async def _stream_audio(self):
        """Continuously stream audio to OpenAI"""
        try:
            while self.is_recording and self.is_connected:
                if self.stream:
                    # Read audio chunk
                    chunk, overflowed = self.stream.read(self.chunk_size)
                    if overflowed:
                        logger.warning("Audio buffer overflow")
                    
                    # Convert to bytes for transmission
                    chunk_bytes = chunk.astype('int16').tobytes()
                    
                    # Calculate audio level for UI
                    import numpy as np
                    audio_array = chunk.flatten()
                    rms = np.sqrt(np.mean(audio_array.astype(np.float32)**2))
                    self.audio_level = min(rms / 10000.0, 1.0)
                    
                    # Check for audio issues
                    if len(audio_array) > 0:
                        min_val, max_val = audio_array.min(), audio_array.max()
                        if min_val == max_val:  # Completely silent
                            if self.on_debug_message and rms > 0:
                                self.on_debug_message(f"⚠️ Silent audio detected")
                        elif abs(min_val) > 30000 or abs(max_val) > 30000:  # Clipping
                            if self.on_debug_message:
                                self.on_debug_message(f"⚠️ Audio clipping: {min_val} to {max_val}")
                    
                    # Update audio level callback
                    if self.on_audio_level:
                        self.on_audio_level(self.audio_level)
                    
                    # Send to OpenAI (prevent feedback in full_conversation mode)
                    should_send = True
                    if self.mode == "full_conversation" and self.is_playing_response:
                        should_send = False
                    
                    if should_send:
                        base64_chunk = base64.b64encode(chunk_bytes).decode('utf-8')
                        # Only log audio chunks occasionally to avoid spam
                        if self.on_debug_message and len(base64_chunk) > 0 and rms > 100:  # Only when speaking
                            import time
                            if not hasattr(self, '_last_audio_log') or time.time() - self._last_audio_log > 2:
                                self.on_debug_message(f"🎵 Audio: RMS: {rms:.0f}, Level: {self.audio_level:.2f}")
                                self._last_audio_log = time.time()
                        await self._send_event({
                            "type": "input_audio_buffer.append",
                            "audio": base64_chunk
                        })
                    
                    await asyncio.sleep(0.01)
                
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
        logger.info(f"📥 Received: {event_type}")
        
        # ALWAYS log speech and transcription events for debugging
        if "speech" in event_type or "transcription" in event_type:
            logger.info(f"🗣️ SPEECH/TRANSCRIPTION EVENT: {event_type}")
            if self.on_debug_message:
                self.on_debug_message(f"🗣️ {event_type}")
        
        if self.on_debug_message:
            if "transcription" in event_type:
                self.on_debug_message(f"📥 {event_type}")
            elif event_type in ["session.created", "session.updated", "error"]:
                self.on_debug_message(f"📥 {event_type}")
            # Show all events at debug level 3
            elif hasattr(self, 'config') and getattr(self.config, 'debug_level', 0) >= 3:
                self.on_debug_message(f"📥 {event_type}")
        
        if event_type == "error":
            error_msg = event['error']['message']
            logger.error(f"OpenAI error: {error_msg}")
            if self.on_debug_message:
                self.on_debug_message(f"❌ OpenAI Error: {error_msg}")
            self._set_state(AudioState.ERROR)
            
        elif event_type == "input_audio_buffer.speech_started":
            logger.info("🗣️  Speech started (VAD)")
            self._set_state(AudioState.TRANSCRIBING)
            # Reset accumulated transcription for new speech
            self.accumulated_transcription = ""
            # Reset delta timing
            if hasattr(self, '_first_delta_time'):
                delattr(self, '_first_delta_time')
            
        elif event_type == "input_audio_buffer.speech_stopped":
            logger.info("🔇 Speech stopped (VAD) - waiting for transcription...")
            # Keep TRANSCRIBING state - already set when speech started
            
            # Commit the audio buffer for transcription
            await self._send_event({"type": "input_audio_buffer.commit"})
            
            # Handle based on mode
            if self.mode == "full_conversation":
                # Trigger OpenAI response
                await self._send_event({"type": "response.create"})
            # For input_only mode, we wait for the completed event to submit
        
        elif event_type == "input_audio_buffer.committed":
            # Audio buffer was committed, track the item ID
            item_id = event.get("item_id")
            if item_id:
                self.pending_item_ids.add(item_id)
                if self.on_debug_message:
                    self.on_debug_message(f"📦 Audio committed: {item_id}")
                    
        elif event_type == "conversation.item.input_audio_transcription.completed":
            # Final transcription - send to LLM
            transcript = event.get("transcript", "")
            item_id = event.get("item_id")
            logger.info(f"📝 Final transcription: {transcript}")
            self.current_transcription = transcript
            
            # Remove from pending if we were tracking it
            if item_id and item_id in self.pending_item_ids:
                self.pending_item_ids.remove(item_id)
            
            if self.on_debug_message:
                self.on_debug_message(f"COMPLETED (conversation.item): {transcript}")
                
            # Set state back to LISTENING when transcription is completed  
            self._set_state(AudioState.LISTENING)
            
            if self.on_transcription:
                self.on_transcription(transcript)
                
            # Only submit if this is the only completion event we get
            # Check if we've already submitted this transcription
            if transcript.strip() and not hasattr(self, '_last_submitted') or self._last_submitted != transcript:
                self._last_submitted = transcript
                if self.on_debug_message:
                    self.on_debug_message(f"CALLBACK CHECK: {self.on_speech_end_submit is not None}")
                if self.on_speech_end_submit:
                    if self.on_debug_message:
                        self.on_debug_message("TRIGGERED")
                    try:
                        await self.on_speech_end_submit(transcript.strip())
                        if self.on_debug_message:
                            self.on_debug_message("✅ CALLBACK EXECUTED")
                    except Exception as e:
                        if self.on_debug_message:
                            self.on_debug_message(f"❌ CALLBACK ERROR: {e}")
                else:
                    if self.on_debug_message:
                        self.on_debug_message("❌ NO CALLBACK SET")
            elif self.on_debug_message:
                self.on_debug_message("🔄 DUPLICATE - SKIPPING")
                
        elif event_type == "conversation.item.input_audio_transcription.delta":
            # Just log deltas, don't use them since they're batched at the end anyway
            delta = event.get("delta", "")
            logger.debug(f"📝 Transcription delta: '{delta}'")
                
        # Handle transcription session events (dedicated API)
        elif event_type == "input_audio_transcription.completed":
            # Final transcription from dedicated API
            transcript = event.get("transcript", "")
            logger.info(f"📝 Final transcription (dedicated): {transcript}")
            self.current_transcription = transcript
            
            if self.on_debug_message:
                self.on_debug_message(f"COMPLETED (input_audio): {transcript}")
                
            # Set state back to LISTENING when transcription is completed
            self._set_state(AudioState.LISTENING)
            
            if self.on_transcription:
                self.on_transcription(transcript)
                
        elif event_type == "input_audio_transcription.delta":
            # Partial transcription from dedicated API
            delta = event.get("delta", "")
            logger.info(f"📝 Transcription delta (dedicated): '{delta}'")
            if self.config.show_transcription_in_input and delta and self.on_transcription_partial:
                self.on_transcription_partial(delta)
        
        # Full conversation mode events
        elif event_type == "response.text.delta" and self.mode == "full_conversation":
            text_delta = event.get("delta", "")
            if self.on_assistant_text:
                self.on_assistant_text(text_delta)
                
        elif event_type == "response.audio.delta" and self.mode == "full_conversation":
            audio_data = base64.b64decode(event["delta"])
            self.audio_buffer += audio_data
            
        elif event_type == "response.audio.done" and self.mode == "full_conversation":
            if self.audio_buffer:
                self.is_playing_response = True
                self._play_audio(self.audio_buffer)
                self.audio_buffer = b''
    
    def _play_audio(self, audio_data):
        """Play audio response (full_conversation mode only)"""
        def play():
            try:
                # Convert bytes to numpy array for sounddevice
                import numpy as np
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                
                sd.play(audio_array, samplerate=self.rate)
                sd.wait()  # Wait until playback is finished
                logger.info("🔊 Audio played")
            except Exception as e:
                logger.error(f"❌ Audio playback error: {e}")
        
        # Calculate playback duration and reset flag afterwards
        duration = len(audio_data) / (self.rate * 2)
        self._reset_playback_flag_after_delay(duration)
        
        # Play in background thread
        playback_thread = threading.Thread(target=play)
        playback_thread.daemon = True
        playback_thread.start()
    
    def _reset_playback_flag_after_delay(self, duration):
        """Reset playback flag after audio finishes"""
        def reset_flag():
            import time
            time.sleep(duration + 1.0)
            self.is_playing_response = False
            logger.info("🎙️  Ready to receive input again")
        
        import threading
        reset_thread = threading.Thread(target=reset_flag)
        reset_thread.daemon = True
        reset_thread.start()
    
    def _set_state(self, new_state: AudioState):
        """Update audio state and notify callback"""
        old_state = self.current_state
        self.current_state = new_state
        if self.on_debug_message:
            self.on_debug_message(f"🔄 STATE CHANGE: {old_state.value} → {new_state.value}")
            self.on_debug_message(f"🔥 CHECKING CALLBACK: {self.on_state_change is not None}")
        if self.on_state_change:
            if self.on_debug_message:
                self.on_debug_message(f"🔥 CALLING UI CALLBACK with {new_state.value}")
            try:
                self.on_state_change(new_state)
                if self.on_debug_message:
                    self.on_debug_message(f"🔥 UI CALLBACK FINISHED")
            except Exception as e:
                if self.on_debug_message:
                    self.on_debug_message(f"🔥 UI CALLBACK FAILED: {e}")
        else:
            if self.on_debug_message:
                self.on_debug_message("❌ NO CALLBACK SET! on_state_change is None!")
    
    
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
        
        # sounddevice doesn't need explicit termination like PyAudio
        logger.info("✅ Disconnected")
    
    @property
    def state(self) -> AudioState:
        """Get current audio state"""
        return self.current_state
    
    async def send_text_for_speech(self, text: str):
        """Send text to OpenAI TTS API and play the audio"""
        try:
            if not self.api_key:
                logger.error("❌ No OpenAI API key available for TTS")
                return
            
            logger.info(f"🔊 Generating TTS for: {text[:50]}...")
            
            # Import OpenAI client
            import openai
            client = openai.AsyncOpenAI(api_key=self.api_key)
            
            # Generate speech
            response = await client.audio.speech.create(
                model="tts-1",  # Use tts-1 for lower latency
                voice="onyx",   # Male voice, more casual
                input=text,
                response_format="wav"  # WAV for easier playback
            )
            
            # Get audio data
            audio_data = response.content
            logger.info(f"🔊 TTS generated successfully, playing audio ({len(audio_data)} bytes)")
            
            # Play the audio
            self._play_tts_audio(audio_data)
            
        except Exception as e:
            logger.error(f"❌ TTS generation failed: {e}")
    
    def _play_tts_audio(self, audio_data):
        """Play TTS audio data"""
        try:
            import io
            import numpy as np
            
            # Set SPEAKING state when TTS starts
            self._set_state(AudioState.SPEAKING)
            
            # Use soundfile to read the WAV data
            audio_io = io.BytesIO(audio_data)
            data, samplerate = sf.read(audio_io)
            
            # Calculate duration for proper state management
            duration = len(data) / samplerate
            
            # Play using sounddevice
            sd.play(data, samplerate=samplerate)
            sd.wait()  # Wait until playback is finished
                
            logger.info("✅ TTS audio playback completed")
            
            # Set back to LISTENING after TTS completes
            self._set_state(AudioState.LISTENING)
            
        except Exception as e:
            logger.error(f"❌ TTS audio playback failed: {e}")
            # Ensure we return to LISTENING even on error
            self._set_state(AudioState.LISTENING)