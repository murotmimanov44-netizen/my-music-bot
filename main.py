import os, asyncio, sqlite3, random
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiohttp import web

# --- ЖӨНДӨӨЛӨР ---
TOKEN = "8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM"
ADMIN_ID = 5334757519  # Сенин ID дарегиң
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Сенин ресурстарыңдын тизмеси
RESOURCES = [
    {"name": "Негизги канал", "url": "https://t.me/argen_70", "id": "@argen_70"},
    {"name": "Жаштар чаты (Группа)", "url": "https://t.me/taanyshuu_zhashtaryy_chat", "id": "@taanyshuu_zhashtaryy_chat"},
    {"name": "Argen 777", "url": "https://t.me/argen_77777", "id": "@argen_77777"},
    {"name": "Esbkovva", "url": "https://t.me/esbkovva", "id": "@esbkovva"},
    {"name": "Таанышуу", "url": "https://t.me/taanyyshuu", "id": "@taanyyshuu"},
]

# Канал кошуу үчүн кадамдар
class AddTask(StatesGroup):
    waiting_for_url = State()
    waiting_for_amount = State()

# --- МААЛЫМАТ БАЗАСЫ ---
def init_db():
    conn = sqlite3.connect('pr_bot.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0)')
    cursor.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, channel_id TEXT, url TEXT, price INTEGER)')
    conn.commit()
    conn.close()

def get_user_balance(user_id):
    if user_id == ADMIN_ID:
        return 999999999
    conn = sqlite3.connect('pr_bot.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)', (user_id,))
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0]

def add_balance(user_id, amount):
    if user_id == ADMIN_ID: return
    conn = sqlite3.connect('pr_bot.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
    conn.commit()
    conn.close()

# --- МЕНЮ ---
def main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="💰 Упай топтоо")],
        [KeyboardButton(text="🚀 Тапшырма кошуу"), KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="👥 Досторду чакыруу"), KeyboardButton(text="🎁 Күнүмдүк бонус")]
    ], resize_keyboard=True)

# --- БОТТУН ФУНКЦИЯЛАРЫ ---

@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
    init_db()
    await message.answer(
        f"Салам {message.from_user.first_name}! Накрутка ботуна кош келипсиз! \n\n"
        "Бул жерден сиз упай топтоп, өзүңүздүн социалдык тармактарыңызды өстүрө аласыз.", 
        reply_markup=main_menu()
    )

@dp.message(F.text == "👤 Профиль")
async def view_profile(message: types.Message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        await message.answer(f"<b>Сиздин профилиңиз:</b>\n\n👤 Статус: <b>💎 Башкы Админ</b>\n💰 Баланс: <b>♾ Чексиз</b>", parse_mode="HTML")
    else:
        balance = get_user_balance(user_id)
        await message.answer(f"<b>Сенин профилиң:</b>\n\n🆔 ID: <code>{user_id}</code>\n💰 Баланс: <b>{balance} упай</b>", parse_mode="HTML")

@dp.message(F.text == "💰 Упай топтоо")
async def earn_points(message: types.Message):
    task = random.choice(RESOURCES)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🔗 {task['name']} кириш", url=task['url'])],
        [InlineKeyboardButton(text="✅ Текшерүү", callback_data=f"check_{task['id']}")]
    ])
    await message.answer(f"<b>Тапшырма:</b>\n\n1. {task['name']} шилтемесине кирип катталыңыз.\n2. Текшерүү баскычын басып 10 упай алыңыз!", reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data.startswith("check_"))
async def check_sub(call: types.CallbackQuery):
    target_id = call.data.replace("check_", "")
    try:
        member = await bot.get_chat_member(chat_id=target_id, user_id=call.from_user.id)
        if member.status in ['member', 'administrator', 'creator']:
            add_balance(call.from_user.id, 10)
            await call.answer("Куттуктайбыз! +10 упай.", show_alert=True)
            await call.message.edit_text("✅ Катталдыңыз! Дагы упай топтоо үчүн баскычты басыңыз.")
        else:
            await call.answer("❌ Катталган жоксуз!", show_alert=True)
    except:
        await call.answer("⚠️ Ката: Бот бул каналда админ эмес.", show_alert=True)

@dp.message(F.text == "📊 Статистика")
async def view_stats(message: types.Message):
    conn = sqlite3.connect('pr_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    users_count = cursor.fetchone()[0]
    conn.close()
    await message.answer(f"📊 <b>Бот статистикасы:</b>\n\n👥 Колдонуучулар: {users_count}\n🚀 Бот активдүү!", parse_mode="HTML")

@dp.message(F.text == "🎁 Күнүмдүк бонус")
async def daily_bonus(message: types.Message):
    add_balance(message.from_user.id, 20)
    await message.answer("🎁 Сизге 20 упай бонус берилди!")

@dp.message(F.text == "👥 Досторду чакыруу")
async def referal(message: types.Message):
    bot_user = await bot.get_me()
    link = f"https://t.me/{bot_user.username}?start={message.from_user.id}"
    await message.answer(f"🤝 Досторду чакырып 50 упай алыңыз!\n\nШилтемеңиз:\n<code>{link}</code>", parse_mode="HTML")

# --- СЕРВЕР ЖАНА ИШТЕТҮҮ ---
async def handle(request): return web.Response(text="PR Bot is Live")
async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 10000)))
    await site.start()
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
