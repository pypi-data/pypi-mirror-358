from elevenlabs import ElevenLabs, play

def speak(text, cfg):
    client = ElevenLabs(api_key=cfg["api_key"])
    audio = client.generate(text=text, voice=cfg.get("voice"), model=cfg.get("model", "eleven_multilingual_v2"))
    play(audio)