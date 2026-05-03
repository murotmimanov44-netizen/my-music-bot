import random
import asyncio
import os
import re
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiohttp import web

# --- КОНФИГУРАЦИЯ ---
TOKEN = "8608898907:AAEITJNP6t-s2CiT3b7nCCSX9rGPFF5fmlU"
ADMIN_ID = 6310214652  
bot = Bot(token=TOKEN)
dp = Dispatcher()

# База данных (в памяти)
users = {}

def get_data(user_id, name):
    if user_id not in users:
        # Для админа бесконечность, для остальных 1 миллион при старте
        initial_balance = 10000000000000000000 if user_id == ADMIN_ID else 1000000
        users[user_id] = {
            "balance": initial_balance,
            "name": name,
            "logs": [],
            "bets": [],
            "last_bonus": None # Время последнего получения бонуса
        }
    return users[user_id]

# Render Health Check
async def handle(request): return web.Response(text="Бот активен")
async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    await web.TCPSite(runner, '0.0.0.0', port).start()

# --- 1. ЕЖЕДНЕВНЫЙ БОНУС ---
@dp.message(F.text.lower() == "бонус")
async def daily_bonus(message: types.Message):
    data = get_data(message.from_user.id, message.from_user.full_name)
    now = datetime.now()
    
    # Проверка времени
    if data["last_bonus"] is None or now > data["last_bonus"] + timedelta(days=1):
        bonus_amount = 1000000
        data["balance"] += bonus_amount
        data["last_bonus"] = now
        await message.answer(
            f"🎁 <b>Ежедневный бонус!</b>\n"
            f"━━━━━━━━━━━━━━\n"
            f"👤 <b>{data['name']}</b>, вы получили <code>{bonus_amount}</code> монет!\n"
            f"💰 Ваш новый баланс: <b>{data['balance']}</b>\n"
            f"🕒 Приходите завтра за новым бонусом!",
            parse_mode=ParseMode.HTML
        )
    else:
        # Расчет времени до следующего бонуса
        next_bonus = data["last_bonus"] + timedelta(days=1)
        remaining = next_bonus - now
        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)
        
        await message.answer(
            f"⏳ <b>{data['name']}</b>, вы уже забирали бонус!\n"
            f"Следующий бонус доступен через: <b>{hours}ч. {minutes}мин.</b>",
            parse_mode=ParseMode.HTML
        )

# --- 2. БАЛАНС (.б) ---
@dp.message(F.text.lower() == ".б")
async def cmd_balance(message: types.Message):
    data = get_data(message.from_user.id, message.from_user.full_name)
    await message.answer(
        f"👤 <b>{data['name']}</b>\n"
        f"💰 Монет в наличии: <code>{data['balance']}</code>",
        parse_mode=ParseMode.HTML
    )

# --- 3. МЕНЮ РУЛЕТКИ ---
@dp.message(F.text.lower() == "рулетка")
async def cmd_roulette_menu(message: types.Message):
    data = get_data(message.from_user.id, message.from_user.full_name)
    history = "".join(data["logs"][-10:]) if data["logs"] else "🔴⚫🔴..."
    text = (
        f"🎰 <b>Мини-рулетка</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"🛑 <b>Лог:</b> {history}\n"
        f"👤 <b>Аккаунт:</b> {data['name']}\n"
        f"💰 <b>Баланс:</b> {data['balance']}\n"
        f"━━━━━━━━━━━━━━\n"
        f"ℹ️ Ставка: [сумма] [к/ч]\n"
        f"Пример: 50000 к"
    )
    await message.answer(text, parse_mode=ParseMode.HTML)

# --- 4. ПРИЕМ СТАВКИ ---
@dp.message(lambda msg: re.match(r'^\d+\s+[кчКЧ]$', msg.text))
async def process_bet(message: types.Message):
    data = get_data(message.from_user.id, message.from_user.full_name)
    parts = message.text.split()
    amount = int(parts[0])
    choice = parts[1].lower()

    if amount > data["balance"]:
        return await message.answer("❌ Недостаточно монет!")
    
    data["balance"] -= amount
    data["bets"].append({"amount": amount, "choice": choice})
    color = "Красное 🔴" if choice == 'к' else "Черное ⚫"
    await message.answer(f"✅ Ставка {amount} на {color} принята!")

# --- 5. ГО (ЗАПУСК) ---
@dp.message(F.text.lower() == "го")
async def play_go(message: types.Message):
    data = get_data(message.from_user.id, message.from_user.full_name)
    if not data["bets"]:
        return await message.answer("ℹ️ Сначала сделайте ставку!")

    m = await message.answer(f"🎡 <b>{data['name']}</b> крутит рулетку...")
    await asyncio.sleep(2)

    num = random.randint(0, 12)
    icon, key = ("🟢", "з") if num == 0 else (("🔴", "к") if num in [1,3,5,7,9,12] else ("⚫", "ч"))
    
    data["logs"].append(icon)
    res_details = ""
    for b in data["bets"]:
        if b["choice"] == key:
            prize = b["amount"] * 2
            data["balance"] += prize
            res_details += f"✅ Выигрыш: +{prize} {icon}\n"
        else:
            res_details += f"❌ Проигрыш: -{b['amount']}\n"

    data["bets"] = []
    await m.edit_text(
        f"🎰 Результат: <b>{num} {icon}</b>\n"
        f"━━━━━━━━━━━━━━\n{res_details}"
        f"━━━━━━━━━━━━━━\n"
        f"💰 Остаток: <b>{data['balance']}</b>",
        parse_mode=ParseMode.HTML
    )

# --- 6. БАНДИТ (СЛОТ) ---
@dp.message(F.text.lower() == "бандит")
async def cmd_bandit(message: types.Message):
    data = get_data(message.from_user.id, message.from_user.full_name)
    bet = 10000
    if data["balance"] < bet: return await message.answer("❌ Недостаточно монет!")
    
    data["balance"] -= bet
    m = await message.answer(f"👤 {data['name']}\n🎰 🎰 🎰\n░░░░░░░░░░ 0%")
    
    for p in ["███░░░ 35%", "██████ 70%", "██████████ 100%"]:
        await asyncio.sleep(0.5); await m.edit_text(f"👤 {data['name']}\n🎰 🎰 🎰\n{p}")

    res = random.choices(["💎", "🍒", "🍋", "🔔"], k=3)
    if res[0] == res[1] == res[2]:
        data["balance"] += 150000
        win = "✅ <b>ВЫИГРЫШ: +150,000</b> 💎"
    else:
        win = f"❌ <b>ПРОИГРЫШ: -{bet}</b>"

    await m.edit_text(
        f"👤 <b>{data['name']}</b>\n{res[0]} | {res[1]} | {res[2]}\n"
        f"━━━━━━━━━━━━━━\n{win}\n"
        f"💰 Баланс: {data['balance']}",
        parse_mode=ParseMode.HTML
    )

# --- ЗАПУСК ---
async def main():
    await asyncio.gather(start_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
