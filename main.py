import asyncio
import os
import wave
import soundfile as sf

from aiogram.types import FSInputFile
from piper import PiperVoice

os.environ["PATH"] += os.pathsep + "/opt/homebrew/bin"
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MELODY_PATH = "otbivka.mp3"
voice = PiperVoice.load("piper_models/ru_RU-irina-medium.onnx")

import torch

device = torch.device('cpu')


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def text_to_speech(text: str, filename: str):
    with wave.open(filename, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)


def mix_audio(voice_path: str, output_path: str):
    """Наложение озвучки на мелодию"""
    voice = AudioSegment.from_file(voice_path)
    melody = AudioSegment.from_file(MELODY_PATH)
    combined = voice + melody
    combined.export(output_path, format="mp3")


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Хеллоу май френд, пишешь текст, делаем частушечку, "
                         "если нужно кастомное ударение - пишешь ' после ударной гласной")


@dp.message()
async def handle_text(message: types.Message):
    text = message.text.strip()
    await message.answer("Ильинишна разогревается сэмом, обожжи...")

    tts_path = "tts.wav"
    output_path = "final.mp3"
    text_to_speech(text, tts_path)
    mix_audio(tts_path, output_path)
    audio = FSInputFile(output_path)
    await message.answer_audio(audio, title="Рви меха")

if __name__ == "__main__":
    print('running bot...')
    asyncio.run(dp.start_polling(bot))
    # tts_path = "tts.wav"
    # text_to_speech('мол+око', tts_path)


