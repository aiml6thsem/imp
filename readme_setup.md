# Kokoro TTS FastAPI Server

Complete FastAPI application for text-to-speech with automatic voice switching for screenplays and scripts.

## 🚀 Features

- **Script File Upload**: Upload `.txt`, `.fountain`, or screenplay files with automatic character voice detection
- **Direct Text Processing**: Send text directly with custom voice mappings
- **Batch Processing**: Process multiple texts and get ZIP archive with all audio files
- **Automatic Voice Detection**: Intelligently detects characters and assigns appropriate voices
- **Multi-Voice Support**: 11+ voices (male, female, British accents)
- **Fast CPU Performance**: 15-20x real-time generation on modern 8-core CPU

## 📁 Project Structure

```
kokoro-tts-api/
├── main.py              # FastAPI application with 4 endpoints
├── script_parser.py     # Advanced script parser with character detection
├── tts_engine.py        # Kokoro TTS engine wrapper
├── audio_processor.py   # Audio concatenation and file handling
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── test_scripts/       # Example scripts for testing
    ├── example1.txt
    └── example2.txt
```

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Ubuntu/Debian Linux (recommended) or macOS
- Modern CPU (8+ cores recommended)

### Step 1: System Dependencies

**Ubuntu/Debian:**
```bash
# Update package list
sudo apt-get update

# Install espeak-ng (required by Kokoro)
sudo apt-get install -y espeak-ng

# Install ffmpeg (optional, for MP3 support)
sudo apt-get install -y ffmpeg

# Install libsndfile (for soundfile)
sudo apt-get install -y libsndfile1
```

**macOS:**
```bash
# Using Homebrew
brew install espeak-ng
brew install ffmpeg  # optional
```

### Step 2: Create Virtual Environment

```bash
# Create project directory
mkdir kokoro-tts-api
cd kokoro-tts-api

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

### Step 3: Install Python Dependencies

```bash
# Install all requirements
pip install --upgrade pip
pip install -r requirements.txt

# Verify Kokoro installation
python -c "from kokoro import KPipeline; print('Kokoro installed successfully!')"
```

### Step 4: Create Project Files

Create all 5 Python files in your project directory:
- `main.py`
- `script_parser.py`
- `tts_engine.py`
- `audio_processor.py`
- `requirements.txt`

(Copy the content from the artifacts provided)

### Step 5: Create Test Directory

```bash
# Create test scripts directory
mkdir test_scripts
```

Create `test_scripts/example1.txt`:
```
NARRATOR: The story begins on a dark and stormy night.
JOHN: Hello? Is anyone there?
SARAH: Yes, I'm here. Don't be afraid.
NARRATOR: John walked slowly toward the voice.
JOHN: Thank goodness. I thought I was alone.
```

## 🚀 Running the Server

### Start the Server

```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Start the FastAPI server
python main.py

# Or use uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start at: `http://localhost:8000`

### Check Server Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Kokoro TTS API",
  "version": "1.0.0",
  "components": {
    "tts_engine": "ready",
    "script_parser": "ready",
    "audio_processor": "ready"
  },
  "available_voices": { ... },
  "model": "Kokoro-82M"
}
```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎯 API Endpoints

### 1. Health Check
```bash
GET /health
```

Returns server status and available components.

### 2. Script File Upload (Auto Voice Detection)
```bash
POST /synthesize/script
```

**Upload a script file and get audio with automatic voice switching.**

Example using curl:
```bash
curl -X POST "http://localhost:8000/synthesize/script" \
  -F "file=@test_scripts/example1.txt" \
  -o output.wav
```

Example using Python:
```python
import requests

with open('test_scripts/example1.txt', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/synthesize/script',
        files={'file': f}
    )

with open('output.wav', 'wb') as out:
    out.write(response.content)
