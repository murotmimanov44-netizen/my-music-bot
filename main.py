import asyncio
import logging
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Сенин маалыматтарың
TELEGRAM_TOKEN = '8576931278:AAECIYTCR9k81pnLy7A8R-xFjeYfgU3KEqo'
GEMINI_API_KEY = 'AIzaSyCC6MVBgZIpBd5e6or6vAbW25LOlT3ooxc'

# AI'ды жөндөө
genai.configure(api_key=GEMINI_API_KEY)

# Эгер 1.5-flash ката берсе, 1.0-pro версиясын колдонуп көрөбүз
model = genai.GenerativeModel('gemini-1.0-pro') 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

SYSTEM_PROMPT = "Сен Аргендин эң акылдуу AI жардамчысысың. Кыргызча жана орусча сүйлөйсүң."

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Салам! Мен сенин AI көчүрмөңмүн. 🤖 Эми баары иштеп жатат, каалаган нерсеңди сура!")

@dp.message()
async def chat_handler(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # prompt'ту жөнөкөйлөтүп жиберебиз
        prompt = f"{SYSTEM_PROMPT}\nКолдонуучу: {message.text}"
        response = model.generate_content(prompt)
        
        if response and response.text:
            await message.answer(response.text)
        else:
            await message.answer("Кечиресиң, жооп таба алган жокмун.")
            
    except Exception as e:
        logging.error(f"Ката: {e}")
        # Эгер 404 кайталанса, моделдин атын текшериш керек
        await message.answer("Бир аз күтө тур, мээмди иретке келтирип алайын... Кайра жазып көрчү?")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
