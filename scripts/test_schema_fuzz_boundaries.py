"""Boundary and property-based fuzzing for transport schemas (TODO-134).

Covers zero/negative/huge numbers, 32-bit overflow, boolean-as-integer, Unicode
digits, control characters, null/empty arrays, pagination edges and date
formats. Nothing here touches the database: schemas are the first trust
boundary, so a crash or silent coercion is a defect on its own.
"""

from __future__ import annotations

import json
import random
import string

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from scripts.api.schemas import (
    BasketItemRequest,
    CheckoutRequest,
    DailyInventoryConfirmRequest,
    DeliveryConfirmRequest,
    DisputeOpenRequest,
    MediaPresignRequest,
    MediaResumableCompleteRequest,
    OrderQueryParams,
    ReturnRequestRequest,
    VendorPartialAcceptanceProposalRequest,
    VendorPriceSetRequest,
    INT8_MAX,
    VerifyOTPRequest,
    RequestOTPRequest,
)

PRODUCT_ID = "00000000-0000-0000-0000-000000000001"
PLAN_ID = "00000000-0000-0000-0000-000000000002"


def _basket(**overrides):
    payload = {
        "product_id": PRODUCT_ID,
        "requested_quantity": 1,
        "expected_version": 1,
    }
    payload.update(overrides)
    return payload


class TestOtpInputBoundaries:
    @pytest.mark.parametrize(
        "code",
        ["\\u0661\\u0662\\u0663\\u0664\\u0665\\u0666", "\\uff11\\uff12\\uff13\\uff14\\uff15\\uff16", "12 456", " 12345", "12345", "1234567", "abcdef", ""],
    )
    def test_non_ascii_or_malformed_otp_is_rejected(self, code):
        with pytest.raises(ValidationError):
            VerifyOTPRequest(mobile_number="+989121234567", otp_code=code)

    def test_ascii_otp_is_accepted(self):
        assert VerifyOTPRequest(mobile_number="+989121234567", otp_code="123456").otp_code == "123456"

    @pytest.mark.parametrize(
        "number",
        [
            "09121234567",
            "+1234567",
            "+\u0669\u0668\u0669\u0661\u0662\u0661\u0662\u0663\u0664\u0665\u0666\u0667",
            "+1234567890123456",
            "+0123456789",
        ],
    )
    def test_mobile_number_outside_e164_is_rejected(self, number):
        with pytest.raises(ValidationError):
            RequestOTPRequest(mobile_number=number)

    def test_unicode_otp_is_rejected_over_http(self):
        from scripts.api.main import app

        client = TestClient(app)
        response = client.post(
            "/api/v1/auth/verify-otp",
            json={
                "mobile_number": "+989121234567",
                "otp_code": "\u0661\u0662\u0663\u0664\u0665\u0666",
            },
        )
        assert response.status_code == 422
        assert response.json()["success"] is False
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"


class TestNumericBoundaries:
    @pytest.mark.parametrize("value", [0, -1, -2_147_483_649])
    def test_non_positive_quantity_is_rejected(self, value):
        with pytest.raises(ValidationError):
            BasketItemRequest(**_basket(requested_quantity=value))

    def test_boolean_quantity_is_rejected(self):
        with pytest.raises(ValidationError):
            BasketItemRequest(**_basket(requested_quantity=True))

    def test_int4_overflow_quantity_is_rejected(self):
        with pytest.raises(ValidationError):
            BasketItemRequest(**_basket(requested_quantity=2_147_483_648))

    def test_int4_maximum_quantity_is_structurally_valid(self):
        model = BasketItemRequest(**_basket(requested_quantity=2_147_483_647))
        assert model.requested_quantity == 2_147_483_647

    def test_integral_float_is_coerced_and_fractional_float_is_rejected(self):
        assert BasketItemRequest(**_basket(requested_quantity=5.0)).requested_quantity == 5
        with pytest.raises(ValidationError):
            BasketItemRequest(**_basket(requested_quantity=5.5))

    @pytest.mark.parametrize("price", [0, -1])
    def test_non_positive_price_is_rejected(self, price):
        with pytest.raises(ValidationError):
            VendorPriceSetRequest(price_toman=price)

    def test_bigint_price_above_int4_range_is_accepted(self):
        value = 2_147_483_648
        assert VendorPriceSetRequest(price_toman=value).price_toman == value

    def test_bigint_price_overflow_is_rejected(self):
        with pytest.raises(ValidationError):
            VendorPriceSetRequest(price_toman=INT8_MAX + 1)

    def test_one_toman_price_is_accepted(self):
        assert VendorPriceSetRequest(price_toman=1).price_toman == 1

    def test_media_size_boundaries(self):
        base = {
            "mime_type": "image/png",
            "target_type": "PRODUCT",
            "target_id": PRODUCT_ID,
        }
        assert MediaPresignRequest(file_size_bytes=5 * 1024 * 1024, **base)
        for size in (0, -1, 5 * 1024 * 1024 + 1):
            with pytest.raises(ValidationError):
                MediaPresignRequest(file_size_bytes=size, **base)


