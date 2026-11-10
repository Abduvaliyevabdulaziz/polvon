import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

# ----------------- КОНФИГУРАЦИЯ -----------------
BOT_TOKEN = "9091596098:AAFmExL612_Ey6ZTyQO2zKvubkAC34vNx1Q"
ADMIN_ID = 1410351628  # Ваш числовой Telegram ID
# ------------------------------------------------

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class Form(StatesGroup):
    language = State()
    category = State()
    waiting_for_input = State()


TEXTS = {
    "ru": {
        "welcome": "👋 Здравствуйте!Заяки можно отправить с 20:00 по 21:00  Пожалуйста, выберите язык:\n\n👋 Assalomu alaykum! Arizalarni faqatgina:20:00 dan 21:00 oralig'ida jo'natishingiz mumkun Iltimos, tilni tanlang:",
        "choose_action": "Выберите нужный раздел из меню ниже:",
        "btn_complaint": "⚠️ Жалоба / Претензия",
        "btn_improvement": "💡 Идея по улучшению продукта",
        "btn_order": "📦 Предложение / Заказ на продукт",
        "btn_lang": "🌐 Сменить язык",
        "prompt_complaint": "Пожалуйста, опишите вашу жалобу подробно. Вы также можете отправить фото.",
        "prompt_improvement": "Напишите ваше предложение или идею, что нам стоит улучшить или добавить:",
        "prompt_order": "Напишите, какой продукт вас интересует, количество или ваши пожелания:",
        "received": "✅ Спасибо! Ваше сообщение принято и передано руководству.",
        "btn_back": "⬅️ Отмена / Назад",
    },
    "uz": {
        "welcome": "👋 Assalomu alaykum! Arizalarni faqatgina:20:00 dan 21:00 oralig'ida jo'natishingiz mumkun Iltimos, tilni tanlang: \n\n👋 Здравствуйте! Заяки можно отправить с 20:00 по 21:00  Пожалуйста, выберите язык:",
        "choose_action": "Quyidagi bo'limlardan birini tanlang:",
        "btn_complaint": "⚠️ Shikoyat / E'tiroz",
        "btn_improvement": "💡 Mahsulotni yaxshilash bo'yicha taklif",
        "btn_order": "📦 Taklif yoki buyurtma berish",
        "btn_lang": "🌐 Tilni o'zgartirish",
        "prompt_complaint": "Iltimos, shikoyatingizni batafsil yozib qoldiring. Rasm ham yuborishingiz mumkin.",
        "prompt_improvement": "Mahsulotimizni qanday yaxshilash yoki nima qo'shish bo'yicha taklifingizni yozing:",
        "prompt_order": "Qaysi mahsulot yoki qanday buyurtma sizni qiziqtirayotganini yozib qoldiring:",
        "received": "✅ Rahmat! Xabaringiz qabul qilindi va rahbariyatga yetkazildi.",
        "btn_back": "⬅️ Bekor qilish / Orqaga",
    },
}


def get_lang_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
                InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz"),
            ]
        ]
    )


def get_main_keyboard(lang: str):
    t = TEXTS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t["btn_complaint"])],
            [KeyboardButton(text=t["btn_improvement"])],
            [KeyboardButton(text=t["btn_order"])],
            [KeyboardButton(text=t["btn_lang"])],
        ],
        resize_keyboard=True,
    )


def get_cancel_keyboard(lang: str):
    t = TEXTS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t["btn_back"])]],
        resize_keyboard=True,
    )


# --- Старт и смена языка ---
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(TEXTS["ru"]["welcome"], reply_markup=get_lang_keyboard())
    await state.set_state(Form.language)


@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(lang=lang)
    await callback.message.delete()
    await callback.message.answer(
        TEXTS[lang]["choose_action"], reply_markup=get_main_keyboard(lang)
    )
    await state.set_state(Form.category)


