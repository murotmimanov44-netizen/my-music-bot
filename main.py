import sqlite3
import logging
import os
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# --- ЖӨНДӨӨЛӨР ---
TOKEN = '8646126657:AAFA0q1Mjv5dDsxiDyId8MDaLeTQgSkZvgs'
ADMIN_ID = 5906232537  # Сенин Telegram ID номериң
MBANK = "+996 999 906700" #
CASSA = "@Argen_70" #

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# --- БАЗА МЕНЕН ИШТӨӨ ---
# Render'де файлдар өчүп кетпеши үчүн базанын жолун так көрсөтүү маанилүү
DB_PATH = "users_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0)")
    conn.commit()
    conn.close()

def get_bal(uid):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE id = ?", (uid,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else 0

def add_bal(uid, amount):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (id, balance) VALUES (?, 0)", (uid,))
    cursor.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, uid))
    conn.commit()
    conn.close()

# --- БАСКЫЧТАР ---
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(KeyboardButton("👤 Профиль"), KeyboardButton("💎 Донат"))
menu.add(KeyboardButton("🛒 Кызматтар"), KeyboardButton("👥 Реферал"))

# --- БОТТУН ЛОГИКАСЫ ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    add_bal(message.from_user.id, 0)
    await message.answer("🛠 **Хакердик Накрутка ботуна кош келиңиз!**", reply_markup=menu, parse_mode="Markdown")

@dp.message_handler(lambda m: m.text == "👤 Профиль")
async def profile(message: types.Message):
    b = get_bal(message.from_user.id)
    await message.answer(f"👤 **Профиль:**\n🆔 ID: `{message.from_user.id}`\n💰 Баланс: **{b} монета**", parse_mode="Markdown")

@dp.message_handler(lambda m: m.text == "💎 Донат")
async def donate(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("💎 1,000 монета — 100 сом", callback_data="p1"),
        InlineKeyboardButton("💎 5,000 монета — 500 сом", callback_data="p2"),
        InlineKeyboardButton("💎 10,000 монета — 1000 сом", callback_data="p3")
    )
    await message.answer("🛒 **Пакетти тандаңыз:**", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data in ['p1', 'p2', 'p3'])
async def pay(call: types.CallbackQuery):
    sums = {"p1": (100, 1000), "p2": (500, 5000), "p3": (1000, 10000)}
    s, c = sums[call.data]
    text = (f"💠 **Заказ:** {c} монета\n💰 **Сумма:** {s} сом\n\n"
            f"🏦 **M BANK:** `{MBANK}`\n👤 **Cassa:** {CASSA}\n\n"
            f"Чекти {CASSA} дарегине жөнөтүңүз.")
    btn = InlineKeyboardMarkup().add(InlineKeyboardButton("📩 Чекти жиберүү", url=f"https://t.me/Argen_70"))
    await bot.send_message(call.from_user.id, text, reply_markup=btn, parse_mode="Markdown")

@dp.message_handler(lambda m: m.text == "🛒 Кызматтар")
async def serv(message: types.Message):
    await message.answer(f"📊 **Кызматтар:**\n\nТГ Катталуучу: 1000 = 2000 монета\n\nЗаказ үчүн: {CASSA}")

# --- АДМИН (МОНЕТА КОШУУ) ---
@dp.message_handler(commands=['add'], user_id=ADMIN_ID)
async def admin_add(message: types.Message):
    try:
        _, uid, amt = message.text.split()
        add_bal(int(uid), int(amt))
        await message.answer(f"✅ ID {uid} үчүн {amt} монета кошулду!")
        await bot.send_message(uid, f"💰 Балансыңызга {amt} монета кошулду!")
    except:
        await message.answer("Формат: `/add ID СУММА` (мисалы: `/add 5906232537 1000`)")

if __name__ == '__main__':
    init_db()
    print("Бот иштеп жатат...")
    executor.start_polling(dp, skip_updates=True)
