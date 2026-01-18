"""
Audio Processing and Concatenation
"""

import numpy as np
from typing import List
import logging

logger = logging.getLogger(__name__)


class AudioProcessor:
    """
    Handles audio concatenation and file operations
    """
    
    def __init__(self, sample_rate: int = 24000):
        self.sample_rate = sample_rate
    
    def concatenate_with_crossfade(
        self,
        audio_segments: List[np.ndarray],
        crossfade_duration_ms: int = 50
    ) -> np.ndarray:
        """
        Concatenate audio segments with crossfade
        
        Args:
            audio_segments: List of audio arrays
            crossfade_duration_ms: Crossfade duration in milliseconds
            
        Returns:
            Concatenated audio
        """
        if not audio_segments:
            raise ValueError("No audio segments to concatenate")
        
        if len(audio_segments) == 1:
            return audio_segments[0]
        
        # Calculate crossfade samples
        crossfade_samples = int(self.sample_rate * crossfade_duration_ms / 1000)
        
        result = audio_segments[0]
        
        for i in range(1, len(audio_segments)):
            current = audio_segments[i]
            
            if crossfade_samples > 0 and len(result) >= crossfade_samples:
                # Apply crossfade
                fade_out = np.linspace(1.0, 0.0, crossfade_samples)
                fade_in = np.linspace(0.0, 1.0, crossfade_samples)
                
                # Get the tail of previous segment
                tail = result[-crossfade_samples:] * fade_out
                
                # Get the head of current segment
                if len(current) >= crossfade_samples:
                    head = current[:crossfade_samples] * fade_in
                    
                    # Mix crossfade region
                    crossfaded = tail + head
                    
                    # Concatenate: result[:-crossfade] + crossfaded + current[crossfade:]
                    result = np.concatenate([
                        result[:-crossfade_samples],
                        crossfaded,
                        current[crossfade_samples:]
                    ])
                else:
                    # Current segment too short for crossfade
                    result = np.concatenate([result, current])
            else:
                # No crossfade, simple concatenation
                result = np.concatenate([result, current])
        
        logger.info(f"Concatenated {len(audio_segments)} segments: {len(result)} samples")
        
        return result
    
    def save_audio(self, audio: np.ndarray, output_path: str):
        """
        Save audio to WAV file
        
        Args:
            audio: Audio data
            output_path: Output file path
        """
        try:
            import soundfile as sf
            
            # Normalize if needed
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)
            
            # Ensure audio is in range [-1, 1]
            max_val = np.abs(audio).max()
            if max_val > 1.0:
                audio = audio / max_val
            
            sf.write(output_path, audio, self.sample_rate)
            logger.info(f"Saved audio to {output_path}")
            
        except ImportError:
            logger.error("soundfile not installed. Install: pip install soundfile")
            raise
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            raise
    
    def save_as_mp3(self, audio: np.ndarray, output_path: str, bitrate: str = "192k"):
        """
        Save audio as MP3 (requires pydub and ffmpeg)
        
        Args:
            audio: Audio data
            output_path: Output file path
            bitrate: MP3 bitrate
        """
        try:
            from pydub import AudioSegment
            import soundfile as sf
            import tempfile
            
            # Save as temporary WAV
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                sf.write(tmp.name, audio, self.sample_rate)
                tmp_path = tmp.name
            
            # Convert to MP3
            audio_segment = AudioSegment.from_wav(tmp_path)
            audio_segment.export(output_path, format="mp3", bitrate=bitrate)
            
            # Clean up
            import os
            os.remove(tmp_path)
            
            logger.info(f"Saved MP3 to {output_path}")
            
        except ImportError:
            logger.error("pydub not installed. Install: pip install pydub")
            raise
        except Exception as e:
            logger.error(f"Failed to save MP3: {e}")
            raise
