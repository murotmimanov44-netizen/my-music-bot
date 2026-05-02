import sqlite3
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# --- ЖӨНДӨӨЛӨР ---
API_TOKEN = '8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM'
ADMIN_ID = 7978591176  
MBANK_NUMBER = "+996 999906700" 

# Логдорду иштетүү
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- МААЛЫМАТ БАЗАСЫ ---
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
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
    conn.commit()
    conn.close()
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("💰 Баланс толтуруу", "👤 Профиль")
    await message.answer(f"<b>Салам, {message.from_user.first_name}!</b>\n\nТөмөнкү баскычтарды колдонуңуз:", 
                         reply_markup=keyboard, parse_mode="HTML")

@dp.message_handler(lambda message: message.text == "💰 Баланс толтуруу")
async def top_up_menu(message: types.Message):
    text = (
        "<b>💎 Упай алуу үчүн тарифтер:</b>\n\n"
        "• 100 сом ➡️ <b>300 упай</b>\n"
        "• 300 сом ➡️ <b>600 упай</b>\n"
        "• 500 сом ➡️ <b>1200 упай</b>\n"
        "• 1000 сом ➡️ <b>2300 упай</b>\n\n"
        f"💳 <b>МБанк номер:</b> <code>{MBANK_NUMBER}</code>\n\n"
        "⚠️ <b>Нускама:</b> Акча которгондон кийин, чекти (скриншот) жөнөтүңүз. "
        "Админ текшергенден кийин упайлар кошулат."
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
    await message.answer(f"👤 <b>Профиль:</b>\n\n🆔 ID: <code>{message.from_user.id}</code>\n💰 Баланс: <b>{balance} упай</b>", parse_mode="HTML")

# --- ЧЕКТИ КАБЫЛ АЛУУ ---

@dp.message_handler(content_types=['photo'])
async def handle_receipt(message: types.Message):
    await message.answer("✅ Чек кабыл алынды! Админ текшерип жатат... ⏳")
    
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("✅ 100с (300у)", callback_data=f"pay_{message.from_user.id}_300"),
        types.InlineKeyboardButton("✅ 300с (600у)", callback_data=f"pay_{message.from_user.id}_600"),
        types.InlineKeyboardButton("✅ 500с (1200у)", callback_data=f"pay_{message.from_user.id}_1200"),
        types.InlineKeyboardButton("✅ 1000с (2300у)", callback_data=f"pay_{message.from_user.id}_2300"),
        types.InlineKeyboardButton("❌ Четке кагуу", callback_data=f"pay_{message.from_user.id}_0")
    )
    
    await bot.send_photo(
        ADMIN_ID, 
        photo=message.photo[-1].file_id, 
        caption=f"🔔 <b>Төлөм:</b>\n👤 {message.from_user.full_name}\n🆔 <code>{message.from_user.id}</code>",
        reply_markup=kb,
        parse_mode="HTML"
    )

# --- АДМИНДИН ЫРАСТООСУ ---

@dp.callback_query_handler(lambda c: c.data.startswith('pay_'))
async def process_callback(callback_query: types.CallbackQuery):
    _, user_id, amount = callback_query.data.split('_')
    user_id, amount = int(user_id), int(amount)

    if amount > 0:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()
        conn.close()
        
        await bot.send_message(user_id, f"🌟 <b>Төлөм ырасталды!</b>\nБалансыңызга <b>+{amount} упай</b> кошулду.", parse_mode="HTML")
        await callback_query.message.edit_caption(caption=f"✅ Ырасталды: {amount} упай берилди.")
    else:
        await bot.send_message(user_id, "❌ Төлөмүңүз кабыл алынган жок.")
        await callback_query.message.edit_caption(caption="❌ Төлөм четке кагылды.")
    
    await callback_query.answer()

if __name__ == '__main__':
    init_db()
    executor.start_polling(dp, skip_updates=True)
