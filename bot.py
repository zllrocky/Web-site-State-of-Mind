import os
import django
import asyncio
import urllib.parse
from asgiref.sync import sync_to_async
from dotenv import load_dotenv

# 1. Сначала грузим настройки из .env
load_dotenv()

# 2. Указываем путь к настройкам проекта
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elite_coach.settings')

# 3. ЗАПУСКАЕМ Django (без этого модели не будут работать)
django.setup()

# 4. ТЕПЕРЬ импортируем модель (когда база данных подключена)
from blog.models import BotSubscriber

# 5. Дальше всё остальное для бота
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

TOKEN = os.getenv('BOT_TOKEN')
YULIA_USERNAME = os.getenv('YULIA_USERNAME')

# НОВОЕ: Готовим текст и превращаем пробелы в безопасные символы
preset_message = "Здравствуйте, Юлия! Я из бота State of Mind, хочу записаться на ознакомительную сессию."
encoded_message = urllib.parse.quote(preset_message)

# Формируем умную ссылку с предзаполненным текстом
contact_url = f"https://t.me/{YULIA_USERNAME}?text={encoded_message}"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- АРХИТЕКТУРА КНОПОК ---

main_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🙋‍♀️ Обо мне", callback_data="about")],
    [InlineKeyboardButton(text="💎 Услуги и цены", callback_data="services")],
    [InlineKeyboardButton(text="✍️ Связаться лично", url=contact_url)]
])

about_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💎 Услуги и цены", callback_data="services")],
    [InlineKeyboardButton(text="✍️ Связаться лично", url=contact_url)]
])

services_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🙋‍♀️ Обо мне", callback_data="about")],
    [InlineKeyboardButton(text="✍️ Связаться лично", url=contact_url)]
])

# --- ХЭНДЛЕРЫ (ЛОГИКА) ---

@dp.message(CommandStart())
async def cmd_start(message: Message):
    # Эта строка сохраняет ID пользователя в базу данных сайта
    await sync_to_async(BotSubscriber.objects.get_or_create)(chat_id=message.chat.id)
    text = (
        "Добро пожаловать в пространство <b>State of Mind</b>! 🌿\n\n"
        "Выберите нужный раздел ниже, чтобы узнать детали или сразу записаться на сессию:"
    )
    await message.answer(text, reply_markup=main_kb, parse_mode="HTML")

@dp.callback_query(F.data == "about")
async def process_about(callback: CallbackQuery):
    text = (
        "<b>Рада нашей встрече!</b> Я здесь для того, чтобы помочь вам сократить путь от текущей точки до той жизни, о которой вы мечтаете.\n\n"
        "Многие приходят в коучинг, когда чувствуют, что упёрлись в «стеклянный потолок», выгорели или просто запутались в бесконечном выборе дорог. Моя роль — не давать вам готовые советы (которые часто не работают), а стать тем профессиональным зеркалом, в котором вы увидите свои истинные возможности и скрытые барьеры."
    )
    await callback.message.answer(text, reply_markup=about_kb, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "services")
async def process_services(callback: CallbackQuery):
    text = (
        "<b>Услуги и цены:</b>\n\n"
        "🔹 Ознакомительная сессия (15 минут) — БЕЗОПЛАТНО\n"
        "🔹 Последующие сессии (60 минут) — 15€\n"
        "🔹 Пакет из 5 сессий — 65€"
    )
    await callback.message.answer(text, reply_markup=services_kb, parse_mode="HTML")
    await callback.answer()

# НОВОЕ: Перехватчик любого текста (если клиент просто что-то написал)
@dp.message()
async def catch_all_messages(message: Message):
    text = "Для навигации, пожалуйста, используйте меню ниже 👇"
    await message.answer(text, reply_markup=main_kb)

async def main():
    print("Бот-воронка успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())