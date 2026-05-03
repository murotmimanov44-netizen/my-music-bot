import logging
import asyncio
import random
import urllib.parse
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# Токенди текшерип кой
API_TOKEN = '8576931278:AAECIYTCR9k81pnLy7A8R-xFjeYfgU3KEqo'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# Мыкты ойлордун тизмеси
WISDOM_QUOTES = [
    "🌟 Ар бир кыйынчылыктын артында бир жеңилдик бар.",
    "🚀 Эң чоң жеңиш — өзүңдү жеңүү.",
    "💎 Убакыт — бул сенин эң баалуу байлыгың, аны туура иштет.",
    "🌈 Бүгүнкү аракет — эртеңки ийгиликтин пайдубалы.",
    "🔥 Максатың болсо, ага жетүүдөн эч качан коркпо!",
    "📚 Билим алуу — ийгиликке баруучу эң кыска жол.",
    "🤝 Жакшы сөз — жан азыгы.",
    "🌱 Сабырдуулук — бардык ийгиликтердин ачкычы.",
    "⚡ Токтоп калбасаң эле, канчалык жай баратканың маанилүү эмес."
]

async def search_deezer(track_name):
    clean_name = track_name.strip()
    safe_name = urllib.parse.quote(clean_name)
    url = f"https://api.deezer.com/search?q={safe_name}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('data') and len(data['data']) > 0:
                    return data['data'][0]
            return None

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Салам! Ыр издөө үчүн мисалы: <b>ыр Бакра за любовь</b> деп жазыңыз.")

@dp.message(F.text)
async def handle_message(message: types.Message):
    text = message.text.lower()
    
    if text.startswith("ыр") or text.startswith("трек"):
        song_name = ""
        if text.startswith("ыр"):
            song_name = message.text[2:].strip()
        elif text.startswith("трек"):
            song_name = message.text[4:].strip()
            
        if not song_name:
            await message.reply("Ырдын атын жазыңыз.")
            return

        msg = await message.answer(f"🔎 <b>{song_name}</b> издеп жатам...")
        result = await search_deezer(song_name)

        if result:
            title = result['title']
            artist = result['artist']['name']
            preview_url = result['preview']
            
            # Тизмеден туш келди бир ойду тандап алуу
            random_quote = random.choice(WISDOM_QUOTES)
            
            # Ойду файлдын астына кошуу
            caption = (
                f"🎶 <b>{artist} — {title}</b>\n\n"
                f"━━━━━━━━━━━━━\n"
                f"💡 <b>Күндүн ою:</b>\n<i>{random_quote}</i>\n"
                f"━━━━━━━━━━━━━\n\n"
                f"👤 Боттун ээси: @Argen_70"
            )
            
            try:
                await message.answer_audio(audio=preview_url, caption=caption, parse_mode='HTML')
                await msg.delete()
            except Exception as e:
                await message.reply("Аудиону жөнөтүүдө ката кетти.")
        else:
            await message.reply(f"Тилекке каршы, '{song_name}' табылган жок.")

async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
          
