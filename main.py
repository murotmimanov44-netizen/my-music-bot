import asyncio
import random
import sqlite3
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, LabeledPrice, PreCheckoutQuery, SuccessfulPayment

# --- КОНФИГУРАЦИЯ ---
API_TOKEN = '8608898907:AAEITJNP6t-s2CiT3b7nCCSX9rGPFF5fmlU'
ADMIN_ID = 504020300 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
game_logs = []

# --- БАЗА ---
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
    return res[0] if res else 5000

def update_balance(user_id, amount):
    if user_id == ADMIN_ID: return
    conn = sqlite3.connect('casino.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
    conn.commit()
    conn.close()

# --- МЕНЮ ---
def get_main_kb():
    kb = [[KeyboardButton(text="🎁 Бонус"), KeyboardButton(text="💰 Пополнить баланс")],
          [KeyboardButton(text="❓ Помощь"), KeyboardButton(text="🔗 Ссылки")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="🏠 S○U I D G ▲ M⬚S")

@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
    get_balance(message.from_user.id)
    await message.answer("👋 Добро пожаловать!", reply_markup=get_main_kb())

# --- БАЛАНС (б) ---
@dp.message(F.text.lower() == "б")
async def check_balance(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name.upper()
    bal = get_balance(user_id)
    display_bal = "♾️ БЕСКОНЕЧНО" if user_id == ADMIN_ID else f"{bal:,}".replace(",", ".")
    await message.answer(f"**WTT·{name}**\nМонеты: {display_bal} 🌚", parse_mode="Markdown")

# --- РУЛЕТКА МЕНЮСУ (Видеодогудай) ---
@dp.message(F.text.lower() == "рулетка")
async def roulette_menu(message: types.Message):
    text = (
        "**Минирулетка**\n"
        "Угадайте число из:\n"
        "0 💚\n"
        "1 ❤️ 2 ⚫ 3 ❤️ 4 ⚫ 5 ❤️ 6 ⚫\n"
        "7 ❤️ 8 ⚫ 9 ❤️ 10 ⚫ 11 ❤️ 12 ⚫\n\n"
        "**Ставки текстом:** 1000 на красное"
    )
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="1-3", callback_data="r_13"), types.InlineKeyboardButton(text="4-6", callback_data="r_46"))
    builder.row(types.InlineKeyboardButton(text="1к на ❤️", callback_data="r_red"), types.InlineKeyboardButton(text="1к на ⚫", callback_data="r_black"))
    builder.row(types.InlineKeyboardButton(text="🔄 Крутить (ГО)", callback_data="r_go"))
    
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")

# --- РУЛЕТКА ЛОГИКАСЫ (ГО) ---
@dp.callback_query(F.data == "r_go")
@dp.message(F.text.lower() == "го")
async def roulette_spin(event):
    message = event if isinstance(event, types.Message) else event.message
    user_id = event.from_user.id
    name = event.from_user.first_name.upper()
    
    msg = await message.answer(f"⚔️ **KR** ⚔️ **{name}** крутит...")
    await asyncio.sleep(2)
    
    num = random.randint(0, 12)
    col = "❤️" if num in [1,3,5,7,9,11] else "⚫" if num != 0 else "💚"
    
    res_text = f"🎰 Рулетка: {num} {col}\n⚔️ **KR** ⚔️ **{name}** результат: {num} {col} 🔥"
    if isinstance(event, types.Message):
        await msg.edit_text(res_text)
    else:
        await message.answer(res_text)

# --- БАНДИТ ---
@dp.message(F.text.lower() == "бандит")
async def bandit_game(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name.upper()
    if get_balance(user_id) < 1000 and user_id != ADMIN_ID:
        return await message.reply("❌ Недостаточно монет!")

    msg = await message.answer(f"⚔️ **KR** ⚔️ **{name}**\n\n▒ ▒ ▒ ▒")
    syms = ["❤️", "♣️", "♦️", "♠️", "🍋", "🍒"]
    
    for _ in range(2):
        await msg.edit_text(f"⚔️ **KR** ⚔️ **{name}**\n\n{''.join(random.choices(syms, k=4))}")
        await asyncio.sleep(0.4)

    final = random.choices(syms, k=4)
    win = 3000 if len(set(final)) <= 2 else 0
    update_balance(user_id, win - 1000)
    
    res = f"Выигрыш: {win}" if win > 0 else "Проигрыш: 1000"
    await msg.edit_text(f"⚔️ **KR** ⚔️ **{name}**\n\n{''.join(final)}\n\n**{res}** 🌚")

# --- ДОНАТ ЖАНА БАШКАЛАР ---
@dp.message(F.text == "💰 Пополнить баланс")
async def top_up(message: types.Message):
    text = "Монеты🌚\n200.000 - 100 ⭐\n500.000 - 230 ⭐\n\nКасса: @Argen_70"
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="Купить за Stars ⭐", callback_data="buy_stars"))
    await message.answer(text, reply_markup=kb.as_markup())

@dp.callback_query(F.data == "buy_stars")
async def pay(call: types.CallbackQuery):
    await call.message.answer_invoice(title="200k Монет", description="Пополнение", payload="p2", provider_token="", currency="XTR", prices=[LabeledPrice(label="X", amount=100)])

@dp.pre_checkout_query()
async def pre(q: PreCheckoutQuery): await bot.answer_pre_checkout_query(q.id, ok=True)

@dp.message(F.successful_payment)
async def ok(m: types.Message):
    update_balance(m.from_user.id, 200000)
    await m.answer("✅ Начислено!")

@dp.message(F.text == "🔗 Ссылки")
async def links(m: types.Message):
    await m.answer("‼️ Новости: @SQUIIDGAMES_NEWS\n🇰🇬 Чат: https://t.me/+hH21fY9ytzRmNmU6", disable_web_page_preview=True)

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
