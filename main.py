import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import aiohttp

# --- ЖӨНДӨӨЛӨР ---
# Бул жерге BotFather'ден алган токениңди жаз
API_TOKEN = 'СЕНИН_ТЕЛЕГРАМ_БОТ_ТОКЕНИҢ'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# Deezer'ден издөө функциясы
async def search_deezer(track_name):
    url = f"https://api.deezer.com/search?q={track_name}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data['data']:
                    return data['data'][0] # Эң биринчи жыйынтык
            return None

# "трек" же "ыр" деп башталган билдирүүлөрдү кармоо
@dp.message_handler(lambda message: message.text and message.text.lower().startswith(('трек', 'ыр')))
async def find_track(message: types.Message):
    # Командадан кийинки текстти (ырдын атын) алуу
    query = message.text.split(maxsplit=1)
    
    if len(query) < 2:
        await message.reply("Ырдын атын жазыңыз. Мисалы: \n`трек Come In` же \n`ыр Кутман таң`", parse_mode='Markdown')
        return

    song_name = query[1]
    await message.answer(f"🔎 <b>{song_name}</b> издеп жатам...")

    result = await search_deezer(song_name)

    if result:
        title = result['title']
        artist = result['artist']['name']
        preview_url = result['preview']  # 30 секунддук үлгүсү
        link = result['link']           # Deezer'деги шилтемеси
        album_cover = result['album']['cover_big'] # Музыканын сүрөтү

        caption = f"🎶 <b>{artist} — {title}</b>\n\n[Deezer'де угуу]({link})"
        
        # Колдонуучуга 30 сек аудиону жана маалыматты жөнөтүү
        try:
            await bot.send_audio(
                message.chat.id, 
                audio=preview_url, 
                caption=caption, 
                parse_mode='HTML',
                title=title,
                performer=artist,
                thumb=album_cover
            )
        except Exception as e:
            await message.reply(f"Ката кетти: {e}")
    else:
        await message.reply("Тилекке каршы, мындай ыр табылган жок. Башкача жазып көрүңүз.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
  
