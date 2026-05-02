import os, asyncio
from aiogram import Bot, Dispatcher, types
import yt_dlp
from aiohttp import web

TOKEN = "8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM"
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def handle(request): return web.Response(text="Бот онлайн!")
async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', os.getenv('PORT', 10000))
    await site.start()

def download_music(query):
    # YouTube бөгөттөп жаткандыктан, башка ачык базалардан издөөгө мажбурлайбыз
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'music.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        # 'noprogress': True,
        'extract_flat': False,
        # Бул жерде бир эле учурда бир нече булакты текшерет
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '128'}]
    }
    
    # Издөө үчүн бир нече вариантты айкалыштырабыз
    search_queries = [f"scsearch1:{query}", f"ytsearch1:{query}"]
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        for s_query in search_queries:
            try:
                info = ydl.extract_info(s_query, download=True)
                if 'entries' in info and len(info['entries']) > 0:
                    return "music.mp3", info['entries'][0].get('title')
            except:
                continue
        return None, None

@dp.message()
async def search(message: types.Message):
    if message.text and message.text.lower().startswith("трек "):
        query = message.text.split(maxsplit=1)[1]
        m = await message.answer(f"🔎 Издеп жатам: {query}...")
        
        try:
            path, title = await asyncio.to_thread(download_music, query)
            if path and os.path.exists(path):
                audio = types.FSInputFile(path)
                await message.answer_audio(audio, caption=f"🎵 {title}\n👤 @Argen_70")
                await m.delete()
                os.remove(path)
            else:
                await m.edit_text("Кечир, бул ыр базада табылган жок. Башка ыр жазып көр?")
        except Exception as e:
            await m.edit_text("Сервер убактылуу бош эмес. 1 мүнөттөн кийин кайра жазып көрчү?")

async def main():
    await start_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
