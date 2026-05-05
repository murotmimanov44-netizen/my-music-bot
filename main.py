import os
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Конфигурация
API_TOKEN = "8214859958:AAHz1JKP_ylFjmjOUK42UMgA4xE_hR0gMq8"
GEMINI_KEY = os.getenv("GEMINI_API_KEY") 

# Сүрөттүн шилтемеси (ушул жерге сүрөттүн интернеттеги шилтемесин кой)
ANISA_PHOTO = "СҮРӨТТҮН_ШИЛТЕМЕСИ" 

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # Саламдашканда сүрөт менен кошо жооп берет
    await message.answer_photo(ANISA_PHOTO, caption="Салам! Мен Анисамын. 🌸 Мени чакырсаңыз, ар дайым жаныңыздамын!")

@dp.message_handler()
async def anisa_talk(message: types.Message):
    text = message.text.lower()
    
    if "аниса" in text:
        prompt = text.replace("аниса", "").strip()
        
        # Эгер жөн эле "Аниса" деп жазса, сүрөтүн көрсөтүп эркелеп жооп берет
        if not prompt:
            await message.answer_photo(ANISA_PHOTO, caption="Ооба, угуп жатам? 😊")
            return

        try:
            ai_prompt = f"Сен - Аниса аттуу кыргыз кызысың. Колдонуучунун мына бул сөзүнө кыргызча жагымдуу жооп бер: {prompt}"
            response = model.generate_content(ai_prompt)
            await message.reply(response.text)
        except Exception:
            await message.reply("Кечиресиз, бир аз ойлонуп калдым. ✨")
          
