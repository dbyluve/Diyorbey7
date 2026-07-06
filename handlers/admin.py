import io
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, BufferedInputFile

from config import ADMIN_IDS, COURSES
from keyboards import admin_menu_keyboard
from database import get_stats, get_all_students, get_all_telegram_ids

router = Router()


class Broadcast(StatesGroup):
    waiting_text = State()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("🛠 Admin panel", reply_markup=admin_menu_keyboard())


@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    stats = await get_stats()
    lines = [
        "📊 <b>Statistika</b>\n",
        f"Jami o'quvchilar: {stats['total']}",
        f"To'lov qilganlar: {stats['paid']}",
        f"Umumiy tushum: {stats['revenue']:,} so'm".replace(",", " "),
        "",
        "<b>Kurslar bo'yicha:</b>",
    ]
    for row in stats["by_course"]:
        course_title = COURSES.get(row["course_key"], {}).get("title", row["course_key"])
        lines.append(f"{course_title}: {row['cnt']} ta ({row['paid_cnt']} to'langan)")
    await callback.message.edit_text("\n".join(lines), reply_markup=admin_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "admin:list")
async def admin_list(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    students = await get_all_students()
    if not students:
        await callback.answer("O'quvchilar yo'q.", show_alert=True)
        return
    lines = ["👥 <b>So'nggi o'quvchilar</b>\n"]
    for s in students[:20]:
        course_title = COURSES.get(s["course_key"], {}).get("title", s["course_key"])
        status = "✅" if s["payment_status"] == "paid" else "⏳"
        lines.append(f"{status} {s['full_name']} | {s['phone']} | {s['grade']}-sinf | {course_title}")
    if len(students) > 20:
        lines.append(f"\n... va yana {len(students) - 20} ta. To'liq ro'yxat uchun Excel yuklab oling.")
    await callback.message.edit_text("\n".join(lines), reply_markup=admin_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "admin:export")
async def admin_export(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    try:
        from openpyxl import Workbook
    except ImportError:
        await callback.answer("openpyxl o'rnatilmagan.", show_alert=True)
        return

    students = await get_all_students()
    wb = Workbook()
    ws = wb.active
    ws.title = "O'quvchilar"
    ws.append(["ID", "Ism", "Telefon", "Sinf", "Kurs", "Summa", "To'lov holati", "Sana"])
    for s in students:
        course_title = COURSES.get(s["course_key"], {}).get("title", s["course_key"])
        ws.append([
            s["id"], s["full_name"], s["phone"], s["grade"],
            course_title, s["amount"], s["payment_status"], s["created_at"],
        ])

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    file = BufferedInputFile(buffer.read(), filename="oquvchilar.xlsx")
    await bot.send_document(callback.from_user.id, file)
    await callback.answer("Yuborildi ✅")


@router.callback_query(F.data == "admin:broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer()
    await state.set_state(Broadcast.waiting_text)
    await callback.message.answer("Barcha o'quvchilarga yuboriladigan xabar matnini kiriting:")
    await callback.answer()


@router.message(Broadcast.waiting_text)
async def admin_broadcast_send(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    ids = await get_all_telegram_ids()
    sent, failed = 0, 0
    for tg_id in ids:
        try:
            await bot.send_message(tg_id, message.text)
            sent += 1
        except Exception:
            failed += 1
    await state.clear()
    await message.answer(f"✅ Yuborildi: {sent} ta\n❌ Xatolik: {failed} ta")
