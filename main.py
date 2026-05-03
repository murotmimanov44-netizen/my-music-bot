import asyncio
import random
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- КОНФИГУРАЦИЯ ---
API_TOKEN = '8608898907:AAEITJNP6t-s2CiT3b7nCCSX9rGPFF5fmlU'
ADMIN_ID = 504020300 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
game_logs = []

# --- БАЗА (Баланс туура иштеши үчүн) ---
def init_db():
    conn = sqlite3.connect('royal.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 5000)')
    conn.commit()
    conn.close()

def get_balance(user_id):
    conn = sqlite3.connect('royal.db')
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
    conn = sqlite3.connect('royal.db')
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
    formatted_bal = f"{bal:,}".replace(",", ".")
    await message.answer(f"**WTT·{name}**\nМонеты: {formatted_bal} 🌚", parse_mode="Markdown")

# --- РУЛЕТКА (Визуалдык меню) ---
@dp.message(F.text.lower() == "рулетка")
async def roulette_menu(message: types.Message):
    text = (
        "Минирулетка\nУгадайте число из:\n0🟢\n"
        "1🔴 2⚫ 3🔴 4⚫ 5🔴 6⚫\n7🔴 8⚫ 9🔴 10⚫ 11🔴 12⚫\n"
        "Ставки можно текстом:\n1000 на красное | 5000 на 12"
    )
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="1 - 3", callback_data="r_13"), types.InlineKeyboardButton(text="4 - 6", callback_data="r_46"), types.InlineKeyboardButton(text="7 - 9", callback_data="r_79"), types.InlineKeyboardButton(text="10 - 12", callback_data="r_1012"))
    builder.row(types.InlineKeyboardButton(text="1к на 🔴", callback_data="r_red"), types.InlineKeyboardButton(text="1к на ⚫", callback_data="r_black"), types.InlineKeyboardButton(text="1к на 0🟢", callback_data="r_zero"))
    builder.row(types.InlineKeyboardButton(text="Повторить", callback_data="r_again"), types.InlineKeyboardButton(text="Удвоить", callback_data="r_double"), types.InlineKeyboardButton(text="Крутить", callback_data="r_spin"))
    
    await message.answer(text, reply_markup=builder.as_markup())

# --- СТАВКА КАБЫЛ АЛУУ ---
@dp.message(F.text.regexp(r"(\d+)\s+(на)\s+(красное|черное|чёрное|0|зеро)"))
async def process_bet_text(message: types.Message):
    match = re.search(r"(\d+)\s+(на)\s+(красное|черное|чёрное|0|зеро)", message.text.lower())
    amount = int(match.group(1))
    target = match.group(3)
    name = message.from_user.first_name.upper()
    
    if get_balance(message.from_user.id) < amount:
        return await message.reply("❌ Недостаточно монет!")
        
    await message.answer(f"Ставка принята: `KR / {name}` {amount} монет на {target}", parse_mode="Markdown")

# --- РУЛЕТКА АНИМАЦИЯСЫ (ГО) ---
@dp.message(F.text.lower() == "го")
async def roulette_go(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name.upper()
    
    # Видеодогудай GIF анимация
    msg_gif = await message.answer_animation(
        animation="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJicnJicnJicnJicnJicnJicnJicnJicnJicnJicnJicnJicnJpZz1m/3o7TKVUn7iM8FMEU24/giphy.gif",
        caption=f"`KR / {name}` крутит (через 3 сек.)"
    )
    
    await asyncio.sleep(3)
    
    num = random.randint(0, 12)
    emoji = "🔴" if num in [1,3,5,7,9,11] else "⚫" if num != 0 else "🟢"
    game_logs.append(f"{num}{emoji}")
    
    await message.answer(f"Рулетка: {num} {emoji}\n`KR / {name}` результат: {num} {emoji} 🔥")

# --- БАНДИТ (1:1 АНИМАЦИЯ) ---
@dp.message(F.text.lower() == "бандит")
async def bandit_game(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name.upper()
    
    if get_balance(user_id) < 1000:
        return await message.reply("❌ Недостаточно монет!")

    update_balance(user_id, -1000)
    msg = await message.answer(f"⚔️ **KR** / **{name}**\n\n▒ ▒ ▒ ▒")
    
    symbols = ["❤️", "♣️", "♦️", "♠️", "🍋", "🍒"]
    for i in range(3):
        roll = "".join(random.choices(symbols, k=4))
        await msg.edit_text(f"⚔️ **KR** / **{name}**\n\n{roll}")
        await asyncio.sleep(0.5)

    final = random.choices(symbols, k=4)
    win = 3000 if len(set(final)) <= 2 else 0
    update_balance(user_id, win)
    
    res = f"Выигрыш: {win}" if win > 0 else "Проигрыш: 1000"
    await msg.edit_text(f"⚔️ **KR** / **{name}**\n\n{''.join(final)}\n\n**{res}** 🌚")

# --- СТАРТ МЕНЮ ---
@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
    init_db()
    kb = [[KeyboardButton(text="🎁 Бонус"), KeyboardButton(text="💰 Пополнить баланс")],
          [KeyboardButton(text="❓ Помощь"), KeyboardButton(text="🔗 Ссылки")]]
    await message.answer("🏠 S○U I D G ▲ M⬚S тутумуна кош келиңиз!", reply_markup=ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True))

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
