import logging
import asyncio
import random
import os
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Сиз берген жаңы токен
API_TOKEN = '8576931278:AAECIYTCR9k81pnLy7A8R-xFjeYfgU3KEqo'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# Мыкты ойлордун тизмеси
WISDOM_QUOTES = [
    "🌟 Ар бир кыйынчылыктын артында бир жеңилдик бар.",
    "🚀 Эң чоң жеңиш — өзүңдү жеңүү.",
    "💎 Убакыт — бул сенин эң баалуу байлыгың, аны туура иштет.",
    "🌈 Бүгүнкү аракет — эртеңки ийгиликтин пайдубалы.",
    "🔥 Максатың болсо, ага жетүүдөн эч качан коркпо!",
    "📚 Билим алуу — ийгиликке баруучу эң кыска жол.",
    "🌱 Сабырдуулук — бардык ийгиликтердин ачкычы.",
    "⚡ Токтоп калбасаң эле, канчалык жай баратканың маанилүү эмес."
]

def download_audio(query):
    """YouTube'дан ыр издөө жана жүктөө функциясы"""
    file_name = f"song_{random.randint(1000, 9999)}.mp3"
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch1',
        'outtmpl': file_name,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        if 'entries' in info:
            info = info['entries'][0]
        return file_name, info.get('title', 'Белгисиз трек')

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Салам! Ыр издөө үчүн: <b>ыр [ырдын аты]</b> деп жазыңыз. \nМисалы: <code>ыр Бакр До луны</code>")

@dp.message_handler(lambda m: m.text and m.text.lower().startswith(('ыр', 'трек')))
async def search_song(message: types.Message):
    # Колдонуучу жазган ырдын атын алуу
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply("Ырдын атын жазыңыз. Мисалы: ыр Камин")

    query = parts[1]
    msg = await message.answer(f"🔎 <b>{query}</b> YouTube'дан издеп жатам...")
    
    try:
        # Издөө жана жүктөө (блок кылбаш үчүн executor колдонобуз)
        loop = asyncio.get_event_loop()
        file_path, title = await loop.run_in_executor(None, download_audio, query)
        
        # Туш келди ойду тандоо
        quote = random.choice(WISDOM_QUOTES)
        caption = (
            f"🎶 <b>{title}</b>\n\n"
            f"━━━━━━━━━━━━━\n"
            f"💡 <b>Күндүн ою:</b>\n<i>{quote}</i>\n"
            f"━━━━━━━━━━━━━\n\n"
            f"👤 Боттун ээси: @Argen_70"
        )
        
        # Аудиону жөнөтүү
        with open(file_path, 'rb') as audio:
            await message.answer_audio(audio, caption=caption)
        
        # Убактылуу файлды өчүрүү
        os.remove(file_path)
        await msg.delete()

    except Exception as e:
        logging.error(f"Ката: {e}")
        await msg.edit_text("Тилекке каршы, ыр табылган жок же жүктөөдө ката кетти.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
