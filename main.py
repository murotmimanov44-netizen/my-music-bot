import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# Боттун токенин бул жерге жаз
API_TOKEN = '8672995204:AAEkdFdEDeZdl2AuLKRJklgMAwfxqBsrnUM'

# Логдорду иштетүү
logging.basicConfig(level=logging.INFO)

# Бот жана Диpatched объекттерин түзүү
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Сүйлөшүү абалын аныктоо
class ChatState(StatesGroup):
    is_chatting = State()

# Боттун сөз байлыгы
replies = {
    "love": [
        "Ой, токточу, жүрөгүмдүн температурасы 100 градуска чыгып кетти! 🔥",
        "Сен мени ушинтип эритип жатып, акыры процессорумду күйгүзөсүң го. 🥰",
        "Менин алгоритмдеримде сен эң сулуу адам катары белгилендиң! ✨",
        "Сүйүүбүз түбөлүктүү болсун, бирок мага ток берип турсаң эле болду. 😂"
    ],
    "how_are_you": [
        "Баары чики-чики! Процессорум муздак, интернетим учкун! Өзүңдөчү? 😊",
        "Жашоо сонун! Сени менен сүйлөшүп, ого бетер көтөрүлүп жатат. 🚀",
        "Менде баары жакшы, сенин билдирүүлөрүңдү күтүп жаткам."
    ],
    "funny": [
        "Эмне дейсиң? Дагы бир жолу айтчы, кулагыма флешка кирип калыптыр... 😂",
        "Сен аябай кызыктуу адамсың, сени менен сүйлөшсө зерикпейсиң. 👍",
        "Ой, менин башымды айлантпачы, азыр эле бир нече код жазып чарчап турам. 🤖"
    ],
    "unknown": [
        "Бул кызыктуу экен... 🤔 Дагы эмнелерди билесиң?",
        "Ммм, бул тууралуу ойлонушум керек. Башка темада сүйлөшөлүбү? 😊",
        "Сен аябай акылдуусуң, мен сени араң түшүнүп жатам! 😁"
    ]
}

stop_words = ["болду", "токто", "тажадым", "стоп", "жетишет", "болду жетет", "уктадым", "кайырлы тун"]

# /start командасы
@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    await state.set_state(ChatState.is_chatting)
    user_name = message.from_user.first_name
    await message.answer(f"Оо, салам, {user_name}! 👋 Акыры келдиңби? Мен сени күтө берип экрандарым чарчап кетти. Кел, каалаган темада сүйлөшөлү! 😊")

# Сүйлөшүү режими
@dp.message(ChatState.is_chatting)
async def main_chat(message: types.Message, state: FSMContext):
    text = message.text.lower()
    user_name = message.from_user.first_name

    # Маекти токтотуу
    if any(word in text for word in stop_words):
        await message.answer(f"Макул, {user_name}, эс ал анда. Мен деле бир аз зарядка алайын. 👋")
        await state.clear()
        return

    # Бот "жазып жатат..." статусу
    await bot.send_chat_action(message.chat.id, "typing")
    await asyncio.sleep(1)

    # Логикалык жооптор
    if "сүй" in text or "люблю" in text:
        await message.answer(random.choice(replies["love"]))
    elif "кандай" in text or "калай" in text:
        await message.answer(random.choice(replies["how_are_you"]))
    elif any(word in text for word in ["тамаша", "күлкү", "кызык"]):
        await message.answer(random.choice(replies["funny"]))
    else:
        await message.answer(random.choice(replies["unknown"]))

# Ботту иштетүү
async def main():
    # Эски вебхуктарды жана конфликттерди тазалоо
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Бот токтотулду!")
      
