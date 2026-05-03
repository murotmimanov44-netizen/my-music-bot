import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# Токенди жаз
API_TOKEN = '8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class ChatState(StatesGroup):
    is_chatting = State()

replies = {
    "love": ["Ой, токточу, жүрөгүмдүн температурасы 100 градуска чыгып кетти! 🔥", "Сен мени ушинтип эритип жатып, акыры процессорумду күйгүзөсүң го. 🥰", "Рахмат! Менин алгоритмдеримде сен эң сулуу адам катары белгилендиң! ✨"],
    "how_are_you": ["Баары чики-чики! Өзүңдөчү? 😊", "Жашоо сонун! Сени менен сүйлөшүп, ого бетер көтөрүлүп жатат."],
    "unknown": ["Бул кызыктуу экен... 🤔", "Ммм, дагы эмнелерди билесиң?", "Кел, башка темада сүйлөшөлү! 😁"]
}

@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    await state.set_state(ChatState.is_chatting)
    await message.answer(f"Салам, {message.from_user.first_name}! 👋 Акыры келдиңби? Кел, сүйлөшөлү, мен бүгүн абдан сөзгө баймын! 😊")

@dp.message(ChatState.is_chatting)
async def main_chat(message: types.Message, state: FSMContext):
    text = message.text.lower()
    
    if any(word in text for word in ["болду", "токто", "тажадым", "стоп"]):
        await message.answer("Макул, эс ал анда! 👋")
        await state.clear()
        return

    await bot.send_chat_action(message.chat.id, "typing")
    await asyncio.sleep(1)

    if "сүй" in text or "люблю" in text:
        await message.answer(random.choice(replies["love"]))
    elif "кандай" in text:
        await message.answer(random.choice(replies["how_are_you"]))
    else:
        await message.answer(random.choice(replies["unknown"]))

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
  
