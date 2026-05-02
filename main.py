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

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- БАЗА ---
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0)')
    conn.commit()
    conn.close()

# --- БОТ ЛОГИКАСЫ ---
@dp.message(Command("start"))
async def start(message: types.Message):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
    conn.commit()
    conn.close()
    
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="💰 Баланс толтуруу"), KeyboardButton(text="👤 Профиль")]
    ], resize_keyboard=True)
    await message.answer(f"Салам, {message.from_user.first_name}!", reply_markup=kb)

@dp.message(F.text == "💰 Баланс толтуруу")
async def top_up(message: types.Message):
    text = (
        "<b>💎 Тарифтер:</b>\n"
        "• 100 сом ➡️ 300 упай\n"
        "• 300 сом ➡️ 600 упай\n"
        "• 500 сом ➡️ 1200 упай\n"
        "• 1000 сом ➡️ 2300 упай\n\n"
        f"💳 МБанк: <code>{MBANK_NUMBER}</code>\n"
        "Чекти (скриншот) жөнөтүңүз."
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text == "👤 Профиль")
async def profile(message: types.Message):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (message.from_user.id,))
    res = cursor.fetchone()
    balance = res[0] if res else 0
    conn.close()
    await message.answer(f"ID: {message.from_user.id}\nБаланс: {balance} упай")

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    await message.answer("Чек кабыл алынды, күтө туруңуз... ⏳")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ 300у", callback_data=f"p_{message.from_user.id}_300"),
         InlineKeyboardButton(text="✅ 600у", callback_data=f"p_{message.from_user.id}_600")],
        [InlineKeyboardButton(text="✅ 1200у", callback_data=f"p_{message.from_user.id}_1200"),
         InlineKeyboardButton(text="✅ 2300у", callback_data=f"p_{message.from_user.id}_2300")],
        [InlineKeyboardButton(text="❌ Четке кагуу", callback_data=f"p_{message.from_user.id}_0")]
    ])
    await bot.send_photo(ADMIN_ID, photo=message.photo[-1].file_id, 
                         caption=f"Төлөм: {message.from_user.id}", reply_markup=kb)

@dp.callback_query(F.data.startswith("p_"))
async def process_pay(callback: types.CallbackQuery):
    _, user_id, amount = callback.data.split("_")
    user_id, amount = int(user_id), int(amount)
    
    if amount > 0:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()
        conn.close()
        await bot.send_message(user_id, f"Баланс толду: +{amount} упай! ✅")
        await callback.message.edit_caption(caption="✅ Ырасталды")
    else:
        await bot.send_message(user_id, "Төлөм четке кагылды. ❌")
        await callback.message.edit_caption(caption="❌ Четке кагылды")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
