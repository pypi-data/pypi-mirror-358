"""
Audio dependency checker for VME Textual CLI Client
Checks if real audio hardware access is available
"""

import logging
import sys
from typing import Tuple, List

logger = logging.getLogger(__name__)

def check_audio_dependencies() -> Tuple[bool, List[str]]:
    """
    Check if audio dependencies are available for real microphone access
    
    Returns:
        (success, missing_dependencies)
    """
    missing = []
    
    # Check audio libraries (sounddevice/soundfile)
    try:
        import sounddevice as sd
        import soundfile as sf
        # Try to query devices
        devices = sd.query_devices()
        logger.info("✅ Audio libraries available")
    except ImportError:
        missing.append("audio-libs")
        logger.warning("❌ Audio libraries not installed")
    except Exception as e:
        missing.append("audio-system")
        logger.warning(f"❌ Audio system error: {e}")
    
    # Check system audio
    try:
        import subprocess
        result = subprocess.run(['pactl', 'info'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            logger.info("✅ PulseAudio/PipeWire: Available")
        else:
            missing.append("pulseaudio")
            logger.warning("❌ PulseAudio/PipeWire not available")
    except FileNotFoundError:
        missing.append("pulseaudio")
        logger.warning("❌ pactl command not found")
    except Exception as e:
        logger.warning(f"❌ Audio system check failed: {e}")
    
    return len(missing) == 0, missing

def get_installation_instructions(missing_deps: List[str]) -> List[str]:
    """Get installation instructions for missing dependencies"""
    instructions = []
    
    if "portaudio-devel" in missing_deps:
        instructions.append("sudo dnf install -y portaudio-devel")
    
    if "audio-libs" in missing_deps:
        instructions.append("pip install 'vme-mcp-cli[audio]'")
    
    if "pulseaudio" in missing_deps:
        instructions.append("sudo dnf install -y pulseaudio-utils")
    
    return instructions

def prompt_user_for_audio_disable() -> bool:
    """
    Prompt user if they want to disable audio when dependencies are missing
    
    Returns:
        True if user wants to disable audio, False to continue with mock
    """
    print("\n🎙️  AUDIO DEPENDENCY ISSUE")
    print("=" * 50)
    print("Audio is enabled in your config, but required dependencies are missing.")
    print("\nOptions:")
    print("1. Install missing dependencies (recommended)")
    print("2. Disable audio in config (text-only mode)")
    print("3. Continue with mock audio (for testing)")
    
    while True:
        try:
            choice = input("\nChoose option (1/2/3): ").strip()
            if choice == "1":
                return False  # Don't disable, show instructions
            elif choice == "2":
                return True   # Disable audio
            elif choice == "3":
                print("🧪 Continuing with mock audio for testing...")
                return False  # Don't disable, use mock
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            sys.exit(1)
        except EOFError:
            # Non-interactive mode, default to mock
            return False

def check_and_handle_audio_dependencies(config) -> Tuple[bool, bool]:
    """
    Check audio dependencies and handle missing ones
    
    Returns:
        (audio_available, should_disable_audio)
    """
    if not config.audio.enabled:
        return False, False
    
    success, missing = check_audio_dependencies()
    
    if success:
        logger.info("🎙️  All audio dependencies available - using real microphone")
        return True, False
    
    print(f"\n❌ Missing audio dependencies: {', '.join(missing)}")
    
    instructions = get_installation_instructions(missing)
    if instructions:
        print("\n📋 To install missing dependencies:")
        for instruction in instructions:
            print(f"   {instruction}")
    
    # In non-interactive mode, default to mock
    if not sys.stdin.isatty():
        logger.warning("Non-interactive mode: using mock audio")
        return False, False
    
    # Interactive mode: ask user
    disable_audio = prompt_user_for_audio_disable()
    
    if disable_audio:
        print("🔇 Audio will be disabled for this session")
        return False, True
    else:
        print("🧪 Using mock audio (no real microphone access)")
        return False, False