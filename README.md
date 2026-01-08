# Mission Alpha - Viral Shorts Factory 🎬

Automated YouTube Shorts content factory generating 20+ videos/day across multiple niches using AI.

## 🎯 Vision

**Multi-channel automated content factory** running 24/7, producing high-quality shorts for:
- Reddit Confessions
- News & Trends
- Motivational Content
- Stories & Narratives
- Custom niches

**Scale:** 5 channels × 4 videos/day = 20 videos/day

---

## 🚀 Features

- ✅ **Modular Plugin Architecture** - swap AI, TTS, video providers without code changes
- ✅ **Multiple TTS Providers** - Edge TTS, Kokoro, Parler-TTS, voice cloning support
- ✅ **AI Script Generation** - Groq, Gemini, OpenAI with fallback chain
- ✅ **Video Assembly** - MoviePy with Pexels backgrounds
- ✅ **Config-driven** - YAML configuration for everything
- 🔄 Multi-niche support (in progress)
- 🔄 YouTube auto-upload (planned)
- 🔄 Full automation with scheduling (planned)

---

## 📁 Project Structure

```
mission-alpha-viral-shorts/
├── backend/
│   └── app/
│       ├── core/           # Core engine
│       ├── plugins/        # Provider plugins (TTS, AI, Video)
│       └── routers/        # API routes
├── test-tts/              # TTS testing tool
│   ├── config.py          # TTS test configuration
│   └── run.py             # Run TTS comparisons
├── config.yaml            # Main app configuration
├── ROADMAP.md            # Development roadmap
└── .env.example          # Environment variables template

```

---

## 🛠️ Setup

### Local Development

1. **Clone the repo**
```bash
git clone https://github.com/yourusername/mission-alpha-viral-shorts.git
cd mission-alpha-viral-shorts
```

2. **Create virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

5. **Run TTS tests**
```bash
python test-tts/run.py
```

---

## 🔧 Google Colab Setup

Perfect for GPU-intensive tasks (Parler-TTS, voice cloning, video rendering).

1. **Open in Colab**
   - Go to https://colab.research.google.com
   - File → New Notebook

2. **Clone repo**
```python
!git clone https://github.com/yourusername/mission-alpha-viral-shorts.git
%cd mission-alpha-viral-shorts
```

3. **Install dependencies**
```python
!pip install -r requirements.txt
!pip install git+https://github.com/ai4bharat/IndicF5.git  # For voice cloning
```

4. **Set secrets** (use Colab's 🔑 Secrets sidebar)
   - Add `HUGGINGFACE_API_KEY`
   - Add `GEMINI_API_KEY`
   - Add other API keys as needed

5. **Run tests**
```python
!python test-tts/run.py
```

---

## 🎙️ TTS Providers

| Provider | Cost | Quality | Notes |
|----------|------|---------|-------|
| **Edge TTS** | Free | ⭐⭐⭐⭐⭐ | Best free Hindi voices |
| **Kokoro** | Free | ⭐⭐⭐⭐⭐ | Neural English TTS |
| **Parler-TTS** | Free | ⭐⭐⭐⭐⭐ | Emotion-based Hindi |
| **IndicF5** | Free | ⭐⭐⭐⭐⭐ | Voice cloning from 10s sample |
| **gTTS** | Free | ⭐⭐⭐ | Basic Google TTS |
| **ElevenLabs** | Freemium | ⭐⭐⭐⭐⭐ | Premium quality |

---

## 🔑 Environment Variables

Required variables (see `.env.example`):

```bash
# AI Providers
GEMINI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here

# TTS (optional)
HUGGINGFACE_API_KEY=your_hf_token
ELEVENLABS_API_KEY=your_key_here

# Video backgrounds
PEXELS_API_KEY=your_key_here
```

---

## 📝 Configuration

Edit `config.yaml` to customize:
- TTS provider and voice
- AI model and prompts
- Video settings
- Content sources

---

## 🗺️ Roadmap

See [ROADMAP.md](ROADMAP.md) for detailed development plan.

**Current status:** Phase 2 (80% complete)
- ✅ Core architecture
- ✅ TTS providers
- ✅ AI integration
- ⏸️ Performance optimization needed
- ⏸️ Multi-niche support in progress

---

## 📊 Cost Breakdown

**Monthly cost for 600 videos (20/day):**
- **Free tier:** $0 (Edge TTS + Groq + Pexels)
- **With premium TTS:** ~$7/mo (OpenAI TTS)
- **Full premium:** ~$22/mo (ElevenLabs)

**Recommended:** Start with free tier!

---

## 🤝 Contributing

This is a personal project, but feel free to fork and adapt for your needs!

---

## 📄 License

MIT License - see LICENSE file

---

## 🙏 Credits

- AI4Bharat for Indic TTS models
- Microsoft Edge TTS
- Groq for fast AI inference
- Pexels for free video backgrounds
