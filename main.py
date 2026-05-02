import os, asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

# Сенин маалыматтарың
TOKEN = "8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM"
USER_NAME = "Арген" # Сенин атың

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Жөнөкөй сервер (Render үчүн)
async def handle(request): return web.Response(text="Jarvis is Online!")
async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', os.getenv('PORT', 10000))
    await site.start()

# /start буйругу
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(f"Салам, {USER_NAME}! Мен сенин жеке жардамчың Жарвисмин.\nКандай буйруктар бар?")

# Жарвистин акылдуу жооптору
@dp.message(F.text)
async def jarvis_logic(message: types.Message):
    msg = message.text.lower()
    
    # 1. Жөнөкөй саламдашуу
    if "салам" in msg or "жарвис" in msg:
        await message.answer(f"Угам сизди, {USER_NAME}. Эмне жардам керек?")
    
    # 2. Аба ырайы (Мисалы, Ош үчүн)
    elif "аба ырайы" in msg:
        await message.answer("Ош шаарында бүгүн күн ачык, ишиңизге ийгилик!")
    
    # 3. Программалоо боюнча суроо
    elif "python" in msg or "код" in msg:
        await message.answer("Сэр, код жазууда ката кетсе, мага жибериңиз. Текшерип берем.")
    
    # 4. Башка суроолорго универсалдуу жооп
    else:
        await message.answer("Түшүндүм. Бул боюнча маалымат издеп жатам...")

async def main():
    await start_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
