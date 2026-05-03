import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import aiohttp
import urllib.parse

API_TOKEN = '8787212087:AAFW-ont6NJARHAdR3JE2uPVUdBn4XepkTk'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

async def search_deezer(track_name):
    # Издөө сөзүн коопсуз форматка келтирүү
    safe_name = urllib.parse.quote(track_name)
    url = f"https://api.deezer.com/search?q={safe_name}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('data'):
                    # Эң биринчи чыккан жыйынтыкты алуу
                    return data['data'][0]
            return None

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Салам! Ыр издөө үчүн мисалы: <b>ыр Бакра за любовь</b> деп жазыңыз.")

@dp.message(F.text.lower().contains("ыр") | F.text.lower().contains("трек"))
async def find_track(message: types.Message):
    # "ыр" же "трек" деген сөздү алып салуу
    raw_text = message.text.lower()
    song_name = raw_text.replace("ыр", "").replace("трек", "").strip()
    
    if not song_name:
        await message.reply("Ырдын атын жазыңыз. Мисалы: ыр До луны")
        return

    msg = await message.answer(f"🔎 <b>{song_name}</b> издеп жатам...")
    result = await search_deezer(song_name)

    if result:
        title = result['title']
        artist = result['artist']['name']
        preview_url = result['preview']
        caption = f"🎶 <b>{artist} — {title}</b>\n\n👤 Боттун ээси: @Argen_70"
        
        try:
            await message.answer_audio(audio=preview_url, caption=caption, parse_mode='HTML')
            await msg.delete()
        except Exception as e:
            await message.reply(f"Ката кетти: {e}")
    else:
        await message.reply(f"Тилекке каршы, '{song_name}' боюнча эч нерсе табылган жок. Башкача жазып көрүңүз.")

async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
      
