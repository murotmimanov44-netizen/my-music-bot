import os, asyncio
from aiogram import Bot, Dispatcher, types, F
from aiohttp import web
import g4f

TOKEN = "8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM"
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def handle(request): return web.Response(text="AI Jarvis is Online!")
async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', os.getenv('PORT', 10000))
    await site.start()

# AI функциясы
async def ask_ai(prompt):
    try:
        response = await g4f.ChatCompletion.create_async(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        return response
    except:
        return "Ката кетти, кайра аракет кыл."

@dp.message(F.text)
async def main_handler(message: types.Message):
    text = message.text
    
    # Эгер билдирүү "AI " менен башталса гана жооп берет
    if text.lower().startswith("ai "):
        # Билдирүүдөн "AI " деген сөздү кесип салып, калган суроону AIга жөнөтөбүз
        prompt = text[3:].strip()
        
        if not prompt:
            await message.answer("Сурооңузду жазыңыз.")
            return

        await bot.send_chat_action(message.chat.id, action="typing")
        answer = await ask_ai(prompt)
        await message.answer(answer)
    
    # Эгер AI деп башталбаса, бот унчукпайт (эч нерсе дебейт)

async def main():
    await start_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
