import asyncio
import sqlite3
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# --- ЖӨНДӨӨЛӨР ---
TOKEN = '8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM'
ADMIN_ID = 7978591176  
MBANK_NUMBER = "+996 999906700" 

# Кызматтар
SERVICES = {
    "inst_subs": {"name": "Instagram Катталуучулар", "price": 50},
    "inst_likes": {"name": "Instagram Лайктар", "price": 20},
    "tt_views": {"name": "TikTok Көрүүлөр", "price": 10},
}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- МААЛЫМАТ БАЗАСЫ ---
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0)')
    conn.commit()
    conn.close()

# --- МЕНЮЛАР ---
@dp.message(Command("start"))
async def start(message: types.Message):
    init_db()
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
    conn.commit()
    conn.close()
    
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🚀 Накрутка буйрутма")],
        [KeyboardButton(text="💰 Баланс толтуруу"), KeyboardButton(text="👤 Профиль")]
    ], resize_keyboard=True)
    await message.answer(f"Салам, {message.from_user.first_name}! Накрутка боту даяр.", reply_markup=kb)

@dp.message(F.text == "👤 Профиль")
async def profile(message: types.Message):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (message.from_user.id,))
    res = cursor.fetchone()
    balance = res[0] if res else 0
    conn.close()
    await message.answer(f"🆔 ID: {message.from_user.id}\n💰 Баланс: {balance} сом")

@dp.message(F.text == "💰 Баланс толтуруу")
async def top_up(message: types.Message):
    await message.answer(f"💳 <b>МБанк:</b> <code>{MBANK_NUMBER}</code>\n\nАкча которуп, чекти (скриншот) жөнөтүңүз.", parse_mode="HTML")

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await message.answer("✅ Чек кабыл алынды! Админ текшерүүдө...")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ 100с", callback_data=f"pay_{message.from_user.id}_100"),
         InlineKeyboardButton(text="✅ 300с", callback_data=f"pay_{message.from_user.id}_300")],
        [InlineKeyboardButton(text="✅ 500с", callback_data=f"pay_{message.from_user.id}_500"),
         InlineKeyboardButton(text="❌ Четке кагуу", callback_data=f"pay_{message.from_user.id}_0")]
    ])
    await bot.send_photo(ADMIN_ID, photo=message.photo[-1].file_