@dp.message(Form.category)
async def process_menu_selection(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    t = TEXTS[lang]
    text = message.text

    if text in [TEXTS["ru"]["btn_lang"], TEXTS["uz"]["btn_lang"]]:
        await message.answer(t["welcome"], reply_markup=get_lang_keyboard())
        await state.set_state(Form.language)
        return

    category_map = {
        t["btn_complaint"]: ("Жалоба / Shikoyat", t["prompt_complaint"]),
        t["btn_improvement"]: (
            "Идея по улучшению / Taklif",
            t["prompt_improvement"],
        ),
        t["btn_order"]: ("Предложение заказа / Buyurtma", t["prompt_order"]),
    }

    if text in category_map:
        cat_name, prompt = category_map[text]
        await state.update_data(selected_category=cat_name)
        await message.answer(prompt, reply_markup=get_cancel_keyboard(lang))
        await state.set_state(Form.waiting_for_input)
    else:
        await message.answer(t["choose_action"], reply_markup=get_main_keyboard(lang))


# --- Приём обращения от клиента ---
@dp.message(Form.waiting_for_input)
async def handle_user_submission(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    category = data.get("selected_category", "Обращение")
    t = TEXTS[lang]

    if message.text in [TEXTS["ru"]["btn_back"], TEXTS["uz"]["btn_back"]]:
        await message.answer(
            t["choose_action"], reply_markup=get_main_keyboard(lang)
        )
        await state.set_state(Form.category)
        return

    user = message.from_user
    username_str = f"@{user.username}" if user.username else "Нет юзернейма"
    
    # В начало сообщения добавляем специальный тег с ID пользователя #id123456789
    admin_header = (
        f"📩 <b>НОВОЕ ОБРАЩЕНИЕ</b> #id{user.id}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>Категория:</b> {category}\n"
        f"👤 <b>Клиент:</b> {user.full_name}\n"
        f"🔗 <b>Username:</b> {username_str}\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
    )

    try:
        if message.text:
            await bot.send_message(
                chat_id=ADMIN_ID,
                text=f"{admin_header}💬 <b>Текст:</b>\n{message.text}",
                parse_mode="HTML",
            )
        elif message.photo:
            photo_id = message.photo[-1].file_id
            await bot.send_photo(
                chat_id=ADMIN_ID,
                photo=photo_id,
                caption=f"{admin_header}💬 <b>Подпись:</b>\n{message.caption or 'Без текста'}",
                parse_mode="HTML",
            )

        await message.answer(t["received"], reply_markup=get_main_keyboard(lang))
        await state.set_state(Form.category)

    except Exception as e:
        logging.error(f"Error forwarding: {e}")
        await message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте позже.",
            reply_markup=get_main_keyboard(lang),
        )


# --- ОТВЕТ АДМИНИСТРАТОРА (Через Reply) ---
@dp.message(F.from_user.id == ADMIN_ID, F.reply_to_message)
async def admin_reply_handler(message: types.Message):
    replied = message.reply_to_message
    
    # Извлекаем текст или подпись исходного сообщения
    source_text = replied.text or replied.caption or ""

    # Ищем метку вида #id123456789
    if "#id" in source_text:
        try:
            # Извлекаем цифровой ID
            target_user_id = int(source_text.split("#id")[1].split()[0])
            
            # Текст для клиента
            client_notification = (
                f"🔔 <b>Ответ от поддержки / Qo'llab-quvvatlash xizmati javobi:</b>\n\n"
                f"{message.text}"
            )
            
            # Отправляем клиенту
            await bot.send_message(
                chat_id=target_user_id,
                text=client_notification,
                parse_mode="HTML",
            )
            await message.reply("✅ Ответ успешно отправлен пользователю!")
            
        except Exception as e:
            await message.reply(f"❌ Не удалось отправить ответ: {e}")
    else:
        await message.reply("⚠️ Не удалось найти ID пользователя в этом сообщении.")


async def main():
    print("Bot is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())