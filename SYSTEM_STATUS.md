# Mission Alpha - System Status & Architecture
**Single Source of Truth** | Last Updated: 2025-12-26

---

## 🎯 Current System State

**Status:** ✅ **FULLY OPERATIONAL** (with performance caveat)
- Full pipeline working: Content → AI → TTS → Video → Database
- **Pexels backgrounds:** ✅ Working (but slow - 8m50s for 83s video)
- Latest test: 83.3s video @ 1080x1920, 77.74 MB
- All 5 providers loaded successfully

---

## 📊 Tech Stack (Current)

### Core Framework
- **Python:** 3.13
- **Architecture:** Plugin-based, zero-coupling
- **Config:** YAML-driven provider swapping

### Active Providers (Production)

| Category | Provider | Model/Version | Status |
|----------|----------|---------------|--------|
| **Content** | `quotes` | Quotable.io + fallback | ✅ Working |
| **AI** | `groq` | llama-3.3-70b-versatile | ✅ Working |
| **TTS** | `edge_tts` | hi-IN-MadhurNeural | ✅ Working |
| **Video** | `moviepy` | 2.2.1 | ✅ Working |
| **Database** | `sqlite` | Local DB | ✅ Working |

### AI Fallback Chain
```
Primary: Groq (llama-3.3-70b-versatile)
  ↓ fails
Fallback 1: Gemini (gemini-2.5-flash)
  ↓ fails  
Fallback 2: OpenAI (requires API key)
```

### Dependencies (Key Versions)
```
moviepy==2.2.1          # Video assembly (upgraded from 1.0.3)
Pillow==11.3.0          # Image processing
edge-tts==7.2.7         # Natural TTS
groq==0.13.0            # AI provider
google-genai==0.8.3     # Gemini fallback
httpx==0.28.1           # Async HTTP
pydantic==2.10.5        # Config validation
```

---

## 🔌 System Wiring Flow

### 1. Entry Point
```
test_full_pipeline.py
  ↓
main() async function
```

### 2. Provider Loading
```python
# Each provider loaded via PluginLoader
PluginLoader.load('content')  → QuotesProvider
PluginLoader.load('ai')       → AIProviderWithFallback(GroqProvider)
PluginLoader.load('tts')      → EdgeTTSProvider
PluginLoader.load('video')    → MoviePyProvider
PluginLoader.load('database') → SQLiteProvider
```

### 3. Data Flow
```
┌─────────────┐
│   Content   │ quotes.py → ContentItem
└──────┬──────┘
       ↓
┌─────────────┐
│     AI      │ groq_plugin.py → ScriptResult
└──────┬──────┘         (with fallback chain)
       ↓
┌─────────────┐
│     TTS     │ edge_tts_plugin.py → MediaFile (audio)
└──────┬──────┘
       ↓
┌─────────────┐
│    Video    │ moviepy_plugin.py → MediaFile (video)
└──────┬──────┘         ├─ Pexels backgrounds (optional)
       ↓                └─ Gradient fallback
┌─────────────┐
│  Database   │ sqlite_plugin.py → Saved record
└─────────────┘
```

### 4. Plugin Registry
```python
# backend/app/core/plugin_loader.py
PLUGIN_REGISTRY = {
    "content": {
        "quotes": "app.plugins.content.quotes_plugin.QuotesProvider",
        "reddit": "app.plugins.content.reddit_plugin.RedditProvider",
        "facts": "app.plugins.content.facts_plugin.FactsProvider"
    },
    "ai": {
        "langchain": "app.plugins.ai.langchain_plugin.LangChainProvider",
        "groq": "app.plugins.ai.groq_plugin.GroqProvider",
        "openai_direct": "app.plugins.ai.openai_plugin.OpenAIProvider",
        "crewai": "app.plugins.ai.crewai_plugin.CrewAIProvider"
    },
    "tts": {
        "gtts": "app.plugins.tts.gtts_plugin.GTTSProvider",
        "elevenlabs": "app.plugins.tts.elevenlabs_plugin.ElevenLabsProvider",
        "edge_tts": "app.plugins.tts.edge_tts_plugin.EdgeTTSProvider"
    },
    "video": {
        "moviepy": "app.plugins.video.moviepy_plugin.MoviePyProvider"
    },
    "upload": {
        "youtube": "app.plugins.upload.youtube_plugin.YouTubeProvider",
        "none": "app.plugins.upload.none_plugin.NoneProvider"
    },
    "database": {
        "sqlite": "app.plugins.database.sqlite_plugin.SQLiteProvider",
        "supabase": "app.plugins.database.supabase_plugin.SupabaseProvider"
    }
}
```

---

## 🎬 Video Assembly Details