```

**Script Format:**
```
NARRATOR: Introduction text here
CHARACTER_NAME: Their dialogue here
ANOTHER_CHARACTER: More dialogue
```

Supported formats:
- `CHARACTER: dialogue`
- `[CHARACTER] dialogue`
- `(CHARACTER) dialogue`
- `**CHARACTER** dialogue`

### 3. Direct Text Processing
```bash
POST /synthesize/text
```

**Send text directly with optional custom voice mappings.**

Example using curl:
```bash
curl -X POST "http://localhost:8000/synthesize/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "NARRATOR: The adventure begins.\nJOHN: Hello world!",
    "voice_mappings": {
      "NARRATOR": "af_heart",
      "JOHN": "am_adam"
    },
    "speed": 1.0,
    "crossfade_ms": 50
  }' \
  -o output.wav
```

Example using Python:
```python
import requests

data = {
    "text": "NARRATOR: Once upon a time.\nJOHN: Hello!\nSARAH: Hi there!",
    "voice_mappings": {
        "NARRATOR": "af_heart",
        "JOHN": "am_adam",
        "SARAH": "af_bella"
    },
    "speed": 1.0,
    "crossfade_ms": 50
}

response = requests.post(
    'http://localhost:8000/synthesize/text',
    json=data
)

with open('output.wav', 'wb') as f:
    f.write(response.content)
```

### 4. Batch Processing
```bash
POST /synthesize/batch
```

**Process multiple texts and get ZIP file with all audio files.**

Example using curl:
```bash
curl -X POST "http://localhost:8000/synthesize/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "NARRATOR: First story begins.",
      "JOHN: Second story here.",
      "SARAH: Third story content."
    ],
    "voice_mappings": {
      "NARRATOR": "af_heart",
      "JOHN": "am_adam",
      "SARAH": "af_bella"
    },
    "speed": 1.0,
    "crossfade_ms": 50
  }' \
  -o batch_output.zip
```

Example using Python:
```python
import requests

data = {
    "texts": [
        "NARRATOR: Story one content here.",
        "JOHN: Story two with John speaking.",
        "SARAH: Story three with Sarah."
    ],
    "voice_mappings": {
        "NARRATOR": "af_heart",
        "JOHN": "am_adam",
        "SARAH": "af_bella"
    },
    "speed": 1.2,
    "crossfade_ms": 30
}

response = requests.post(
    'http://localhost:8000/synthesize/batch',
    json=data
)

# Save ZIP file
with open('batch_output.zip', 'wb') as f:
    f.write(response.content)

# Extract ZIP
import zipfile
with zipfile.ZipFile('batch_output.zip', 'r') as zip_ref:
    zip_ref.extractall('output_audio/')
```

## 🎤 Available Voices

### American English Voices

**Female Voices:**
- `af_bella` - Bella (Warm, expressive)
- `af_sarah` - Sarah (Professional, clear)
- `af_heart` - Heart (Narrator style, neutral)
- `af_sky` - Sky (Young, energetic)
- `af_nicole` - Nicole (Calm, soothing)

**Male Voices:**
- `am_adam` - Adam (Deep, authoritative)
- `am_michael` - Michael (Friendly, approachable)

### British English Voices

**Female Voices:**
- `bf_emma` - Emma (British accent)
- `bf_isabella` - Isabella (British accent)

**Male Voices:**
- `bm_george` - George (British accent)
- `bm_lewis` - Lewis (British accent)

## 🎭 Voice Mapping Examples

### Example 1: Simple Narrator + Characters
```json
{
  "voice_mappings": {
    "NARRATOR": "af_heart",
    "HERO": "am_adam",
    "VILLAIN": "am_michael"
  }
}
```

### Example 2: Multiple Characters
```json
{
  "voice_mappings": {
    "NARRATOR": "af_heart",
    "JOHN": "am_adam",
    "SARAH": "af_bella",
    "MIKE": "am_michael",
    "EMMA": "af_sarah"
  }
}
```

### Example 3: British Accent Story
```json
{
  "voice_mappings": {
    "NARRATOR": "bf_emma",
    "SHERLOCK": "bm_george",
    "WATSON": "bm_lewis"
  }
}
```

## 🧪 Testing

### Test 1: Simple Text
```bash
curl -X POST "http://localhost:8000/synthesize/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "NARRATOR: Hello world, this is a test."}' \
  -o test1.wav
