import os, asyncio
from aiogram import Bot, Dispatcher, types
import yt_dlp
from aiohttp import web

# Сенин бот токениң
TOKEN = "8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Render үчүн веб-сервер
async def handle(request): return web.Response(text="Бот иштеп жатат!")
async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', os.getenv('PORT', 10000))
    await site.start()

# YouTube'дан жүктөө функциясы
def download_yt(query):
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'music.%(ext)s',
        'default_search': 'ytsearch',
        'quiet': True,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=True)['entries'][0]
        return "music.mp3", info.get('title')

@dp.message()
async def search(message: types.Message):
    if not message.text: return
    
    text_lower = message.text.lower()
    
    # Эми бир гана "трек " менен башталганда иштейт
    if text_lower.startswith("трек "):
        # "трек " деген сөздү алып салып, ырдын атын гана алабыз
        query = message.text.split(maxsplit=1)[1]
        m = await message.answer(f"🔎 Ютубдан издеп жатам: {query}...")
        
        try:
            path, title = await asyncio.to_thread(download_yt, query)
            audio = types.FSInputFile(path)
            
            # Жөнөтүү
            await message.answer_audio(
                audio, 
                caption=f"🎵 {title}\n👤 Жүктөдү: @Argen_70", 
                performer="@Argen_70",
                title=title
            )
            await m.delete()
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            await m.edit_text("Ыр табылган жок же ката кетти.")

async def main():
    await start_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
