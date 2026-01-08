#!/bin/bash
# Git setup and push script for Mission Alpha

echo "🚀 Initializing Git repository..."
git init

echo "📝 Adding files..."
git add .

echo "💾 Creating first commit..."
git commit -m "Initial commit: Mission Alpha Viral Shorts Factory

- Modular plugin architecture for TTS, AI, Video providers
- TTS testing framework with Edge TTS, Kokoro, Parler-TTS
- Config-driven system with YAML configuration
- Ready for multi-channel automation
- Prepared for Google Colab GPU integration"

echo "
🎯 Next steps:

1. Create GitHub repository:
   - Go to https://github.com/new
   - Repository name: mission-alpha-viral-shorts
   - Make it PRIVATE (has API keys in history)
   - Don't initialize with README (we have one)

2. Run these commands:
   git remote add origin https://github.com/YOUR_USERNAME/mission-alpha-viral-shorts.git
   git branch -M main
   git push -u origin main

3. Done! 🎉
"
