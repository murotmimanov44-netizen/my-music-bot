import asyncio
import random
import sqlite3
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- КОНФИГУРАЦИЯ ---
API_TOKEN = '8608898907:AAEITJNP6t-s2CiT3b7nCCSX9rGPFF5fmlU' # BotFather'ден алган токенди бул жерге кой
ADMIN_ID = 123456789  # Өзүңдүн ID-ңди бул жерге жаз (чексиз баланс үчүн)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
active_bets = {}

# --- БАЗА МЕНЕН ИШТӨӨ ---
def init_db():
    conn = sqlite3.connect('casino.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 5000)''')
    conn.commit()
    conn.close()

def get_balance(user_id):
    if user_id == ADMIN_ID: return 999999999999 # Сен үчүн чексиз монета
    conn = sqlite3.connect('casino.db')
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    res = cursor.fetchone()
    if res is None:
        cursor.execute('INSERT INTO users (user_id, balance) VALUES (?, 5000)')
        conn.commit()
        return 5000
    return res[0]

def update_balance(user_id, amount):
    if user_id == ADMIN_ID: return # Админдин балансы эч качан азайбайт
    conn = sqlite3.connect('casino.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
    conn.commit()
    conn.close()

# --- РУЛЕТКА ДИЗАЙНЫ (Сүрөттөгүдөй) ---
@dp.message(F.text.lower() == "рулетка")
async def cmd_roulette(message: types.Message):
    text = (
        "Минирулетка\n"
        "Угадайте число из:\n"
        "0💚\n"
        "1🔴 2⚫ 3🔴 4⚫ 5🔴 6⚫\n"
        "7🔴 8⚫ 9🔴 10⚫ 11🔴 12⚫\n"
        "Ставки можно текстом:\n"
        "1000 на красное | 5000 на 12"
    )
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="1-3", callback_data="none"), types.InlineKeyboardButton(text="4-6", callback_data="none"))
    kb.row(types.InlineKeyboardButton(text="1к на 🔴", callback_data="none"), types.InlineKeyboardButton(text="1к на ⚫", callback_data="none"))
    kb.row(types.InlineKeyboardButton(text="Крутить", callback_data="none"))
    await message.answer(text, reply_markup=kb.as_markup())

# --- СТАВКА КАБЫЛ АЛУУ ---
@dp.message(F.text.regexp(r'(\d+)\s*([кчз])'))
async def handle_bet(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name.upper()
    match = re.search(r'(\d+)\s*([кчз])', message.text.lower())
    amount = int(match.group(1))
    code = match.group(2)
    
    balance = get_balance(user_id)
    if balance < amount and user_id != ADMIN_ID:
        return await message.reply(f"❌ **{name}**, недостаточно монет!")

    target = "red" if code == 'к' else "black" if code == 'ч' else "zero"
    active_bets[user_id] = {'amount': amount, 'target': target}
    
    color_text = "красное 🔴" if target == "red" else "черное ⚫" if target == "black" else "зеленое 🟢"
    await message.answer(f"Ставка принята: ⚔️ **KR** ⚔️ **{name}** {amount} монет на {color_text}")

# --- ОЮНДУ БАШТОО (ГО) ---
@dp.message(F.text.lower() == "го")
async def spin_go(message: types.Message):
    user_id = message.from_user.id
    if user_id not in active_bets: 
        return await message.reply("Сначала сделай ставку! (Например: 5000 ч)")
    
    name = message.from_user.first_name.upper()
    bet = active_bets[user_id]
    
    msg = await message.answer("🔄 **Рулетка крутится...**")
    await asyncio.sleep(2)
    
    win_num = random.randint(0, 12)
    win_col = "🟢" if win_num == 0 else "🔴" if win_num in [1,3,5,7,9,11] else "⚫"
    
    is_win = (bet['target'] == "red" and win_col == "🔴") or \
             (bet['target'] == "black" and win_col == "⚫") or \
             (bet['target'] == "zero" and win_col == "🟢")

    if is_win:
        multiplier = 14 if bet['target'] == "zero" else 2
        win_amount = bet['amount'] * multiplier
        update_balance(user_id, win_amount - bet['amount']) # Таза утушту кошуу
        res = (f"🎰 **Рулетка: {win_num}{win_col}**\n"
               f"⚔️ **KR** ⚔️ **{name}** {bet['amount']} на {win_col}\n"
               f"🔥 **ВЫИГРАЛ {win_amount}!**\n"
               f"💰 Баланс: {get_balance(user_id)} 🪙")
    else:
        update_balance(user_id, -bet['amount']) # Тиккен гана суммасы минус болот
        res = (f"🎰 **Рулетка: {win_num}{win_col}**\n"
               f"⚔️ **KR** ⚔️ **{name}** {bet['amount']} на {win_col}\n"
               f"☁️ **ПРОИГРАЛ {bet['amount']}!**\n"
               f"💰 Баланс: {get_balance(user_id)} 🪙")
    
    await msg.edit_text(res, parse_mode="Markdown")
    del active_bets[user_id]

# --- МОНЕТА БЕРҮҮ (+ 1000) ---
@dp.message(F.reply_to_message, F.text.regexp(r'^[+]\s*(\d+)'))
async def transfer(message: types.Message):
    sender_id = message.from_user.id
    amount = int(re.search(r'(\d+)', message.text).group(1))
    
    if amount > 10000 and sender_id != ADMIN_ID:
        return await message.reply("⚠️ Лимит 10 000!")
    
    if get_balance(sender_id) < amount and sender_id != ADMIN_ID:
        return await message.reply("❌ Недостаточно монет!")

    update_balance(sender_id, -amount)
    update_balance(message.reply_to_message.from_user.id, amount)
    await message.answer(f"✅ Перевод {amount} выполнен!")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
