import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityVideo, HighQualityAudio
from yt_dlp import YoutubeDL

# Сиздин маалыматтар
API_ID = 1234567  # my.telegram.org сайтынан аласыз
API_HASH = "your_api_hash"
BOT_TOKEN = "7233777085:AAFq4B6Z8jGZ3uYn_Q88xIe2p1Y9t3_v0k4"

app = Client("VideoMusicBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

# Плеердин баскычтары
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
        return await message.reply("Видео же ырдын атын жазыңыз!")

    m = await message.reply("🎬 Видео изделүүдө...")

    # YouTube'дан видеону издөө
    ydl_opts = {"format": "best[height<=720]", "quiet": True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        url = info['url']
        title = info['title']
        thumb = info['thumbnail']

    # Видео чатка кошулуу
    await call_py.join_group_call(
        message.chat.id,
        AudioVideoPiped(url, HighQualityAudio(), HighQualityVideo())
    )

    await m.delete()
    await message.reply_photo(
        photo=thumb,
        caption=f"🎥 <b>Түз эфирде ойнолууда:</b>\n{title}\n\n👤 <b>Буйрутма берди:</b> {message.from_user.mention}\n\n𝐊𝐆𝐙🇰🇬 𝐙𝐄𝐑𝐎",
        reply_markup=buttons
    )

# Ботту ишке киргизүү
app.run()
