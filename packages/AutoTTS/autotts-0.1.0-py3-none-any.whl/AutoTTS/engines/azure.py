import azure.cognitiveservices.speech as speechsdk

def speak(text, cfg):
    key = cfg["api_key"]
    region = cfg["region"]
    speech = speechsdk.SpeechConfig(subscription=key, region=region)
    speech.speech_synthesis_voice_name = cfg.get("voice")
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech)
    synthesizer.speak_text_async(text).get()