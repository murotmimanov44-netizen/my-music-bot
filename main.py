import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio, HighQualityVideo
import yt_dlp
--- СЕНИН МААЛЫМАТТАРЫҢ ---
API_ID = 36507092
API_HASH = "10e840d07af74d2882b11de01394d308"
BOT_TOKEN = "8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM"
app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)
@app.on_message(filters.command("argen") & filters.group)
async def play_func(client, message):
if len(message.command) < 2:
return await message.reply("🎙️ Ырдын же видеонун атын жазыңыз!")
query = " ".join(message.command[1:])
status = await message.reply("🚀 Издеп жатам...")
ydl_opts = {'format': 'best[height<=720]', 'quiet': True}
try:
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
info = ydl.extract_info(f"ytsearch1:{query}", download=False)
url = info['entries'][0]['url']
title = info['entries'][0]['title']
await call_py.join_group_call(
message.chat.id,
AudioVideoPiped(
url,
HighQualityAudio(),
HighQualityVideo()
)
)
await status.edit(f"🎬 Азыр ойноп жатат: {title}")
except Exception as e:
await status.edit(f"❌ Ката: Видеочат күйгөнүн текшериңиз!")
@app.on_message(filters.command("pause") & filters.group)
async def pause_func(client, message):
await call_py.pause_stream(message.chat.id)
await message.reply("⏸️ Паузага коюлду.")
@app.on_message(filters.command("resume") & filters.group)
async def resume_func(client, message):
await call_py.resume_stream(message.chat.id)
await message.reply("▶️ Кайра улантылды.")
@app.on_message(filters.command("stop") & filters.group)
async def stop_func(client, message):
await call_py.leave_group_call(message.chat.id)
await message.reply("⏹️ Бот токтотулду жана чыгып кетти.")
@app.on_message(filters.command("skip") & filters.group)
async def skip_func(client, message):
await call_py.leave_group_call(message.chat.id)
await message.reply("⏭️ Өткөрүлдү (Токтотулду).")
async def main():
await app.start()
await call_py.start()
await asyncio.Idle()
if name == "main":
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