class TestTextBoundaries:
    @pytest.mark.parametrize("value", ["a\x00b", "line\x1bbreak", "tab\x0bvertical"])
    def test_control_characters_are_rejected(self, value):
        with pytest.raises(ValidationError):
            CheckoutRequest(
                allocation_plan_id=PLAN_ID,
                delivery_address="خیابان " + value + " پلاک ۱",
                preferred_payment_method="CASH_ON_DELIVERY",
            )

    def test_persian_text_with_newlines_is_accepted(self):
        model = CheckoutRequest(
            allocation_plan_id=PLAN_ID,
            delivery_address="خیابان ولیعصر\nکوچه بهار، پلاک ۱۲ — واحد ۳",
            preferred_payment_method="CASH_ON_DELIVERY",
        )
        assert "ولیعصر" in model.delivery_address

    def test_too_short_and_too_long_addresses_are_rejected(self):
        for value in ("کوت", "x" * 1001):
            with pytest.raises(ValidationError):
                CheckoutRequest(
                    allocation_plan_id=PLAN_ID,
                    delivery_address=value,
                    preferred_payment_method="CASH_ON_DELIVERY",
                )

    def test_emoji_and_combining_marks_round_trip_through_json(self):
        model = DeliveryConfirmRequest(recipient_name="کاربر 😀 e\u0301", issue_reported=None)
        restored = DeliveryConfirmRequest(**json.loads(model.model_dump_json()))
        assert restored.recipient_name == model.recipient_name

    def test_delivery_otp_rejects_unicode_digits(self):
        with pytest.raises(ValidationError):
            DeliveryConfirmRequest(otp_code="\u0661\u0662\u0663\u0664")


class TestCollectionAndPaginationBoundaries:
    def test_empty_collections_are_rejected_where_items_are_required(self):
        with pytest.raises(ValidationError):
            ReturnRequestRequest(
                items=[],
                reason="reason",
                idempotency_key="k",
                claimed_refund_amount_toman=1,
            )
        with pytest.raises(ValidationError):
            DisputeOpenRequest(
                claimed_amount_toman=1,
                description="d",
                evidence_media_id=PRODUCT_ID,
                items=[],
            )
        with pytest.raises(ValidationError):
            VendorPartialAcceptanceProposalRequest(items=[])
        with pytest.raises(ValidationError):
            MediaResumableCompleteRequest(session_id=PRODUCT_ID, parts=[])

    def test_pagination_edges(self):
        assert OrderQueryParams(limit=200, offset=0).limit == 200
        for kwargs in ({"limit": 0}, {"limit": 201}, {"limit": -1}, {"offset": -1}):
            with pytest.raises(ValidationError):
                OrderQueryParams(**kwargs)

    def test_date_format_is_strict_ascii(self):
        assert DailyInventoryConfirmRequest(confirmation_date="2026-10-23")
        for value in ("2026-2-3", "۲۶-۱۰-۲۳", "2026/10/23", "2026-13-01", "2026-02-30", ""):
            with pytest.raises(ValidationError):
                DailyInventoryConfirmRequest(confirmation_date=value)

    def test_extra_payload_fields_are_rejected(self):
        with pytest.raises(ValidationError):
            BasketItemRequest(**_basket(unexpected="x"))


class TestSeededRandomFuzz:
    MODELS = [
        (RequestOTPRequest, {"mobile_number": "+989121234567"}),
        (VerifyOTPRequest, {"mobile_number": "+989121234567", "otp_code": "123456"}),
        (BasketItemRequest, _basket()),
        (
            CheckoutRequest,
            {
                "allocation_plan_id": PLAN_ID,
                "delivery_address": "خیابان آزادی پلاک ۱",
                "preferred_payment_method": "CASH_ON_DELIVERY",
            },
        ),
    ]

    def _random_scalar(self, rng):
        return rng.choice(
            [
                None,
                True,
                False,
                0,
                -1,
                2**40,
                3.5,
                "",
                " ",
                "x" * 50,
                "\x00",
                "\u200c",
                "😀",
                "9" * 20,
                "\u0661\u0662",
                [],
                {},
            ]
        )

    def test_random_payloads_never_crash_the_validator(self):
        rng = random.Random(20261023)
        letters = string.ascii_letters + string.digits
        for model, valid in self.MODELS:
            for _ in range(150):
                payload = dict(valid)
                key = rng.choice(list(valid.keys()))
                roll = rng.random()
                if roll < 0.6:
                    payload[key] = self._random_scalar(rng)
                elif roll < 0.8:
                    payload.pop(key)
                else:
                    payload["".join(rng.choices(letters, k=6))] = self._random_scalar(rng)
                try:
                    instance = model(**payload)
                except ValidationError:
                    continue
                json.dumps(instance.model_dump(), default=str)
