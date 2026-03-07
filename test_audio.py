import sys
from main import text_to_speech, mix_audio, MELODY_PATH

if __name__ == "__main__":
    text = input("Введите текст")
    tts_path = "test_tts.wav"
    output_path = "test_final.mp3"
    text_to_speech(text, tts_path)
    mix_audio(tts_path, output_path)
    print(output_path)