### Pexels Integration (Attempted)
**Status:** ⚠️ Downloads videos but MoviePy 2.x API issues remain

**Flow:**
```python
MoviePyProvider.assemble_video()
  ↓
pexels_backgrounds.get_pexels_provider()
  ↓
fetch_video(query="nature", duration_min=5)
  ↓
Download to: cache/backgrounds/pexels_XXXXX.mp4
  ↓
Load with VideoFileClip
  ↓
Loop via concatenate_videoclips
  ↓
Resize & crop to 1080x1920
  ↓
CURRENT ISSUE: API incompatibilities
```

**Known Issues:**
- TextClip font parameter conflicts
- Some MoviePy 2.x methods still incompatible
- Falls back to gradient backgrounds

**Fallback:** Gradient backgrounds (working)

---

## 📁 Project Structure

```
mission-alpha-viral-shorts/
├── config.yaml                    # Provider configuration
├── .env                          # API keys (gitignored)
├── test_full_pipeline.py         # Main test script
│
├── backend/app/
│   ├── core/
│   │   ├── interfaces.py         # Provider interfaces
│   │   ├── plugin_loader.py      # Dynamic plugin loading
│   │   ├── ai_fallback.py        # AI fallback wrapper
│   │   ├── config.py             # Pydantic config models
│   │   └── logger.py             # Rich logging
│   │
│   └── plugins/
│       ├── content/              # 3 providers
│       ├── ai/                   # 4 providers (+ fallback)
│       ├── tts/                  # 3 providers
│       ├── video/                # 1 provider + pexels helper
│       ├── upload/               # 2 providers
│       └── database/             # 2 providers
│
├── output/
│   ├── audio/                    # Generated TTS files
│   └── videos/                   # Final videos
│
├── cache/
│   └── backgrounds/              # Pexels video cache
│
└── data/
    └── factory.db                # SQLite database
```

---

## 🔑 Required API Keys

### Currently Active
```bash
GROQ_API_KEY=xxx                  # Primary AI (FREE)
GEMINI_API_KEY=xxx                # AI fallback (FREE)
PEXELS_API_KEY=xxx                # Video backgrounds (FREE)
```

### Optional
```bash
OPENAI_API_KEY=xxx                # AI fallback (PAID)
UNSPLASH_ACCESS_KEY=xxx           # Alternative backgrounds
ELEVENLABS_API_KEY=xxx            # Premium TTS
```

---

## 📈 Performance Metrics (Latest Test)

```
Total Time: 530.0s (8m 50s)

Breakdown:
- Content fetch:    ~3s
- AI generation:    ~3s  (Groq - super fast!)
- TTS synthesis:    ~12s (Edge TTS)
- Video assembly:   ~506s (8m 26s) ⚠️ BOTTLENECK
- Database save:    <1s

Output:
- Video: 83.3s @ 1080x1920
- Size: 77.74 MB
- Format: MP4 (H.264 + AAC)
- Background: Real Pexels video (ocean, 14s looped 7x)
- Processing: ~6 frames/second (2499 frames)
```

**Performance Issues:**
- Video export is CPU-intensive
- MoviePy processing Pexels videos in real-time (slow)
- Need optimization: pre-processing, GPU encoding, or lower resolution

---

## 🚀 Next Steps (Prioritized)

### High Priority
1. **Fix Pexels Integration**
   - Resolve remaining MoviePy 2.x API issues
   - Test with real background videos
   
2. **Improve Voice Quality**
   - Consider ElevenLabs integration
   - Test different Edge TTS voices

### Medium Priority
3. **YouTube Upload**
   - Implement OAuth flow
   - Auto-publish to Shorts

4. **Caption Enhancement**
   - Word-by-word highlighting
   - Better styling

### Low Priority
5. **Reddit Content**
   - Resolve API policy issues
   - Alternative: use Reddit scraping

---

## 🔧 Configuration Reference

### Swap Providers (Zero Code Changes)
```yaml
# config.yaml
ai:
  provider: groq              # Change to: langchain, openai_direct
  
tts:
  provider: edge_tts          # Change to: gtts, elevenlabs
  language: hi-male           # hi, hi-male, en, en-male
  
video:
  provider: moviepy
  resolution: 1080x1920       # Portrait for Shorts
  fps: 30
```

---

## 📝 Notes

- **No monkey patches:** Clean MoviePy 2.x upgrade
- **Fallback chain:** Ensures high availability
- **Plugin architecture:** Add providers without touching core
- **Config-driven:** Change entire stack via YAML

---

**Last Successful Run:** 2025-12-26 20:12:31
**Video Output:** `output/videos/short_1766759975_faa06d73.mp4`
