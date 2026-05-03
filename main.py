import asyncio
import random
import sqlite3
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, LabeledPrice, PreCheckoutQuery, SuccessfulPayment

# --- КОНФИГУРАЦИЯ ---
API_TOKEN = '8608898907:AAEITJNP6t-s2CiT3b7nCCSX9rGPFF5fmlU'
ADMIN_ID = 504020300  # Өзүңдүн ID-ңди ушул жерге жаз!

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

# --- МЕНЮ ---
def get_main_kb():
    kb = [
        [KeyboardButton(text="🎁 Бонус"), KeyboardButton(text="💰 Пополнить баланс")],
        [KeyboardButton(text="❓ Помощь"), KeyboardButton(text="🔗 Ссылки")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="🏠 S○U I D G ▲ M⬚S")

@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
    get_balance(message.from_user.id)
    await message.answer("👋 Добро пожаловать!", reply_markup=get_main_kb())

# --- БАЛАНС (Б) ---
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

# --- БАНДИТ ---
@dp.message(F.text.lower() == "бандит")
async def bandit(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name.upper()
    if get_balance(user_id) < 1000 and user_id != ADMIN_ID:
        return await message.reply("❌ Недостаточно монет (1000)!")
    
    symbols = ["❤️", "♣️", "♦️", "♠️", "🍋", "🍒"]
    s = [random.choice(symbols) for _ in range(4)]
    win = 3000 if len(set(s)) <= 2 else 0
    update_balance(user_id, win - 1000)
    
    res = f"Выигрыш: {win}" if win > 0 else "Проигрыш"
    await message.answer(f"⚔️ **KR** ⚔️ **{name}**\n\n{''.join(s)}\n\n**{res}**", parse_mode="Markdown")

# --- РУЛЕТКА ЖАНА ЛОГ ---
@dp.message(F.text.lower() == "рулетка")
async def roulette(message: types.Message):
    text = "Минирулетка\nУгадайте число из:\n0💚\n1🔴 2⚫ 3🔴 4⚫ 5🔴 6⚫\nСтавки текстом: 1000 на красное"
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="Крутить", callback_data="spin"))
    await message.answer(text, reply_markup=kb.as_markup())

@dp.message(F.text.lower() == "лог")
async def show_log(message: types.Message):
    if not game_logs: return await message.answer("Игр не было.")
    await message.answer("\n".join(game_logs[-5:]))

# --- ДОНАТ (STARS) ---
@dp.message(F.text == "💰 Пополнить баланс")
async def donate_menu(message: types.Message):
    text = "Монеты🌚\n200.000 - 100 ⭐\n500.000 - 230 ⭐\nОбратиться к: @Argen_70"
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="Купить 200к (100 ⭐)", callback_data="buy_200"))
    await message.answer(text, reply_markup=kb.as_markup())

@dp.callback_query(F.data == "buy_200")
async def send_inv(call: types.CallbackQuery):
    await call.message.answer_invoice(
        title="200.000 Монет", description="Пополнение", payload="p200",
        provider_token="", currency="XTR", prices=[LabeledPrice(label="Цена", amount=100)]
    )

@dp.pre_checkout_query()
async def pre_check(q: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(q.id, ok=True)

@dp.message(F.successful_payment)
async def pay_ok(message: types.Message):
    update_balance(message.from_user.id, 200000)
    await message.answer("✅ Монеты начислены!")

# --- ССЫЛКИ ---
@dp.message(F.text == "🔗 Ссылки")
async def links(message: types.Message):
    await message.answer("💰 Канал: @SQUIIDGAMES_NEWS\n💎 Касса: @Argen_70\n🇰🇬 Киргизия: https://t.me/+hH21fY9ytzRmNmU6", disable_web_page_preview=True)

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
