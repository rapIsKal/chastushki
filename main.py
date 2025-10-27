import asyncio
import os
import subprocess

from TTS.api import TTS

os.environ["PATH"] += os.pathsep + "/opt/homebrew/bin"
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from pydub import AudioSegment


BOT_TOKEN = "ВАШ_ТОКЕН_ОТ_BOTFATHER"
MELODY_PATH = "otbivka.mp3"

tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False)
#print(tts.speakers)

#bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# === Функции ===


def text_to_speech(text: str, filename: str, language: str = 'ru'):
    tts.tts_to_file(text=text, file_path=filename, language=language, speaker_id='Claribel Dervla')


def mix_audio(voice_path: str, output_path: str):
    """Наложение озвучки на мелодию"""
    voice = AudioSegment.from_file(voice_path)
    melody = AudioSegment.from_file(MELODY_PATH)
    combined = voice + melody
    combined.export(output_path, format="mp3")

# === Хендлеры ===

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Отправь мне текст — я спою его как частушку 🎤🎶")

@dp.message()
async def handle_text(message: types.Message):
    text = message.text.strip()
    await message.answer("🎙 Озвучиваю твой текст, подожди немного...")

    tts_path = "tts.wav"
    output_path = "final.mp3"

    # 1️⃣ Озвучиваем текст
    text_to_speech(text, tts_path)

    # 2️⃣ Склеиваем с мелодией
    mix_audio(tts_path, output_path)

    # 3️⃣ Отправляем результат
    with open(output_path, "rb") as audio:
        await message.answer_audio(audio, title="Твоя частушка 🎶")

if __name__ == "__main__":
    # asyncio.run(dp.start_polling(bot))
    tts_path = "tts.wav"
    output_path = "final.mp3"
    text = 'сидит Гитлер на берёзе, а берёза гнётся, посмотри, товарищ Сталин, как он наебнётся, '
    text_to_speech(text, tts_path)
    mix_audio(tts_path, output_path)

