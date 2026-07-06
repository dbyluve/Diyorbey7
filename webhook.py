"""
Click to'lov tizimi webhook (Prepare/Complete) handlerlari.
"""
import hashlib
from datetime import datetime
from aiohttp import web

from config import CLICK_SECRET_KEY, CLICK_SERVICE_ID
from database import (
    get_student_by_id,
    mark_payment_confirmed,
    mark_payment_cancelled,
)

ERROR_SUCCESS = 0
ERROR_SIGN_CHECK_FAILED = -1
ERROR_TRANSACTION_NOT_FOUND = -6
ERROR_ALREADY_PAID = -4


def check_prepare_sign(data: dict) -> bool:
    sign_string = (
        f"{data['click_trans_id']}{data['service_id']}{CLICK_SECRET_KEY}"
        f"{data['merchant_trans_id']}{data['amount']}{data['action']}{data['sign_time']}"
    )
    return hashlib.md5(sign_string.encode()).hexdigest() == data['sign_string']


def check_complete_sign(data: dict) -> bool:
    sign_string = (
        f"{data['click_trans_id']}{data['service_id']}{CLICK_SECRET_KEY}"
        f"{data['merchant_trans_id']}{data.get('merchant_prepare_id', '')}"
        f"{data['amount']}{data['action']}{data['sign_time']}"
    )
    return hashlib.md5(sign_string.encode()).hexdigest() == data['sign_string']


async def click_prepare(request: web.Request):
    data = await request.post()
    data = dict(data)

    if not check_prepare_sign(data):
        return web.json_response({
            "click_trans_id": data.get("click_trans_id"),
            "merchant_trans_id": data.get("merchant_trans_id"),
            "error": ERROR_SIGN_CHECK_FAILED,
            "error_note": "Sign check failed",
        })

    student_id = int(data["merchant_trans_id"])
    student = await get_student_by_id(student_id)

    if not student:
        return web.json_response({
            "click_trans_id": data.get("click_trans_id"),
            "merchant_trans_id": data.get("merchant_trans_id"),
            "error": ERROR_TRANSACTION_NOT_FOUND,
            "error_note": "Student not found",
        })

    return web.json_response({
        "click_trans_id": data["click_trans_id"],
        "merchant_trans_id": data["merchant_trans_id"],
        "merchant_prepare_id": student_id,
        "error": ERROR_SUCCESS,
        "error_note": "Success",
    })


async def click_complete(request: web.Request):
    data = await request.post()
    data = dict(data)

    if not check_complete_sign(data):
        return web.json_response({
            "click_trans_id": data.get("click_trans_id"),
            "merchant_trans_id": data.get("merchant_trans_id"),
            "error": ERROR_SIGN_CHECK_FAILED,
            "error_note": "Sign check failed",
        })

    error = int(data.get("error", 0))
    merchant_trans_id = data["merchant_trans_id"]
    click_trans_id = data["click_trans_id"]

    if error < 0:
        await mark_payment_cancelled(merchant_trans_id)
        return web.json_response({
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_i
