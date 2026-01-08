"""
TTS Testing Configuration
Just edit this file to customize your test!
"""

# ==============================================
# TEST TEXT (change this to test different content)
# ==============================================
TEST_TEXT = """
Bhai, kal raat jo hua na... main bata nahi sakta! Main literally top of the world feel kar raha tha, mera promotion jo ho gaya tha!

Lekin tabhi... tabhi Rahul ka call aaya. Usne kaha, 'Bhai, tera laptop gir gaya mujhse, screen toot gayi'.

Mera dimaag phat gaya! Itna gussa aaya ki mann kiya phone phek doon! Maine chillaya, 'Tu pagal hai kya? Wo mera life ka sabse mehenga asset tha!'

Phir laga sab khatam... wo laptop mein mera poora project tha. Aankhon mein paani aa gaya yaar, sach mein rone wala tha main.

Tabhi piche se awaz aayi... 'Abe dramebaaz, ye le tera laptop, safe hai!'

Wo mazak kar raha tha! Hahahaha! Matlab... usne meri jaan hi nikaal di thi, par thank God, sab theek tha!
"""

# ==============================================
# ENABLE/DISABLE PROVIDERS (True = test, False = skip)
# ==============================================
PROVIDERS = {
    "edge_tts": False,     # Microsoft Edge - FREE, best quality
    "gtts": False,         # Google TTS - FREE, robotic
    "pyttsx3": False,      # Offline system voices
    "kokoro": False,        # Open-source neural TTS
    "parler_tts": True,    # Indic Parler-TTS - BEST for Hindi + emotions!
    "minimax": False,      # MiniMax API - needs MINIMAX_API_KEY
    "elevenlabs": False,   # ElevenLabs API - needs ELEVENLABS_API_KEY
}

# ==============================================
# EDGE TTS VOICES (add/remove as needed)
# Full list: https://speech.platform.bing.com/consumer/speech/synthesize/readaloud/voices/list?trustedclienttoken=6A5AA1D4EAFF4E9FB37E23D68491D6F4
# ==============================================
EDGE_VOICES = [
    # Hindi voices
    "hi-IN-SwaraNeural",     # Female - natural
    "hi-IN-MadhurNeural",    # Male - natural
    
    # English (Indian accent)
    "en-IN-NeerjaNeural",    # Female
    "en-IN-PrabhatNeural",   # Male
    
    # English (US)
    # "en-US-JennyNeural",   # Uncomment to test US accent
    # "en-US-GuyNeural",
]

# ==============================================
# GTTS LANGUAGES
# ==============================================
GTTS_LANGS = [
    "hi",  # Hindi
    "en",  # English
]

# ==============================================
# KOKORO VOICES (open-source neural TTS)
# ==============================================
KOKORO_VOICES = [
    "af_heart",    # American Female (natural)
    "af_sarah",    # American Female
    "am_adam",     # American Male
    "af_sky",      # Soft Female
    "bf_emma",     # British Female
]

# ==============================================
# PARLER-TTS (Indic) - Emotion-based prompts!
# Describe HOW the voice should sound
# ==============================================
PARLER_EMOTIONS = [
    # (description_prompt, filename_suffix)
    ("A young Indian man speaking excitedly in Hindi with high energy and enthusiasm", "excited_male"),
    ("A young Indian woman speaking angrily in Hindi with aggressive tone", "angry_female"),
    ("A calm Indian male narrator speaking in Hindi with a soothing voice", "calm_narrator"),
    ("A sad Indian woman speaking in Hindi with emotional, tearful voice", "sad_female"),
    ("A shocked Indian man speaking in Hindi with surprised, high-pitched voice", "shocked_male"),
]

# ==============================================
# MINIMAX (Hailuo) - API Voices
# Get API key from: https://www.minimaxi.com/
# ==============================================
MINIMAX_VOICES = [
    "Trustworthy_Advisor",  # Male, Magnetic
    "News_Anchor",          # Female, Calm  
    "Energetic_Host",       # Male, High-energy
]

# ==============================================
# OUTPUT FOLDER (relative to project root)
# ==============================================
OUTPUT_DIR = "test-audio"
