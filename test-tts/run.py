"""
TTS Voice Comparison Tool
Run: python test-tts/run.py

Generates audio samples with different voices for comparison.
Edit config.py to customize voices and providers.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass  # dotenv not installed, use system env vars

from config import TEST_TEXT, PROVIDERS, EDGE_VOICES, GTTS_LANGS, OUTPUT_DIR

# Try to import optional config, fallback if not defined
try:
    from config import KOKORO_VOICES
except ImportError:
    KOKORO_VOICES = ["af_heart"]

try:
    from config import PARLER_EMOTIONS
except ImportError:
    PARLER_EMOTIONS = [("A young Indian man speaking excitedly in Hindi", "excited_male")]

try:
    from config import MINIMAX_VOICES
except ImportError:
    MINIMAX_VOICES = ["Trustworthy_Advisor"]


def setup_output_dir():
    """Create output directory."""
    output_path = PROJECT_ROOT / OUTPUT_DIR
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


async def test_edge_tts(output_dir: Path):
    """Test Microsoft Edge TTS voices."""
    try:
        import edge_tts
    except ImportError:
        print("❌ edge-tts not installed. Run: pip install edge-tts")
        return
    
    print("\n🎙️ Testing Edge TTS...")
    
    for voice in EDGE_VOICES:
        filename = f"edge_tts_{voice}.mp3"
        output_path = output_dir / filename
        
        try:
            communicate = edge_tts.Communicate(TEST_TEXT.strip(), voice)
            await communicate.save(str(output_path))
            print(f"  ✅ {filename}")
        except Exception as e:
            print(f"  ❌ {voice}: {e}")


def test_gtts(output_dir: Path):
    """Test Google TTS."""
    try:
        from gtts import gTTS
    except ImportError:
        print("❌ gtts not installed. Run: pip install gtts")
        return
    
    print("\n🎙️ Testing gTTS...")
    
    for lang in GTTS_LANGS:
        filename = f"gtts_{lang}.mp3"
        output_path = output_dir / filename
        
        try:
            tts = gTTS(text=TEST_TEXT.strip(), lang=lang)
            tts.save(str(output_path))
            print(f"  ✅ {filename}")
        except Exception as e:
            print(f"  ❌ {lang}: {e}")


def test_pyttsx3(output_dir: Path):
    """Test offline system voices."""
    try:
        import pyttsx3
    except ImportError:
        print("❌ pyttsx3 not installed. Run: pip install pyttsx3")
        return
    
    print("\n🎙️ Testing pyttsx3 (system voices)...")
    
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    
    for i, voice in enumerate(voices[:3]):  # Test first 3 voices
        filename = f"pyttsx3_voice_{i}_{voice.name[:20]}.mp3"
        output_path = output_dir / filename
        
        try:
            engine.setProperty('voice', voice.id)
            engine.save_to_file(TEST_TEXT.strip(), str(output_path))
            engine.runAndWait()
            print(f"  ✅ {filename}")
        except Exception as e:
            print(f"  ❌ Voice {i}: {e}")


def test_kokoro(output_dir: Path):
    """Test Kokoro ONNX neural TTS."""
    try:
        from kokoro_onnx import Kokoro
        import soundfile as sf
    except ImportError:
        print("❌ kokoro-onnx not installed. Run: pip install kokoro-onnx soundfile")
        return
    
    print("\n🎙️ Testing Kokoro TTS...")
    
    # Model files in test-tts folder
    model_path = Path(__file__).parent / "kokoro-v1.0.onnx"
    voices_path = Path(__file__).parent / "voices-v1.0.bin"
    
    if not model_path.exists() or not voices_path.exists():
        print("  ❌ Model files not found. Download from:")
        print("     https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0")
        return
    
    try:
        kokoro = Kokoro(str(model_path), str(voices_path))
    except Exception as e:
        print(f"  ❌ Failed to load model: {e}")
        return
    
    for voice in KOKORO_VOICES:
        filename = f"kokoro_{voice}.wav"
        output_path = output_dir / filename
        
        try:
            samples, sample_rate = kokoro.create(TEST_TEXT.strip(), voice=voice)
            sf.write(str(output_path), samples, sample_rate)
            print(f"  ✅ {filename}")
        except Exception as e:
            print(f"  ❌ {voice}: {e}")


async def test_elevenlabs(output_dir: Path):
    """Test ElevenLabs (requires API key)."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("⚠️ ELEVENLABS_API_KEY not set. Skipping...")
        return
    
    try:
        from elevenlabs import generate, save
    except ImportError:
        print("❌ elevenlabs not installed. Run: pip install elevenlabs")
        return
    
    print("\n🎙️ Testing ElevenLabs...")
    
    voices = ["Bella", "Josh", "Rachel"]
    
    for voice in voices:
        filename = f"elevenlabs_{voice}.mp3"
        output_path = output_dir / filename
        
        try:
            audio = generate(text=TEST_TEXT.strip(), voice=voice, api_key=api_key)
            save(audio, str(output_path))
            print(f"  ✅ {filename}")
        except Exception as e:
            print(f"  ❌ {voice}: {e}")


