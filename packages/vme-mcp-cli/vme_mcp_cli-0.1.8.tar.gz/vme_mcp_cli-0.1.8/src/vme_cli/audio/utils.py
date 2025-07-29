"""
Audio utility functions for device management and configuration
"""

try:
    import sounddevice as sd
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AudioDevice:
    index: int
    name: str
    channels: int
    sample_rate: float
    is_input: bool
    is_output: bool

def list_audio_devices() -> List[AudioDevice]:
    """List all available audio devices"""
    devices = []
    
    try:
        audio = pyaudio.PyAudio()
        
        for i in range(audio.get_device_count()):
            try:
                info = audio.get_device_info_by_index(i)
                device = AudioDevice(
                    index=i,
                    name=info['name'],
                    channels=info['maxInputChannels'] if info['maxInputChannels'] > 0 else info['maxOutputChannels'],
                    sample_rate=info['defaultSampleRate'],
                    is_input=info['maxInputChannels'] > 0,
                    is_output=info['maxOutputChannels'] > 0
                )
                devices.append(device)
            except Exception as e:
                logger.warning(f"Could not get info for device {i}: {e}")
                continue
        
        audio.terminate()
        
    except Exception as e:
        logger.error(f"Failed to list audio devices: {e}")
    
    return devices

def get_default_devices() -> Tuple[Optional[int], Optional[int]]:
    """Get default input and output device indices"""
    try:
        audio = pyaudio.PyAudio()
        
        # Get default devices
        default_input = None
        default_output = None
        
        try:
            default_input_info = audio.get_default_input_device_info()
            default_input = default_input_info['index']
        except Exception:
            pass
        
        try:
            default_output_info = audio.get_default_output_device_info()
            default_output = default_output_info['index']
        except Exception:
            pass
        
        audio.terminate()
        
        return default_input, default_output
        
    except Exception as e:
        logger.error(f"Failed to get default devices: {e}")
        return None, None

def find_device_by_name(name: str, input_only: bool = False, output_only: bool = False) -> Optional[AudioDevice]:
    """Find audio device by name (case-insensitive partial match)"""
    devices = list_audio_devices()
    
    name_lower = name.lower()
    
    for device in devices:
        if name_lower in device.name.lower():
            if input_only and not device.is_input:
                continue
            if output_only and not device.is_output:
                continue
            return device
    
    return None

def validate_audio_config(sample_rate: int, channels: int, input_device: Optional[int] = None, output_device: Optional[int] = None) -> Dict[str, bool]:
    """Validate audio configuration parameters"""
    results = {
        'sample_rate_supported': False,
        'input_device_valid': False,
        'output_device_valid': False,
        'configuration_valid': False
    }
    
    try:
        audio = pyaudio.PyAudio()
        
        # Check sample rate support (test with default devices)
        try:
            if input_device is None:
                input_device = audio.get_default_input_device_info()['index']
            if output_device is None:
                output_device = audio.get_default_output_device_info()['index']
        except Exception:
            pass
        
        # Test input device and sample rate
        if input_device is not None:
            try:
                if audio.is_format_supported(
                    rate=sample_rate,
                    input_device=input_device,
                    input_channels=channels,
                    input_format=pyaudio.paInt16
                ):
                    results['input_device_valid'] = True
                    results['sample_rate_supported'] = True
            except Exception as e:
                logger.debug(f"Input validation failed: {e}")
        
        # Test output device and sample rate
        if output_device is not None:
            try:
                if audio.is_format_supported(
                    rate=sample_rate,
                    output_device=output_device,
                    output_channels=channels,
                    output_format=pyaudio.paInt16
                ):
                    results['output_device_valid'] = True
                    if not results['sample_rate_supported']:
                        results['sample_rate_supported'] = True
            except Exception as e:
                logger.debug(f"Output validation failed: {e}")
        
        # Overall configuration validity
        results['configuration_valid'] = (
            results['sample_rate_supported'] and
            (results['input_device_valid'] or input_device is None) and
            (results['output_device_valid'] or output_device is None)
        )
        
        audio.terminate()
        
    except Exception as e:
        logger.error(f"Audio validation failed: {e}")
    
    return results

def print_audio_devices():
    """Print all available audio devices (for debugging)"""
    devices = list_audio_devices()
    default_input, default_output = get_default_devices()
    
    print("Available Audio Devices:")
    print("-" * 80)
    
    for device in devices:
        default_marker = ""
        if device.index == default_input:
            default_marker += " [DEFAULT INPUT]"
        if device.index == default_output:
            default_marker += " [DEFAULT OUTPUT]"
        
        io_type = []
        if device.is_input:
            io_type.append("INPUT")
        if device.is_output:
            io_type.append("OUTPUT")
        
        print(f"{device.index:2d}: {device.name}")
        print(f"     Type: {'/'.join(io_type)} | Channels: {device.channels} | Sample Rate: {device.sample_rate:.0f}Hz{default_marker}")
        print()

if __name__ == "__main__":
    # Test script
    print_audio_devices()
    
    # Test validation
    print("\nTesting audio configuration (24kHz, 1 channel):")
    results = validate_audio_config(24000, 1)
    for key, value in results.items():
        print(f"  {key}: {value}")