"""
Click to'lov tizimi integratsiyasi.
"""
import hashlib
from config import (
    CLICK_SERVICE_ID,
    CLICK_MERCHANT_ID,
    CLICK_MERCHANT_USER_ID,
    CLICK_SECRET_KEY,
    CLICK_CHECKOUT_URL,
)

ERROR_SUCCESS = 0
ERROR_SIGN_CHECK_FAILED = -1
ERROR_TRANSACTION_NOT_FOUND = -6
ERROR_ALREADY_PAID = -4


def generate_checkout_link(student_id: int, amount: int) -> str:
    return (
        f"{CLICK_CHECKOUT_URL}?service_id={CLICK_SERVICE_ID}"
        f"&merchant_id={CLICK_MERCHANT_ID}"
        f"&amount={amount}"
        f"&transaction_param={student_id}"
        f"&merchant_user_id={CLICK_MERCHANT_USER_ID}"
    )


def _md5(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hex
