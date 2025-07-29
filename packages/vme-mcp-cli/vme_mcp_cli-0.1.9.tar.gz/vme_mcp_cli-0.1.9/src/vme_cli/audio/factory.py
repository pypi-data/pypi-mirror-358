"""
Audio factory for creating configured audio manager from client settings
"""

import os
import logging
from typing import Optional, Union

from vme_cli.config.settings import AudioConfig
from vme_cli.audio.flexible_audio_manager import FlexibleAudioManager

logger = logging.getLogger(__name__)

def create_audio_manager(audio_config: AudioConfig, config=None) -> Optional[FlexibleAudioManager]:
    """Create flexible audio manager supporting multiple modes"""
    
    logger.info(f"🎧 Audio factory called - enabled: {audio_config.enabled}, mode: {audio_config.mode}")
    
    if not audio_config.enabled:
        logger.info("Audio is disabled in configuration")
        return None
    
    # Get OpenAI API key
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        logger.error("❌ OPENAI_API_KEY environment variable not set!")
        logger.error("❌ Audio manager needs OpenAI API key for real-time audio")
        return None
    
    logger.info(f"🎙️  Creating flexible audio manager (mode: {audio_config.mode})...")
    
    try:
        manager = FlexibleAudioManager(audio_config, openai_api_key=openai_api_key)
        logger.info(f"✅ FlexibleAudioManager created successfully in {audio_config.mode} mode")
        return manager
    except Exception as e:
        logger.error(f"❌ Failed to create FlexibleAudioManager: {e}")
        logger.exception("Full exception:")
        return None