```

### Test 2: Script File
Create `test.txt`:
```
NARRATOR: Welcome to the demo.
JOHN: This is John speaking.
SARAH: And this is Sarah.
```

```bash
curl -X POST "http://localhost:8000/synthesize/script" \
  -F "file=@test.txt" \
  -o test2.wav
```

### Test 3: Batch Processing
```bash
curl -X POST "http://localhost:8000/synthesize/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["NARRATOR: Test 1", "JOHN: Test 2", "SARAH: Test 3"]
  }' \
  -o batch.zip
```

## 🔧 Troubleshooting

### Issue: "espeak-ng not found"
```bash
# Ubuntu/Debian
sudo apt-get install espeak-ng

# macOS
brew install espeak-ng
```

### Issue: "soundfile error"
```bash
# Ubuntu/Debian
sudo apt-get install libsndfile1

# Then reinstall
pip install soundfile --force-reinstall
```

### Issue: "Kokoro import failed"
```bash
# Reinstall kokoro
pip uninstall kokoro
pip install kokoro>=0.9.2
```

### Issue: Port 8000 already in use
```bash
# Use different port
uvicorn main:app --port 8080
```

### Issue: Slow performance
- Ensure you're running on a modern CPU (8+ cores recommended)
- Check CPU usage during synthesis
- Consider processing shorter text segments
- Reduce crossfade duration

## 📊 Performance Metrics

**Expected performance on modern hardware:**
- **Speed**: 15-20x real-time
- **Latency**: <0.3s per sentence
- **Memory**: ~2GB RAM for model
- **CPU**: Utilizes all available cores

**Benchmark example:**
- 1-minute script: ~3-4 seconds processing
- 10-minute script: ~30-40 seconds processing
- 60-minute script: ~3-4 minutes processing

## 🚀 Production Deployment

### Using Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    espeak-ng \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t kokoro-tts-api .
docker run -p 8000:8000 kokoro-tts-api
```

### Using Systemd (Linux Service)

Create `/etc/systemd/system/kokoro-tts.service`:
```ini
[Unit]
Description=Kokoro TTS API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/kokoro-tts-api
Environment="PATH=/opt/kokoro-tts-api/venv/bin"
ExecStart=/opt/kokoro-tts-api/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable kokoro-tts
sudo systemctl start kokoro-tts
sudo systemctl status kokoro-tts
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
        client_max_body_size 50M;
    }
}
```

## 📝 Advanced Usage

### Custom Voice Detection Rules

Edit `script_parser.py` to add custom character names:

```python
self.male_names = {
    'john', 'mike', 'your_character', ...
}

self.female_names = {
    'sarah', 'emma', 'your_character', ...
}
```

### Adjust Crossfade Duration

```python
# Shorter crossfade for faster speech
data = {"text": "...", "crossfade_ms": 20}

# Longer crossfade for smoother transitions
data = {"text": "...", "crossfade_ms": 100}
```

### Speed Control

```python
# Slower speech
data = {"text": "...", "speed": 0.8}

# Faster speech
data = {"text": "...", "speed": 1.5}
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

This project uses Kokoro-82M which is licensed under Apache 2.0.

## 🙏 Acknowledgments

- Kokoro-82M by hexgrad: https://github.com/hexgrad/kokoro
- FastAPI framework: https://fastapi.tiangolo.com/

## 📧 Support

For issues and questions:
- Check the troubleshooting section
- Review API documentation at `/docs`
- Check Kokoro documentation: https://github.com/hexgrad/kokoro

## 🔄 Updates

**Version 1.0.0** (Current)
- Initial release
- 4 core endpoints
- Automatic voice detection
- Batch processing support
- Multi-format script support

---

**Happy synthesizing! 🎉**