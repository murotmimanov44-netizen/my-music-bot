import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from yt_dlp import YoutubeDL
from pyrogram import idle

# Сенин жаңы токениң жана API маалыматтарың
API_ID = 26500416
API_HASH = "815615f79119c968940e4f215e966835"
BOT_TOKEN = "8565294339:AAGUssz0u8u2yJzmLXw8t8TDfJj8hjduHDM"

app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

# yt-dlp жөндөөлөрү
ydl_opts = {
    "format": "bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "default_search": "ytsearch",
    "nocheckcertificate": True,
}

@app.on_message(filters.command("play") & filters.group)
async def play_music(client, message):
    if len(message.command) < 2:
        return await message.reply("🎵 Ырдын атын же шилтемесин жаз! Мисалы: `/play Phonk`")
    
    query = " ".join(message.command[1:])
    m = await message.reply("🔍 Издеп жатам...")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)['entries'][0]
            url = info['url']
            title = info['title']

        await call_py.play(
            message.chat.id,
            AudioPiped(url)
        )
        await m.edit(f"🎶 Ойноп жатат: **{title}**")
    except Exception as e:
        await m.edit(f"❌ Ката кетти: {str(e)}")

async def start_bot():
    await app.start()
    await call_py.start()
    print("✅ Бот ийгиликтүү иштеди!")
    await idle()
    await app.stop()

if __name__ == "__main__":
    # Render'деги 'RuntimeError: no running event loop' катасын ушул сап чечет
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
  
