import random
import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiohttp import web

# --- КОНФИГУРАЦИЯ ---
TOKEN = "8608898907:AAEITJNP6t-s2CiT3b7nCCSX9rGPFF5fmlU"
USER_DESIGN = "⚔️KR🗡️ARGEN"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Колдонуучунун балансы
user_data = {"balance": 5000}

# --- ВЕБ-СЕРВЕР (Render үчүн) ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_webserver():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render берген портту колдонот же стандарттык 8080
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- БАЛАНС (.б) ---
@dp.message(F.text == ".б")
async def check_balance(message: types.Message):
    await message.answer(
        f"👤 <b>{USER_DESIGN}</b>\n💰 Калдык: <code>{user_data['balance']}</code>",
        parse_mode=ParseMode.HTML
    )

# --- БАНДИТ (Видеодогу дизайн) ---
@dp.message(F.text == "Бандит")
async def play_slots(message: types.Message):
    bet = 1000
    if user_data["balance"] < bet:
        return await message.answer("❌ Баланс жетишсиз!")

    user_data["balance"] -= bet
    status_msg = await message.answer(f"👤 {USER_DESIGN}\n🎰 🎰 🎰\n░░░░░░░░░░ 0%")
    
    frames = ["█░░░░░░░░░ 20%", "████░░░░░░ 45%", "███████░░░ 75%", "██████████ 100%"]
    for frame in frames:
        await asyncio.sleep(0.5)
        await status_msg.edit_text(f"👤 {USER_DESIGN}\n🎰 🎰 🎰\n{frame}")

    symbols = ["💎", "🍒", "🍋", "🔔", "⭐"]
    res = random.choices(symbols, k=3)
    
    if res[0] == res[1] == res[2]:
        user_data["balance"] += 3000
        result_text = "Выигрыш: 3000 💎"
        icon = "✅"
    else:
        result_text = f"Проигрыш: {bet} 🌑"
        icon = "❌"

    await status_msg.edit_text(
        f"👤 <b>{USER_DESIGN}</b>\n{res[0]} | {res[1]} | {res[2]}\n━━━━━━━━━━━━\n"
        f"{icon} {result_text}\n💰 Баланс: {user_data['balance']}",
        parse_mode=ParseMode.HTML
    )

# --- РУЛЕТКА (Го) ---
@dp.message(F.text == "Го")
async def play_roulette(message: types.Message):
    if user_data["balance"] < 1000:
        return await message.answer("❌ Баланс жетишсиз!")

    user_data["balance"] -= 1000
    await message.answer(f"<b>{USER_DESIGN}</b> крутит...", parse_mode=ParseMode.HTML)
    await asyncio.sleep(2)
    
    win_num = random.randint(0, 12)
    win_color = "🟢" if win_num == 0 else ("🔴" if win_num in [1,3,5,7,9,12] else "⚫")
    
    if win_color == "🔴":
        user_data["balance"] += 2000
        status = f"уттуңуз! (+2000)"
    else:
        status = f"утулдуңуз..."

    await message.answer(
        f"Рулетка: {win_num} {win_color}\n<b>{USER_DESIGN}</b> {status}\n💰 Калдык: {user_data['balance']}",
        parse_mode=ParseMode.HTML
    )

# --- БОТТУ ИШТЕТҮҮ ---
async def main():
    # Веб-серверди жана ботту бир убакта иштетүү
    await asyncio.gather(
        start_webserver(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
