import os
import asyncio
from aiogram import Bot, Dispatcher, types
import yt_dlp

# Сенин бот токениң кошулду
TOKEN = "8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Ыкчам жүктөө жөндөөлөрү
def download_music(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'music.%(ext)s',
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
        return "music.mp3", info.get('title', 'Unknown Track')

@dp.message()
async def handle_message(message: types.Message):
    # "трек" же "w" деп жазганда иштейт
    text = message.text.lower() if message.text else ""
    if text.startswith("трек") or text.startswith("w"):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("Ырдын атын жаз. Мисалы: w Кайрат Нуртас")
            return

        query = parts[1]
        wait_msg = await message.answer("Ырды издеп жатам... 🚀")
        
        try:
            # Ылдам издөө
            file_path, title = await asyncio.to_thread(download_music, query)
            audio = types.FSInputFile(file_path)
            
            # Файлды жөнөтүү
            await message.answer_audio(
                audio, 
                caption=f"✅ Даяр: {title}\n👤 Жүктөдү: @Argen_70",
                performer="@Argen_70",
                title=title
            )
            await wait_msg.delete()
            
            if os.path.exists(file_path):
                os.remove(file_path)
                
        except Exception as e:
            await wait_msg.edit_text("Ыр табылган жок. Башкачараак жазып көр?")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