def test_parler_tts(output_dir: Path):
    """Test Indic Parler-TTS with emotion prompts."""
    try:
        import torch
        from parler_tts import ParlerTTSForConditionalGeneration
        from transformers import AutoTokenizer
        import soundfile as sf
    except ImportError:
        print("❌ parler-tts not installed. Run: pip install git+https://github.com/huggingface/parler-tts.git")
        return
    
    # Check for HuggingFace token in .env
    hf_token = os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN")
    if not hf_token:
        print("⚠️ HUGGINGFACE_API_KEY not set in .env. Skipping Parler-TTS...")
        print("  Get token from: https://huggingface.co/settings/tokens")
        return
    
    print("\n🎙️ Testing Parler-TTS (Indic with emotions)...")
    print("  ⏳ Loading model (this may take a minute first time)...")
    
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = ParlerTTSForConditionalGeneration.from_pretrained(
            "ai4bharat/indic-parler-tts",
            token=hf_token
        ).to(device)
        tokenizer = AutoTokenizer.from_pretrained("ai4bharat/indic-parler-tts", token=hf_token)
        
        for description, suffix in PARLER_EMOTIONS:
            filename = f"parler_tts_{suffix}.wav"
            output_path = output_dir / filename
            
            try:
                input_ids = tokenizer(description, return_tensors="pt").input_ids.to(device)
                prompt_ids = tokenizer(TEST_TEXT.strip(), return_tensors="pt").input_ids.to(device)
                
                generation = model.generate(input_ids=input_ids, prompt_input_ids=prompt_ids)
                audio = generation.cpu().numpy().squeeze()
                
                sf.write(str(output_path), audio, model.config.sampling_rate)
                print(f"  ✅ {filename}")
            except Exception as e:
                print(f"  ❌ {suffix}: {e}")
    except Exception as e:
        print(f"  ❌ Model loading failed: {e}")


async def test_minimax(output_dir: Path):
    """Test MiniMax (Hailuo) API."""
    api_key = os.getenv("MINIMAX_API_KEY") or os.getenv("MINIMAX_GROUP_ID")
    if not api_key:
        print("⚠️ MINIMAX_API_KEY not set. Skipping...")
        print("  Get your key from: https://www.minimaxi.com/")
        return
    
    try:
        import httpx
    except ImportError:
        print("❌ httpx not installed. Run: pip install httpx")
        return
    
    print("\n🎙️ Testing MiniMax TTS...")
    
    for voice in MINIMAX_VOICES:
        filename = f"minimax_{voice}.mp3"
        output_path = output_dir / filename
        
        try:
            # MiniMax API call (simplified)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.minimax.chat/v1/text_to_speech",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "text": TEST_TEXT.strip(),
                        "voice_id": voice,
                        "model": "speech-01"
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                    print(f"  ✅ {filename}")
                else:
                    print(f"  ❌ {voice}: API error {response.status_code}")
        except Exception as e:
            print(f"  ❌ {voice}: {e}")


async def main():
    print("=" * 50)
    print("🔊 TTS Voice Comparison Tool")
    print("=" * 50)
    
    output_dir = setup_output_dir()
    print(f"📁 Output: {output_dir}")
    
    # Run enabled providers
    if PROVIDERS.get("edge_tts"):
        await test_edge_tts(output_dir)
    
    if PROVIDERS.get("gtts"):
        test_gtts(output_dir)
    
    if PROVIDERS.get("pyttsx3"):
        test_pyttsx3(output_dir)
    
    if PROVIDERS.get("kokoro"):
        test_kokoro(output_dir)
    
    if PROVIDERS.get("parler_tts"):
        test_parler_tts(output_dir)
    
    if PROVIDERS.get("minimax"):
        await test_minimax(output_dir)
    
    if PROVIDERS.get("elevenlabs"):
        await test_elevenlabs(output_dir)
    
    # Summary
    print("\n" + "=" * 50)
    files = list(output_dir.glob("*.mp3"))
    print(f"✅ Generated {len(files)} audio files in '{OUTPUT_DIR}/'")
    print("🎧 Listen and compare to find your best voice!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
