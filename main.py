import logging
import asyncio
import random
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Сенин акыркы токениң
API_TOKEN = '8576931278:AAECIYTCR9k81pnLy7A8R-xFjeYfgU3KEqo'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# Күндүн ойлору
WISDOM_QUOTES = [
    "🌟 Ар бир кыйынчылыктын артында бир жеңилдик бар.",
    "🚀 Эң чоң жеңиш — өзүңдү жеңүү.",
    "💎 Убакыт — бул сенин эң баалуу байлыгың, аны туура иштет.",
    "🔥 Максатың болсо, ага жетүүдөн эч качан коркпо!",
    "⚡ Токтоп калбасаң эле, канчалык жай баратканың маанилүү эмес.",
    "🌱 Сабырдуулук — бардык ийгиликтердин ачкычы.",
    "🌈 Бүгүнкү аракет — эртеңки ийгиликтин пайдубалы."
]

def get_audio_data(query):
    """YouTube'дан издөө жана маалымат алуу"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch1',
        'no_warnings': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if 'entries' in info:
            info = info['entries'][0]
        return info['url'], info.get('title', 'Трек')

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Салам, Арген! <b>ыр [аты]</b> деп жазсаңыз, YouTube'дан таап берем. \nМисалы: <code>ыр Бакр</code>")

@dp.message_handler(lambda m: m.text and m.text.lower().startswith(('ыр', 'трек')))
async def search_song(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply("Ырдын атын жазыңыз. Мисалы: ыр Камин")

    query = parts[1]
    msg = await message.answer(f"🔎 <b>{query}</b> YouTube'дан издеп жатам...")
    
    try:
        loop = asyncio.get_event_loop()
        # YouTube'дан маалымат алуу
        audio_url, title = await loop.run_in_executor(None, get_audio_data, query)
        
        quote = random.choice(WISDOM_QUOTES)
        caption = (
            f"🎶 <b>{title}</b>\n\n"
            f"━━━━━━━━━━━━━\n"
            f"💡 <b>Күндүн ою:</b>\n<i>{quote}</i>\n"
            f"━━━━━━━━━━━━━\n\n"
            f"👤 Боттун ээси: @Argen_70"
        )
        
        # Түз шилтеме аркылуу аудиону жөнөтүү
        await message.answer_audio(audio=audio_url, caption=caption, title=title)
        await msg.delete()

    except Exception as e:
        logging.error(f"Ката: {e}")
        await msg.edit_text("Ыр табылган жок. Башкачараак жазып көрүңүз.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
  
