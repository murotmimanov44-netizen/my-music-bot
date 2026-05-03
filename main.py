import os
import threading
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, URLInputFile
from sclib import SoundcloudAPI

# ТОКЕНИҢ
API_TOKEN = '8576931278:AAECIYTCR9k81pnLy7A8R-xFjeYfgU3KEqo'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
api = SoundcloudAPI()

# Render үчүн веб-сервер (өчүрүп салбашы үчүн)
class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), WebServer)
    server.serve_forever()

@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer("Салам! Бот иштеди. Ырдын атын жаз.")

@dp.message()
async def search(message: Message):
    query = message.text
    msg = await message.answer(f"🔎 Издеп жатам: {query}")
    try:
        tracks = api.search_tracks(query)
        if tracks:
            track = tracks[0]
            url = track.get_stream_url()
            audio = URLInputFile(url, filename=f"{track.title}.mp3")
            await message.answer_audio(audio=audio, title=track.title)
            await msg.delete()
        else:
            await msg.edit_text("Табылбады.")
    except Exception:
        await msg.edit_text("Ката кетти.")

async def main():
    threading.Thread(target=run_server, daemon=True).start()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
  
