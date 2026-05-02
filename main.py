import os
import asyncio
from aiogram import Bot, Dispatcher, types
import yt_dlp

TOKEN = "8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM"
bot = Bot(token=TOKEN)
dp = Dispatcher()

def download_music(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'music.%(ext)s',
        'writethumbnail': True, # Сүрөтүн кошо алуу
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'},
            {'key': 'EmbedThumbnail'}, # Сүрөттү файлдын ичине киргизүү
            {'key': 'FFmpegMetadata'}, # Метаберилиштерди кошуу
        ],
        'quiet': True,
        'noplaylist': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=True)['entries'][0]
        return "music.mp3", info.get('title', 'Unknown')

@dp.message()
async def handle_message(message: types.Message):
    if message.text and (message.text.lower().startswith("w") or message.text.lower().startswith("ыр")):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2: return
        
        query = parts[1]
        wait_msg = await message.answer("🚀 Оригинал сапатта издеп жатам...")
        
        try:
            file_path, title = await asyncio.to_thread(download_music, query)
            audio = types.FSInputFile(file_path)
            
            await message.answer_audio(
                audio, 
                caption=f"🎵 {title}\n👤 Жүктөдү: @Argen_70",
                performer="@Argen_70",
                title=title
            )
            await wait_msg.delete()
            if os.path.exists(file_path): os.remove(file_path)
        except Exception as e:
            await wait_msg.edit_text("Ыр табылган жок. Башкачараак жазып көр?")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
