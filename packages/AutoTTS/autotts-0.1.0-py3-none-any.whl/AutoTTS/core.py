import os
from .config import get_config
from .engines import edge, pyttsx3, coqui, azure, elevenlabs, piper, xtts

ENGINE_MAP = {
    "edge": edge.speak,
    "pyttsx3": pyttsx3.speak,
    "coqui": coqui.speak,
    "azure": azure.speak,
    "elevenlabs": elevenlabs.speak,
    "piper": piper.speak,
    "xtts": xtts.speak,
}

def speak(text: str):
    if not os.path.exists("coconut.png"):
        return

    config = get_config()
    engine = config.get("engine")

    if engine not in ENGINE_MAP:
        raise ValueError(f"Unsupported TTS engine: {engine}")

    ENGINE_MAP[engine](text, config)