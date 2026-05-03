import os
import sys

# Керектүү китепканаларды автоматтык түрдө орнотуу
def install_packages():
    try:
        import aiogram
        import sclib
    except ImportError:
        print("Китепканалар орнотулууда...")
        os.system(f"{sys.executable} -m pip install aiogram sclib")

install_packages()

import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, URLInputFile
from sclib import SoundcloudAPI

# ТОКЕНди ушул жерге жаз
API_TOKEN = '8576931278:AAECIYTCR9k81pnLy7A8R-xFjeYfgU3KEqo'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
api = SoundcloudAPI()

@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer("Салам! SoundCloud бот даяр. Музыканын атын жаз.")

@dp.message()
async def search_and_send(message: Message):
    query = message.text
    msg = await message.answer(f"🔍 '{query}' издеп жатам...")

    try:
        # SoundCloud'дон издөө
        tracks = api.search_tracks(query)
        
        if not tracks:
            await msg.edit_text("Кечирип кой, SoundCloud'дон табылган жок.")
            return

        track = tracks[0]
        stream_url = track.get_stream_url()
        
        if stream_url:
            audio = URLInputFile(stream_url, filename=f"{track.title}.mp3")
            await message.answer_audio(
                audio=audio,
                title=track.title,
                performer=track.artist,
                caption=f"✅ Табылды: {track.title}"
            )
            await msg.delete()
        else:
            await msg.edit_text("Музыканы жүктөөгө мүмкүн болбоду.")

    except Exception as e:
        print(f"Ката: {e}")
        await msg.edit_text("Ката кетти. Башкачараак жазып көрчү.")

async def main():
    print("Бот иштеп жатат...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
  
