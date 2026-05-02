import os, asyncio
from aiogram import Bot, Dispatcher, types
import yt_dlp
from aiohttp import web

# Сенин токениң
TOKEN = "8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Render үчүн сервер
async def handle(request): return web.Response(text="Бот SoundCloud аркылуу иштеп жатат!")
async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', os.getenv('PORT', 10000))
    await site.start()

# SoundCloud'дан издөө жана жүктөө
def download_music(query):
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'music.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        # scsearch — бул SoundCloud'дан издөө дегенди билдирет
        info = ydl.extract_info(f"scsearch1:{query}", download=True)
        if 'entries' in info and len(info['entries']) > 0:
            entry = info['entries'][0]
            return "music.mp3", entry.get('title')
        return None, None

@dp.message()
async def search(message: types.Message):
    if message.text and message.text.lower().startswith("трек "):
        query = message.text.split(maxsplit=1)[1]
        m = await message.answer(f"☁️ SoundCloud'дан издеп жатам: {query}...")
        
        try:
            path, title = await asyncio.to_thread(download_music, query)
            if path and os.path.exists(path):
                audio = types.FSInputFile(path)
                await message.answer_audio(
                    audio, 
                    caption=f"🎵 {title}\n👤 @Argen_70", 
                    performer="@Argen_70",
                    title=title
                )
                await m.delete()
                os.remove(path)
            else:
                await m.edit_text("Кечир, бул ыр SoundCloud'та табылган жок.")
        except Exception as e:
            await m.edit_text(f"❌ Ката кетти: {str(e)[:50]}")

async def main():
    await start_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
