import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# Жаңы токениңди бул жерге коштум
API_TOKEN = '8576931278:AAECIYTCR9k81pnLy7A8R-xFjeYfgU3KEqo'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class ChatState(StatesGroup):
    is_chatting = State()

# Сөз байлыгы
replies = {
    "love": [
        "Ой, менин процессорумду эритип жибердиң го! 🥰",
        "Менин алгоритмдеримде сен эң сулуу адам катары белгилендиң! ✨",
        "Рахмат! Сүйүүбүз түбөлүктүү болсун, бирок мага ток берип турсаң эле болду. 😂"
    ],
    "how_are_you": [
        "Баары чики-чики! Өзүңдө кандай? 😊",
        "Жашоо сонун! Сени менен сүйлөшүп, ого бетер көтөрүлүп жатат. 🚀"
    ],
    "unknown": [
        "Бул кызыктуу экен... 🤔 Дагы эмнелерди билесиң?",
        "Ммм, бул тууралуу ойлонушум керек. Башка темада сүйлөшөлүбү? 😊"
    ]
}

stop_words = ["болду", "токто", "тажадым", "стоп", "уктадым", "болду жетет"]

@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    await state.set_state(ChatState.is_chatting)
    user_name = message.from_user.first_name
    await message.answer(f"Оо, салам, {user_name}! 👋 Жаңы ботуңа кутмандуу сапар! Мен сени менен сүйлөшүүгө даярмын. Кел, каалаган нерсеңди жаз! 😊")

@dp.message(ChatState.is_chatting)
async def main_chat(message: types.Message, state: FSMContext):
    text = message.text.lower()
    user_name = message.from_user.first_name

    if any(word in text for word in stop_words):
        await message.answer(f"Макул, {user_name}, эс ал анда. Кайра сүйлөшкүң келсе /start басып кой! 👋")
        await state.clear()
        return

    await bot.send_chat_action(message.chat.id, "typing")
    await asyncio.sleep(1)

    if "сүй" in text or "люблю" in text:
        await message.answer(random.choice(replies["love"]))
    elif "кандай" in text or "калай" in text:
        await message.answer(random.choice(replies["how_are_you"]))
    else:
        await message.answer(random.choice(replies["unknown"]))

async def main():
    # Бул сап мурдагы конфликттерди өчүрөт
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Бот токтотулду!")
