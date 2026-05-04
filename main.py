import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Сиздин боттун токени
API_TOKEN = '7233777085:AAFq4B6Z8jGZ3uYn_Q88xIe2p1Y9t3_v0k4'

# Логдорду жөндөө
logging.basicConfig(level=logging.INFO)

# Бот жана диспетчер
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# 1. Жаңы адам киргенде саламдашуу жана сизди (@Argen_70) белгилөө
@dp.message_handler(content_types=[types.ContentType.NEW_CHAT_MEMBERS])
async def welcome_new_member(message: types.Message):
    for new_member in message.new_chat_members:
        first_name = new_member.first_name
        # Текст жана "KGZ ZERO" кол тамгасы
        welcome_text = (
            f"Салам, {first_name}! 👋\n\n"
            f"Сураныч, топко адам кошуп бере аласызбы? 🙏\n"
            f"Же болбосо админ болгуңуз келсе, владелец Аргенге жазыңыз: @Argen_70\n\n"
            f"𝐊𝐆𝐙🇰🇬 𝐙𝐄𝐑𝐎"
        )
        await message.reply(welcome_text)

# 2. "Админ" командасы - бардык админдерди белгилейт
@dp.message_handler(lambda message: message.text.lower() == "админ")
async def tag_admins(message: types.Message):
    # Топтогу администраторлорду алуу
    admins = await message.chat.get_administrators()
    
    admin_mentions = []
    for admin in admins:
        if not admin.user.is_bot:
            # Админдердин атын шилтеме катары даярдоо
            mention = admin.user.get_mention(as_html=True)
            admin_mentions.append(mention)
    
    if admin_mentions:
        response = "🆘 <b>Чакырылган администраторлор:</b>\n" + ", ".join(admin_mentions)
        await message.reply(response, parse_mode='HTML')

if __name__ == '__main__':
    # Ботту ишке киргизүү
    executor.start_polling(dp, skip_updates=True)
  
