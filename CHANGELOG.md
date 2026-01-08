# Changelog - Mission Alpha

**All fixes and changes tracked here** | Updated after every modification

---

## 2025-12-26 - Session 1: Viral Video Enhancements

### ✅ Pexels Background Integration - COMPLETE

**Status:** Working but slow

**Changes:**
- Fixed all MoviePy 2.x API incompatibilities
- Pexels videos now successfully download, loop, resize, and crop
- Real background videos working in production

**Performance:**
- Total pipeline: 530s (8m 50s) for 83s video
- Video export: 506s (8m 26s) - **BOTTLENECK**
- Processing speed: ~6 frames/second (2499 frames @ 30fps)

**Known Issues:**
- Export is CPU-intensive and slow
- File size: 77.74 MB for 83s video (high)
- Minor: FFMPEG cleanup warning on Windows (harmless)

**Next Steps:**
- Pre-process Pexels videos (cache resized versions)
- Consider GPU encoding (NVENC)
- Or lower resolution/fps for faster testing

**Files Modified:**
- `backend/app/plugins/video/moviepy_plugin.py`

---

### MoviePy 1.0.3 → 2.2.1 Migration
**Reason:** Pillow 11.3.0 incompatibility (removed `ANTIALIAS` constant)

**Changes:**
- Upgraded MoviePy from 1.0.3 to 2.2.1
- Updated all API calls to MoviePy 2.x syntax:
  - `set_duration()` → `with_duration()`
  - `set_position()` → `with_position()`
  - `set_start()` → `with_start()`
  - `set_audio()` → `with_audio()`
  - `resize()` → `resized()`
  - `subclip()` → `subclipped()`
  - `clip.loop(n=x)` → `concatenate_videoclips([clip] * x)`
  - `fontsize=` → `font_size=`
  - Removed `verbose=False` parameter from `write_videofile()`

**Files Modified:**
- `backend/app/plugins/video/moviepy_plugin.py`

---

### AI Provider Updates

#### Groq Model Update
**Issue:** `llama-3.1-70b-versatile` decommissioned by Groq

**Fix:**
- Updated to `llama-3.3-70b-versatile` (current model as of Dec 2024)
- Removed invalid `model` parameter from `ScriptResult` return
- Now returns `metadata={"model": self.model}` instead

**Files Modified:**
- `backend/app/plugins/ai/groq_plugin.py`

#### HuggingFace Removal
**Issue:** No working free models for text-generation task

**Fix:**
- Removed HuggingFace from fallback chain
- Simplified to: Groq → Gemini → OpenAI

**Files Modified:**
- `config.yaml`

---

### Pexels Background Integration

#### Created Pexels Provider
**New File:** `backend/app/plugins/video/pexels_backgrounds.py`

**Features:**
- Fetches HD portrait videos from Pexels API
- Caches downloads in `cache/backgrounds/`
- Random category selection (nature, cooking, abstract, etc.)
- Accepts videos 5+ seconds, loops to match audio duration

**Status:** ⚠️ Partially working (downloads videos but MoviePy integration has issues)

#### Integration Attempts
**File:** `backend/app/plugins/video/moviepy_plugin.py`

**Changes:**
- Added Pexels video fetching in `assemble_video()`
- Implemented video looping via `concatenate_videoclips()`
- Added resize and crop logic for 1080x1920 portrait
- Falls back to gradient backgrounds on error

**Current Issues:**
- TextClip font parameter conflicts
- Some MoviePy 2.x API incompatibilities remain
- Successfully downloads videos but fails during processing

---

### TTS Provider Enhancement

#### Edge TTS Integration
**New File:** `backend/app/plugins/tts/edge_tts_plugin.py`

**Features:**
- Microsoft Edge TTS (FREE, unlimited)
- Natural Hindi voice: `hi-IN-MadhurNeural` (male)
- Much better quality than gTTS
- Async audio generation

**Configuration:**
```yaml
tts:
  provider: edge_tts
  language: hi-male  # hi, hi-male, en, en-male
```

**Files Modified:**
- `backend/app/core/plugin_loader.py` (added to registry)
- `config.yaml` (switched from gtts to edge_tts)

---

### Configuration Updates

#### AI Fallback Chain
**File:** `config.yaml`

**Changes:**
- Primary: `groq` (llama-3.3-70b-versatile)
- Fallback 1: `langchain` (Gemini gemini-2.5-flash)
- Fallback 2: `openai_direct` (requires API key)

#### Environment Variables
**File:** `.env.example`

**Added:**
- `GROQ_API_KEY` - Groq AI provider
- `HUGGINGFACE_API_KEY` - HuggingFace (deprecated)
- Updated comments with API key URLs

---

### Database Schema Fix

#### SQLite Videos Table
**File:** `backend/app/plugins/database/sqlite_plugin.py`

**Issue:** Column mismatch between test script and schema

**Fix:**
- Updated `videos` table schema to match test script columns:
  - `content_title`
  - `script_hook`
  - `audio_path`
  - `video_path`
  - `duration`
  - `resolution`

---

### Dependencies Installed

```bash
pip install groq                    # Groq AI provider
pip install huggingface_hub         # HuggingFace (later removed)
pip install edge-tts mutagen        # Edge TTS + audio metadata
pip install openai                  # OpenAI fallback
pip uninstall moviepy -y            # Removed old version
pip install moviepy --upgrade       # Installed 2.2.1
```

---

### Debug Enhancements

#### Added Debug Logging
**File:** `backend/app/plugins/video/moviepy_plugin.py`

**Added `[DEBUG]` print statements:**
- Pexels provider initialization
- API key status check
- Video fetch results
- Video loading and processing steps
- Error details for troubleshooting

**Purpose:** Track Pexels integration issues without verbose MoviePy output

---

## Summary Statistics

**Files Created:** 3
- `backend/app/plugins/video/pexels_backgrounds.py`
- `backend/app/plugins/tts/edge_tts_plugin.py`
- `backend/app/plugins/ai/groq_plugin.py` (already existed, updated)

**Files Modified:** 6
- `backend/app/plugins/video/moviepy_plugin.py`
- `backend/app/plugins/ai/groq_plugin.py`
- `backend/app/core/plugin_loader.py`
- `backend/app/plugins/database/sqlite_plugin.py`
- `config.yaml`
- `.env.example`

**Dependencies Changed:** 5
- MoviePy: 1.0.3 → 2.2.1
- Added: groq, edge-tts, mutagen, openai
- Removed: (none, but HuggingFace deprecated)

**API Calls Updated:** 11 MoviePy method changes

---

**Next Session:** Continue here with new fixes
