import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from yt_dlp import YoutubeDL

# --- МААЛЫМАТТАР ---
API_ID = 23908868  # Өзүңдүн API_ID'ни жаз
API_HASH = "сенин_api_hash_бул_жерде"
BOT_TOKEN = "7233777085:AAFq4B6Z8jGZ3uYn_Q88xIe2p1Y9t3_v0k4"
SESSION = "10e840d07af74d2882b11de01394d30836507092" 

app = Client("MusicBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_app = Client("UserBot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
call_py = PyTgCalls(user_app)

@app.on_message(filters.command("play") & filters.group)
async def play_music(client, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("🎥 Издөө үчүн атты жазыңыз!")

    m = await message.reply("🎬 Издөөдө...")
    
    ydl_opts = {"format": "bestaudio", "quiet": True}
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            url = info['url']
            title = info['title']
        except Exception as e:
            return await m.edit(f"❌ YouTube катасы: {e}")

    try:
        # pytgcalls 3.0.0.dev24 үчүн иштөө ыкмасы
        await call_py.play(message.chat.id, MediaStream(url))
        await m.edit(f"🎶 <b>Ойноп жатат:</b>\n{title}\n\n👤 Буйрутма: {message.from_user.mention}")
    except Exception as e:
        await m.edit(f"❌ Ката: {e}")

async def main():
    await app.start()
    await user_app.start()
    await call_py.start()
    print("✅ Бот ийгиликтүү ишке кирди!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
  
