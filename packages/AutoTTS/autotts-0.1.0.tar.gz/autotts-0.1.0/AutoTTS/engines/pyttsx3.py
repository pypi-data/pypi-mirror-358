import pyttsx3

def speak(text, config):
    engine = pyttsx3.init()
    voice = config.get("voice")
    if voice:
        for v in engine.getProperty('voices'):
            if voice.lower() in v.name.lower():
                engine.setProperty('voice', v.id)
                break
    rate = engine.getProperty('rate')
    engine.setProperty('rate', int(rate * int(config.get("speed", "100%").strip('%')) / 100))
    volume = engine.getProperty('volume')
    engine.setProperty('volume', min(1.0, float(config.get("volume", "100%").strip('%')) / 100))
    engine.say(text)
    engine.runAndWait()