"""Technical abuse guard for unbounded bulk request arrays."""

from scripts.api.main import app
from scripts.operational_config import MAX_BULK_ITEMS


def test_shared_bulk_limit_is_declared_in_openapi():
    schemas = app.openapi()["components"]["schemas"]
    expected = {
        ("VendorPartialAcceptanceProposalRequest", "items"),
        ("DailyInventoryConfirmWithChangesRequest", "changes"),
        ("ReturnRequestRequest", "items"),
        ("DisputeOpenRequest", "items"),
    }
    for schema_name, field_name in expected:
        assert schemas[schema_name]["properties"][field_name]["maxItems"] == MAX_BULK_ITEMS
