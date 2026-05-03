import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from youtubesearchpython import VideosSearch
import yt_dlp

API_TOKEN = '8576931278:AAECIYTCR9k81pnLy7A8R-xFjeYfgU3KEqo'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Жүктөө жөндөөлөрү
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'quiet': True,
    'noplaylist': True,
}

@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer("Салам! Ырдын атын жаз, мен таап берем.")

@dp.message()
async def download_song(message: Message):
    query = message.text
    msg = await message.answer(f"🔍 '{query}' издеп жатам...")
    
    try:
        # YouTube'дан издөө
        search = VideosSearch(query, limit=1)
        result = search.result()['result']
        
        if not result:
            await msg.edit_text("Эч нерсе табылган жок 😔")
            return

        video_url = result[0]['link']
        title = result[0]['title']

        # YouTube шилтемесин алуу
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(video_url, download=False)
            audio_url = info['url']

        # Музыканы жөнөтүү
        await message.answer_audio(
            audio=audio_url,
            title=title,
            caption=f"🎵 {title}\n\n@сенин_ботуң"
        )
        await msg.delete()

    except Exception as e:
        print(f"Ката: {e}")
        await msg.edit_text("Ката кетти. Башка ыр издеп көрчү.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
  
