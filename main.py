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
    # SoundCloud издөөсүн негизги кылабыз, ал блоктолбойт
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'writethumbnail': True,
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata'}
        ]
    }
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        # Бир нече булактан кезек менен издейт
        search_engines = [f"scsearch1:{query}", f"ytsearch1:{query}"]
        for engine in search_engines:
            try:
                info = ydl.extract_info(engine, download=True)
                if 'entries' in info:
                    entry = info['entries'][0]
                else:
                    entry = info
                
                filename = ydl.prepare_filename(entry).replace('.webm', '.mp3').replace('.m4a', '.mp3')
                return filename, entry.get('title'), entry.get('uploader')
            except:
                continue
        return None, None, None

@dp.message()
async def search(message: types.Message):
    if message.text and message.text.lower().startswith("трек "):
        query = message.text.split(maxsplit=1)[1]
        m = await message.answer(f"🚀 '{query}' издеп жатам...")
        
        try:
            # Издөөнү ишке киргизүү
            path, title, author = await asyncio.to_thread(download_music, query)
            
            if path and os.path.exists(path):
                audio = types.FSInputFile(path)
                await message.answer_audio(
                    audio, 
                    performer=author,
                    title=title
                )
                await m.delete()
                os.remove(path)
            else:
                await m.edit_text("❌ Кечир, бул ыр табылган жок. Автордун атын кошуп жазып көрчү (мисалы: Bakr - Камин)")
        except Exception as e:
            await m.edit_text(f"❌ Ката кетти. Башкачараак жазып көрчү?")

async def main():
    await start_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
