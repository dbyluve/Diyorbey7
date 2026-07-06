"""
Click serveridan keladigan Prepare/Complete so'rovlarini qabul qilish.
"""
from aiohttp import web
from aiogram import Bot

from payment.click import (
    verify_prepare_sign,
    verify_complete_sign,
    ERROR_SUCCESS,
    ERROR_SIGN_CHECK_FAILED,
    ERROR_TRANSACTION_NOT_FOUND,
)
from database import (
    get_student_by_id,
    mark_payment_created,
    mark_payment_confirmed,
    mark_payment_cancelled,
)


def register_click_routes(app: web.Application, bot: Bot):
    async def prepare(request: web.Request):
        data = dict(await request.post())
        if not verify_prepare_sign(data):
            return web.json_response({"error": ERROR_SIGN_CHECK_FAILED, "error_note": "Sign xato"})

        merchant_trans_id = data.get("merchant_trans_id")
        student = await get_student_by_id(int(merchant_trans_id))
        if not student:
            return web.json_response({"error": ERROR_TRANSACTION_NOT_FOUND, "error_note": "Talaba topilmadi"})

        await mark_payment_created(
            student_id=student["id"],
            click_trans_id=data.get("click_trans_id"),
            merchant_trans_id=merchant_trans_id,
            amount=int(float(data.get("amount", 0))),
        )
        return web.json_response({
            "click_trans_id": data.get("click_trans_id"),
            "merchant_trans_id": merchant_trans_id,
            "merchant_prepare_id": student["id"],
            "error": ERROR_SUCCESS,
            "error_note": "OK",
        })

    async def complete(request: web.Request):
        data = dict(await request.post())
        if not verify_complete_sign(data):
            return web.json_response({"error": ERROR_SIGN_CHECK_FAILED, "error_note": "Sign xato"})

        merchant_trans_id = data.get("merchant_trans_id")
        error = int(data.get("error", 0))

        student = await get_student_by_id(int(merchant_trans_id))
        if not student:
            return web.json_response({"error": ERROR_TRANSACTION_NOT_FOUND, "error_note": "Talaba topilmadi"})

        if error == 0:
            await mark_payment_confirmed(merchant_trans_id, data.get("click_trans_id"))
            try:
                await bot.send_message(
                    student["telegram_id"],
                    "✅ To'lovingiz muvaffaqiyatli qabul qilindi! Tez orada siz bilan bog'lanamiz.",
                )
            except Exception:
                pass
        else:
            await mark_payment_cancelled(merchant_trans_id)

        return web.json_response({
            "click_trans_id": data.get("click_trans_id"),
            "merchant_trans_id": merchant_trans_id,
            "error": ERROR_SUCCESS,
            "error_note": "OK",
        })

    app.router.add_post("/click/prepare", prepare)
    app.router.add_post("/click/complete", complete)
