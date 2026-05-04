import os
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioVideoPiped
from yt_dlp import YoutubeDL

# --- МААЛЫМАТТАР ---
API_ID = 23908868 
API_HASH = "сенин_api_hash"
BOT_TOKEN = "7233777085:AAFq4B6Z8jGZ3uYn_Q88xIe2p1Y9t3_v0k4"
SESSION = "СИЗДИН_STRING_SESSION"

app = Client("MusicBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_app = Client("UserBot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
call_py = PyTgCalls(user_app)

@app.on_message(filters.command("play") & filters.group)
async def play(client, message):
    query = " ".join(message.command[1:])
    m = await message.reply("🔎 Изделүүдө...")
    
    ydl_opts = {"format": "bestaudio", "quiet": True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        url = info['url']
        title = info['title']

    await call_py.join_group_call(
        message.chat.id,
        AudioVideoPiped(url)
    )
    await m.edit(f"▶️ Ойноп жатат: **{title}**")

if __name__ == "__main__":
    call_py.start()
    app.run()
  
