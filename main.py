import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, URLInputFile
from sclib import SoundcloudAPI, Track

API_TOKEN = '8576931278:AAECIYTCR9k81pnLy7A8R-xFjeYfgU3KEqo'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
api = SoundcloudAPI()

@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer("Салам, Арген! SoundCloud'дон музыка издейбиз. Ырдын атын же шилтемесин жаз.")

@dp.message()
async def search_soundcloud(message: Message):
    query = message.text
    msg = await message.answer(f"☁️ SoundCloud'дан '{query}' издеп жатам...")

    try:
        # SoundCloud'дон издөө
        tracks = api.search_tracks(query)
        
        if not tracks:
            await msg.edit_text("Кечирип кой, SoundCloud'дан бул ырды таба алган жокмун.")
            return

        # Биринчи табылган ырды алабыз
        track = tracks[0]
        
        # Ырдын агымын (stream) алуу
        stream_url = track.get_stream_url()
        
        if stream_url:
            audio = URLInputFile(stream_url, filename=f"{track.title}.mp3")
            await message.answer_audio(
                audio=audio,
                title=track.title,
                performer=track.artist,
                caption=f"🎵 {track.title}\n👤 {track.artist}"
            )
            await msg.delete()
        else:
            await msg.edit_text("Ырды жүктөөгө мүмкүн болгон жок.")

    except Exception as e:
        print(f"Ката: {e}")
        await msg.edit_text("Ката кетти. Башкачараак жазып көрчү (мисалы: 'Artist - Song').")

async def main():
    print("SoundCloud бот ишке кирди...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
  
