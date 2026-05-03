import random
import asyncio
import os
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiohttp import web

# --- КОНФИГУРАЦИЯ ---
TOKEN = "8608898907:AAEITJNP6t-s2CiT3b7nCCSX9rGPFF5fmlU"
ADMIN_ID = 6310214652  # Бул жерге өзүңүздүн Telegram ID'ңизди жазсаңыз болот
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Маалымат базасы
users = {}

def get_data(user_id, name):
    if user_id not in users:
        # Жаңы келген колдонуучуга 1,000,000 монета
        # Ал эми Сиз (Админ) болсоңуз, чексиз баланс
        initial_balance = 10000000000000000000 if user_id == ADMIN_ID else 1000000
        users[user_id] = {
            "balance": initial_balance,
            "name": name,
            "logs": [],
            "bets": []
        }
    return users[user_id]

# Render үчүн сервер
async def handle(request): return web.Response(text="Bot is Active")
async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    await web.TCPSite(runner, '0.0.0.0', port).start()

# --- 1. БАЛАНС (.б) ---
@dp.message(F.text.lower() == ".б")
async def cmd_balance(message: types.Message):
    data = get_data(message.from_user.id, message.from_user.full_name)
    await message.answer(
        f"👤 <b>{data['name']}</b>\n"
        f"💰 Баланс: <code>{data['balance']}</code> монета",
        parse_mode=ParseMode.HTML
    )

# --- 2. РУЛЕТКА МЕНЮСУ ---
@dp.message(F.text.lower() == "рулетка")
async def cmd_roulette_menu(message: types.Message):
    data = get_data(message.from_user.id, message.from_user.full_name)
    history = "".join(data["logs"][-10:]) if data["logs"] else "---"
    
    text = (
        f"🎰 <b>Минирулетка</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"🛑 <b>Лог:</b> {history}\n"
        f"👤 <b>Аккаунт:</b> {data['name']}\n"
        f"💰 <b>Баланс:</b> {data['balance']}\n"
        f"━━━━━━━━━━━━━━\n"
        f"ℹ️ Ставка: [сумма] [к/ч]\n"
        f"Мисалы: 50000 к"
    )
    await message.answer(text, parse_mode=ParseMode.HTML)

# --- 3. СТАВКА КАБЫЛ АЛУУ ---
@dp.message(lambda msg: re.match(r'^\d+\s+[кчКЧ]$', msg.text))
async def process_bet(message: types.Message):
    data = get_data(message.from_user.id, message.from_user.full_name)
    parts = message.text.split()
    amount = int(parts[0])
    choice = parts[1].lower()

    if amount > data["balance"]:
        return await message.answer("❌ Балансыңыз жетишсиз!")
    
    data["balance"] -= amount
    data["bets"].append({"amount": amount, "choice": choice})
    color_text = "Кызыл 🔴" if choice == 'к' else "Кара ⚫"
    await message.answer(f"✅ <b>{data['name']}</b>, {amount} на {color_text} кабыл алынды!")

# --- 4. ГО (ОЮНДУ БАШТОО) ---
@dp.message(F.text.lower() == "го")
async def play_go(message: types.Message):
    data = get_data(message.from_user.id, message.from_user.full_name)
    if not data["bets"]:
        return await message.answer("ℹ️ Алгач ставка коюңуз!")

    msg = await message.answer(f"🎡 <b>{data['name']}</b> крутит...")
    await asyncio.sleep(2)

    win_num = random.randint(0, 12)
    win_color, win_key = ("🟢", "з") if win_num == 0 else (("🔴", "к") if win_num in [1,3,5,7,9,12] else ("⚫", "ч"))
    
    data["logs"].append(win_color)
    res_details = ""
    for b in data["bets"]:
        if b["choice"] == win_key:
            prize = b["amount"] * 2
            data["balance"] += prize
            res_details += f"✅ <b>Утуш: +{prize}</b> ({win_color})\n"
        else:
            res_details += f"❌ <b>Утулду: -{b['amount']}</b>\n"

    data["bets"] = []
    await msg.edit_text(
        f"🎰 Жыйынтык: <b>{win_num} {win_color}</b>\n"
        f"━━━━━━━━━━━━━━\n{res_details}"
        f"━━━━━━━━━━━━━━\n"
        f"💰 Баланс: {data['balance']}",
        parse_mode=ParseMode.HTML
    )

# --- 5. БАНДИТ (СЛОТ) ---
@dp.message(F.text.lower() == "бандит")
async def cmd_bandit(message: types.Message):
    data = get_data(message.from_user.id, message.from_user.full_name)
    bet = 10000
    if data["balance"] < bet: return await message.answer("❌ Монета жетишсиз!")
    
    data["balance"] -= bet
    m = await message.answer(f"👤 {data['name']}\n🎰 🎰 🎰\n░░░░░░░░░░ 0%")
    
    for p in ["███░░░ 35%", "██████ 70%", "██████████ 100%"]:
        await asyncio.sleep(0.5); await m.edit_text(f"👤 {data['name']}\n🎰 🎰 🎰\n{p}")

    res = random.choices(["💎", "🍒", "🍋", "🔔", "⭐"], k=3)
    if res[0] == res[1] == res[2]:
        data["balance"] += 100000
        status = "✅ <b>ВЫИГРЫШ: +100,000</b> 💎"
    else:
        status = f"❌ <b>ПРОИГРЫШ: -{bet}</b>"

    await m.edit_text(
        f"👤 <b>{data['name']}</b>\n{res[0]} | {res[1]} | {res[2]}\n"
        f"━━━━━━━━━━━━━━\n{status}\n"
        f"💰 Баланс: {data['balance']}",
        parse_mode=ParseMode.HTML
    )

# --- БОТТУ ИШТЕТҮҮ ---
async def main():
    await asyncio.gather(start_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
  
