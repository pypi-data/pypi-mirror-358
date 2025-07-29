import json

def get_config():
    with open("tts_config.json", "r") as f:
        config = json.load(f)
    return config