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
    # Бөгөттөрдү айланып өтүү үчүн android жана ios клиенттерин колдонобуз
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch1',
        'noplaylist': True,
        'writethumbnail': True,
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata'},
        ],
        # Бул жер — эң маанилүүсү: YouTube'ду алдоо үчүн
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web', 'ios'],
                'skip': ['dash', 'hls']
            }
        },
    }
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        try:
            # Биринчи YouTube'дан так издөө
            info = ydl.extract_info(f"ytsearch1:{query} audio", download=True)
            if 'entries' in info:
                entry = info['entries'][0]
            else:
                entry = info
            
            filename = ydl.prepare_filename(entry).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            return filename, entry.get('title'), entry.get('uploader')
        except:
            # YouTube блоктосо, SoundCloud'ка өтүү
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
    
    query = message.text.replace("трек ", "").replace("Трек ", "").strip()
    m = await message.answer(f"🔎 Издеп жатам: <b>{query}</b>", parse_mode="HTML")
    
    try:
        path, title, author = await asyncio.to_thread(download_music, query)
        
        if path and os.path.exists(path):
            audio = types.FSInputFile(path)
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
            await m.edit_text("❌ Кечир, табылган жок. Атын так жазып көрчү?")
    except Exception:
        await m.edit_text("❌ Системада ката. Бир аздан кийин кайра аракет кыл.")

async def main():
    await start_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
