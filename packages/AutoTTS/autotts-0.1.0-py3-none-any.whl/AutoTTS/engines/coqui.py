import os, torch
from TTS.api import TTS

def speak(text, cfg):
    model = cfg.get("voice")
    tts = TTS(model).to("cuda" if torch.cuda.is_available() else "cpu")
    out = cfg.get("output_path", "temp.wav")
    tts.tts_to_file(text=text, speaker=cfg.get("speaker"), language=cfg.get("language"), file_path=out)
    os.system(f"play {out}")