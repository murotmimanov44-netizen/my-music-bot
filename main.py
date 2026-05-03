import asyncio
import random
import sqlite3
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, LabeledPrice, PreCheckoutQuery, SuccessPayment

# --- КОНФИГУРАЦИЯ ---
API_TOKEN = '8608898907:AAEITJNP6t-s2CiT3b7nCCSX9rGPFF5fmlU'
ADMIN_ID = 123456789 # Өзүңдүн ID-ңди жаз

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

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

# --- РЕПЛИ МЕНЮ (START) ---
def main_menu_kb():
    kb = [
        [KeyboardButton(text="🎁 Бонус"), KeyboardButton(text="💰 Пополнить баланс")],
        [KeyboardButton(text="❓ Помощь"), KeyboardButton(text="🔗 Ссылки")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="🏠 S○U I D G ▲ M⬚S")

@dp.message(F.text == "/start")
async def start_command(message: types.Message):
    # Жаңы оюнчуну базага кошуу
    get_balance(message.from_user.id)
    await message.answer("👋 Добро пожаловать в SQUID GAMES BOT!\nИспользуйте меню ниже для навигации.", reply_markup=main_menu_kb())

# --- ПОПОЛНИТЬ БАЛАНС (STARS МЕНЮ) ---
@dp.message(F.text == "💰 Пополнить баланс")
async def top_up_stars(message: types.Message):
    text = (
        "Монеты🌚\n"
        "200.000 - 100 ⭐\n"
        "500.000 - 230 ⭐\n"
        "1.000.000 - 450 ⭐\n"
        "2.000.000 - 845 ⭐\n\n"
        "Выберите пакет для покупки через Telegram Stars:"
    )
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="200.000 🪙 (100 ⭐)", callback_data="buy_200k"))
    builder.row(types.InlineKeyboardButton(text="500.000 🪙 (230 ⭐)", callback_data="buy_500k"))
    builder.row(types.InlineKeyboardButton(text="Связаться с тех. поддержкой ↗️", url="https://t.me/Argen_70"))
    
    await message.answer(text, reply_markup=builder.as_markup())

# --- ТӨЛӨМДҮ ЧЫГАРУУ ---
@dp.callback_query(F.data.startswith("buy_"))
async def create_invoice(callback: types.CallbackQuery):
    pack = callback.data.split("_")[1]
    
    prices = {"200k": 100, "500k": 230}
    amounts = {"200k": 200000, "500k": 500000}
    
    await callback.message.answer_invoice(
        title=f"{amounts[pack]} Монет",
        description=f"Покупка игровых монет через Stars",
        payload=f"pay_{pack}",
        provider_token="", # Stars үчүн бош калат
        currency="XTR",
        prices=[LabeledPrice(label="Цена", amount=prices[pack])]
    )

# --- ТӨЛӨМДҮ ТЕКШЕРҮҮ ---
@dp.pre_checkout_query()
async def pre_checkout(pre_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_query.id, ok=True)

# --- УТУШТУ ЖАНА МОНЕТАНЫ АВТОМАТТЫК КОШУУ ---
@dp.message(F.successful_payment)
async def on_success_pay(message: types.Message):
    payload = message.successful_payment.invoice_payload
    user_id = message.from_user.id
    
    amt = 200000 if "200k" in payload else 500000
    update_balance(user_id, amt)
    
    await message.answer(f"✅ Оплата прошла! Вам начислено {amt} монет. Баланс жаңыртылды! 🌚")

# --- АДМИН КОМАНДАСЫ (ЧЕК ҮЧҮН) ---
@dp.message(F.text.regexp(r'^[+]\s*(\d+)'), F.from_user.id == ADMIN_ID)
async def manual_add(message: types.Message):
    if message.reply_to_message:
        amount = int(re.search(r'(\d+)', message.text).group(1))
        target_id = message.reply_to_message.from_user.id
        update_balance(target_id, amount)
        await message.answer(f"✅ Кошулду: {amount} монета.")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
