from setuptools import setup, find_packages

setup(
    name="AutoTTS",
    version="0.1.0",
    description="Multi-engine TTS wrapper with coconut protection",
    author="PDGadm",
    packages=find_packages(),
    install_requires=[
        "edge-tts", "pyttsx3", "TTS", "azure-cognitiveservices-speech", "elevenlabs"
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "easytts=easytts.cli:cli",
        ]
    },
)