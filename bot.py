"""
shirA Kitchen Bot — принимает заявки из Mini App и шлёт админу.
Запуск: python bot.py
"""
import asyncio
import json
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import MenuButtonWebApp, WebAppInfo

BOT_TOKEN = "8723187362:AAHFcK5nK0cW1rM43brdG8ioYGf1nsHjE5w"
ADMIN_ID = None  # ← Заполнится автоматически по /start от админа
WEBAPP_URL = "https://mmo-rgb.github.io/mini-app/?v=3"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище админов (в проде — БД)
admins = set()


@dp.message(F.text == "/start")
async def cmd_start(msg: types.Message):
    admins.add(msg.from_user.id)
    await msg.answer(
        "👋 Добро пожаловать в <b>shirA Kitchen</b>!\n\n"
        "Нажмите кнопку <b>«shirA»</b> внизу, чтобы открыть калькулятор кухни.",
        parse_mode="HTML"
    )
    logging.info(f"Admin registered: {msg.from_user.id} (@{msg.from_user.username})")


@dp.message(F.web_app_data)
async def handle_webapp_data(msg: types.Message):
    """Ловим данные из Mini App (sendData)"""
    try:
        data = json.loads(msg.web_app_data.data)
    except json.JSONDecodeError:
        return

    if data.get("action") == "order":
        # Формируем красивое сообщение для админа
        text = (
            "🔔 <b>НОВАЯ ЗАЯВКА НА ЗАМЕР</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 <b>Имя:</b> {data.get('name', '—')}\n"
            f"📞 <b>Телефон:</b> {data.get('phone', '—')}\n"
            f"📍 <b>Адрес:</b> {data.get('address', '—') or 'не указан'}\n"
            f"💬 <b>Комментарий:</b> {data.get('comment', '—') or 'нет'}\n"
        )

        # Если клиент прошёл калькулятор — добавляем расчёт
        calc = data.get("calc")
        if calc:
            text += (
                "\n📐 <b>Расчёт из калькулятора:</b>\n"
                f"  • Форма: {calc.get('form', '—')}\n"
                f"  • Фасады: {calc.get('facade', '—')}\n"
                f"  • Столешница: {calc.get('counter', '—')}\n"
                f"  • Длина: {calc.get('length', '—')} м\n"
                f"  • 💰 Примерная цена: <b>{calc.get('price', '—')}</b>\n"
            )

        text += (
            f"\n━━━━━━━━━━━━━━━━━━\n"
            f"👤 Telegram: {msg.from_user.full_name}"
        )
        if msg.from_user.username:
            text += f" (@{msg.from_user.username})"

        # Шлём всем админам
        for admin_id in admins:
            try:
                await bot.send_message(admin_id, text, parse_mode="HTML")
            except Exception as e:
                logging.error(f"Failed to send to admin {admin_id}: {e}")

        # Ответ клиенту
        await msg.answer(
            "✅ <b>Заявка принята!</b>\n\n"
            "Мы свяжемся с вами в ближайшее время.",
            parse_mode="HTML"
        )

    logging.info(f"WebApp data from {msg.from_user.id}: {data}")


async def main():
    # Устанавливаем кнопку меню
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="shirA",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    )
    logging.info("Bot started, menu button set")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
