"""
Test Client for Kokoro TTS API
Run this to test all endpoints
"""

import requests
import json
import time
from pathlib import Path


class KokoroTTSClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def health_check(self):
        """Test health endpoint"""
        print("\n" + "="*60)
        print("TEST 1: Health Check")
        print("="*60)
        
        try:
            response = requests.get(f"{self.base_url}/health")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_script_file(self, script_path="test_script.txt"):
        """Test script file upload endpoint"""
        print("\n" + "="*60)
        print("TEST 2: Script File Upload")
        print("="*60)
        
        # Create test script if doesn't exist
        if not Path(script_path).exists():
            with open(script_path, 'w') as f:
                f.write("""NARRATOR: The story begins on a cold winter morning.
JOHN: Good morning, Sarah! How are you today?
SARAH: I'm doing well, thank you for asking.
NARRATOR: They walked together through the park.
JOHN: Isn't it beautiful here?
SARAH: Yes, absolutely stunning.""")
            print(f"✓ Created test script: {script_path}")
        
        try:
            with open(script_path, 'rb') as f:
                files = {'file': f}
                
                print("Sending request...")
                start_time = time.time()
                
                response = requests.post(
                    f"{self.base_url}/synthesize/script",
                    files=files
                )
                
                elapsed = time.time() - start_time
                
                print(f"Status Code: {response.status_code}")
                print(f"Processing Time: {elapsed:.2f} seconds")
                
                if response.status_code == 200:
                    output_file = "output_script.wav"
                    with open(output_file, 'wb') as out:
                        out.write(response.content)
                    print(f"✓ Audio saved to: {output_file}")
                    print(f"✓ File size: {len(response.content)} bytes")
                    return True
                else:
                    print(f"❌ Error: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_direct_text(self):
        """Test direct text endpoint"""
        print("\n" + "="*60)
        print("TEST 3: Direct Text Processing")
        print("="*60)
        
        data = {
            "text": """NARRATOR: This is a test of direct text processing.
JOHN: Hello, this is John speaking with a male voice.
SARAH: And I'm Sarah, speaking with a female voice.
NARRATOR: The system automatically detects speakers and assigns voices.""",
            "voice_mappings": {
                "NARRATOR": "af_heart",
                "JOHN": "am_adam",
                "SARAH": "af_bella"
            },
            "speed": 1.0,
            "crossfade_ms": 50
        }
        
        try:
            print(f"Sending text ({len(data['text'])} characters)...")
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/synthesize/text",
                json=data
            )
            
            elapsed = time.time() - start_time
            
            print(f"Status Code: {response.status_code}")
            print(f"Processing Time: {elapsed:.2f} seconds")
            
            if response.status_code == 200:
                output_file = "output_text.wav"
                with open(output_file, 'wb') as out:
                    out.write(response.content)
                print(f"✓ Audio saved to: {output_file}")
                print(f"✓ File size: {len(response.content)} bytes")
                return True
            else:
                print(f"❌ Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_batch_processing(self):
        """Test batch processing endpoint"""
        print("\n" + "="*60)
        print("TEST 4: Batch Processing")
        print("="*60)
        
        data = {
            "texts": [
                "NARRATOR: This is the first audio file in the batch.",
                "JOHN: This is the second file with John speaking.",
                "SARAH: And this is the third file with Sarah.",
                "NARRATOR: Finally, the fourth file wraps things up."
            ],
            "voice_mappings": {
                "NARRATOR": "af_heart",
                "JOHN": "am_adam",
                "SARAH": "af_bella"
            },
            "speed": 1.0,
            "crossfade_ms": 50
        }
        
        try:
            print(f"Processing {len(data['texts'])} texts...")
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/synthesize/batch",
                json=data
            )
            
            elapsed = time.time() - start_time
            
            print(f"Status Code: {response.status_code}")
            print(f"Processing Time: {elapsed:.2f} seconds")
            
            if response.status_code == 200:
                output_file = "output_batch.zip"
                with open(output_file, 'wb') as out:
                    out.write(response.content)
                print(f"✓ ZIP saved to: {output_file}")
                print(f"✓ File size: {len(response.content)} bytes")
                
                # Extract and show contents
                import zipfile
                with zipfile.ZipFile(output_file, 'r') as zip_ref:
                    files = zip_ref.namelist()
                    print(f"✓ Contains {len(files)} audio files:")
                    for f in files:
                        print(f"  - {f}")
                    
                    # Extract
                    zip_ref.extractall("batch_output/")
                    print(f"✓ Extracted to: batch_output/")
                
                return True
            else:
                print(f"❌ Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "🚀"*30)
        print(" "*20 + "KOKORO TTS API TEST SUITE")
        print("🚀"*30)
        
        results = {
            "Health Check": self.health_check(),
            "Script File Upload": self.test_script_file(),
            "Direct Text Processing": self.test_direct_text(),
            "Batch Processing": self.test_batch_processing()
        }
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        for test_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name}: {status}")
        
        total = len(results)
        passed = sum(results.values())
        
        print("\n" + "-"*60)
        print(f"Total: {passed}/{total} tests passed")
        print("-"*60 + "\n")
        
        if passed == total:
            print("🎉 All tests passed! Your API is working correctly!")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")


def main():
    # Check if server is running
    print("Checking if server is running at http://localhost:8000...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        print("✓ Server is running!")
    except:
        print("\n❌ ERROR: Cannot connect to server!")
        print("\nPlease start the server first:")
        print("  python main.py")
        print("\nOr:")
        print("  uvicorn main:app --reload")
        return
    
    # Run tests
    client = KokoroTTSClient()
    client.run_all_tests()


if __name__ == "__main__":
    main()
