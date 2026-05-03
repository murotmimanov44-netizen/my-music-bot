import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import aiohttp

API_TOKEN = '8787212087:AAFW-ont6NJARHAdR3JE2uPVUdBn4XepkTk'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

async def search_deezer(track_name):
    url = f"https://api.deezer.com/search?q={track_name}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data['data']:
                    return data['data'][0]
            return None

@dp.message_handler(lambda message: message.text and message.text.lower().startswith(('трек', 'ыр')))
async def find_track(message: types.Message):
    query = message.text.split(maxsplit=1)
    if len(query) < 2:
        await message.reply("Ырдын атын жазыңыз. Мисалы: ыр Come In")
        return

    song_name = query[1]
    msg = await message.answer(f"🔎 <b>{song_name}</b> издеп жатам...")
    result = await search_deezer(song_name)

    if result:
        title = result['title']
        artist = result['artist']['name']
        preview_url = result['preview']
        caption = f"🎶 <b>{artist} — {title}</b>\n\n👤 Боттун ээси: @Argen_70"
        
        await bot.send_audio(message.chat.id, audio=preview_url, caption=caption, parse_mode='HTML')
        await bot.delete_message(message.chat.id, msg.message_id)
    else:
        await message.reply("Тилекке каршы, мындай ыр табылган жок.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
