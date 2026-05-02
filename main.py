import os, asyncio
from aiogram import Bot, Dispatcher, types
import yt_dlp
from aiohttp import web

TOKEN = "8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM"
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def handle(request): return web.Response(text="Music Bot is Professional!")
async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', os.getenv('PORT', 10000))
    await site.start()

def download_music(query):
    # Spotify ботторуна окшоштуруу үчүн жөндөөлөр
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch1',
        'noplaylist': True,
        'writethumbnail': True, # Сүрөтүн кошо жүктөө
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'},
            {'key': 'EmbedThumbnail'}, # Сүрөттү файлдын ичине киргизүү
            {'key': 'FFmpegMetadata'}, # Метамаалыматтарды (автор, альбом) кошуу
        ],
        # YouTube бөгөттөрүн айланып өтүү үчүн маанилүү
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
    }
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        try:
            # Издөөгө "audio" деп кошуу тактыкты 100% кылат
            info = ydl.extract_info(f"ytsearch1:{query} audio", download=True)
            if 'entries' in info:
                entry = info['entries'][0]
            else:
                entry = info
            
            # Таза файл атын түзүү
            filename = ydl.prepare_filename(entry).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            return filename, entry.get('title'), entry.get('uploader')
        except Exception:
            return None, None, None

@dp.message()
async def search(message: types.Message):
    if not message.text: return
    
    # "трек" дегенди алып салып, таза издөө
    query = message.text.lower().replace("трек", "").strip()
    m = await message.answer(f"🔍 <b>{query}</b> изделүүдө...")
    
    try:
        path, title, author = await asyncio.to_thread(download_music, query)
        
        if path and os.path.exists(path):
            audio = types.FSInputFile(path)
            # Так Spotify стилинде жөнөтүү
            await message.answer_audio(
                audio, 
                performer=author,
                title=title,
                caption=f"🎵 <b>{title}</b>\n👤 @Argen_70",
                parse_mode="HTML"
            )
            await m.delete()
            os.remove(path)
        else:
            await m.edit_text("❌ Кечир, так ушул ыр табылган жок.")
    except Exception:
        await m.edit_text("❌ Ката кетти. Башкачараак жазып көрчү?")

async def main():
    await start_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
