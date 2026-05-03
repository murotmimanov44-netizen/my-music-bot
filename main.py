import os
import threading
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, URLInputFile
from sclib import SoundcloudAPI

# 1. СЕНИН ТОКЕНИҢ (Ушул бойдон калсын)
API_TOKEN = '8576931278:AAECIYTCR9k81pnLy7A8R-xFjeYfgU3KEqo'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
api = SoundcloudAPI()

# 2. RENDER ҮЧҮН ЖАЛГАН ВЕБ-СЕРВЕР (Өчүрбөшү үчүн)
class FakeServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot is Live!")

def run_server():
    # Render берген портту же 8080ди колдонот
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), FakeServer)
    print(f"Веб-сервер {port} портунда иштеди...")
    server.serve_forever()

# 3. БОТТУН ФУНКЦИЯЛАРЫ
@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer("Арген, бот иштеди! Эми ырдын атын жазсаң болот.")

@dp.message()
async def search(message: Message):
    query = message.text
    msg = await message.answer(f"🔎 SoundCloud'дан издеп жатам: {query}")
    try:
        tracks = api.search_tracks(query)
        if tracks:
            track = tracks[0]
            stream_url = track.get_stream_url()
            audio = URLInputFile(stream_url, filename=f"{track.title}.mp3")
            await message.answer_audio(audio=audio, title=track.title)
            await msg.delete()
        else:
            await msg.edit_text("Эч нерсе таба алган жокмун.")
    except Exception as e:
        await msg.edit_text("Ката кетти. Кайра жазып көр.")

# 4. БААРЫН БИРГЕ ИШТЕТҮҮ
async def main():
    # Веб-серверди өзүнчө агымда баштайбыз
    threading.Thread(target=run_server, daemon=True).start()
    # Ботту иштетебиз
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
  
