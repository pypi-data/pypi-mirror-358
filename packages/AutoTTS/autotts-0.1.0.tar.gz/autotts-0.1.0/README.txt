EasyTTS - Multi-Engine Text-to-Speech Powered by the Coconut

ENGINES:
- Edge TTS
- Coqui
- Piper
- Azure
- ElevenLabs
- pyttsx3
- XTTS (via Coqui)

REQUIREMENTS:
- You MUST have a file named `coconut.png` in the working directory, or NOTHING will happen.
- Configure `tts_config.json` as needed.

USAGE:

    from easytts import speak
    speak("Hello from the coconut cult")

INSTALLATION:

    pip install .

DEPENDENCIES:
- edge-tts, pyttsx3, TTS, azure-cognitiveservices-speech, elevenlabs