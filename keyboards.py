from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from config import COURSES


def courses_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=info["title"], callback_data=f"course:{key}")]
        for key, info in COURSES.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm:yes"),
                InlineKeyboardButton(text="🔄 Qaytadan", callback_data="confirm:no"),
            ]
        ]
    )


def phone_request_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def payment_keyboard(link: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="💳 To'lash (Click)", url=link)]]
    )


def admin_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Statistika", callback_data="admin:stats")],
            [InlineKeyboardButton(text="👥 O'quvchilar ro'yxati", callback_data="admin:list")],
            [InlineKeyboardButton(text="📥 Excel yuklab olish", callback_data="admin:export")],
            [InlineKeyboardButton(text="📢 Xabar yuborish", callback_data="admin:broadcast")],
        ]
    )
