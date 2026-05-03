import subprocess
import sys
import os

# Render китепканаларды таппай жатса, мажбурлап орнотуу
def force_install():
    try:
        import aiogram
        import sclib
    except ImportError:
        print("Китепканалар орнотулууда...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiogram==3.4.1", "soundcloud-lib"])

force_install()

import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, URLInputFile
from sclib import SoundcloudAPI

# Сенин токениң кошулду
API_TOKEN = '8576931278:AAECIYTCR9k81pnLy7A8R-xFjeYfgU3KEqo'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
api = SoundcloudAPI()

@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer("Салам, Арген! SoundCloud бот иштеп жатат. Мага ырдын атын жаз, мен таап берем.")

@dp.message()
async def search_music(message: Message):
    query = message.text
    temp_msg = await message.answer(f"🔍 SoundCloud'дан '{query}' издеп жатам...")

    try:
        # SoundCloud'дон издөө
        tracks = api.search_tracks(query)
        
        if not tracks:
            await temp_msg.edit_text("Кечирип кой, SoundCloud'дан эч нерсе табылган жок. Башкачараак жазып көр.")
            return

        # Эң биринчи чыккан ырды алуу
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
            await temp_msg.delete()
        else:
            await temp_msg.edit_text("Тилекке каршы, бул ырды жүктөөгө мүмкүн болбоду.")
            
    except Exception as e:
        print(f"Ката: {e}")
        await temp_msg.edit_text("Ката кетти. Кийинчерээк кайра байкап көрчү.")

async def main():
    print("Бот иштеп жатат...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
