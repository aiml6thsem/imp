"""
═══════════════════════════════════════════════════════════════
FILE 1: main.py - FastAPI Application with 4 Endpoints
═══════════════════════════════════════════════════════════════
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import tempfile
import logging
from pathlib import Path

from script_parser import ScriptParser
from tts_engine import KokoroTTSEngine
from audio_processor import AudioProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Kokoro TTS API",
    description="Text-to-Speech with automatic voice switching",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize
script_parser = ScriptParser()
tts_engine = KokoroTTSEngine()
audio_processor = AudioProcessor()


# Models
class TextTTSRequest(BaseModel):
    text: str
    voice_mappings: Optional[Dict[str, str]] = None
    speed: Optional[float] = 1.0
    crossfade_ms: Optional[int] = 50


class BatchTTSRequest(BaseModel):
    texts: List[str]
    voice_mappings: Optional[Dict[str, str]] = None
    speed: Optional[float] = 1.0
    crossfade_ms: Optional[int] = 50


# ═══════════════════════════════════════════════════════════════
# ENDPOINT 1: Health Check
# ═══════════════════════════════════════════════════════════════
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        engine_status = tts_engine.is_ready()
        
        return {
            "status": "healthy" if engine_status else "degraded",
            "service": "Kokoro TTS API",
            "version": "1.0.0",
            "components": {
                "tts_engine": "ready" if engine_status else "not_ready",
                "script_parser": "ready",
                "audio_processor": "ready"
            },
            "available_voices": tts_engine.get_voice_list(),
            "model": "Kokoro-82M"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# ═══════════════════════════════════════════════════════════════
# ENDPOINT 2: Script File Upload with Auto Voice Detection
# ═══════════════════════════════════════════════════════════════
@app.post("/synthesize/script")
async def synthesize_script(
    file: UploadFile = File(...),
):
    """
    Upload a script file and get audio with automatic voice switching
    
    Supported formats: .txt, .fountain, .screenplay
    
    Example script format:
    ```
    NARRATOR: The story begins on a dark night.
    JOHN: Hello, is anyone there?
    SARAH: Yes, I'm here. Don't be afraid.
    ```
    
    Returns: WAV audio file
    """
    try:
        logger.info(f"Processing script file: {file.filename}")
        
        # Read file content
        content = await file.read()
        script_text = content.decode('utf-8')
        
        if not script_text.strip():
            raise HTTPException(status_code=400, detail="Empty script file")
        
        logger.info(f"Script length: {len(script_text)} characters")
        
        # Parse script to detect dialogue and speakers
        segments = script_parser.parse_script(script_text)
        logger.info(f"Detected {len(segments)} dialogue segments")
        
        if not segments:
            raise HTTPException(
                status_code=400,
                detail="No dialogue detected. Use format like 'CHARACTER: dialogue'"
            )
        
        # Generate audio for each segment
        audio_segments = []
        for i, (voice, text) in enumerate(segments):
            logger.info(f"Segment {i+1}/{len(segments)}: voice={voice}, text_length={len(text)}")
            
            audio_data = tts_engine.synthesize(
                text=text.strip(),
                voice=voice
            )
            audio_segments.append(audio_data)
        
        # Concatenate with crossfade
        logger.info("Concatenating audio segments...")
        final_audio = audio_processor.concatenate_with_crossfade(
            audio_segments,
            crossfade_duration_ms=50
        )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            audio_processor.save_audio(final_audio, tmp_file.name)
            output_path = tmp_file.name
        
        logger.info(f"Script synthesis complete: {output_path}")
        
        return FileResponse(
            output_path,
            media_type="audio/wav",
            filename=f"{Path(file.filename).stem}_audio.wav"
        )
        
    except Exception as e:
        logger.error(f"Script synthesis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════
# ENDPOINT 3: Direct Text with Voice Mapping
# ═══════════════════════════════════════════════════════════════
@app.post("/synthesize/text")
async def synthesize_text(request: TextTTSRequest):
    """
    Send text directly with optional voice mappings
    
    Request body:
    {
        "text": "NARRATOR: Story begins\\nJOHN: Hello there",
        "voice_mappings": {
            "NARRATOR": "af_heart",
            "JOHN": "am_adam"
        },
        "speed": 1.0,
        "crossfade_ms": 50
    }
    
    If voice_mappings not provided, auto-detection with default voices
    
    Returns: WAV audio file
    """
    try:
        logger.info(f"Processing direct text: {len(request.text)} characters")
        
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Parse script
        segments = script_parser.parse_script(
            request.text,
            voice_mappings=request.voice_mappings
        )
        
        logger.info(f"Detected {len(segments)} segments")
        
        if not segments:
            raise HTTPException(
                status_code=400,
                detail="No dialogue detected. Use format: 'CHARACTER: dialogue'"
            )
        
        # Generate audio
        audio_segments = []
        for voice, text in segments:
            audio_data = tts_engine.synthesize(
                text=text.strip(),
                voice=voice,
                speed=request.speed
            )
            audio_segments.append(audio_data)
        
        # Concatenate
        final_audio = audio_processor.concatenate_with_crossfade(
            audio_segments,
            crossfade_duration_ms=request.crossfade_ms
        )
        
        # Save
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            audio_processor.save_audio(final_audio, tmp_file.name)
            output_path = tmp_file.name
        
        logger.info(f"Text synthesis complete: {output_path}")
        
        return FileResponse(
            output_path,
            media_type="audio/wav",
            filename="text_audio.wav"
        )
        
    except Exception as e:
        logger.error(f"Text synthesis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════
# ENDPOINT 4: Batch Processing Multiple Texts
# ═══════════════════════════════════════════════════════════════
@app.post("/synthesize/batch")
async def synthesize_batch(request: BatchTTSRequest):
    """
    Process multiple texts in batch and get individual audio files in ZIP
    
    Request body:
    {
        "texts": [
            "NARRATOR: First story",
            "JOHN: Second story",
            "SARAH: Third story"
        ],
        "voice_mappings": {
            "NARRATOR": "af_heart",
            "JOHN": "am_adam",
            "SARAH": "af_bella"
        },
        "speed": 1.0
    }
    
    Returns: ZIP file containing multiple WAV files
    """
    try:
        import zipfile
        
        logger.info(f"Batch processing {len(request.texts)} texts")
        
        if not request.texts:
            raise HTTPException(status_code=400, detail="No texts provided")
        
        output_files = []
        
        for idx, text in enumerate(request.texts):
            logger.info(f"Processing batch item {idx+1}/{len(request.texts)}")
            
            if not text.strip():
                logger.warning(f"Skipping empty text at index {idx}")
                continue
            
            # Parse
            segments = script_parser.parse_script(
                text,
                voice_mappings=request.voice_mappings
            )
            
            if not segments:
                logger.warning(f"No dialogue in text {idx}, treating as single segment")
                segments = [("af_heart", text)]
            
            # Generate audio
            audio_segments = []
            for voice, seg_text in segments:
                audio_data = tts_engine.synthesize(
                    text=seg_text.strip(),
                    voice=voice,
                    speed=request.speed
                )
                audio_segments.append(audio_data)
            
            # Concatenate
            final_audio = audio_processor.concatenate_with_crossfade(
                audio_segments,
                crossfade_duration_ms=request.crossfade_ms
            )
            
            # Save
            output_path = f"/tmp/batch_audio_{idx+1}.wav"
            audio_processor.save_audio(final_audio, output_path)
            output_files.append(output_path)
        
        # Create ZIP
        zip_path = "/tmp/batch_output.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for i, file_path in enumerate(output_files):
                zipf.write(file_path, f"audio_{i+1}.wav")
        
        logger.info(f"Batch processing complete: {len(output_files)} files")
        
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename="batch_audio.zip"
        )
        
    except Exception as e:
        logger.error(f"Batch processing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


"""
═══════════════════════════════════════════════════════════════
FILE 2: script_parser.py - Advanced Script Parser
═══════════════════════════════════════════════════════════════
"""
# (See next artifact)

"""
═══════════════════════════════════════════════════════════════
FILE 3: tts_engine.py - Kokoro TTS Engine
═══════════════════════════════════════════════════════════════
"""
# (See next artifact)

"""
═══════════════════════════════════════════════════════════════
FILE 4: audio_processor.py - Audio Processing
═══════════════════════════════════════════════════════════════
"""
# (See next artifact)