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

# Маалымат базасы (Ар бир колдонуучу үчүн өзүнчө)
users = {}

def get_user_data(user_id, name):
    if user_id not in users:
        users[user_id] = {
            "balance": 100000,
            "name": name,
            "logs": [],
            "current_bets": []
        }
    return users[user_id]

# --- RENDER WEB SERVER ---
async def handle(request): return web.Response(text="Bot is online")
async def start_webserver():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    await web.TCPSite(runner, '0.0.0.0', port).start()

# --- 1. БАЛАНС (.б) ---
@dp.message(F.text.lower() == ".б")
async def show_balance(message: types.Message):
    data = get_user_data(message.from_user.id, message.from_user.full_name)
    await message.answer(f"👤 <b>{data['name']}</b>\n💰 Баланс: <code>{data['balance']}</code>", parse_mode=ParseMode.HTML)

# --- 2. РУЛЕТКА МЕНЮСУ ---
@dp.message(F.text.lower() == "рулетка")
async def roulette_menu(message: types.Message):
    data = get_user_data(message.from_user.id, message.from_user.full_name)
    history = "".join(data["logs"][-10:]) if data["logs"] else "---"
    text = (
        f"🎰 <b>Минирулетка</b>\n━━━━━━━━━━━━━━\n"
        f"🛑 <b>Лог:</b> {history}\n"
        f"👤 <b>Аккаунт:</b> {data['name']}\n"
        f"💰 <b>Баланс:</b> {data['balance']}\n"
        f"━━━━━━━━━━━━━━\n"
        f"ℹ️ Ставка: [сумма] [к/ч] (мис: 5000 к)"
    )
    await message.answer(text, parse_mode=ParseMode.HTML)

# --- 3. СТАВКА КАБЫЛ АЛУУ (мис: 1000 к) ---
@dp.message(lambda msg: re.match(r'^\d+\s+[кчКЧ]$', msg.text))
async def place_bet(message: types.Message):
    data = get_user_data(message.from_user.id, message.from_user.full_name)
    amount, choice = message.text.split()
    amount = int(amount)
    
    if amount > data["balance"]:
        return await message.answer("❌ Баланс жетишсиз!")
    if amount <= 0: return
    
    data["balance"] -= amount
    data["current_bets"].append({"amount": amount, "choice": choice.lower()})
    await message.answer(f"✅ Ставка кабыл алынды: {amount} на {'Кызыл 🔴' if choice.lower()=='к' else 'Кара ⚫'}")

# --- 4. ГО (РУЛЕТКА ОЙНОО) ---
@dp.message(F.text.lower() == "го")
async def play_roulette(message: types.Message):
    data = get_user_data(message.from_user.id, message.from_user.full_name)
    if not data["current_bets"]:
        return await message.answer("ℹ️ Алгач ставка коюңуз!")

    msg = await message.answer(f"<b>{data['name']}</b> крутит рулетку... 🎡")
    await asyncio.sleep(2)

    win_num = random.randint(0, 12)
    win_color = "🔴" if win_num in [1,3,5,7,9,12] else ("⚫" if win_num != 0 else "🟢")
    color_key = "к" if win_color == "🔴" else ("ч" if win_color == "⚫" else "з")

    data["logs"].append(win_color)
    total_won = 0
    res_text = ""

    for bet in data["current_bets"]:
        if bet["choice"] == color_key:
            won = bet["amount"] * 2
            data["balance"] += won
            total_won += won
            res_text += f"✅ {bet['amount']} -> {won}\n"
        else:
            res_text += f"❌ {bet['amount']} -> 0\n"

    data["current_bets"] = []
    await msg.edit_text(
        f"🎰 Сан: <b>{win_num} {win_color}</b>\n━━━━━━━━━━━━━━\n{res_text}"
        f"━━━━━━━━━━━━━━\n💰 Калдык: {data['balance']}", parse_mode=ParseMode.HTML
    )

# --- 5. БАНДИТ (СЛОТ) ---
@dp.message(F.text.lower() == "бандит")
async def bandit(message: types.Message):
    data = get_user_data(message.from_user.id, message.from_user.full_name)
    bet = 5000
    if data["balance"] < bet: return await message.answer("❌ Баланс жетишсиз!")
    
    data["balance"] -= bet
    m = await message.answer(f"👤 {data['name']}\n🎰 🎰 🎰\n░░░░░░░░░░ 0%")
    
    for p in ["██░░░░ 30%", "████░░ 60%", "██████ 100%"]:
        await asyncio.sleep(0.5); await m.edit_text(f"👤 {data['name']}\n🎰 🎰 🎰\n{p}")

    res = random.choices(["💎", "🍒", "🍋", "🔔"], k=3)
    win = (res[0] == res[1] == res[2])
    if win: data["balance"] += 50000
    
    await m.edit_text(
        f"👤 <b>{data['name']}</b>\n{res[0]} | {res[1]} | {res[2]}\n━━━━━━━━━━━━━━\n"
        f"{'✅ +50000' if win else '❌ -5000'}\n💰 Баланс: {data['balance']}", parse_mode=ParseMode.HTML
    )

# --- 6. МОНЕТА БЕРҮҮ (+ [сан]) ---
@dp.message(F.text.startswith("+"))
async def gift_money(message: types.Message):
    if not message.reply_to_message: return
    try:
        amount = int(message.text.replace("+", ""))
        giver = get_user_data(message.from_user.id, message.from_user.full_name)
        receiver = get_user_data(message.reply_to_message.from_user.id, message.reply_to_message.from_user.full_name)
        
        if giver["balance"] < amount: return await message.answer("❌ Монета жетишсиз!")
        
        giver["balance"] -= amount
        receiver["balance"] += amount
        await message.answer(f"✅ <b>{giver['name']}</b> ➡️ <b>{receiver['name']}</b> ка {amount} монета берди!")
    except: pass

async def main():
    await asyncio.gather(start_webserver(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
  
