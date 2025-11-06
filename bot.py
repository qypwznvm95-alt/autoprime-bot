import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime
from flask import Flask
from threading import Thread
import time

# Создаем Flask приложение для порта
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Бот AUTOPRIME работает! 🚗"

@app.route('/health')
def health():
    return "OK", 200

@app.route('/ping')
def ping():
    return "pong", 200

def run_flask():
    """Запускает Flask сервер на порту"""
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

# Настройка бота
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Токен из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '5533990703')

# Прямая ссылка на PDF в GitHub (ЗАМЕНИТЕ НА ВАШУ)
PDF_URL = "https://raw.githubusercontent.com/ВАШ_ЛОГИН/autoprime-bot/main/catalog.pdf"

def create_keyboard():
    keyboard = [
        [InlineKeyboardButton("📢 Подписаться на канал", callback_data="subscribe_channel")],
        [InlineKeyboardButton("👥 Подписаться на группу", callback_data="subscribe_group")],
        [InlineKeyboardButton("💬 Написать в WhatsApp", url="https://wa.me/79188999006")],
        [InlineKeyboardButton("✍️ Написать в Telegram", url="https://t.me/AUTOPRIMEmanager")],
        [InlineKeyboardButton("📥 ПОЛУЧИТЬ КАТАЛОГ PDF", callback_data="get_catalog")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def send_admin_notification(application, message: str):
    """Отправляет уведомление администратору"""
    try:
        await application.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=message,
            parse_mode='HTML'
        )
        print("📢 Уведомление отправлено администратору")
    except Exception as e:
        print(f"❌ Ошибка отправки уведомления админу: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_info = (
        f"👤 <b>{user.first_name or 'Не указано'}</b>\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"📛 Username: @{user.username or 'Не указан'}\n"
        f"🌐 Язык: {user.language_code or 'Не указан'}\n"
        f"🕐 Время: {datetime.now().strftime('%H:%M %d.%m.%Y')}"
    )
    
    welcome_text = (
        "🚗 AUTOPRIME - Ваш надежный партнер в мире экспорта автомобилей!\n\n"
        "✅ Быстрый и профессиональный подбор\n"
        "✅ Полная проверка авто перед покупкой\n"
        "✅ Гарантия юридической чистоты\n"
        "✅ Консультации экспертов\n\n"
        "📋 <b>Нажмите кнопку ниже чтобы получить каталог автомобилей до 160 л.с. в PDF</b>"
    )

    await update.message.reply_text(
        text=welcome_text,
        reply_markup=create_keyboard(),
        parse_mode='HTML'
    )
    
    notification = (
        "🚀 <b>НОВЫЙ ПОЛЬЗОВАТЕЛЬ</b>\n\n"
        f"{user_info}\n"
        f"📲 <b>Действие:</b> Запустил бота"
    )
    await send_admin_notification(context.application, notification)
    
    print(f"👤 Пользователь {user.first_name} запустил бота")

async def send_pdf_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    try:
        await context.bot.send_message(
            chat_id=user.id,
            text="📥 <b>Спасибо! Отправляем каталог...</b>",
            parse_mode='HTML'
        )

        await context.bot.send_document(
            chat_id=user.id,
            document=PDF_URL,
            filename="Каталог AUTOPRIME до 160 л.с..pdf",
            caption="📋 <b>Каталог автомобилей до 160 л.с.</b>\n\n"
                   "🚗 Проходные модели от ведущих брендов\n"
                   "💰 Лучшие цены на рынке\n" 
                   "⚡ Быстрая доставка\n\n"
                   "📞 По всем вопросам:\n"
                   "• <a href='https://t.me/AUTOPRIMEmanager'>Telegram менеджер</a>\n"
                   "• <a href='https://wa.me/79188999006'>WhatsApp менеджер</a>",
            parse_mode='HTML'
        )
        
        user_info = (
            f"👤 <b>{user.first_name or 'Не указано'}</b>\n"
            f"🆔 ID: <code>{user.id}</code>\n"
            f"📛 Username: @{user.username or 'Не указан'}\n"
            f"🕐 Время: {datetime.now().strftime('%H:%M %d.%m.%Y')}"
        )
        
        notification = (
            "📥 <b>КАЧЕСТВЕННЫЙ ЛИД!</b>\n\n"
            f"{user_info}\n"
            f"📲 <b>Действие:</b> Скачал каталог PDF\n\n"
            f"💬 <b>Написать пользователю:</b>\n"
            f"• <a href='tg://user?id={user.id}'>Написать в Telegram</a>\n"
            f"• <a href='https://wa.me/79188999006'>Перейти в WhatsApp</a>"
        )
        await send_admin_notification(context.application, notification)
        
        print(f"✅ PDF каталог отправлен пользователю {user.first_name}")

    except Exception as e:
        print(f"❌ Ошибка отправки PDF: {e}")
        await context.bot.send_message(
            chat_id=user.id,
            text="❌ Не удалось отправить файл автоматически.\n\n"
                 "🔗 <b>Скачайте каталог по ссылке:</b>\n"
                 f"{PDF_URL}\n\n"
                 "Если ссылка не работает, напишите менеджеру: @AUTOPRIMEmanager",
            parse_mode='HTML'
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    button_data = query.data
    
    print(f"🔄 Пользователь {user.first_name} нажал кнопку: {button_data}")
    
    if button_data in ["subscribe_channel", "subscribe_group", "get_catalog"]:
        await send_pdf_catalog(update, context)

async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    print(f"📋 Пользователь {user.first_name} запросил каталог командой")
    
    user_info = (
        f"👤 <b>{user.first_name or 'Не указано'}</b>\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"📛 Username: @{user.username or 'Не указан'}\n"
        f"🕐 Время: {datetime.now().strftime('%H:%M %d.%m.%Y')}"
    )
    
    notification = (
        "🔘 <b>КОМАНДА ОТ ПОЛЬЗОВАТЕЛЯ</b>\n\n"
        f"{user_info}\n"
        f"📲 <b>Действие:</b> Использовал команду /catalog\n\n"
        f"💬 <b>Написать пользователю:</b>\n"
        f"• <a href='tg://user?id={user.id}'>Написать в Telegram</a>\n"
        f"• <a href='https://wa.me/79188999006'>Перейти в WhatsApp</a>"
    )
    await send_admin_notification(context.application, notification)
    
    await send_pdf_catalog(update, context)

def run_bot():
    """Запускает Telegram бота"""
    print("✅ Бот запускается...")
    
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("catalog", catalog))
        application.add_handler(CallbackQueryHandler(button_handler))
        
        print("🤖 Бот AUTOPRIME запущен на Render!")
        print("📢 Система уведомлений активирована")
        print(f"📁 PDF файл: {PDF_URL}")
        
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Критическая ошибка бота: {e}")

if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    print("🌐 Flask сервер запущен на порту 10000")
    
    # Даем Flask время запуститься
    time.sleep(2)
    
    # Запускаем бота
    run_bot()
