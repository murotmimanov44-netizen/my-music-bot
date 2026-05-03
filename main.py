import random
import asyncio
import os
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiohttp import web

# --- КОНФИГУРАЦИЯ ---
TOKEN = "8608898907:AAEITJNP6t-s2CiT3b7nCCSX9rGPFF5fmlU"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Маалыматтарды сактоо (ар бир колдонуучу үчүн)
users = {}

def get_data(user_id, name):
    if user_id not in users:
        users[user_id] = {
            "balance": 100000,
            "name": name,
            "logs": [],
            "bets": []
        }
    return users[user_id]

# --- RENDER HEALTH CHECK ---
async def handle(request): return web.Response(text="Bot is running")
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
        f"💰 Сиздин балансыңыз: <code>{data['balance']}</code> монета",
        parse_mode=ParseMode.HTML
    )

# --- 2. РУЛЕТКА МЕНЮСУ ---
@dp.message(F.text.lower() == "рулетка")
async def cmd_roulette(message: types.Message):
    data = get_data(message.from_user.id, message.from_user.full_name)
    history = "".join(data["logs"][-10:]) if data["logs"] else "Оюндар жок"
    text = (
        f"🎰 <b>Минирулетка</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"🛑 <b>Лог:</b> {history}\n"
        f"👤 <b>Аккаунт:</b> {data['name']}\n"
        f"💰 <b>Баланс:</b> {data['balance']}\n"
        f"━━━━━━━━━━━━━━\n"
        f"ℹ️ <i>Ставка коюу: [сумма] [к/ч]\nМисалы: 5000 к</i>"
    )
    await message.answer(text, parse_mode=ParseMode.HTML)

# --- 3. СТАВКА КАБЫЛ АЛУУ ---
@dp.message(lambda msg: re.match(r'^\d+\s+[кчКЧ]$', msg.text))
async def place_bet(message: types.Message):
    data = get_data(message.from_user.id, message.from_user.full_name)
    parts = message.text.split()
    amount = int(parts[0])
    choice = parts[1].lower()

    if amount > data["balance"]:
        return await message.answer("❌ Сизде жетиштүү монета жок!")
    
    data["balance"] -= amount
    data["bets"].append({"amount": amount, "choice": choice})
    await message.answer(f"✅ <b>Ставка кабыл алынды:</b> {amount} на {'Кызыл 🔴' if choice=='к' else 'Кара ⚫'}")

# --- 4. ГО (ОЮНДУ БАШТОО) ---
@dp.message(F.text.lower() == "го")
async def play_go(message: types.Message):
    data = get_data(message.from_user.id, message.from_user.full_name)
    if not data["bets"]:
        return await message.answer("ℹ️ Алгач ставка коюңуз!")

    msg = await message.answer(f"<b>{data['name']}</b> крутит рулетку... 🎡")
    await asyncio.sleep(2)

    win_num = random.randint(0, 12)
    if win_num == 0:
        win_color, color_key = "🟢", "з"
    elif win_num in [1,3,5,7,9,12]:
        win_color, color_key = "🔴", "к"
    else:
        win_color, color_key = "⚫", "ч"

    data["logs"].append(win_color)
    if len(data["logs"]) > 10: data["logs"].pop(0)

    res_details = ""
    for bet in data["bets"]:
        if bet["choice"] == color_key:
            prize = bet["amount"] * 2
            data["balance"] += prize
            res_details += f"✅ {bet['amount']} на {bet['choice']} — <b>Утуш: {prize}</b>\n"
        else:
            res_details += f"❌ {bet['amount']} на {bet['choice']} — Утулду\n"

    data["bets"] = [] # Ставкаларды тазалоо
    await msg.edit_text(
        f"🎰 Жыйынтык: <b>{win_num} {win_color}</b>\n"
        f"━━━━━━━━━━━━━━\n{res_details}"
        f"━━━━━━━━━━━━━━\n"
        f"💰 Калдык баланс: <b>{data['balance']}</b>",
        parse_mode=ParseMode.HTML
    )

# --- 5. БАНДИТ (СЛОТ) ---
@dp.message(F.text.lower() == "бандит")
async def bandit(message: types.Message):
    data = get_data(message.from_user.id, message.from_user.full_name)
    bet = 2000
    if data["balance"] < bet: return await message.answer("❌ Баланс жетишсиз!")
    
    data["balance"] -= bet
    m = await message.answer(f"👤 {data['name']}\n🎰 🎰 🎰\n░░░░░░░░░░ 0%")
    
    for p in ["███░░░░░ 35%", "██████░░ 75%", "████████ 100%"]:
        await asyncio.sleep(0.5)
        await m.edit_text(f"👤 {data['name']}\n🎰 🎰 🎰\n{p}")

    symbols = ["💎", "🍒", "🍋", "🔔", "⭐"]
    res = random.choices(symbols, k=3)
    
    if res[0] == res[1] == res[2]:
        data["balance"] += 20000
        status = "✅ ВЫИГРЫШ: +20000 💎"
    else:
        status = "❌ ПРОИГРЫШ: -2000"

    await m.edit_text(
        f"👤 <b>{data['name']}</b>\n{res[0]} | {res[1]} | {res[2]}\n"
        f"━━━━━━━━━━━━━━\n{status}\n"
        f"💰 Баланс: {data['balance']}",
        parse_mode=ParseMode.HTML
    )

# --- 6. МОНЕТА БЕРҮҮ (+1000) ---
@dp.message(F.text.startswith("+"))
async def give_money(message: types.Message):
    if not message.reply_to_message: return
    try:
        val = int(message.text.replace("+", ""))
        giver = get_data(message.from_user.id, message.from_user.full_name)
        receiver = get_data(message.reply_to_message.from_user.id, message.reply_to_message.from_user.full_name)
        
        if giver["balance"] >= val:
            giver["balance"] -= val
            receiver["balance"] += val
            await message.answer(f"✅ {giver['name']} берди {val} монета {receiver['name']}ка")
    except: pass

async def main():
    await asyncio.gather(start_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
