import os
from dotenv import load_dotenv
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
YULIA_USERNAME = os.getenv('YULIA_USERNAME')

# Формируем умную ссылку с предзаполненным текстом
contact_url = f"https://t.me/{YULIA_USERNAME}"

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
        "🔹 Первая сессия (45 минут) — 300 грн\n"
        "🔹 Последующие сессии (60 минут) — 400 грн\n"
        "🔹 Пакет из 5 сессий — 1750 грн"
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
