import os, torch
from TTS.api import TTS

def speak(text, cfg):
    model = cfg.get("voice", "tts_models/multilingual/multi-dataset/xtts_v2")
    tts = TTS(model).to("cuda" if torch.cuda.is_available() else "cpu")
    out = cfg.get("output_path", "temp.wav")
    speaker_wav = cfg.get("speaker_wav", None)
    language = cfg.get("language", "en")
    tts.tts_to_file(text=text, speaker_wav=speaker_wav, language=language, file_path=out)
    os.system(f"play {out}")