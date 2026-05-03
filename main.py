import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, URLInputFile
from sclib import SoundcloudAPI

# СЕНИН ТОКЕНИҢ
API_TOKEN = '8576931278:AAECIYTCR9k81pnLy7A8R-xFjeYfgU3KEqo'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
api = SoundcloudAPI()

@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer("Салам, Арген! Бот Background Worker катары иштеди. Ырдын атын жаз.")

@dp.message()
async def search(message: Message):
    query = message.text
    msg = await message.answer(f"🔍 SoundCloud'дан издеп жатам: {query}")
    try:
        tracks = api.search_tracks(query)
        if tracks:
            track = tracks[0]
            stream_url = track.get_stream_url()
            audio = URLInputFile(stream_url, filename=f"{track.title}.mp3")
            await message.answer_audio(audio=audio, title=track.title)
            await msg.delete()
        else:
            await msg.edit_text("Эч нерсе таба алган жокмун.")
    except Exception as e:
        await msg.edit_text("Ката кетти. Башкачараак жазып көр.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
