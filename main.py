import os, asyncio
from aiogram import Bot, Dispatcher, types
import yt_dlp
from aiohttp import web

TOKEN = "8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM"
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def handle(request): return web.Response(text="Бот так режимде!")
async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', os.getenv('PORT', 10000))
    await site.start()

def download_music(query):
    # Издөөгө 'official' жана 'audio' деген сөздөрдү кошуп, тактыкты арттырабыз
    search_query = f"{query} official audio"
    
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch1', # Биринчи, эң популярдуу жыйынтыкты ал
        'noplaylist': True,
        'writethumbnail': True,
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'},
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata'}
        ]
    }
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        try:
            # YouTube'дан издөө
            info = ydl.extract_info(f"ytsearch1:{search_query}", download=True)
            if 'entries' in info:
                entry = info['entries'][0]
            else:
                entry = info
            
            filename = ydl.prepare_filename(entry).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            return filename, entry.get('title'), entry.get('uploader')
        except:
            # Эгер YouTube бөгөттөсө, SoundCloud аркылуу так издөө
            try:
                info = ydl.extract_info(f"scsearch1:{query}", download=True)
                if 'entries' in info:
                    entry = info['entries'][0]
                else:
                    entry = info
                filename = ydl.prepare_filename(entry).replace('.webm', '.mp3').replace('.m4a', '.mp3')
                return filename, entry.get('title'), entry.get('uploader')
            except:
                return None, None, None

@dp.message()
async def search(message: types.Message):
    if not message.text: return
    
    # "трек" деген сөздү алып салып, таза издөө жүргүзөбүз
    query = message.text.replace("трек ", "").replace("Трек ", "").strip()
    m = await message.answer(f"🎯 Так издеп жатам: {query}...")
    
    try:
        path, title, author = await asyncio.to_thread(download_music, query)
        
        if path and os.path.exists(path):
            audio = types.FSInputFile(path)
            # Ырды ашыкча текстсиз, оригиналдуу маалыматтары менен жөнөтөбүз
            await message.answer_audio(
                audio, 
                performer=author,
                title=title
            )
            await m.delete()
            os.remove(path)
        else:
            await m.edit_text("❌ Кечир, так ушул ыр табылган жок. Атын туура жазганыңды текшерчи.")
    except Exception:
        await m.edit_text("Ката кетти. Кайра аракет кылып көрчү?")

async def main():
    await start_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
