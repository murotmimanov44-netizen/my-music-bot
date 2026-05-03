import asyncio
import random
import sqlite3
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, LabeledPrice, PreCheckoutQuery, SuccessfulPayment

# --- КОНФИГУРАЦИЯ ---
API_TOKEN = '8608898907:AAEITJNP6t-s2CiT3b7nCCSX9rGPFF5fmlU'
ADMIN_ID = 504020300 # Өзүңдүн ID-ңди жаз

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
game_logs = [] # Лог үчүн тизме

# --- БАЗА МЕНЕН ИШТӨӨ ---
def init_db():
    conn = sqlite3.connect('casino.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 5000)')
    conn.commit()
    conn.close()

def get_balance(user_id):
    conn = sqlite3.connect('casino.db')
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    res = cursor.fetchone()
    if not res:
        cursor.execute('INSERT INTO users (user_id, balance) VALUES (?, 5000)', (user_id,))
        conn.commit()
        res = (5000,)
    conn.close()
    return res[0]

def update_balance(user_id, amount):
    conn = sqlite3.connect('casino.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
    conn.commit()
    conn.close()

# --- БАЛАНС (б) ---
@dp.message(F.text.lower() == "б")
async def check_balance(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name.upper()
    bal = get_balance(user_id)
    display_bal = f"{bal:,}".replace(",", ".")
    await message.answer(f"⚔️ **KR** / **{name}**\nМонеты: {display_bal} 🌚")

# --- РУЛЕТКА (ВИДЕОДОГУДАЙ GIF МЕНЕН) ---
@dp.message(F.text.lower() == "го")
async def roulette_spin(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name.upper()
    
    if get_balance(user_id) < 1000:
        return await message.answer("❌ Недостаточно монет (1000)!")

    update_balance(user_id, -1000) # Ставканы кемитүү
    
    # Видеодогудай анимация
    msg = await message.answer_animation(
        animation="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJicnJicnJicnJicnJicnJicnJicnJicnJicnJicnJicnJicnJpZz1m/3o7TKVUn7iM8FMEU24/giphy.gif",
        caption=f"⚔️ **KR** / **{name}**\nСтавка принята: 1000 на Зеро 💚"
    )
    
    await asyncio.sleep(3)
    
    num = random.randint(0, 12)
    col_emoji = "🔴" if num in [1,3,5,7,9,11] else "⚫" if num != 0 else "🟢"
    col_name = "Красное" if num in [1,3,5,7,9,11] else "Чёрное" if num != 0 else "Зеро"
    
    game_logs.append(f"{num} {col_emoji}") # Логко кошуу
    
    win_amt = 2000 if num != 0 else 10000 # Жөнөкөй утуш логикасы
    if num == 0: update_balance(user_id, win_amt)
    
    await message.answer(f"🎰 Рулетка: {num} {col_emoji}\n⚔️ **KR** / **{name}** результат: {num} {col_name} 🔥")

# --- БАНДИТ (RDNO СТИЛИНДЕ) ---
@dp.message(F.text.lower() == "бандит")
async def bandit_game(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name.upper()
    
    if get_balance(user_id) < 1000:
        return await message.answer("❌ Недостаточно монет!")

    update_balance(user_id, -1000)
    
    msg = await message.answer(f"⚔️ **KR** / **{name}**\n\n▒ ▒ ▒ ▒")
    symbols = ["💎", "🍒", "🍋", "🔔", "⭐", "🍀"]
    
    for _ in range(3):
        temp = "".join(random.choices(symbols, k=4))
        await msg.edit_text(f"⚔️ **KR** / **{name}**\n\n{temp}")
        await asyncio.sleep(0.5)

    final = random.choices(symbols, k=4)
    win = 5000 if len(set(final)) == 1 else 2000 if len(set(final)) == 2 else 0
    update_balance(user_id, win)
    
    res = f"Выигрыш: {win}" if win > 0 else "Проигрыш: 1000"
    await msg.edit_text(f"⚔️ **KR** / **{name}**\n\n{''.join(final)}\n\n**{res}** 🌚")

# --- ЛОГ ---
@dp.message(F.text.lower() == "лог")
async def show_log(message: types.Message):
    if not game_logs:
        return await message.answer("📜 Игр еще не было.")
    text = "📜 **Последние игры:**\n\n" + "\n".join(game_logs[-10:])
    await message.answer(text, parse_mode="Markdown")

# --- БАШКА МЕНЮЛАР ---
@dp.message(F.text == "/start")
async def start(m: types.Message):
    init_db()
    kb = [
        [KeyboardButton(text="🎁 Бонус"), KeyboardButton(text="💰 Пополнить баланс")],
        [KeyboardButton(text="❓ Помощь"), KeyboardButton(text="🔗 Ссылки")]
    ]
    await m.answer("👋 Добро пожаловать!", reply_markup=ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True))

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
                      
