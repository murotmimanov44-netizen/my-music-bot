import os
from pyrogram import Client, filters
from yt_dlp import YoutubeDL
from flask import Flask
from threading import Thread

# Render үчүн сервер
web = Flask('')
@web.route('/')
def home(): return "Бот иштеп жатат!"
def run(): web.run(host='0.0.0.0', port=8080)

# --- ЖӨНДӨӨЛӨР ---
API_ID = 21453678 
API_HASH = "b456e7f8901234567890abcd12345678" 
BOT_TOKEN = "8565294339:AAGUssz0u8u2yJzmLXw8t8TDfJj8hjduHDM"

app = Client("music_downloader", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Youtube'дан жүктөө жөндөөлөрү
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': True,
}

@app.on_message(filters.text & filters.group)
async def download_track(client, message):
    # Колдонуучу "трек [ырдын аты]" деп жазганда гана иштейт
    if message.text.lower().startswith("трек"):
        query = message.text.replace("трек", "").strip()
        
        if not query:
            return await message.reply("Ырдын атын жазыңыз. Мисалы: `трек Phonk`")

        m = await message.reply(f"🔎 **{query}** издеп жатам...")

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
                file_name = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
                title = info['title']

            # Файлды жөнөтүү
            await message.reply_audio(
                audio=file_name,
                caption=f"🎶 трек {title}\n\n𝐊𝐆𝐙🇰🇬 𝐙𝐄𝐑𝐎\n👤 @Argen_70"
            )
            
            # Жүктөлгөн файлды серверден тазалоо
            await m.delete()
            if os.path.exists(file_name):
                os.remove(file_name)

        except Exception as e:
            await m.edit(f"❌ Ката кетти: {e}")

if __name__ == "__main__":
    Thread(target=run).start()
    print("Бот файл жөнөтүүгө даяр...")
    app.run()
  
