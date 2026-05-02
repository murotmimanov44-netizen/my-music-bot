import os, asyncio, re
from aiogram import Bot, Dispatcher, types
import yt_dlp
from aiohttp import web

TOKEN = "8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM"
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def handle(request): return web.Response(text="Бот 100% так иштеп жатат!")
async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', os.getenv('PORT', 10000))
    await site.start()

def download_music(query):
    # Биз бир эле учурда 5 жыйынтык сурайбыз, анан ичинен эң туурасын тандайбыз
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch5', # 5 видеону текшеребиз
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
            # "Official Audio" же "Official Video" дегендерге артыкчылык беребиз
            info = ydl.extract_info(f"{query}", download=False)
            if 'entries' in info:
                best_match = None
                # Издөөдөгү ар бир ырды текшерип чыгабыз
                for entry in info['entries']:
                    title = entry.get('title', '').lower()
                    uploader = entry.get('uploader', '').lower()
                    q_lower = query.lower()
                    
                    # Эгер ырдын атында же автордун атында сен жазган сөз болсо - бул бизге керек!
                    if any(word in title or word in uploader for word in q_lower.split()):
                        best_match = entry
                        break
                
                if not best_match:
                    best_match = info['entries'][0] # Эгер эч нерсе окшобосо, биринчисин алабыз
                
                # Тандалган ырды жүктөп алуу
                actual_info = ydl.extract_info(best_match['webpage_url'], download=True)
                filename = ydl.prepare_filename(actual_info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
                return filename, actual_info.get('title'), actual_info.get('uploader')
        except:
            return None, None, None

@dp.message()
async def search(message: types.Message):
    if message.text and message.text.lower().startswith("трек "):
        query = message.text.split(maxsplit=1)[1]
        m = await message.answer(f"🎯 Так издеп жатам: {query}...")
        
        try:
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
                await m.edit_text("❌ Кечир, так ушул ыр табылган жок. Автордун атын кошуп жазып көрчү?")
        except Exception as e:
            await m.edit_text("Ката кетти. Кайра аракет кылып көр.")

async def main():
    await start_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
              
