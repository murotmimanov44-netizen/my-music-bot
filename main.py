import asyncio
import random
import sqlite3
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- КОНФИГУРАЦИЯ ---
API_TOKEN = '8608898907:AAEITJNP6t-s2CiT3b7nCCSX9rGPFF5fmlU' # BotFather'ден алган токен
ADMIN_ID = 123456789  # Өзүңдүн Telegram ID-ң (мисалы: 504020300)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
active_bets = {}
game_logs = [] # Логдорду сактоо үчүн

# --- БАЗА (SQLite) ---
def init_db():
    conn = sqlite3.connect('casino.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 5000)''')
    conn.commit()
    conn.close()

def get_balance(user_id):
    if user_id == ADMIN_ID: return 999999999999
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
    if user_id == ADMIN_ID: return
    conn = sqlite3.connect('casino.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SELECT balance = balance + ? WHERE user_id = ?', (amount, user_id))
    conn.commit()
    conn.close()

# --- 1. БАЛАНС (Б) ---
@dp.message(F.text.lower() == "б")
async def check_balance_style(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name.upper()
    balance = get_balance(user_id)
    display_balance = "♾️ БЕСКОНЕЧНО" if user_id == ADMIN_ID else f"{balance:,}".replace(",", ".")
    
    text = f"**WTT·{name}**\nМонеты: {display_balance} 🌚"
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Бонус ↗️", callback_data="get_bonus"))
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

# --- 2. РУЛЕТКА ДИЗАЙНЫ ---
@dp.message(F.text.lower() == "рулетка")
async def cmd_roulette(message: types.Message):
    text = (
        "Минирулетка\nУгадайте число из:\n0💚\n"
        "1🔴 2⚫ 3🔴 4⚫ 5🔴 6⚫\n"
        "7🔴 8⚫ 9🔴 10⚫ 11🔴 12⚫\n"
        "Ставки можно текстом:\n1000 на красное | 5000 на 12"
    )
    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(text="1 - 3", callback_data="b1"),
        types.InlineKeyboardButton(text="4 - 6", callback_data="b2"),
        types.InlineKeyboardButton(text="7 - 9", callback_data="b3"),
        types.InlineKeyboardButton(text="10 - 12", callback_data="b4")
    )
    kb.row(
        types.InlineKeyboardButton(text="1к на 🔴", callback_data="b_r"),
        types.InlineKeyboardButton(text="1к на ⚫", callback_data="b_b"),
        types.InlineKeyboardButton(text="1к на 0💚", callback_data="b_z")
    )
    kb.row(
        types.InlineKeyboardButton(text="Повторить", callback_data="rep"),
        types.InlineKeyboardButton(text="Удвоить", callback_data="dbl"),
        types.InlineKeyboardButton(text="Крутить", callback_data="go")
    )
    await message.answer(text, reply_markup=kb.as_markup())

# --- 3. СТАВКА ЖАНА ГО ---
@dp.message(F.text.regexp(r'(\d+)\s*([кчз])'))
async def handle_bet(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name.upper()
    match = re.search(r'(\d+)\s*([кчз])', message.text.lower())
    amount = int(match.group(1))
    target = "red" if match.group(2) == 'к' else "black" if match.group(2) == 'ч' else "zero"
    
    if get_balance(user_id) < amount and user_id != ADMIN_ID:
        return await message.reply("❌ Недостаточно монет!")

    active_bets[user_id] = {'amount': amount, 'target': target}
    col_t = "красное 🔴" if target == "red" else "черное ⚫" if target == "black" else "зеленое 🟢"
    await message.answer(f"Ставка принята: ⚔️ **KR** ⚔️ **{name}** {amount} на {col_t}")

@dp.message(F.text.lower() == "го")
async def spin_go(message: types.Message):
    user_id = message.from_user.id
    if user_id not in active_bets: return await message.reply("Сделайте ставку!")
    
    bet = active_bets[user_id]
    win_num = random.randint(0, 12)
    win_col = "🟢" if win_num == 0 else "🔴" if win_num in [1,3,5,7,9,11] else "⚫"
    
    is_win = (bet['target'] == "red" and win_col == "🔴") or (bet['target'] == "black" and win_col == "⚫") or (bet['target'] == "zero" and win_col == "🟢")
    
    name = message.from_user.first_name.upper()
    if is_win:
        mult = 14 if bet['target'] == "zero" else 2
        win_amt = bet['amount'] * mult
        update_balance(user_id, win_amt - bet['amount'])
        res = f"🎰 Рулетка: {win_num}{win_col}\n⚔️ **KR** ⚔️ **{name}** {bet['amount']} на {win_col}\n🔥 **выиграл {win_amt} на {win_col}**"
    else:
        update_balance(user_id, -bet['amount'])
        res = f"🎰 Рулетка: {win_num}{win_col}\n⚔️ **KR** ⚔️ **{name}** {bet['amount']} на {win_col}\n☁️ **проиграл {bet['amount']}**"
    
    game_logs.append(f"{win_num}{win_col}")
    await message.answer(res, parse_mode="Markdown")
    del active_bets[user_id]

# --- 4. ЛОГ ---
@dp.message(F.text.lower() == "лог")
async def show_logs(message: types.Message):
    if not game_logs: return await message.answer("Игр еще не было.")
    await message.answer("\n".join(game_logs[-5:]))

# --- 5. БАНДИТ ---
@dp.message(F.text.lower() == "бандит")
async def bandit(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name.upper()
    if get_balance(user_id) < 1000 and user_id != ADMIN_ID: return await message.reply("Нужно 1000 монет!")
    
    smb = ["❤️", "♣️", "♦️", "♠️", "🔔"]
    slots = [random.choice(smb) for _ in range(4)]
    win = 3000 if len(set(slots)) <= 2 else 0 # Жөнөкөйлөтүлгөн логика
    
    if win > 0: update_balance(user_id, win - 1000)
    else: update_balance(user_id, -1000)
    
    await message.answer(f"⚔️ **KR** ⚔️ **{name}**\n\n{''.join(slots)}\n\n**Выигрышь: {win}**")

# --- 6. ДОНАТ ---
@dp.message(F.text.lower().in_(['донат', 'магазин']))
async def donate(message: types.Message):
    text = (
        "Монеты🌚\n200.000 - 100₽\n500.000 - 230₽\n1.000.000 - 450₽\n2.000.000 - 845₽\n5.000.000 - 2.000₽\n"
        "10.000.000 - 4.000₽\n50.000.000 - 20000₽\n100.000.000 - 40000₽\n\n"
        "Telegram не сможет помочь с покупками...\nОбратиться к: @Argen_70\n\n"
        "🏦 **M-BANK: +996 999906700**"
    )
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="📄 Правила ↗️", callback_data="r"), types.InlineKeyboardButton(text="💡 Информация ↗️", callback_data="i"))
    kb.row(types.InlineKeyboardButton(text="200.000", callback_data="p1"), types.InlineKeyboardButton(text="500.000", callback_data="p2"))
    await message.answer(text, reply_markup=kb.as_markup(), parse_mode="Markdown")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
