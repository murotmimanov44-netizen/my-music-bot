import subprocess
import sys
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Китепканаларды мажбурлап орнотуу
def force_install():
    try:
        import aiogram
        import sclib
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiogram==3.4.1", "soundcloud-lib"])

force_install()

import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, URLInputFile
from sclib import SoundcloudAPI

# ТОКЕН
API_TOKEN = '8576931278:AAECIYTCR9k81pnLy7A8R-xFjeYfgU3KEqo'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
api = SoundcloudAPI()

# --- ВЕБ-СЕРВЕР (Render өчүрүп салбашы үчүн) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# ---------------------------------------------

@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer("Салам, Арген! Мен эми өчпөй иштейм. SoundCloud'дон музыка издейли. Ырдын атын жаз.")

@dp.message()
async def search_music(message: Message):
    query = message.text
    temp_msg = await message.answer(f"🔍 '{query}' издеп жатам...")
    try:
        tracks = api.search_tracks(query)
        if not tracks:
            await temp_msg.edit_text("Эч нерсе табылган жок.")
            return
        track = tracks[0]
        stream_url = track.get_stream_url()
        if stream_url:
            audio = URLInputFile(stream_url, filename=f"{track.title}.mp3")
            await message.answer_audio(audio=audio, title=track.title, caption=f"✅ {track.title}")
            await temp_msg.delete()
        else:
            await temp_msg.edit_text("Жүктөөгө мүмкүн болбоду.")
    except Exception as e:
        await temp_msg.edit_text("Ката кетти, кайра байкап көр.")

async def main():
    # Веб-серверди өзүнчө агымда (thread) баштоо
    threading.Thread(target=run_health_check, daemon=True).start()
    print("Бот жана Веб-сервер ишке кирди...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
