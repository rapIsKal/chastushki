import asyncio
import wave
import os
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

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def text_to_speech(text: str, filename: str) -> None:
    with wave.open(filename, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)


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
    text = message.text.strip().replace("'", "<[stress]>")
    await message.answer("Ильинишна разогревается сэмом, обожжи...")

    tts_path = "tts.wav"
    output_path = "final.mp3"
    text_to_speech(text, tts_path)
    mix_audio(tts_path, output_path)
    audio = FSInputFile(output_path)
    await message.answer_audio(audio, title="Рви меха")


if __name__ == "__main__":
    print("running bot...")
    asyncio.run(dp.start_polling(bot))
    # tts_path = "tts.wav"
    # text_to_speech('мол+око', tts_path)
