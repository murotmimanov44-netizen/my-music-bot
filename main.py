import logging
import asyncio
import random
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Сенин акыркы токениң
API_TOKEN = '8576931278:AAECIYTCR9k81pnLy7A8R-xFjeYfgU3KEqo'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

WISDOM_QUOTES = [
    "🌟 Ар бир кыйынчылыктын артында бир жеңилдик бар.",
    "🚀 Эң чоң жеңиш — өзүңдү жеңүү.",
    "💎 Убакыт — бул сенин эң баалуу байлыгың.",
    "🔥 Максатың болсо, ага жетүүдөн эч качан коркпо!",
    "🌈 Бүгүнкү аракет — эртеңки ийгиликтин пайдубалы."
]

async def search_music(query):
    # SoundCloud/Deezer аркылуу издөө (кошумча китепканасыз)
    url = f"https://api.deezer.com/search?q={query}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('data'):
                    return data['data'][0]
            return None

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Салам, Арген! <b>ыр [аты]</b> деп жазыңыз, мен таап берем.")

@dp.message_handler(lambda m: m.text and m.text.lower().startswith(('ыр', 'трек')))
async def handle_music(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply("Ырдын атын жазыңыз.")

    query = parts[1]
    msg = await message.answer(f"🔎 <b>{query}</b> издеп жатам...")
    
    result = await search_music(query)
    if result:
        title = result['title']
        artist = result['artist']['name']
        audio_url = result['preview'] # Түз шилтеме
        
        quote = random.choice(WISDOM_QUOTES)
        caption = f"🎶 <b>{artist} - {title}</b>\n\n💡 <b>Ой:</b> {quote}\n\n👤 @Argen_70"
        
        await message.answer_audio(audio=audio_url, caption=caption)
        await msg.delete()
    else:
        await msg.edit_text("Тилекке каршы, бул ыр табылган жок.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
  
