import wave
from piper.voice import PiperVoice

if __name__ == "__main__":
    # Choose a voice
    # voice = PiperVoice.load("piper_models/ru_RU-irina-medium.onnx")
    voice2 = PiperVoice.load("piper_models/ru_RU-ruslan-medium.onnx")

    text = "Привет, мир!"
    with wave.open("test2.wav", "wb") as wav_file:
        voice2.synthesize_wav(text, wav_file)
    print("✅ Saved test2.wav")
