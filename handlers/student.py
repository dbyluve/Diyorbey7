from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from config import COURSES, CHANNEL_USERNAME, ADMIN_IDS
from keyboards import courses_keyboard, confirm_keyboard, phone_request_keyboard, payment_keyboard
from database import upsert_student
from payment.click import generate_checkout_link

router = Router()


class Registration(StatesGroup):
    choosing_course = State()
    entering_name = State()
    entering_phone = State()
    entering_grade = State()
    confirming = State()


WELCOME_TEXT = (
    "👋 Assalomu alaykum!\n\n"
    "🧩 <b>Prezident maktabiga kirishingizga yordam beramiz</b>\n\n"
    "🔢 Matematika\n"
    "📖 Ingliz tili\n"
    "📈 Mantiqiy masalalar\n"
    "⚡️ Tanqidiy fikrlash\n"
    "🎯 Olimpiadalarga tayyorgarlik\n\n"
    "Quyidan kursni tanlang 👇"
)


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=courses_keyboard())


@router.callback_query(F.data.startswith("course:"))
async def course_chosen(callback: CallbackQuery, state: FSMContext):
    course_key = callback.data.split(":", 1)[1]
    course = COURSES[course_key]
    await state.update_data(course_key=course_key)
    await state.set_state(Registration.entering_name)
    await callback.message.edit_text(
        f"{course['title']}\n{course['description']}\n"
        f"Narxi: {course['price']:,} so'm\n\n"
        f"Ro'yxatdan o'tish uchun to'liq ismingizni kiriting (F.I.Sh):".replace(",", " ")
    )
    await callback.answer()


@router.message(Registration.entering_name)
async def name_entered(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 3:
        await message.answer("Iltimos, to'liq ismingizni kiriting (kamida 3 ta harf).")
        return

    await state.update_data(full_name=message.text.strip())
    await state.set_state(Registration.entering_phone)
    await message.answer(
        "Telefon raqamingizni yuboring 👇",
        reply_markup=phone_request_keyboard(),
    )


@router.message(Registration.entering_phone, F.contact)
async def phone_shared(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await state.set_state(Registration.entering_grade)
    await message.answer(
        "Nechanchi sinfda o'qiysiz? (masalan: 5)",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(Registration.entering_grade)
async def grade_entered(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().isdigit():
        await message.answer("Iltimos, sinfingizni raqamda kiriting (masalan: 5).")
        return

    grade = int(message.text.strip())
    await state.update_data(grade=grade)
    await state.set_state(Registration.confirming)

    data = await state.get_data()
    course = COURSES[data["course_key"]]

    summary = (
        "📋 Ma'lumotlaringizni tekshiring:\n\n"
        f"👤 Ism: {data['full_name']}\n"
        f"📱 Telefon: {data['phone']}\n"
        f"🏫 Sinf: {grade}\n"
        f"📚 Kurs: {course['title']}\n"
        f"💰 Narxi: {course['price']:,} so'm\n\n"
        "Ma'lumotlar to'g'rimi?"
    ).replace(",", " ")

    await message.answer(summary, reply_markup=confirm_keyboard())


@router.callback_query(Registration.confirming, F.data == "confirm_yes")
async def registration_confirmed(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    course = COURSES[data["course_key"]]

    student_id = await upsert_student(
        telegram_id=callback.from_user.id,
        full_name=data["full_name"],
        phone=data["phone"],
        grade=data["grade"],
        course_key=data["course_key"],
        amount=course["price"],
    )

    checkout_url = generate_checkout_link(
        student_id=student_id,
        amount=course["price"],
    )

    admin_text = (
        "🆕 <b>Yangi buyurtma!</b>\n\n"
        f"👤 Ism: {data['full_name']}\n"
        f"📱 Telefon: {data['phone']}\n"
        f"🏫 Sinf: {data['grade']}\n"
        f"📚 Kurs: {course['title']}\n"
        f"💰 Narxi: {course['price']:,} so'm\n"
        f"🆔 Telegram ID: {callback.from_user.id}\n"
        f"👤 Username: @{callback.from_user.username or 'yoq'}"
    ).replace(",", " ")

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text)
        except Exception as e:
            print(f"Adminga xabar yuborishda xatolik ({admin_id}): {e}")

    await callback.message.edit_text(
        "✅ Ro'yxatdan muvaffaqiyatli o'tdingiz!\n\n"
        "To'lovni amalga oshirish uchun quyidagi tugmani bosing 👇",
        reply_markup=payment_keyboard(checkout_url),
    )
    await callback.answer()


@router.callback_query(Registration.confirming, F.data == "confirm_no")
async def registration_restart(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(WELCOME_TEXT, reply_markup=courses_keyboard())
    await callback.answer()
