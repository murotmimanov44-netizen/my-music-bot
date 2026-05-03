import asyncio
import random
import sqlite3
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- КОНФИГУРАЦИЯ ---
API_TOKEN = '8608898907:AAEITJNP6t-s2CiT3b7nCCSX9rGPFF5fmlU'
ADMIN_ID = 504020300 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
game_logs = []
user_bets = {} # Бул жерде ставкалар убактылуу сакталат

# --- БАЗА (Баланс жоголбошу үчүн) ---
def init_db():
    conn = sqlite3.connect('royal_casino.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 5000)')
    conn.commit()
    conn.close()

def get_balance(user_id):
    conn = sqlite3.connect('royal_casino.db')
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
    conn = sqlite3.connect('royal_casino.db')
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
    text = f"**WTT·{name}**\nМонеты: {formatted_bal} 🌚"
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Бонус ↗️", callback_data="bonus_get"))
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

# --- РУЛЕТКА: СТАВКАНЫ ТААНУУ (Оңдолду!) ---
# Бул жерде 'на' сөзү менен сумманы жана кайда койгонун так ажыратат
@dp.message(F.text.regexp(r'(\d+)\s+(на)\s+(кызыл|кара|зеро|0|красное|черное)'))
async def handle_roulette_bet(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name.upper()
    
    match = re.search(r'(\d+)\s+(на)\s+(кызыл|кара|зеро|0|красное|черное)', message.text.lower())
    amount = int(match.group(1))
    target = match.group(3)
    
    if get_balance(user_id) < amount:
        return await message.reply("❌ Недостаточно монет!")

    # Ставканы базага эмес, RAM'га убактылуу сактайбыз
    user_bets[user_id] = {"amount": amount, "target": target}
    update_balance(user_id, -amount) # Ставканы дароо баланстан кемитүү
    
    await message.answer(f"✅ Ставка кабыл алынды: `{amount:,}` на `{target}`\nЭми **'го'** деп жазыңыз!")

# --- РУЛЕТКА: ОЮН (Оңдолду!) ---
@dp.message(F.text.lower() == "го")
async def roulette_spin(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name.upper()
    
    if user_id not in user_bets:
        return await message.answer("❌ Сиз ставка коё элексиз! Мисалы: `1000 на кызыл` деп жазыңыз.")

    bet = user_bets.pop(user_id) # Ставканы алып чыгабыз
    amount = bet["amount"]
    target = bet["target"]

    msg = await message.answer(f"⚔️ **KR** / **{name}** крутит... 🎰")
    await asyncio.sleep(2)
    
    num = random.randint(0, 12)
    # Түстү аныктоо
    if num == 0: color = "зеро"; emoji = "🟢"
    elif num in [1,3,5,7,9,11]: color = "кызыл"; emoji = "🔴"
    else: color = "кара"; emoji = "⚫"
    
    game_logs.append(f"{num}{emoji}")
    
    # Утушту текшерүү
    win = 0
    if target in ["кызыл", "красное"] and color == "кызыл": win = amount * 2
    elif target in ["кара", "черное"] and color == "кара": win = amount * 2
    elif target in ["0", "зеро"] and color == "зеро": win = amount * 12
    
    if win > 0:
        update_balance(user_id, win)
        status = f"выиграл {win:,} 💰"
    else:
        status = f"проиграл {amount:,} ☁️"

    await msg.edit_text(f"🎰 Рулетка: {num} {emoji}\n⚔️ **KR** / **{name}** {status} 🔥")

# --- БАНДИТ ---
@dp.message(F.text.lower() == "бандит")
async def bandit_game(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name.upper()
    if get_balance(user_id) < 1000: return await message.reply("❌ Недостаточно монет!")
    
    update_balance(user_id, -1000)
    msg = await message.answer(f"⚔️ **KR** / **{name}**\n\n▒ ▒ ▒ ▒")
    syms = ["💎", "🍒", "🍋", "🔔", "⭐", "🍀"]
    for _ in range(2):
        await msg.edit_text(f"⚔️ **KR** / **{name}**\n\n{''.join(random.choices(syms, k=4))}")
        await asyncio.sleep(0.4)
    final = random.choices(syms, k=4)
    win = 3000 if len(set(final)) <= 2 else 0
    update_balance(user_id, win)
    res = f"Выигрыш: {win}" if win > 0 else "Проигрыш: 1000"
    await msg.edit_text(f"⚔️ **KR** / **{name}**\n\n{''.join(final)}\n\n**{res}** 🌚")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
