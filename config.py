"""
Konfiguratsiya fayli.
Barcha maxfiy ma'lumotlarni (token, kalitlar) .env faylida saqlang.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ---- Telegram bot ----
BOT_TOKEN = os.getenv("BOT_TOKEN", "PASTE_YOUR_BOT_TOKEN_HERE")

# Admin(lar)ning Telegram ID raqamlari (bir nechta bo'lishi mumkin)
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

# ---- Click to'lov tizimi ----
CLICK_SERVICE_ID = os.getenv("CLICK_SERVICE_ID", "")
CLICK_MERCHANT_ID = os.getenv("CLICK_MERCHANT_ID", "")
CLICK_MERCHANT_USER_ID = os.getenv("CLICK_MERCHANT_USER_ID", "")
CLICK_SECRET_KEY = os.getenv("CLICK_SECRET_KEY", "")

CLICK_CHECKOUT_URL = "https://my.click.uz/services/pay"

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8080"))

DB_PATH = os.getenv("DB_PATH", "prezident_bot.db")

COURSES = {
    "math": {
        "title": "🔢 Matematika",
        "description": "Prezident maktabi imtihoni uchun matematika kursi",
        "price": 300_000,
    },
    "english": {
        "title": "📖 Ingliz tili",
        "description": "Grammatika, lug'at va test topshiriqlari",
        "price": 300_000,
    },
    "logic": {
        "title": "📈 Mantiqiy masalalar",
        "description": "Mantiqiy fikrlash va masalalar yechish",
        "price": 250_000,
    },
    "critical_thinking": {
        "title": "⚡️ Tanqidiy fikrlash",
        "description": "Tahlil qilish va tanqidiy fikrlash ko'nikmalari",
        "price": 250_000,
    },
    "olympiad": {
        "title": "🎯 Olimpiadalarga tayyorgarlik",
        "description": "Respublika va xalqaro olimpiadalarga tayyorgarlik",
        "price": 350_000,
    },
}

CHANNEL_USERNAME = "@piimaolympiad_edu_manager"
ADS_USERNAME = "@piima_edu_reklama"
