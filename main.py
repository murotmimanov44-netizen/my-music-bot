import random
import asyncio
import os
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiohttp import web

# --- КОНФИГУРАЦИЯ ---
TOKEN = "8608898907:AAEITJNP6t-s2CiT3b7nCCSX9rGPFF5fmlU"
USER_DESIGN = "⚔️KR🗡️ARGEN"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Маалыматтарды сактоо
user_data = {
    "balance": 5000,
    "last_bets": [], # Учурдагы ставкалар
    "logs": []       # Акыркы 10 оюндун тарыхы
}

# Render үчүн веб-сервер
async def handle(request): return web.Response(text="Bot is running!")
async def start_webserver():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    await web.TCPSite(runner, '0.0.0.0', port).start()

# --- БАЛАНС (.б) ---
@dp.message(F.text.lower() == ".б")
async def check_balance(message: types.Message):
    await message.answer(f"👤 <b>{USER_DESIGN}</b>\n💰 Калдык: <code>{user_data['balance']}</code>", parse_mode=ParseMode.HTML)

# --- РУЛЕТКА МЕНЮСУ (сүрөттөгүдөй) ---
@dp.message(F.text.lower() == "рулетка")
async def roulette_menu(message: types.Message):
    history = "".join(user_data["logs"][-10:]) if user_data["logs"] else "Оюндар боло элек"
    menu_text = (
        f"🎰 <b>Минирулетка</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"🛑 <b>Лог:</b> {history}\n"
        f"👤 <b>Аккаунт:</b> {USER_DESIGN}\n"
        f"💰 <b>Баланс:</b> {user_data['balance']}\n"
        f"━━━━━━━━━━━━━━\n"
        f"ℹ️ <i>Ставка коюу үчүн: [сумма] [к/ч]\nМисалы: 1000 к</i>"
    )
    await message.answer(menu_text, parse_mode=ParseMode.HTML)

# --- СТАВКА КАБЫЛ АЛУУ (1000 к же 5000 ч) ---
@dp.message(lambda msg: re.match(r'^\d+\s+[кчКЧ]$', msg.text))
async def process_bet(message: types.Message):
    amount, choice = message.text.split()
    amount = int(amount)
    choice = choice.lower()

    if amount > user_data["balance"]:
        return await message.answer("❌ Баланс жетишсиз!")

    user_data["balance"] -= amount
    user_data["last_bets"].append({"amount": amount, "choice": choice})
    
    color_full = "Кызыл 🔴" if choice == "к" else "Кара ⚫"
    await message.answer(f"✅ <b>Ставка кабыл алынды:</b> {amount} на {color_full}")

# --- ОЮНДУ БАШТОО (го) ---
@dp.message(F.text.lower() == "го")
async def play_go(message: types.Message):
    if not user_data["last_bets"]:
        return await message.answer("ℹ️ Алгач ставка коюңуз (мис: 1000 к)")

    await message.answer(f"<b>{USER_DESIGN}</b> крутит рулетку... 🎡")
    await asyncio.sleep(2)

    win_num = random.randint(0, 12)
    red_nums = [1, 3, 5, 7, 9, 12]
    
    if win_num == 0:
        win_color = "🟢"
        color_key = "з"
    elif win_num in red_nums:
        win_color = "🔴"
        color_key = "к"
    else:
        win_color = "⚫"
        color_key = "ч"

    # Логду жаңыртуу
    user_data["logs"].append(win_color)
    if len(user_data["logs"]) > 10: user_data["logs"].pop(0)

    total_win = 0
    results_detail = ""

    for bet in user_data["last_bets"]:
        if bet["choice"] == color_key:
            prize = bet["amount"] * 2
            user_data["balance"] += prize
            total_win += prize
            results_detail += f"✅ {bet['amount']} на {bet['choice']} — Утуш: {prize}\n"
        else:
            results_detail += f"❌ {bet['amount']} на {bet['choice']} — Утулду\n"

    # Тазалоо
    user_data["last_bets"] = []

    final_msg = (
        f"🎰 Жыйынтык: <b>{win_num} {win_color}</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"{results_detail}"
        f"━━━━━━━━━━━━━━\n"
        f"👤 <b>{USER_DESIGN}</b>\n"
        f"💰 Жаңы баланс: {user_data['balance']}"
    )
    await message.answer(final_msg, parse_mode=ParseMode.HTML)

# --- БОТТУ ИШТЕТҮҮ ---
async def main():
    await asyncio.gather(start_webserver(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
