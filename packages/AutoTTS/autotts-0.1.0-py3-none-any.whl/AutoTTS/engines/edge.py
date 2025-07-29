import asyncio
import edge_tts

async def _speak_async(text, voice, rate):
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
    await communicate.stream()

def speak(text, config):
    voice = config.get("voice", "en-US-AriaNeural")
    speed = config.get("speed", "100%")
    asyncio.run(_speak_async(text, voice, speed))