import sqlite3
import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# --- ЖӨНДӨӨЛӨР ---
API_TOKEN = '8646126657:AAFA0q1Mjv5dDsxiDyId8MDaLeTQgSkZvgs'
ADMIN_ID = 5906232537  # Бул жерге өзүңдүн Telegram ID'ңди жаз (эгер билбесең @userinfobot аркылуу билсең болот)
MBANK_NUMBER = "+996 999 906700"
CASSA_USER = "@Argen_70"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- БАЗА (МОНЕТАЛАРДЫ САКТОО) ---
def init_db():
    conn = sqlite3.connect("money_system.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def update_balance(user_id, amount):
    conn = sqlite3.connect("money_system.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)", (user_id,))
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def get_balance(user_id):
    conn = sqlite3.connect("money_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else 0

# --- КЛАВИАТУРАЛАР ---
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("👤 Профиль"), KeyboardButton("💎 Донат"))
main_menu.add(KeyboardButton("🛒 Кызматтар"), KeyboardButton("👥 Реферал"))

# --- БОТТУН ЛОГИКАСЫ ---

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    update_balance(message.from_user.id, 0)
    await message.answer("🛠 **Хакердик Накрутка ботуна кош келдиңиз!**\n\nТөмөнкү баскычтарды колдонуп, кызматтарды тандаңыз.", reply_markup=main_menu, parse_mode="Markdown")

@dp.message_handler(lambda m: m.text == "👤 Профиль")
async def view_profile(message: types.Message):
    balance = get_balance(message.from_user.id)
    await message.answer(f"👤 **Профиль:**\n\n🆔 ID: `{message.from_user.id}`\n💰 Баланс: **{balance} монета**", parse_mode="Markdown")

@dp.message_handler(lambda m: m.text == "💎 Донат")
async def donate_menu(message: types.Message):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💎 1,000 монета — 100 сом", callback_data="buy_100"),
        InlineKeyboardButton("💎 5,000 монета — 500 сом", callback_data="buy_500"),
        InlineKeyboardButton("💎 10,000 монета — 1000 сом", callback_data="buy_1000")
    )
    await message.answer("🛒 **Сатып алуу үчүн пакетти тандаңыз:**", reply_markup=markup, parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data.startswith('buy_'))
async def pay_process(callback_query: types.CallbackQuery):
    plans = {"buy_100": (100, 1000), "buy_500": (500, 5000), "buy_1000": (1000, 10000)}
    som, coins = plans[callback_query.data]
    
    text = (
        f"✅ **Заказ:** {coins} монета\n"
        f"💰 **Сумма:** {som} сом\n\n"
        f"------------------------------\n"
        f"🏦 **M BANK:** `{MBANK_NUMBER}`\n"
        f"👤 **Cassa:** {CASSA_USER}\n"
        f"------------------------------\n\n"
        f"⚠️ Төлөмдү которуп, чекти {CASSA_USER} дарегине жөнөтүңүз."
    )
    
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("📩 Чекти жиберүү", url=f"https://t.me/Argen_70"))
    await bot.send_message(callback_query.from_user.id, text, reply_markup=markup, parse_mode="Markdown")

# --- АДМИН КОМАНДАСЫ (МОНЕТА КОШУУ) ---
@dp.message_handler(commands=['add'], user_id=ADMIN_ID)
async def add_money_admin(message: types.Message):
    try:
        parts = message.text.split()
        target_id = int(parts[1])
        amount = int(parts[2])
        update_balance(target_id, amount)
        await message.answer(f"✅ ID `{target_id}` үчүн {amount} монета кошулду!", parse_mode="Markdown")
        await bot.send_message(target_id, f"💰 Сиздин балансыңызга **{amount} монета** кошулду!")
    except:
        await message.answer("❌ Ката! Формат: `/add ID СУММА`")

if __name__ == '__main__':
    init_db()
    print("Бот иштеп жатат...")
    executor.start_polling(dp, skip_updates=True)
