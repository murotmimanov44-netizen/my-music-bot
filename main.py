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

# YouTube'ду колдонбостон, башка булактардан издөө
def download_music(query):
    # 'default_search'ди өчүрүп, ар түрдүү сайттардан издөөгө уруксат бердик
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'music.mp3',
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '128'}]
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        # Ырды SoundCloud же башка булактан издөө үчүн:
        info = ydl.extract_info(f"scsearch1:{query}", download=True)
        if 'entries' in info and info['entries']:
            return "music.mp3", info['entries'][0].get('title')
        return None, None

@dp.message()
async def search(message: types.Message):
    if message.text and message.text.lower().startswith("трек "):
        query = message.text.split(maxsplit=1)[1]
        m = await message.answer(f"⏳ '{query}' издеп жатам...")
        try:
            path, title = await asyncio.to_thread(download_music, query)
            if path and os.path.exists(path):
                await message.answer_audio(types.FSInputFile(path), caption=f"🎵 {title}\n👤 @Argen_70")
                await m.delete()
                os.remove(path)
            else:
                await m.edit_text("Бул ыр SoundCloud'та табылган жок.")
        except Exception as e:
            await m.edit_text("Ката кетти, башка ыр же башка ат жазып көр.")

async def main():
    await start_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
