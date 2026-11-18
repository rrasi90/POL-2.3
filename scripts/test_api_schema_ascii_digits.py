"""D-018 input validation must accept ASCII digits only at the HTTP boundary."""

import pytest
from pydantic import ValidationError

from scripts.api.schemas import DeliveryConfirmRequest, RequestOTPRequest, VerifyOTPRequest


def test_request_otp_rejects_non_ascii_phone_digits():
    with pytest.raises(ValidationError):
        RequestOTPRequest(mobile_number="+9891۱۲۳۴۵۶۷۸۹")


def test_verify_otp_rejects_persian_digits():
    with pytest.raises(ValidationError):
        VerifyOTPRequest(mobile_number="+989161234567", otp_code="۱۲۳۴")


def test_verify_otp_rejects_arabic_indic_digits():
    with pytest.raises(ValidationError):
        VerifyOTPRequest(mobile_number="+989161234567", otp_code="١٢٣٤")


def test_delivery_confirmation_rejects_non_ascii_otp():
    with pytest.raises(ValidationError):
        DeliveryConfirmRequest(otp_code="۱۲۳۴")
