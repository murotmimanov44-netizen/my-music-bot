import sqlite3
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# --- ЖӨНДӨӨЛӨР ---
# Сиз берген токенди бул жерге коштум
API_TOKEN = '8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM'
ADMIN_ID = 7978591176  # Сиздин Телеграм ID номериңиз
MBANK_NUMBER = "+996 XXX XX XX XX" # Бул жерге МБанк номериңизди жазып коюңуз

# Логдорду иштетүү (каталарды көрүү үчүн)
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

# --- ПАЙДАЛАНУУЧУ ҮЧҮН ФУНКЦИЯЛАР ---

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
        f"💳 <b>МБанк номер:</b> <code>{MBANK_NUMBER}</code>\n"
        "(Номерди басса
