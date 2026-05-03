import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import aiohttp

# Токенди текшерип кой
API_TOKEN = '8787212087:AAFW-ont6NJARHAdR3JE2uPVUdBn4XepkTk'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

async def search_deezer(track_name):
    url = f"https://api.deezer.com/search?q={track_name}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('data'):
                    return data['data'][0]
            return None

# Старт командасы
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Салам! Ыр издөө үчүн 'ыр [ырдын аты]' деп жазыңыз.")

# Ыр издөө командасы
@dp.message(F.text.lower().startswith("ыр") | F.text.lower().startswith("трек"))
async def find_track(message: types.Message):
    text = message.text.split(maxsplit=1)
    if len(text) < 2:
        await message.reply("Ырдын атын жазыңыз. Мисалы: ыр Come In")
        return

    song_name = text[1]
    msg = await message.answer(f"🔎 <b>{song_name}</b> издеп жатам...")
    result = await search_deezer(song_name)

    if result:
        title = result['title']
        artist = result['artist']['name']
        preview_url = result['preview']
        caption = f"🎶 <b>{artist} — {title}</b>\n\n👤 Боттун ээси: @Argen_70"
        
        await message.answer_audio(audio=preview_url, caption=caption, parse_mode='HTML')
        await msg.delete()
    else:
        await message.reply("Тилекке каршы, мындай ыр табылган жок.")

async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
  
