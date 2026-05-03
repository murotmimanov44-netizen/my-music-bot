import os
import logging
import random
from aiogram import Bot, Dispatcher, types, executor
from yt_dlp import YoutubeDL
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- ЖӨНДӨӨЛӨР ---
TOKEN = '8646126657:AAFA0q1Mjv5dDsxiDyId8MDaLeTQgSkZvgs'
MY_NICK = "@Argen_70"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Render үчүн жасалма веб-сервер (Өчүп калбашы үчүн)
def run_dummy_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Music Bot is running!")
    port = int(os.environ.get("PORT", 8080))
    httpd = HTTPServer(('', port), Handler)
    httpd.serve_forever()

# Музыка жүктөө жөндөөлөрү (320kbps сапат)
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
    }],
    'quiet': True,
    'noplaylist': True
}

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(f"🎵 Салам! Музыка издөө үчүн **трек [ырдын аты]** деп жазыңыз.\n\n👤 Автор: {MY_NICK}")

@dp.message_handler(lambda message: message.text.lower().startswith('трек'))
async def search_track(message: types.Message):
    query = message.text[4:].strip()
    if not query:
        await message.answer("⚠️ Сураныч, ырдын атын жазыңыз! Мисалы: `трек Самара`")
        return

    status_msg = await message.answer("🔎 **Оригинал трек табылды, оюн даярдалууда...**")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
            title = info.get('title', 'music')
            file_path = ydl.prepare_filename(info).rsplit('.', 1)[0] + ".mp3"
            
            # --- ОЮН БӨЛҮМҮ ---
            luck = random.randint(1, 100)
            game_text = f"🎰 **Сиздин бүгүнкү ийгилигиңиз:** {luck}%"
            
            await status_msg.edit_text("📤 **Файл жөнөтүлүүдө...**")
            
            with open(file_path, 'rb') as audio:
                await message.answer_audio(
                    audio, 
                    caption=f"🎵 **{title}**\n\n{game_text}\n\n👤 Издөөчү: {MY_NICK}",
                    performer=MY_NICK
                )
            
            await status_msg.delete()
            if os.path.exists(file_path): os.remove(file_path)

    except Exception as e:
        logging.error(e)
        await status_msg.edit_text("❌ Кечириңиз, музыка табылган жок.")

if __name__ == '__main__':
    if not os.path.exists('downloads'): os.makedirs('downloads')
    
    # Портту өзүнчө агымда иштетүү
    Thread(target=run_dummy_server, daemon=True).start()
    
    print("Бот иштеп жатат...")
    executor.start_polling(dp, skip_updates=True)
      
