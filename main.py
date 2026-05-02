import asyncio
import sqlite3
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# --- ЖӨНДӨӨЛӨР ---
TOKEN = '8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM'
ADMIN_ID = 7978591176  
MBANK_NUMBER = "+996 999906700" 

# Кызматтардын тизмеси жана баалары (сом менен)
SERVICES = {
    "inst_subs": {"name": "Instagram Катталуучулар", "price": 50},
    "inst_likes": {"name": "Instagram Лайктар", "price": 20},
    "tt_views": {"name": "TikTok Көрүүлөр", "price": 10},
}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- МААЛЫМАТ БАЗАСЫ ---
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

# --- БОТТУН НЕГИЗГИ МЕНЮСУ ---
@dp.message(Command("start"))
async def start(message: types.Message):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
    conn.commit()
    conn.close()
    
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🚀 Накрутка буйрутма"), KeyboardButton(text="💰 Баланс толтуруу")],
        [KeyboardButton(text="👤 Профиль")]
    ], resize_keyboard=True)
    
    await message.answer(f"Салам, {message.from_user.first_name}! Накрутка ботко кош келиңиз.", reply_markup=kb)

# --- ПРОФИЛЬ ---
@dp.message(F.text == "👤 Профиль")
async def profile(message: types.Message):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (message.from_user.id,))
    res = cursor.fetchone()
    balance = res[0] if res else 0
    conn.close()
    await message.answer(f"👤 <b>Сиздин профилиңиз:</b>\n🆔 ID: <code>{message.from_user.id}</code>\n💰 Баланс: <b>{balance} сом</b>", parse_mode="HTML")

# --- БАЛАНС ТОЛТУРУУ (МБАНК) ---
@dp.message(F.text == "💰 Баланс толтуруу")
async def top_up(message: types.Message):
    text = (
        "<b>💳 Балансты толтуруу:</b>\n\n"
        f"МБанк номер: <code>{MBANK_NUMBER}</code>\n\n"
        "1. Номерге акча которуңуз.\n"
        "2. Чекти (скриншот) бул жерге жөнөтүңүз.\n"
        "3. Админ текшергенден кийин баланс кошулат."
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.photo)
async def handle_receipt(message: types.Message):
    await message.answer("✅ Чек кабыл алынды! Админ текшерип жатат...")
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ 100 сом берүү", callback_data=f"pay_{message.from_user.id}_100")],
        [InlineKeyboardButton(text="✅ 300 сом берүү", callback_data=f"pay_{message.from_user.id}_300")],
        [InlineKeyboardButton(text="✅ 500 сом берүү", callback_data=f"pay_{message.from_user.id}_500")],
        [InlineKeyboardButton(text="❌ Четке кагуу", callback_data=f"pay_{message.from_user.id}_0")]
    ])
    
    await bot.send_photo(ADMIN_ID, photo=message.photo[-1].file_id, 
                         caption=f"🔔 Төлөм келди!\nID: {message.from_user.id}\nАты: {message.from_user.full_name}", 
                         reply_markup=kb)

@dp.callback_query(F.data.startswith("pay_"))
async def admin_approve(callback: types.CallbackQuery):
    _, user_id, amount = callback.data.split("_")
    user_id, amount = int(user_id), int(amount)
    
    if amount > 0:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()
        conn.close()
        await bot.send_message(user_id, f"✅ Балансыңыз {amount} сомго толтурулду!")
        await callback.message.edit_caption(caption=f"✅ Ырасталды: {amount} сом")
    else:
        await bot.send_message(user_id, "❌ Сиздин чегиңиз кабыл алынган жок.")
        await callback.message.edit_caption(caption="❌ Четке кагылды")

# --- НАКРУТКА БУЙРУТМА БЕРҮҮ ---
@dp.message(F.text == "🚀 Накрутка буйрутма")
async def services_list(message: types.Message):
    kb_list = []
    for key, value in SERVICES.items():
        kb_list.append([InlineKeyboardButton(text=f"{value['name']} - {value['price']}с", callback_data=f"buy_{key}")])
    
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list)
    await message.answer("Керектүү кызматты тандаңыз:", reply_markup=kb)

@dp.callback_query(F.data.startswith("buy_"))
async def process_buy(callback: types.CallbackQuery):
    service_id = callback.data.split("_")[1]
    service = SERVICES[service_id]
    
    # Колдонуучунун балансын текшерүү
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (callback.from_user.id,))
    balance = cursor.fetchone()[0]
    conn.close()
    
    if balance >= service['price']:
        # Бул жерде азырынча жөн гана билдирүү, кийин SMM API кошсо болот
        await callback.message.answer(f"✅ Сиз тандадыңыз: {service['name']}\n\nНакрутка үчүн ссылканы (ссылка) жазыңыз. Админ жакында аткарат.")
        # Балансты кемитүү (мисалы):
        # conn = sqlite3.connect('users.db'); cursor = conn.cursor()
        # cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (service['price'], callback.from_user.id))
        # conn.commit(); conn.close()
    else:
        await callback.message.answer("❌ Балансыңыз жетишсиз. Сураныч, балансты толтуруңуз.")
    
    await callback.answer()

# --- ИШКЕ КИРГИЗҮҮ ---
async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
