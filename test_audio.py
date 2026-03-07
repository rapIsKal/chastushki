import sys
import re
from main import text_to_speech, mix_audio, MELODY_PATH

if __name__ == "__main__":
    with open("test.txt", "r") as f:
        text = f.read().strip()
    # Replace vowel + ' with stress tags around vowel (same as main.py)
    text = re.sub(r'([аеиоуыэюя])\'', r'<[stress]>\1</[stress]>', text)
    tts_path = "test_tts.wav"
    output_path = "test_final.mp3"
    text_to_speech(text, tts_path)
    mix_audio(tts_path, output_path)
    print(output_path)
