import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from yt_dlp import YoutubeDL

# Керектүү класстарды динамикалык түрдө импорттоо
try:
    from pytgcalls.types import MediaStream
except ImportError:
    # Эски версиялар үчүн
    from pytgcalls.types.input_stream import AudioVideoPiped as MediaStream

# --- МААЛЫМАТТАР ---
# Эскертүү: Бул жерге өзүңдүн API_ID жана API_HASH маалыматтарыңды жаз
API_ID = 23908868 
API_HASH = "your_api_hash_here"
BOT_TOKEN = "7233777085:AAFq4B6Z8jGZ3uYn_Q88xIe2p1Y9t3_v0k4"
SESSION = "СИЗДИН_STRING_SESSION" 

# Клиенттерди түзүү
app = Client("MusicBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_app = Client("UserBot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
call_py = PyTgCalls(user_app)

# Башкаруу баскычтары
buttons = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("⏸ Пауза", callback_data="pause"),
        InlineKeyboardButton("▶️ Улантуу", callback_data="resume"),
        InlineKeyboardButton("⏹ Токтотуу", callback_data="stop")
    ]
])

@app.on_message(filters.command("play") & filters.group)
async def play_video(client, message):
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply("🎥 Видео же ырдын атын жазыңыз! Мисалы: `/play Phonk`")

    m = await message.reply("🎬 Издөөдө...")
    
    # YouTube'дан видео издөө (480p формат серверге жеңил болот)
    ydl_opts = {"format": "best[height<=480]", "quiet": True}
    
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            url = info['url']
            title = info['title']
            thumb = info['thumbnail']
        except Exception as e:
            return await m.edit(f"❌ YouTube катасы: {e}")

    try:
        # Универсалдуу ойнотуу (жаңы жана эски версиялар үчүн)
        try:
            await call_py.play(message.chat.id, MediaStream(url))
        except:
            # Эгер .play() иштебесе, .join_group_call() колдонулат
            await call_py.join_group_call(message.chat.id, MediaStream(url))
            
    except Exception as e:
        return await m.edit(f"❌ Видео чат катасы: {e}. Бот же UserBot админ экенин текшериңиз.")

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

# Ботту ишке киргизүү
if __name__ == "__main__":
    call_py.start()
    app.run()
  
