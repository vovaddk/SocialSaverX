import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
import yt_dlp
import asyncio

API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
DOWNLOADS_DIR = 'downloads'
MAX_FILESIZE = 49 * 1024 * 1024

logging.basicConfig(level=logging.INFO)
if not os.path.exists(DOWNLOADS_DIR):
    os.makedirs(DOWNLOADS_DIR)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привіт! Надішли мені посилання з TikTok, YouTube, Instagram, Twitter/X, Facebook, Reddit або іншої популярної соцмережі — а я скачаю для тебе відео або інший медіа-файл без водяних знаків.\n\n"
        "❗️ Максимальний розмір файлу — 49 МБ (обмеження Telegram).\n"
        "⚡️ Просто кидай посилання у чат!"
    )

@dp.message(lambda message: message.text and message.text.startswith('http'))
async def process_url(message: Message):
    url = message.text.strip()
    msg = await message.answer("🔎 Обробляю посилання, зачекай…")
    try:
        ydl_opts = {
            'outtmpl': f'{DOWNLOADS_DIR}/%(title).80s_%(id)s.%(ext)s',
            'format': 'best[filesize<50M]/best',
            'noplaylist': True,
            'quiet': True,
            'merge_output_format': 'mp4',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if os.path.getsize(filename) > MAX_FILESIZE:
            await msg.edit_text("❌ Відео занадто велике для Telegram (макс 49 МБ). Спробуй коротший ролик або інший лінк.")
            os.remove(filename)
            return

        file = FSInputFile(filename)
        await message.answer_document(file, caption="✅ Ось твоє відео!")
        await msg.delete()
        os.remove(filename)
    except Exception as e:
        await msg.edit_text(f"❗️ Помилка: {e}\nМожливо, цей тип контенту не підтримується або недоступний.")
        logging.error(e)

@dp.message()
async def fallback(message: Message):
    await message.answer("🤔 Надішли мені посилання на відео чи пост із соцмережі, наприклад TikTok, YouTube, Instagram або Twitter/X.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
