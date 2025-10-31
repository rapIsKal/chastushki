import wave

if __name__ == "__main__":
    import numpy as np
    import soundfile as sf
    from piper.voice import PiperVoice

    voice = PiperVoice.load("piper_models/ru_RU-irina-medium.onnx")
    # OR another voice
    voice2 = PiperVoice.load("piper_models/ru_RU-ruslan-medium.onnx")


    # Voice parameters
    with wave.open("test2.wav", "wb") as wav_file:
        audio_gen = voice2.synthesize_wav(text, wav_file)
    print("✅ Saved out.wav")

