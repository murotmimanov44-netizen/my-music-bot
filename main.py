import os, asyncio
from aiogram import Bot, Dispatcher, types
import yt_dlp
from aiohttp import web

TOKEN = "8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM"
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def handle(request): return web.Response(text="Бот иштеп жатат!")
async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', os.getenv('PORT', 10000))
    await site.start()

def download_music(query):
    # YouTube издөөсүн максималдуу туруктуу кылуу
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'music.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'source_address': '0.0.0.0', # IPv4 мажбурлоо
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        # Биринчи YouTube'дан издейт, эгер болбосо SoundCloud'ка өтөт
        try:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            if 'entries' in info and len(info['entries']) > 0:
                entry = info['entries'][0]
                return "music.mp3", entry.get('title')
        except:
            info = ydl.extract_info(f"scsearch1:{query}", download=True)
            if 'entries' in info and len(info['entries']) > 0:
                entry = info['entries'][0]
                return "music.mp3", entry.get('title')
        return None, None

@dp.message()
async def search(message: types.Message):
    if message.text and message.text.lower().startswith("трек "):
        query = message.text.split(maxsplit=1)[1]
        m = await message.answer(f"🚀 '{query}' издеп жатам...")
        
        try:
            path, title = await asyncio.to_thread(download_music, query)
            if path and os.path.exists(path):
                audio = types.FSInputFile(path)
                await message.answer_audio(audio, caption=f"🎵 {title}\n👤 @Argen_70")
                await m.delete()
                os.remove(path)
            else:
                await m.edit_text("Кечир, ыр эч жерден табылган жок.")
        except Exception as e:
            await m.edit_text(f"❌ Ката: Башка ыр жазып көрчү?")

async def main():
    await start_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
              
