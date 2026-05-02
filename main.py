import os, asyncio
from aiogram import Bot, Dispatcher, types
import yt_dlp
from aiohttp import web

TOKEN = "8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM"
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def handle(request): return web.Response(text="Live!")
async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', os.getenv('PORT', 10000))
    await site.start()

def download_yt(query):
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'music.%(ext)s',
        'default_search': 'ytsearch',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        # YouTube'дун бөгөтүн айланып өтүү үчүн маанилүү жөндөөлөр:
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=True)
        if 'entries' in info:
            entry = info['entries'][0]
            return "music.mp3", entry.get('title')
        return None, None

@dp.message()
async def search(message: types.Message):
    if message.text and message.text.lower().startswith("трек "):
        query = message.text.split(maxsplit=1)[1]
        m = await message.answer(f"🚀 '{query}' издеп жатам...")
        try:
            path, title = await asyncio.to_thread(download_yt, query)
            if path and os.path.exists(path):
                audio = types.FSInputFile(path)
                await message.answer_audio(audio, caption=f"🎵 {title}\n👤 @Argen_70", title=title)
                await m.delete()
                os.remove(path)
            else:
                await m.edit_text("Ыр табылган жок.")
        except Exception as e:
            # Ката кетсе дагы тереңирээк издөөгө аракет кылат
            await m.edit_text(f"❌ YouTube бөгөттөп жатат. Башкачараак жазып көрчү?")

async def main():
    await start_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
          
