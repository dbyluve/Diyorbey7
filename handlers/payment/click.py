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
    """Foydalanuvchi bosadigan to'lov havolasini yaratadi."""
    return (
        f"{CLICK_CHECKOUT_URL}?service_id={CLICK_SERVICE_ID}"
        f"&merchant_id={CLICK_MERCHANT_ID}"
        f"&amount={amount}"
        f"&transaction_param={student_id}"
        f"&merchant_user_id={CLICK_MERCHANT_USER_ID}"
    )


def _md5(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def verify_prepare_sign(data: dict) -> bool:
    """Prepare so'rovi uchun sign_string ni tekshiradi."""
    raw = (
        f"{data.get('click_trans_id')}{data.get('service_id')}{CLICK_SECRET_KEY}"
        f"{data.get('merchant_trans_id')}{data.get('amount')}"
        f"{data.get('action')}{data.get('sign_time')}"
    )
    return _md5(raw) == data.get("sign_string")


def verify_complete_sign(data: dict) -> bool:
    """Complete so'rovi uchun sign_string ni tekshiradi (merchant_prepare_id bilan)."""
    raw = (
        f"{data.get('click_trans_id')}{data.get('service_id')}{CLICK_SECRET_KEY}"
        f"{data.get('merchant_trans_id')}{data.get('merchant_prepare_id')}"
        f"{data.get('amount')}{data.get('action')}{data.get('sign_time')}"
    )
    return _md5(raw) == data.get("sign_string")
