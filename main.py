import os
import asyncio
from aiogram import Bot, Dispatcher, types
import yt_dlp
from aiohttp import web

TOKEN = "8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Render өчүрүп салбашы үчүн веб-сервер
async def handle(request): return web.Response(text="Bot is Live!")
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
        'default_search': 'ytsearch',
        'quiet': True,
        'noplaylist': True,
        'nocheckcertificate': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Издөө 100% иштеши үчүн "ytsearch1:" колдонобуз
        search_result = ydl.extract_info(f"ytsearch1:{query}", download=True)
        if 'entries' in search_result and len(search_result['entries']) > 0:
            info = search_result['entries'][0]
            return "music.mp3", info.get('title', 'Unknown'), info.get('thumbnail')
        return None, None, None

@dp.message()
async def handle_message(message: types.Message):
    if not message.text: return
    cmd = message.text.lower()
    
    if cmd.startswith("w ") or cmd.startswith("ыр ") or cmd.startswith("трек "):
        query = message.text.split(maxsplit=1)[1]
        wait_msg = await message.answer(f"🔎 '{query}' издеп жатам...")
        
        try:
            file_path, title, thumb = await asyncio.to_thread(download_music, query)
            if file_path and os.path.exists(file_path):
                audio = types.FSInputFile(file_path)
                if thumb: await message.answer_photo(photo=thumb)
                await message.answer_audio(audio, caption=f"👤 @Argen_70", performer="@Argen_70", title=title)
                await wait_msg.delete()
                os.remove(file_path)
            else:
                await wait_msg.edit_text("Ыр табылган жок. Башкачараак жазып көр?")
        except Exception as e:
            await wait_msg.edit_text("Ката кетти. Кайра аракет кылып көр.")

async def main():
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
