"""Technical abuse guard for unbounded bulk request arrays."""

import pytest
from pydantic import ValidationError

from scripts.api.schemas import (
    DisputeOpenRequest,
    ReturnRequestRequest,
    VendorPartialAcceptanceProposalRequest,
)
from scripts.operational_config import MAX_BULK_ITEMS


def test_shared_bulk_limit_is_documented_in_schema():
    from scripts.api.main import app

    schemas = app.openapi()["components"]["schemas"]
    assert schemas["VendorPartialAcceptanceProposalRequest"]["properties"]["items"]["maxItems"] == MAX_BULK_ITEMS
    assert schemas["ReturnRequestRequest"]["properties"]["items"]["maxItems"] == MAX_BULK_ITEMS
    assert schemas["DisputeOpenRequest"]["properties"]["items"]["maxItems"] == MAX_BULK_ITEMS


def test_vendor_partial_acceptance_rejects_oversized_array():
    with pytest.raises(ValidationError):
        VendorPartialAcceptanceProposalRequest(items=[{}] * (MAX_BULK_ITEMS + 1))


def test_return_request_rejects_oversized_array():
    with pytest.raises(ValidationError):
        ReturnRequestRequest(
            items=[{}] * (MAX_BULK_ITEMS + 1),
            reason="bulk guard",
            idempotency_key="bulk-guard",
            claimed_refund_amount_toman=0,
        )


def test_dispute_request_rejects_oversized_array():
    with pytest.raises(ValidationError):
        DisputeOpenRequest(
            claimed_amount_toman=1,
            description="bulk guard",
            evidence_media_id="00000000-0000-0000-0000-000000000001",
            items=[{}] * (MAX_BULK_ITEMS + 1),
        )
