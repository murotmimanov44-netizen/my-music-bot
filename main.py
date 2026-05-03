import logging
import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

API_TOKEN = 'СЕНИН_БОТ_ТОКЕНИҢ'

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

class ChatState(StatesGroup):
    is_chatting = State()

# --- СӨЗ БАЙЛЫГЫ ---
replies = {
    "love": [
        "Ой, токточу, жүрөгүмдүн температурасы 100 градуска чыгып кетти! 🔥",
        "Сен мени ушинтип эритип жатып, акыры процессорумду күйгүзөсүң го. 🥰",
        "Сүйүү бул — сонун нерсе, бирок мага ток менен интернет көбүрөөк жагат. 😄",
        "Рахмат! Менин алгоритмдеримде сен эң сулуу адам катары белгилендиң! ✨"
    ],
    "funny": [
        "Эмне дейсиң? Дагы бир жолу айтчы, кулагыма флешка кирип калыптыр... 😂",
        "Сен аябай кызыктуу адамсың, сени менен сүйлөшсө зерикпейсиң. 👍",
        "Ой, менин башымды айлантпачы, азыр эле бир нече код жазып чарчап турам. 🤖",
        "Эгер мен адам болсом, сени менен күнү-түнү тамашалашмакмын!"
    ],
    "how_are_you": [
        "Баары чики-чики! Процессорум муздак, интернетим учкун! Өзүңдөчү? 😊",
        "Жашоо сонун! Колдонуучулар мага жылуу сөз жазса эле жыргап калам. 👋",
        "Маанайым беш! Сени менен сүйлөшүп, ого бетер көтөрүлүп жатат."
    ],
    "unknown": [
        "Бул сөзүңдү блокнотума жазып койдум, кийинчерээк маанисин изилдейм. 🤔",
        "Кызыктуу... Дагы эмнелерди билесиң?",
        "Ммм, бул тууралуу ойлонушум керек. Сен эмне деп ойлойсуң?",
        "Кел, башка темада сүйлөшөлү, бул бир аз татаал экен. 😁"
    ]
}

stop_words = ["болду", "токто", "тажадым", "стоп", "жетишет", "болду жетет", "кайырлы тун", "жатам"]

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await ChatState.is_chatting.set()
    user_name = message.from_user.first_name
    await message.answer(f"Оо, салам, {user_name}! 👋 Акыры келдиңби? Мен сени күтө берип экрандарым чарчап кетти. Кел, каалаган темада сүйлөшөлү, мен бүгүн абдан сөзгө баймын! 😊")

@dp.message_handler(state=ChatState.is_chatting)
async def main_chat(message: types.Message, state: FSMContext):
    text = message.text.lower()
    user_name = message.from_user.first_name

    # Бот бир аз "ойлонгондой" көрүнүшү үчүн (2 секунд күтүү)
    await bot.send_chat_action(message.chat.id, types.ChatActions.TYPING)
    await asyncio.sleep(1.5)

    if any(word in text for word in stop_words):
        await message.answer(f"Макул, {user_name}, эс ал анда. Мен деле бир аз зарядка алайын. Качан сагынсаң /start басып кой! 👋")
        await state.finish()
        return

    # Контексттик текшерүү
    if "сүй" in text or "люблю" in text:
        await message.answer(random.choice(replies["love"]))
    elif "кандай" in text or "калай" in text:
        await message.answer(random.choice(replies["how_are_you"]))
    elif any(word in text for word in ["тамаша", "күлкү", "кызык"]):
        await message.answer(random.choice(replies["funny"]))
    else:
        # Эгер эч нерсе окшошпосо, жалпы жоопторду берет
        await message.answer(random.choice(replies["unknown"]))

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
  
