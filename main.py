import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, BufferedInputFile
from yt_dlp import YoutubeDL

# Бул жерге өзүңдүн токениңди жаз
API_TOKEN = '8576931278:AAECIYTCR9k81pnLy7A8R-xFjeYfgU3KEqo'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# YouTube издөө жөндөөлөрү
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'default_search': 'ytsearch',
    'quiet': True,
}

@dp.message(F.text == "/start")
async def start_cmd(message: Message):
    await message.answer("Салам, Арген! Кандай музыка издейбиз? Мага ырдын атын жөнөт.")

@dp.message()
async def search_and_send(message: Message):
    query = message.text
    waiting_msg = await message.answer(f"🔍 '{query}' издеп жатам...")

    try:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            url = info['url']
            title = info.get('title', 'music')
            
            # Файлды жүктөп алуунун ордуна, түздөн-түз жөнөтүүгө аракет кылабыз
            await message.answer_audio(
                audio=url,
                caption=f"🎵 {title}\n\n@сенин_ботуңдун_аты",
                title=title
            )
            await waiting_msg.delete()
            
    except Exception as e:
        await waiting_msg.edit_text("Кечирип кой, ырды таба алган жокмун же ката кетти.")
        print(f"Ката: {e}")

async def main():
    print("Бот ишке кирди...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
