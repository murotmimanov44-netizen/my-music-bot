import logging
import random
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import urllib.parse

# Сенин акыркы токениң
API_TOKEN = '8576931278:AAECIYTCR9k81pnLy7A8R-xFjeYfgU3KEqo'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# Күндүн ойлору
WISDOM_QUOTES = [
    "🌟 Ар бир кыйынчылыктын артында бир жеңилдик бар.",
    "🚀 Эң чоң жеңиш — өзүңдү жеңүү.",
    "💎 Убакыт — бул сенин эң баалуу байлыгың.",
    "🔥 Максатың болсо, ага жетүүдөн эч качан коркпо!",
    "🌈 Бүгүнкү аракет — эртеңки ийгиликтин пайдубалы."
]

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Салам, Арген! <b>ыр [аты]</b> деп жазыңыз, мен Deezer'ден таап берем.")

@dp.message_handler(lambda m: m.text and m.text.lower().startswith(('ыр', 'трек')))
async def handle_music(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply("Ырдын атын жазыңыз.")

    query = parts[1]
    msg = await message.answer(f"🔎 <b>{query}</b> издеп жатам...")
    
    # Deezer API колдонуу (кошумча китепканасыз)
    safe_query = urllib.parse.quote(query)
    url = f"https://api.deezer.com/search?q={safe_query}"
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                if data.get('data'):
                    result = data['data'][0]
                    title = result['title']
                    artist = result['artist']['name']
                    audio_url = result['preview']
                    
                    quote = random.choice(WISDOM_QUOTES)
                    caption = f"🎶 <b>{artist} - {title}</b>\n\n💡 <b>Ой:</b> {quote}\n\n👤 @Argen_70"
                    
                    await message.answer_audio(audio=audio_url, caption=caption)
                    await msg.delete()
                else:
                    await msg.edit_text("Тилекке каршы, эч нерсе табылган жок.")
    except Exception as e:
        logging.error(f"Error: {e}")
        await msg.edit_text("Издөө учурунда ката кетти.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
  
