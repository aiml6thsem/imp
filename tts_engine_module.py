"""
Kokoro TTS Engine Wrapper
"""

import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class KokoroTTSEngine:
    """
    Wrapper for Kokoro-82M TTS model
    """
    
    def __init__(self):
        self.pipeline = None
        self.sample_rate = 24000
        
        # Available voices in Kokoro
        self.voices = {
            # Female voices
            'af_bella': 'Bella (Female, Warm)',
            'af_sarah': 'Sarah (Female, Professional)',
            'af_heart': 'Heart (Female, Narrator)',
            'af_sky': 'Sky (Female, Young)',
            'af_nicole': 'Nicole (Female, Calm)',
            
            # Male voices
            'am_adam': 'Adam (Male, Deep)',
            'am_michael': 'Michael (Male, Friendly)',
            
            # British accents
            'bf_emma': 'Emma (British Female)',
            'bf_isabella': 'Isabella (British Female)',
            'bm_george': 'George (British Male)',
            'bm_lewis': 'Lewis (British Male)',
        }
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Kokoro model"""
        try:
            from kokoro import KPipeline
            
            # Initialize with American English
            self.pipeline = KPipeline(lang_code='a')
            logger.info("Kokoro TTS engine initialized successfully")
            
        except ImportError as e:
            logger.error(f"Failed to import Kokoro: {e}")
            logger.error("Please install: pip install kokoro")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Kokoro: {e}")
            raise
    
    def is_ready(self) -> bool:
        """Check if engine is ready"""
        return self.pipeline is not None
    
    def synthesize(
        self,
        text: str,
        voice: str = 'af_heart',
        speed: float = 1.0,
        language: str = 'en-us'
    ) -> np.ndarray:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            voice: Voice ID
            speed: Speech speed (0.5-2.0)
            language: Language code
            
        Returns:
            Audio data as numpy array
        """
        if not self.pipeline:
            raise RuntimeError("TTS engine not initialized")
        
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Validate voice
        if voice not in self.voices:
            logger.warning(f"Voice '{voice}' not found, using default 'af_heart'")
            voice = 'af_heart'
        
        try:
            logger.info(f"Synthesizing: voice={voice}, length={len(text)}, speed={speed}")
            
            # Generate audio
            generator = self.pipeline(text, voice=voice, speed=speed)
            
            # Collect all audio chunks
            audio_chunks = []
            for _, _, audio in generator:
                audio_chunks.append(audio)
            
            # Concatenate
            if not audio_chunks:
                raise RuntimeError("No audio generated")
            
            final_audio = np.concatenate(audio_chunks)
            
            logger.info(f"Generated audio: {len(final_audio)} samples")
            
            return final_audio
            
        except Exception as e:
            logger.error(f"Synthesis failed: {e}", exc_info=True)
            raise RuntimeError(f"Synthesis failed: {e}")
    
    def get_voice_list(self) -> dict:
        """Get available voices"""
        return self.voices
    
    def get_voice_info(self) -> dict:
        """Get detailed voice information"""
        return {
            'count': len(self.voices),
            'voices': self.voices,
            'sample_rate': self.sample_rate
        }
