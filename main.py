import asyncio
import wave
import os
import re
import numpy as np
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from dotenv import load_dotenv
from piper import PiperVoice
from pydub import AudioSegment

os.environ["PATH"] += os.pathsep + "/opt/homebrew/bin"

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MELODY_PATH = "otbivka.mp3"
voice = PiperVoice.load("piper_models/ru_RU-irina-medium.onnx")

dp = Dispatcher()


VOWEL_LETTERS = "аеёиоуыэюя"
VOWEL_PHONEMES = set("aeiouyɨʌəɐɪʊɛɔɵæɑʉ")
# Безударные (редуцированные) гласные, которые под ударением
# нужно заменить на полные
REDUCED_PHONEMES = set("iɪʌəɐʊɨ")
STRESSED_PHONEME = {
    "а": "a", "о": "o", "у": "u", "ы": "ɨ", "э": "ɛ",
    "е": "e", "ё": "ɵ", "и": "i", "ю": "u", "я": "a",
}
STRESS_MARK = "ˈ"
WORD_RE = re.compile(r"[\w'-]+")


def parse_stress(text: str) -> tuple[str, dict[int, int]]:
    """Убирает ' после гласных и возвращает
    {номер слова: номер ударной гласной в слове}"""
    words = [w for w in WORD_RE.findall(text) if any(c.isalnum() for c in w)]
    stresses = {}
    for word_idx, word in enumerate(words):
        vowel_idx = -1
        for i, char in enumerate(word):
            if char.lower() in VOWEL_LETTERS:
                vowel_idx += 1
                if word[i + 1:i + 2] == "'":
                    stresses[word_idx] = vowel_idx
    clean_text = re.sub(f"([{VOWEL_LETTERS}])'", r"\1", text, flags=re.I)
    return clean_text, stresses


def restress_word(phonemes: list[str], letter: str, vowel_idx: int) -> None:
    """Переносит ударение на vowel_idx-ю гласную слова"""
    phonemes[:] = [p for p in phonemes if p not in (STRESS_MARK, "ˌ")]
    vowel_positions = [
        i for i, p in enumerate(phonemes) if p in VOWEL_PHONEMES
    ]
    pos = vowel_positions[vowel_idx]
    if phonemes[pos] in REDUCED_PHONEMES:
        phonemes[pos] = STRESSED_PHONEME[letter]
    phonemes.insert(pos, STRESS_MARK)


def text_to_phonemes(text: str) -> list[list[str]]:
    """Фонемы по предложениям с учётом пользовательских ударений"""
    clean_text, stresses = parse_stress(text)
    sentences = voice.phonemize(clean_text)
    if not stresses:
        return sentences

    # Разбиваем каждое предложение на слова, пропуская чистую пунктуацию
    sentence_words = []
    phoneme_words = []
    for sentence in sentences:
        words = [[]]
        for p in sentence:
            if p == " ":
                words.append([])
            else:
                words[-1].append(p)
        sentence_words.append(words)
        phoneme_words.extend(
            w for w in words if any(p.isalpha() for p in w)
        )

    text_words = [
        w for w in WORD_RE.findall(clean_text)
        if any(c.isalnum() for c in w)
    ]
    if len(text_words) != len(phoneme_words):
        # Например, числа espeak раскрывает в несколько слов
        print("ударения пропущены: не удалось сопоставить слова с фонемами")
        return sentences

    for word_idx, vowel_idx in stresses.items():
        letters = [c for c in text_words[word_idx].lower()
                   if c in VOWEL_LETTERS]
        word_phonemes = phoneme_words[word_idx]
        vowel_count = sum(p in VOWEL_PHONEMES for p in word_phonemes)
        if vowel_count != len(letters):
            print(f"ударение пропущено: {text_words[word_idx]}")
            continue
        restress_word(word_phonemes, letters[vowel_idx], vowel_idx)

    return [
        [p for i, w in enumerate(words) for p in ([" "] if i else []) + w]
        for words in sentence_words
    ]


def text_to_speech(text: str, filename: str) -> None:
    with wave.open(filename, "wb") as wav_file:
        wav_file.setframerate(voice.config.sample_rate)
        wav_file.setsampwidth(2)
        wav_file.setnchannels(1)
        for phonemes in text_to_phonemes(text):
            ids = voice.phonemes_to_ids(phonemes)
            audio = voice.phoneme_ids_to_audio(ids)
            peak = np.max(np.abs(audio))
            if peak > 1e-8:
                audio = audio / peak
            audio = np.clip(audio * 32767, -32767, 32767).astype(np.int16)
            wav_file.writeframes(audio.tobytes())


def mix_audio(voice_path: str, output_path: str) -> None:
    """Наложение озвучки на мелодию"""
    voice_segment = AudioSegment.from_file(voice_path)
    melody = AudioSegment.from_file(MELODY_PATH)
    combined = voice_segment + melody
    combined.export(output_path, format="mp3")


@dp.message(Command("start"))
async def start(message: types.Message) -> None:
    await message.answer(
        "Хеллоу май френд, пишешь текст, делаем частушечку, "
        "если нужно кастомное ударение - пишешь ' после ударной гласной"
    )


@dp.message()
async def handle_text(message: types.Message) -> None:
    text = message.text.strip()
    await message.answer("Ильинишна разогревается сэмом, обожжи...")

    tts_path = "tts.wav"
    output_path = "final.mp3"
    text_to_speech(text, tts_path)
    mix_audio(tts_path, output_path)
    audio = FSInputFile(output_path)
    await message.answer_audio(audio, title="Рви меха")


if __name__ == "__main__":
    print("running bot...")
    bot = Bot(token=BOT_TOKEN)
    asyncio.run(dp.start_polling(bot))
    # tts_path = "tts.wav"
    # text_to_speech('мол+око', tts_path)
