import os
import asyncio
from aiogram import Bot, Dispatcher, types
import yt_dlp
from aiohttp import web

# Сенин бот токениң
TOKEN = "8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Render үчүн жасалма веб-сервер (Бот өчүп калбашы үчүн)
async def handle(request):
    return web.Response(text="Бот иштеп жатат!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', os.getenv('PORT', 10000))
    await site.start()

def download_music(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'music.%(ext)s',
        'quiet': True,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=True)['entries'][0]
        return "music.mp3", info.get('title', 'Unknown'), info.get('thumbnail')

@dp.message()
async def handle_message(message: types.Message):
    if message.text and (message.text.lower().startswith("w") or message.text.lower().startswith("ыр")):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2: return
        query = parts[1]
        wait_msg = await message.answer("🚀 Издеп жатам...")
        try:
            file_path, title, thumb_url = await asyncio.to_thread(download_music, query)
            audio = types.FSInputFile(file_path)
            await message.answer_photo(photo=thumb_url, caption=f"🎵 {title}")
            await message.answer_audio(audio, caption=f"👤 @Argen_70", performer="@Argen_70", title=title)
            await wait_msg.delete()
            if os.path.exists(file_path): os.remove(file_path)
        except:
            await wait_msg.edit_text("Ыр табылган жок.")

async def main():
    # Веб-серверди жана ботту чогуу иштетүү
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
