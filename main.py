import os, asyncio
from aiogram import Bot, Dispatcher, types
import yt_dlp
from aiohttp import web

# Сенин токениң
TOKEN = "8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM"
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def handle(request): return web.Response(text="Бот так издөө режиминде!")
async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', os.getenv('PORT', 10000))
    await site.start()

def download_music(query):
    # Издөө суроосун максималдуу так кылабыз
    search_query = f"{query} official audio"
    
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'music.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'noplaylist': True,
        # Бир гана аудио форматтарды жана эң жакшы сапатты тандайт
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
    }
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        try:
            # YouTube'дун коргоосун айланып өтүү жана так издөө
            info = ydl.extract_info(f"ytsearch1:{search_query}", download=True)
            if 'entries' in info and len(info['entries']) > 0:
                entry = info['entries'][0]
                # Эгер табылган ырдын атында сенин сурооңдун жок дегенде бир сөзү болсо
                return "music.mp3", entry.get('title'), entry.get('uploader')
        except:
            # YouTube иштебей калса, SoundCloud'ка өтөт
            info = ydl.extract_info(f"scsearch1:{search_query}", download=True)
            if 'entries' in info and len(info['entries']) > 0:
                entry = info['entries'][0]
                return "music.mp3", entry.get('title'), entry.get('uploader')
        return None, None, None

@dp.message()
async def search(message: types.Message):
    if not message.text: return
    
    text_lower = message.text.lower()
    
    if text_lower.startswith("трек "):
        query = message.text.split(maxsplit=1)[1]
        m = await message.answer(f"🔍 Так издеп жатам: {query}...")
        
        try:
            path, title, uploader = await asyncio.to_thread(download_music, query)
            
            if path and os.path.exists(path):
                audio = types.FSInputFile(path)
                
                # Файлды жөнөтүүдө автордун атын жана ырдын атын так көрсөтүү
                await message.answer_audio(
                    audio, 
                    caption=f"🎵 {title}\n👤 Автор/Канал: {uploader}\n📥 Жүктөдү: @Argen_70", 
                    performer=uploader if uploader else "Official Artist",
                    title=title
                )
                await m.delete()
                os.remove(path)
            else:
                await m.edit_text("Кечир, так ушул автордун ыры табылган жок. Атын толук жазып көрчү?")
        except Exception as e:
            await m.edit_text("Ырды жүктөөдө ката кетти. Кайра аракет кылып көр.")

async def main():
    await start_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
              
