import os, asyncio, sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# --- ЖӨНДӨӨЛӨР ---
TOKEN = "8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM"
ADMIN_ID = 5334757519  # Өзүңдүн ID дарегиңди жаз
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- МААЛЫМАТ БАЗАСЫ ---
def init_db():
    conn = sqlite3.connect('pr_bot.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0)')
    cursor.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, channel_id TEXT, url TEXT, price INTEGER)')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('pr_bot.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)', (user_id,))
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    res = cursor.fetchone()
    conn.commit()
    conn.close()
    return res[0]

def add_balance(user_id, amount):
    conn = sqlite3.connect('pr_bot.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
    conn.commit()
    conn.close()

# --- МЕНЮЛАР ---
def main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="💰 Упай топтоо")],
        [KeyboardButton(text="🚀 Тапшырма кошуу"), KeyboardButton(text="📊 Статистика")]
    ], resize_keyboard=True)

# --- БОТТУН ЛОГИКАСЫ ---
@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
    init_db()
    await message.answer(f"Салам {message.from_user.first_name}! Бул накрутка (алмашуу) боту. \nКаналдарга катталып упай топтойсуң жана аны өзүңдү өстүрүүгө жумшайсың.", reply_markup=main_menu())

@dp.message(F.text == "👤 Профиль")
async def view_profile(message: types.Message):
    balance = get_user(message.from_user.id)
    await message.answer(f"👤 Колдонуучу: {message.from_user.full_name}\n💰 Баланс: {balance} упай")

@dp.message(F.text == "💰 Упай топтоо")
async def earn_points(message: types.Message):
    # Бул жерде мисал катары бир каналды чыгарабыз (кийин базадан алса болот)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Каналга катталуу", url="https://t.me/Argen_70")], # Өз каналыңды кой
        [InlineKeyboardButton(text="✅ Текшерүү", callback_data="check_sub")]
    ])
    await message.answer("Төмөнкү каналга каттал жана 10 упай ал:", reply_markup=kb)

@dp.callback_query(F.data == "check_sub")
async def check_subscription(call: types.CallbackQuery):
    user_id = call.from_user.id
    # Каналга катталганын текшерүү (Бот каналда админ болушу керек!)
    try:
        member = await bot.get_chat_member(chat_id="@Argen_70", user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            add_balance(user_id, 10)
            await call.answer("Куттуктайбыз! +10 упай берилди.", show_alert=True)
            await call.message.delete()
        else:
            await call.answer("Сиз катталган жоксуз!", show_alert=True)
    except:
        await call.answer("Ката кетти. Бот каналда админ экенин текшериңиз.")

# --- RENDER СЕРВЕР ---
async def handle(request): return web.Response(text="Bot is running")
async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 10000)))
    await site.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    init_db()
    asyncio.run(main())
