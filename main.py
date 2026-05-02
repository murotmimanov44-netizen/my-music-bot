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
    # YouTube'дун жаңы чектөөлөрүн айланып өтүү үчүн жөндөөлөр
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'music.%(ext)s',
        'default_search': 'ytsearch',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'source_address': '0.0.0.0', # IPv4 колдонуу
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        # Издөө 
        info = ydl.extract_info(f"ytsearch1:{query}", download=True)
        if 'entries' in info and len(info['entries']) > 0:
            return "music.mp3", info['entries'][0].get('title')
        return None, None

@dp.message()
async def search(message: types.Message):
    if not message.text: return
    text = message.text.lower()
    
    if text.startswith("трек "):
        query = message.text.split(maxsplit=1)[1]
        m = await message.answer(f"🚀 '{query}' издеп жатам...")
        
        try:
            # Издөө процессин иштетүү
            path, title = await asyncio.to_thread(download_yt, query)
            
            if path:
                audio = types.FSInputFile(path)
                await message.answer_audio(
                    audio, 
                    caption=f"🎵 {title}\n👤 Жүктөдү: @Argen_70",
                    performer="@Argen_70"
                )
                await m.delete()
                os.remove(path)
            else:
                await m.edit_text("Кечир, YouTube бул ырды бербей койду. Башка ыр жазып көрчү?")
        except Exception as e:
            print(f"Ката: {e}")
            await m.edit_text("Ката кетти. Кайра аракет кылып көр.")

async def main():
    await start_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
