import sqlite3
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# --- ЖӨНДӨӨЛӨР ---
# Сиздин боттун токени
API_TOKEN = '8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM'
# Сиздин Телеграм ID (Админ)
ADMIN_ID = 7978591176  
# Сиздин МБанк номериңиз
MBANK_NUMBER = "+996 999906700" 

# Логдорду иштетүү (каталарды текшерүү үчүн)
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- МААЛЫМАТ БАЗАСЫ (SQLite) ---
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

# --- ПАЙДАЛАНУУЧУ ҮЧҮН БӨЛҮМ ---

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    # Колдонуучуну базага кошуу
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
    conn.commit()
    conn.close()
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("💰 Баланс толтуруу", "👤 Профиль")
    await message.answer(f"<b>Салам, {message.from_user.first_name}!</b>\n\nБул бот аркылуу балансыңызды толтуруп, кызматтарды колдонсоңуз болот.", 
                         reply_markup=keyboard, parse_mode="HTML")

@dp.message_handler(lambda message: message.text == "💰 Баланс толтуруу")
async def top_up_menu(message: types.Message):
    text = (
        "<b>💎 Упай алуу үчүн тарифтер:</b>\n\n"
        "• 100 сом ➡️ <b>300 упай</b>\n"
        "• 300 сом ➡️ <b>600 упай</b>\n"
        "• 500 сом ➡️ <b>1200 упай</b>\n"
        "• 1000 сом ➡️ <b>2300 упай</b>\n\n"
        f"💳 <b>МБанк номер:</b> <code>{MBANK_NUMBER}</code>\n"
        "(Номерди бассаңыз автоматтык түрдө көчүрүлөт)\n\n"
        "⚠️ <b>Нускама:</b> Акча которгондон кийин, чекти (скриншот) ушул жерге жөнөтүңүз. "
        "Мен текшерип чыгып, упайларды балансыңызга кошом."
    )
    await message.answer(text, parse_mode="HTML")

@dp.message_handler(lambda message: message.text == "👤 Профиль")
async def profile(message: types.Message):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (message.from_user.id,))
    res = cursor.fetchone()
    conn.close()
    
    balance = res[0] if res else 0
    await message.answer(f"👤 <b>Сиздин профилиңиз:</b>\n\n"
                         f"🆔 ID: <code>{message.from_user.id}</code>\n"
                         f"💰 Баланс: <b>{balance} упай</b>", parse_mode="HTML")

# --- СҮРӨТТҮ (ЧЕКТИ) КАБЫЛ АЛУУ ЖАНА АДМИНГЕ ЖӨНӨТҮҮ ---

@dp.message_handler(content_types=['photo'])
async def handle_receipt(message: types.Message):
    # Колдонуучуга кабар берүү
    await message.answer("✅ Чек кабыл алынды! Мен текшерип чыкканча бир аз күтө туруңуз. ⏳")
    
    # Админ (сиз) үчүн баскычтар
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("✅ 100с (300у)", callback_data=f"pay_{message.from_user.id}_300"),
        types.InlineKeyboardButton("✅ 300с (600у)", callback_data=f"pay_{message.from_user.id}_600"),
        types.InlineKeyboardButton("✅ 500с (1200у)", callback_data=f"pay_{message.from_user.id}_1200"),
        types.InlineKeyboardButton("✅ 1000с (2300у)", callback_data=f"pay_{message.from_user.id}_2300"),
        types.InlineKeyboardButton("❌ Четке кагуу", callback_data=f"pay_{message.from_user.id}_0")
    )
    
    # Сизге сүрөттү баскычтар менен жиберүү
    await bot.send_photo(
        ADMIN_ID, 
        photo=message.photo[-1].file_id, 
        caption=f"🔔 <b>Жаңы төлөм!</b>\n\n👤 Аты: {message.from_user.full_name}\n🆔 ID: <code>{message.from_user.id}</code>\n🔗 Юзернейм: @{message.from_user.username}",
        reply_markup=kb,
        parse_mode="HTML"
    )

# --- АДМИН БАСКЫЧТЫ БАСКАНДАГЫ ЛОГИКА ---

@dp.callback_query_handler(lambda c: c.data.startswith('pay_'))
async def process_callback(callback_query: types.CallbackQuery):
    # callback_data'дан маалыматты алуу
    _, user_id, amount = callback_query.data.split('_')
    user_id, amount = int(user_id), int(amount)

    if amount > 0:
        # Базада балансты жаңыртуу
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()
        conn.close()
        
        # Колдонуучуга сүйүнчү
        await bot.send_message(user_id, f"🌟 <b>Төлөмүңүз ырасталды!</b>\n\nБалансыңызга <b>+{amount} упай</b> кошулду. Рахмат!", parse_mode="HTML")
        # Сиздин чатыңыздагы билдирүүнү өзгөртүү
        await callback_query.message.edit_caption(caption=f"✅ <b>Ырасталды!</b>\nКолдонуучуга {amount} упай берилди.", parse_mode="HTML")
    else:
        # Төлөм четке кагылса
        await bot.send_message(user_id, "❌ Кечириңиз, сиздин төлөмүңүз текшерүүдөн өткөн жок. Скриншотту же сумманы кайра текшериңиз.")
        await callback_query.message.edit_caption(caption="❌ <b>Төлөм четке кагылды.</b>", parse_mode="HTML")
    
    await callback_query.answer()

if __name__ == '__main__':
    init_db() # Базаны ишке киргизүү
    executor.start_polling(dp, skip_updates=True)
