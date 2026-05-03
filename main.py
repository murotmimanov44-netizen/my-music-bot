import random
import asyncio
import os
import re
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiohttp import web

# --- CONFIGURATION ---
TOKEN = "8608898907:AAEITJNP6t-s2CiT3b7nCCSX9rGPFF5fmlU"
ADMIN_ID = 6310214652  
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Database
users = {}

def get_data(user_id, name):
    if user_id not in users:
        # Админге чексиз, башкаларга 1,000,000
        is_admin = user_id == ADMIN_ID
        users[user_id] = {
            "balance": 10**20 if is_admin else 1000000,
            "name": name,
            "logs": [],
            "bets": [],
            "last_bonus": None,
            "design": "⚔️KR🗡️ARGEN" if is_admin else name
        }
    return users[user_id]

# Render Web Server (Anti-Sleep)
async def handle(request): return web.Response(text="Bot is Elite & Active")
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
        f"👤 <b>{data['design']}</b>\n"
        f"💰 Монет в наличии: <code>{data['balance']:,}</code>",
        parse_mode=ParseMode.HTML
    )

# --- 2. БОНУС ---
@dp.message(F.text.lower() == "бонус")
async def get_bonus(message: types.Message):
    data = get_data(message.from_user.id, message.from_user.full_name)
    now = datetime.now()
    if data["last_bonus"] is None or now > data["last_bonus"] + timedelta(days=1):
        bonus = 1000000
        data["balance"] += bonus
        data["last_bonus"] = now
        await message.answer(f"🎁 <b>Ежедневный бонус!</b>\n━━━━━━━━━━━━━━\n👤 {data['design']}\n✅ Зачислено: <code>{bonus:,}</code>")
    else:
        rem = (data["last_bonus"] + timedelta(days=1)) - now
        await message.answer(f"⏳ Бонус через: <b>{int(rem.total_seconds()//3600)}ч. {int((rem.total_seconds()%3600)//60)}мин.</b>")

# --- 3. РУЛЕТКА МЕНЮ ---
@dp.message(F.text.lower() == "рулетка")
async def cmd_roulette(message: types.Message):
    data = get_data(message.from_user.id, message.from_user.full_name)
    history = "".join(data["logs"][-10:]) if data["logs"] else "🔴⚫🔴..."
    text = (
        f"🎰 <b>МИНИ-РУЛЕТКА</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"🛑 <b>Лог:</b> {history}\n"
        f"👤 <b>Аккаунт:</b> {data['design']}\n"
        f"💰 <b>Баланс:</b> {data['balance']:,}\n"
        f"━━━━━━━━━━━━━━\n"
        f"ℹ️ <i>Ставка: [сумма] [к/ч]\nПример: 50000 к</i>"
    )
    await message.answer(text, parse_mode=ParseMode.HTML)

# --- 4. ПРИЕМ СТАВКИ ---
@dp.message(lambda msg: re.match(r'^\d+\s+[кчКЧ]$', msg.text))
async def bet_handler(message: types.Message):
    data = get_data(message.from_user.id, message.from_user.full_name)
    amount, choice = message.text.split()
    amount = int(amount)
    if amount > data["balance"]: return await message.answer("❌ Баланс жетишсиз!")
    data["balance"] -= amount
    data["bets"].append({"amount": amount, "choice": choice.lower()})
    color = "🔴" if choice.lower() == 'к' else "⚫"
    await message.answer(f"✅ <b>Ставка:</b> {amount:,} на {color} принята!")

# --- 5. ГО (РУЛЕТКА) ---
@dp.message(F.text.lower() == "го")
async def go_handler(message: types.Message):
    data = get_data(message.from_user.id, message.from_user.full_name)
    if not data["bets"]: return await message.answer("ℹ️ Сначала сделайте ставку!")

    m = await message.answer(f"🎡 <b>{data['design']}</b> крутит рулетку...")
    await asyncio.sleep(2.5)

    num = random.randint(0, 12)
    win_icon, win_key = ("🟢", "з") if num == 0 else (("🔴", "к") if num in [1,3,5,7,9,12] else ("⚫", "ч"))
    data["logs"].append(win_icon)

    res_str = ""
    for b in data["bets"]:
        if b["choice"] == win_key:
            prize = b["amount"] * 2
            data["balance"] += prize
            res_str += f"✅ <b>Выиграл: +{prize:,}</b> {win_icon}\n"
        else: res_str += f"❌ <b>Проиграл: -{b['amount']:,}</b>\n"
    
    data["bets"] = []
    await m.edit_text(
        f"🎰 Результат: <b>{num} {win_icon}</b>\n"
        f"━━━━━━━━━━━━━━\n{res_str}"
        f"━━━━━━━━━━━━━━\n💰 Баланс: {data['balance']:,}",
        parse_mode=ParseMode.HTML
    )

# --- 6. БАНДИТ (ИДЕАЛЬНЫЙ ДИЗАЙН) ---
@dp.message(F.text.lower() == "бандит")
async def bandit_handler(message: types.Message):
    data = get_data(message.from_user.id, message.from_user.full_name)
    bet = 10000
    if data["balance"] < bet: return await message.answer("❌ Недостаточно монет!")
    data["balance"] -= bet

    m = await message.answer(f"👤 {data['design']}\n🎰 🎰 🎰\n░░░░░░░░░░ 0%")
    frames = ["███░░░░░░░ 30%", "██████░░░░ 65%", "██████████ 100%"]
    for f in frames:
        await asyncio.sleep(0.6); await m.edit_text(f"👤 {data['design']}\n🎰 🎰 🎰\n{f}")

    res = random.choices(["💎", "🍒", "🍋", "🔔", "⭐"], k=3)
    is_win = (res[0] == res[1] == res[2])
    if is_win:
        data["balance"] += 250000
        res_text = "✅ <b>ВЫИГРЫШ: +250,000</b> 💎"
    else: res_text = f"❌ <b>ПРОИГРЫШ: -{bet:,}</b>"

    await m.edit_text(
        f"👤 <b>{data['design']}</b>\n{res[0]} | {res[1]} | {res[2]}\n"
        f"━━━━━━━━━━━━━━\n{res_text}\n"
        f"💰 Баланс: {data['balance']:,}",
        parse_mode=ParseMode.HTML
    )

async def main():
    await asyncio.gather(start_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
  
