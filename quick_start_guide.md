# 🚀 QUICK START - Get Running in 5 Minutes

## Step-by-Step Setup

### 1️⃣ Install System Dependencies (1 minute)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y espeak-ng libsndfile1
```

**macOS:**
```bash
brew install espeak-ng
```

### 2️⃣ Create Project (30 seconds)

```bash
# Create directory
mkdir kokoro-tts-api
cd kokoro-tts-api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows
```

### 3️⃣ Install Python Packages (2 minutes)

```bash
# Install dependencies
pip install --upgrade pip
pip install fastapi uvicorn[standard] python-multipart pydantic
pip install kokoro soundfile numpy
```

### 4️⃣ Create Files (1 minute)

Save these 4 files in your project directory:

**File 1: `main.py`** (copy from artifacts)
**File 2: `script_parser.py`** (copy from artifacts)
**File 3: `tts_engine.py`** (copy from artifacts)
**File 4: `audio_processor.py`** (copy from artifacts)

### 5️⃣ Start Server (30 seconds)

```bash
python main.py
```

✅ **Done!** Server running at http://localhost:8000

---

## 🎯 Test It Immediately

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

### Test 2: Quick Text-to-Speech
```bash
curl -X POST "http://localhost:8000/synthesize/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "NARRATOR: Hello, this is a test!"}' \
  -o test.wav
```

**Play the audio:**
```bash
# Linux
aplay test.wav

# macOS
afplay test.wav

# Windows
start test.wav
```

---

## 📝 Example Scripts

### Example 1: Simple Dialogue

Create `test1.txt`:
```
NARRATOR: Welcome to the test.
JOHN: Hello everyone!
SARAH: Nice to meet you.
```

Test it:
```bash
curl -X POST "http://localhost:8000/synthesize/script" \
  -F "file=@test1.txt" \
  -o output1.wav
```

### Example 2: Story with Multiple Characters

Create `story.txt`:
```
NARRATOR: Once upon a time, in a land far away.
HERO: I must go on this quest!
MENTOR: Remember what I taught you, young one.
VILLAIN: You'll never succeed!
HERO: We shall see about that!
NARRATOR: And so the adventure began.
```

Test it:
```bash
curl -X POST "http://localhost:8000/synthesize/script" \
  -F "file=@story.txt" \
  -o story.wav
```

### Example 3: Custom Voice Mapping

```bash
curl -X POST "http://localhost:8000/synthesize/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "WIZARD: I shall cast a spell!\nWARRIOR: And I will charge into battle!",
    "voice_mappings": {
      "WIZARD": "bm_george",
      "WARRIOR": "am_adam"
    }
  }' \
  -o battle.wav
```

---

## 🐍 Python Client Example

Save as `quick_test.py`:

```python
import requests

# Test 1: Simple text
response = requests.post(
    'http://localhost:8000/synthesize/text',
    json={
        "text": "NARRATOR: Python test successful!",
        "speed": 1.0
    }
)

with open('python_test.wav', 'wb') as f:
    f.write(response.content)

print("✓ Audio saved to python_test.wav")

# Test 2: With custom voices
response = requests.post(
    'http://localhost:8000/synthesize/text',
    json={
        "text": """NARRATOR: This is a story.
JOHN: With multiple characters.
SARAH: And different voices!""",
        "voice_mappings": {
            "NARRATOR": "af_heart",
            "JOHN": "am_adam", 
            "SARAH": "af_bella"
        }
    }
)

with open('multi_voice.wav', 'wb') as f:
    f.write(response.content)

print("✓ Multi-voice audio saved to multi_voice.wav")
```

Run it:
```bash
python quick_test.py
```

---

## 🎤 Available Voices - Quick Reference

**Female Voices:**
- `af_bella` - Warm, expressive
- `af_sarah` - Professional
- `af_heart` - Narrator (default)
- `af_sky` - Young, energetic
- `af_nicole` - Calm

**Male Voices:**
- `am_adam` - Deep, authoritative
- `am_michael` - Friendly

**British Voices:**
- `bf_emma`, `bf_isabella` (female)
- `bm_george`, `bm_lewis` (male)

---

## 🔧 Common Issues

### "espeak-ng not found"
```bash
sudo apt-get install espeak-ng
```

### "Module 'kokoro' not found"
```bash
pip install kokoro --upgrade
```

### "Port 8000 in use"
```bash
uvicorn main:app --port 8080
```

### "Slow performance"
- Normal for first run (model loading)
- Subsequent requests are fast (15-20x real-time)

---

## 📊 Performance Expectations

On modern 8-core CPU:
- **First request**: 5-10 seconds (model loading)
- **Subsequent requests**: <0.3s per sentence
- **1-minute script**: ~3-4 seconds
- **10-minute script**: ~30-40 seconds

---

## 🌐 Web Interface

Visit these URLs after starting the server:
- **API Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

---

## 📦 All-in-One Test Script

Create `run_all_tests.sh`:

```bash
#!/bin/bash

echo "🧪 Running All Tests..."

# Test 1: Health
echo -e "\n1️⃣ Health Check..."
curl -s http://localhost:8000/health | jq

# Test 2: Simple text
echo -e "\n2️⃣ Simple Text..."
curl -X POST "http://localhost:8000/synthesize/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "NARRATOR: Test successful!"}' \
  -o test_simple.wav
echo "✓ Saved to test_simple.wav"

# Test 3: Multiple voices
echo -e "\n3️⃣ Multiple Voices..."
cat > temp_script.txt << 'EOF'
NARRATOR: Testing multiple voices.
JOHN: This is John speaking.
SARAH: And this is Sarah.
EOF

curl -X POST "http://localhost:8000/synthesize/script" \
  -F "file=@temp_script.txt" \
  -o test_multi.wav
echo "✓ Saved to test_multi.wav"

# Test 4: Batch
echo -e "\n4️⃣ Batch Processing..."
curl -X POST "http://localhost:8000/synthesize/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "NARRATOR: Batch test 1",
      "JOHN: Batch test 2",
      "SARAH: Batch test 3"
    ]
  }' \
  -o test_batch.zip
echo "✓ Saved to test_batch.zip"

echo -e "\n✅ All tests complete!"
echo "Files created: test_simple.wav, test_multi.wav, test_batch.zip"

# Cleanup
rm temp_script.txt
```

Run it:
```bash
chmod +x run_all_tests.sh
./run_all_tests.sh
```

---

## 🎓 Next Steps

1. ✅ Server is running
2. ✅ Basic tests pass
3. 📖 Read full README.md for advanced features
4. 🔧 Customize voice mappings in `script_parser.py`
5. 🚀 Deploy to production (see README.md)

---

## 💡 Pro Tips

**Tip 1: Faster Processing**
```python
# Reduce crossfade for speed
{"text": "...", "crossfade_ms": 20}
```

**Tip 2: Better Quality**
```python
# Slower speed, longer crossfade
{"text": "...", "speed": 0.9, "crossfade_ms": 100}
```

**Tip 3: Auto-detect Works Best With:**
- Character names in ALL CAPS
- Colon after character name: `CHARACTER: dialogue`
- Consistent formatting

---

## 📞 Need Help?

1. Check logs: Look at terminal output
2. Test health: `curl http://localhost:8000/health`
3. Check Kokoro: `python -c "from kokoro import KPipeline; print('OK')"`
4. Review README.md for detailed troubleshooting

---

**🎉 You're all set! Happy synthesizing!**