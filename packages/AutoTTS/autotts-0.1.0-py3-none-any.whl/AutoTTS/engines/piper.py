import os

def speak(text, cfg):
    voice = cfg.get("voice", "en_US-amy-low")
    speed = cfg.get("speed", "1.0")
    volume = cfg.get("volume", "1.0")
    os.system(f'echo "{text}" | piper --voice {voice} --rate {speed} --volume {volume}')