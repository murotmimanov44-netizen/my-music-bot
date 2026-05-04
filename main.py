import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from pytgcalls.types.stream import StreamArgument # dev21 үчүн керек болушу мүмкүн
from yt_dlp import YoutubeDL

# --- МААЛЫМАТТАР ---
API_ID = 1234567  # my.telegram.org сайтынан алыңыз
API_HASH = "your_api_hash"
BOT_TOKEN = "7233777085:AAFq4B6Z8jGZ3uYn_Q88xIe2p1Y9t3_v0k4"
SESSION = "СИЗДИН_STRING_SESSION" 

app = Client("MusicBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_app = Client("UserBot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
call_py = PyTgCalls(user_app)

buttons = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("⏸ Стоп", callback_data="pause"),
        InlineKeyboardButton("▶️ Улантуу", callback_data="resume"),
        InlineKeyboardButton("⏹ Өчүрүү", callback_data="stop")
    ]
])

@app.on_message(filters.command("play") & filters.group)
async def play_video(client, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("🎥 Видео же ырдын атын жазыңыз!")

    m = await message.reply("🎬 Издөөдө...")

    ydl_opts = {"format": "best[height<=480]", "quiet": True}
    
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            url = info['url']
            title = info['title']
            thumb = info['thumbnail']
        except Exception as e:
            return await m.edit(f"❌ Ката: {e}")

    # Сен айткан MediaStream бөлүгү кошулду:
    try:
        await call_py.play(
            message.chat.id,
            MediaStream(
                url, 
                video_flags=MediaStream.Flags.VIDEO
            )
        )
    except Exception as e:
        return await m.edit(f"❌ Видео чат катасы: {e}")

    await m.delete()
    await message.reply_photo(
        photo=thumb,
        caption=(
            f"🎶 <b>Түз эфирде:</b>\n{title}\n\n"
            f"👤 <b>Буйрутма:</b> {message.from_user.mention}\n\n"
            f"𝐊𝐆𝐙🇰🇬 𝐙𝐄𝐑𝐎"
        ),
        reply_markup=buttons
    )

if __name__ == "__main__":
    call_py.start()
    app.run()
  
