import asyncio
import logging
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# Сенин маалыматтарың
TELEGRAM_TOKEN = '8576931278:AAECIYTCR9k81pnLy7A8R-xFjeYfgU3KEqo'
GEMINI_API_KEY = 'AIzaSyCC6MVBgZIpBd5e6or6vAbW25LOlT3ooxc'

# AI'ды жөндөө
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash') # Эң тез иштеген модель

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Боттун "мүнөзү"
SYSTEM_PROMPT = "Сен Аргендин эң акылдуу жана ишенимдүү AI жардамчысысың. Кыргыз жана орус тилдеринде сонун сүйлөйсүң. Сенин максатың - Аргенге жана анын досторуна жардам берүү, тамашалашуу жана акылдуу кеңештерди берүү."

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Салам! Мен сенин AI көчүрмөңмүн. 🤖 Эми менде чыныгы акыл бар! Каалаган нерсеңди сура, ыр жазалы же жөн эле сүйлөшөлү. Эмнеден баштайбыз?")

@dp.message()
async def chat_handler(message: types.Message):
    # Колдонуучуга бот ойлонуп жатканын көрсөтүү
    await bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # AI'га суроо жиберүү
        prompt = f"{SYSTEM_PROMPT}\nКолдонуучу: {message.text}\nЖооп:"
        response = model.generate_content(prompt)
        
        # Жоопту жөнөтүү
        if response.text:
            await message.answer(response.text)
        else:
            await message.answer("Ммм, бул суроо боюнча ойлонуп жатам...")
            
    except Exception as e:
        logging.error(e)
        await message.answer("Бир аз техникалык мүчүлүштүк болду, кайра жазып көрчү?")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
  
