import asyncio
import random
import sqlite3
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, LabeledPrice, PreCheckoutQuery, SuccessfulPayment

# --- КОНФИГУРАЦИЯ ---
API_TOKEN = '8608898907:AAEITJNP6t-s2CiT3b7nCCSX9rGPFF5fmlU'
ADMIN_ID = 504020300 # Бул жерге өзүңдүн ID-ңди жазсаң болот

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
active_bets = {}
game_logs = []

# --- БАЗА (SQLite) ---
def init_db():
    conn = sqlite3.connect('casino.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 5000)')
    conn.commit()
    conn.close()

def get_balance(user_id):
    if user_id == ADMIN_ID: return 999999999
    conn = sqlite3.connect('casino.db')
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    res = cursor.fetchone()
    conn.close()
    if res is None:
        conn = sqlite3.connect('casino.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (user_id, balance) VALUES (?, 5000)', (user_id,))
        conn.commit()
        conn.close()
        return 5000
    return res[0]

def update_balance(user_id, amount):
    if user_id == ADMIN_ID: return
    conn = sqlite3.connect('casino.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
    conn.commit()
    conn.close()

# --- НЕГИЗГИ МЕНЮ ---
def get_main_kb():
    kb = [
        [KeyboardButton(text="🎁 Бонус"), KeyboardButton(text="💰 Пополнить баланс")],
        [KeyboardButton(text="❓ Помощь"), KeyboardButton(text="🔗 Ссылки")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="🏠 S○U I D G ▲ M⬚S")

@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
    get_balance(message.from_user.id)
    await message.answer("👋 Добро пожаловать в S○U I D G ▲ M⬚S!", reply_markup=get_main_kb())

# --- БАЛАНС (б) ---
@dp.message(F.text.lower() == "б")
async def check_balance(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name.upper()
    bal = get_balance(user_id)
    display_bal = "♾️ БЕСКОНЕЧНО" if user_id == ADMIN_ID else f"{bal:,}".replace(",", ".")
    text = f"**WTT·{name}**\nМонеты: {display_bal} 🌚"
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="Бонус ↗️", callback_data="bonus"))
    await message.answer(text, reply_markup=kb.as_markup(), parse_mode="Markdown")

# --- БАНДИТ (Анимация менен) ---
@dp.message(F.text.lower() == "бандит")
async def bandit(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name.upper()
    if get_balance(user_id) < 1000 and user_id != ADMIN_ID:
        return await message.reply("❌ Недостаточно монет (1000)!")

    msg = await message.answer(f"⚔️ **KR** ⚔️ **{name}**\n\n▒ ▒ ▒ ▒")
    symbols = ["❤️", "♣️", "♦️", "♠️", "🍋", "🍒", "🔔"]
    
    for _ in range(3):
        temp = "".join([random.choice(symbols) for _ in range(4)])
        await msg.edit_text(f"⚔️ **KR** ⚔️ **{name}**\n\n{temp}")
        await asyncio.sleep(0.4)

    final = [random.choice(symbols) for _ in range(4)]
    win = 3000 if len(set(final)) <= 2 else 0
    update_balance(user_id, win - 1000)
    
    res = f"Выигрыш: {win} 🔥" if win > 0 else "Проигрыш: 1000 ☁️"
    await msg.edit_text(f"⚔️ **KR** ⚔️ **{name}**\n\n{''.join(final)}\n\n**{res}** 🌚")

# --- РУЛЕТКА (ГО) ---
@dp.message(F.text.lower() == "го")
async def roulette_go(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name.upper()
    
    msg = await message.answer(f"⚔️ **KR** ⚔️ **{name}** крутит...")
    await asyncio.sleep(2)
    
    win_num = random.randint(0, 12)
    win_col = "🔴" if win_num in [1,3,5,7,9,11] else "⚫" if win_num != 0 else "🟢"
    game_logs.append(f"{win_num}{win_col}")
    
    await msg.edit_text(f"🎰 Рулетка: {win_num} {win_col}\n⚔️ **KR** ⚔️ **{name}** результат: {win_num} {win_col} 🔥")

@dp.message(F.text.lower() == "лог")
async def show_log(message: types.Message):
    if not game_logs: return await message.answer("Игр еще не было.")
    await message.answer("📜 Акыркы оюндар:\n" + "\n".join(game_logs[-5:]))

# --- ДОНАТ (STARS + M-BANK) ---
@dp.message(F.text == "💰 Пополнить баланс")
async def top_up(message: types.Message):
    text = (
        "Монеты🌚\n"
        "200.000 - 100 ⭐\n"
        "500.000 - 230 ⭐\n"
        "1.000.000 - 450 ⭐\n\n"
        "Если возникнут вопросы: @Argen_70\n"
        "🏦 **M-BANK: +996 999906700**"
    )
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="Купить за Stars ⭐", callback_data="buy_200k"))
    kb.row(types.InlineKeyboardButton(text="ВЕБ ПРИЛОЖЕНИЕ ⬚", callback_data="web"))
    await message.answer(text, reply_markup=kb.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == "buy_200k")
async def stars_pay(call: types.CallbackQuery):
    await call.message.answer_invoice(
        title="200.000 Монет", description="Пополнение баланса", payload="p200",
        provider_token="", currency="XTR", prices=[LabeledPrice(label="Цена", amount=100)]
    )

@dp.pre_checkout_query()
async def pre_checkout(q: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(q.id, ok=True)

@dp.message(F.successful_payment)
async def success_pay(message: types.Message):
    update_balance(message.from_user.id, 200000)
    await message.answer("✅ Оплата прошла! 200.000 монет начислены. 🌚")

# --- ССЫЛКИ ---
@dp.message(F.text == "🔗 Ссылки")
async def show_links(message: types.Message):
    text = (
        "‼️ Все новости: @SQUIIDGAMES_NEWS\n"
        "💰 Актуальный донат: @Argen_70\n\n"
        "🇰🇬 Kyrgyzstan: https://t.me/+hH21fY9ytzRmNmU6\n"
        "🇷🇺 Russia: https://t.me/+xGq42clRQVZlNDli"
    )
    await message.answer(text, disable_web_page_preview=True)

# --- АДМИН КОМАНДАСЫ (+ сумма) ---
@dp.message(F.text.regexp(r'^[+]\s*(\d+)'), F.from_user.id == ADMIN_ID)
async def manual_add(message: types.Message):
    if message.reply_to_message:
        amt = int(re.search(r'(\d+)', message.text).group(1))
        update_balance(message.reply_to_message.from_user.id, amt)
        await message.answer(f"✅ Игрокко {amt} монета кошулду!")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
