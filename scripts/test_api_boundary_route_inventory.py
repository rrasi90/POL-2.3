"""Static API/boundary route inventory gate for POL Stage 07."""

from scripts.api.main import create_app


EXPECTED_BUSINESS_ROUTES = {
    ("DELETE", "/api/v1/auth/sessions/current"),
    ("DELETE", "/api/v1/auth/sessions/{session_id}"),
    ("GET", "/api/v1/admin/audit-logs"),
    ("GET", "/api/v1/admin/exceptions/dashboard"),
    ("GET", "/api/v1/admin/organizations"),
    ("GET", "/api/v1/admin/product-candidates"),
    ("GET", "/api/v1/admin/users"),
    ("GET", "/api/v1/baskets/current"),
    ("GET", "/api/v1/catalog/barcode/lookup"),
    ("GET", "/api/v1/catalog/categories"),
    ("GET", "/api/v1/catalog/products/{product_id}"),
    ("GET", "/api/v1/catalog/products/{product_id}/compare-inventory"),
    ("GET", "/api/v1/catalog/products/{product_id}/compare-prices"),
    ("GET", "/api/v1/catalog/products/{product_id}/vendors"),
    ("GET", "/api/v1/catalog/search"),
    ("GET", "/api/v1/catalog/vendors/products"),
    ("GET", "/api/v1/catalog/vendors/products/{vendor_product_id}/inventory"),
    ("GET", "/api/v1/catalog/vendors/products/{vendor_product_id}/prices"),
    ("GET", "/api/v1/catalog/vendors/products/{vendor_product_id}/prices/current"),
    ("GET", "/api/v1/categories"),
    ("GET", "/api/v1/disputes/{dispute_id}"),
    ("GET", "/api/v1/field/tasks"),
    ("GET", "/api/v1/field/tasks/{task_id}"),
    ("GET", "/api/v1/finance/reconciliation"),
    ("GET", "/api/v1/finance/reconciliation/{case_id}"),
    ("GET", "/api/v1/finance/refunds"),
    ("GET", "/api/v1/finance/refunds/{refund_id}"),
    ("GET", "/api/v1/inbox/items"),
    ("GET", "/api/v1/inventory/daily/{confirmation_date}"),
    ("GET", "/api/v1/invoices"),
    ("GET", "/api/v1/invoices/{invoice_id}"),
    ("GET", "/api/v1/membership/profile"),
    ("GET", "/api/v1/notifications"),
    ("GET", "/api/v1/notifications/preferences"),
    ("GET", "/api/v1/ops/analytics"),
    ("GET", "/api/v1/ops/analytics/weekly"),
    ("GET", "/api/v1/ops/permissions"),
    ("GET", "/api/v1/ops/permissions/audit"),
    ("GET", "/api/v1/ops/returns"),
    ("GET", "/api/v1/orders"),
    ("GET", "/api/v1/orders/delivery-exceptions/{exception_id}"),
    ("GET", "/api/v1/orders/group/{order_group_id}"),
    ("GET", "/api/v1/orders/group/{order_group_id}/orders"),
    ("GET", "/api/v1/orders/{order_id}"),
    ("GET", "/api/v1/orders/{order_id}/delivery"),
    ("GET", "/api/v1/orders/{order_id}/delivery-exceptions"),
    ("GET", "/api/v1/orders/{order_id}/delivery/proof"),
    ("GET", "/api/v1/orders/{order_id}/disputes"),
    ("GET", "/api/v1/orders/{order_id}/invoice"),
    ("GET", "/api/v1/orders/{order_id}/items"),
    ("GET", "/api/v1/orders/{order_id}/partial-acceptance-proposals"),
    ("GET", "/api/v1/orders/{order_id}/payments/evidence"),
    ("GET", "/api/v1/orders/{order_id}/returns"),
    ("GET", "/api/v1/orders/{order_id}/timeline"),
    ("GET", "/api/v1/products/search"),
    ("GET", "/api/v1/profile"),
    ("GET", "/api/v1/profile/completion"),
    ("GET", "/api/v1/profile/context"),
    ("GET", "/api/v1/referrals"),
    ("GET", "/api/v1/referrals/{referral_id}"),
    ("GET", "/api/v1/returns/{return_id}"),
    ("GET", "/api/v1/search"),
    ("GET", "/api/v1/settlements/{settlement_id}"),
    ("GET", "/api/v1/storefront/vendors"),
    ("GET", "/api/v1/storefront/vendors/{vendor_id}"),
    ("GET", "/api/v1/storefront/vendors/{vendor_id}/products"),
    ("GET", "/api/v1/support/cases"),
    ("GET", "/api/v1/support/cases/{case_id}"),
    ("GET", "/api/v1/support/cases/{case_id}/messages"),
    ("GET", "/api/v1/vendors/customers"),
    ("GET", "/api/v1/vendors/settlements"),
    ("GET", "/api/v1/vendors/staff"),
    ("GET", "/api/v1/vendors/staff/{membership_id}/permissions"),
    ("PATCH", "/api/v1/admin/categories/{category_id}"),
    ("PATCH", "/api/v1/admin/organizations/{organization_id}/status"),
    ("PATCH", "/api/v1/admin/product-candidates/{candidate_id}"),
    ("PATCH", "/api/v1/admin/users/{user_id}/status"),
    ("PATCH", "/api/v1/catalog/vendors/products/{vendor_product_id}"),
    ("PATCH", "/api/v1/catalog/vendors/products/{vendor_product_id}/inventory"),
    ("PATCH", "/api/v1/disputes/{dispute_id}/resolve"),
    ("PATCH", "/api/v1/field/tasks/{task_id}"),
    ("PATCH", "/api/v1/finance/reconciliation/{case_id}/resolve"),
    ("PATCH", "/api/v1/inbox/items/read-all"),
    ("PATCH", "/api/v1/inbox/items/{item_id}/read"),
    ("PATCH", "/api/v1/orders/delivery-exceptions/{exception_id}/escalate"),
    ("PATCH", "/api/v1/orders/delivery-exceptions/{exception_id}/resolve"),
    ("PATCH", "/api/v1/returns/{return_id}"),
    ("PATCH", "/api/v1/support/cases/{case_id}"),
    ("PATCH", "/api/v1/support/cases/{case_id}/status"),
    ("PATCH", "/api/v1/vendors/staff/{membership_id}"),
    ("POST", "/api/v1/admin/broadcasts"),
    ("POST", "/api/v1/admin/broadcasts/{broadcast_id}/dispatch"),
    ("POST", "/api/v1/admin/categories"),
    ("POST", "/api/v1/admin/sla-overrides"),
    ("POST", "/api/v1/auth/logout-all"),
    ("POST", "/api/v1/auth/refresh"),
    ("POST", "/api/v1/auth/request-otp"),
    ("POST", "/api/v1/auth/switch-organization"),
    ("POST", "/api/v1/auth/verify-otp"),
    ("POST", "/api/v1/baskets"),
    ("POST", "/api/v1/baskets/{basket_id}/allocation-preview"),
    ("POST", "/api/v1/baskets/{basket_id}/items"),
    ("POST", "/api/v1/catalog/vendors/products"),
    ("POST", "/api/v1/catalog/vendors/products/{vendor_product_id}/prices"),
    ("POST", "/api/v1/disputes/{dispute_id}/close"),
    ("POST", "/api/v1/disputes/{dispute_id}/investigate"),
    ("POST", "/api/v1/field/tasks"),
    ("POST", "/api/v1/finance/refunds/issue"),
    ("POST", "/api/v1/finance/refunds/{refund_id}/approve"),
    ("POST", "/api/v1/finance/refunds/{refund_id}/complete"),
    ("POST", "/api/v1/inventory/daily/{confirmation_date}/confirm"),
    ("POST", "/api/v1/inventory/daily/{confirmation_date}/confirm-with-changes"),
    ("POST", "/api/v1/media/confirm-upload"),
    ("POST", "/api/v1/media/presigned-url"),
    ("POST", "/api/v1/media/resumable/complete"),
    ("POST", "/api/v1/media/resumable/init"),
    ("POST", "/api/v1/orders"),
    ("POST", "/api/v1/orders/{order_id}/accept"),
    ("POST", "/api/v1/orders/{order_id}/cancel"),
    ("POST", "/api/v1/orders/{order_id}/deliver"),
    ("POST", "/api/v1/orders/{order_id}/delivery-exceptions"),
    ("POST", "/api/v1/orders/{order_id}/delivery/arrived"),
    ("POST", "/api/v1/orders/{order_id}/delivery/failed"),
    ("POST", "/api/v1/orders/{order_id}/delivery/in-transit"),
    ("POST", "/api/v1/orders/{order_id}/delivery/picked-up"),
    ("POST", "/api/v1/orders/{order_id}/dispatch"),
    ("POST", "/api/v1/orders/{order_id}/disputes"),
    ("POST", "/api/v1/orders/{order_id}/partial-acceptance-proposals"),
    ("POST", "/api/v1/orders/{order_id}/partial-acceptance-proposals/{proposal_id}/approve"),
    ("POST", "/api/v1/orders/{order_id}/partial-acceptance-proposals/{proposal_id}/decline"),
    ("POST", "/api/v1/orders/{order_id}/payments/direct-transfer"),
    ("POST", "/api/v1/orders/{order_id}/payments/evidence"),
    ("POST", "/api/v1/orders/{order_id}/payments/verify"),
    ("POST", "/api/v1/orders/{order_id}/payments/{payment_id}/verify"),
    ("POST", "/api/v1/orders/{order_id}/preparing"),
    ("POST", "/api/v1/orders/{order_id}/ready"),
    ("POST", "/api/v1/orders/{order_id}/reject"),
    ("POST", "/api/v1/orders/{order_id}/returns"),
    ("POST", "/api/v1/privacy/deletion"),
    ("POST", "/api/v1/privacy/export"),
    ("POST", "/api/v1/product-candidates"),
    ("POST", "/api/v1/products/match-barcode"),
    ("POST", "/api/v1/referrals"),
    ("POST", "/api/v1/referrals/{referral_id}/redeem"),
    ("POST", "/api/v1/returns/{return_id}/refund/approve"),
    ("POST", "/api/v1/support/cases"),
    ("POST", "/api/v1/support/cases/{case_id}/assign"),
    ("POST", "/api/v1/support/cases/{case_id}/messages"),
    ("POST", "/api/v1/vendors/inventory/continuous-scan"),
    ("POST", "/api/v1/vendors/inventory/publish"),
    ("POST", "/api/v1/vendors/staff/invite"),
    ("POST", "/api/v1/vendors/staff/{membership_id}/permissions"),
    ("POST", "/api/v1/vendors/staff/{membership_id}/permissions/{permission_key}/revoke"),
    ("PUT", "/api/v1/membership/profile"),
    ("PUT", "/api/v1/notifications/preferences"),
    ("PUT", "/api/v1/profile"),
}


EXPECTED_OPERATIONAL_ROUTES = {
    ("GET", "/healthz"),
    ("GET", "/readyz"),
}


def test_fastapi_runtime_route_inventory_is_explicit():
    # Reuse the module-level production app: building a second FastAPI instance
    # in the same process re-analyzes stringified endpoint annotations and
    # trips pydantic's cached-incomplete TypeAdapter for the _auth fields.
    from scripts.api.main import app
    # FastAPI may expose nested _IncludedRouter wrappers in app.routes. OpenAPI is
    # the normalized transport surface after router inclusion and prefix composition.
    actual = {
        (method.upper(), path)
        for path, operations in app.openapi()["paths"].items()
        for method in operations
        if method.lower() in {"get", "post", "put", "patch", "delete", "options", "head"}
    }

    assert actual == EXPECTED_BUSINESS_ROUTES | EXPECTED_OPERATIONAL_ROUTES
# All routes in EXPECTED_BUSINESS_ROUTES are now implemented.
# This set is empty and kept for structural compatibility.
DOCUMENTED_BUT_UNIMPLEMENTED_ROUTES = set()


def test_documented_but_unimplemented_routes_remain_explicit_gaps():
    from scripts.api.main import app

    actual = {
        (method.upper(), path)
        for path, operations in app.openapi()["paths"].items()
        for method in operations
        if method.lower() in {"get", "post", "put", "patch", "delete", "options", "head"}
    }
    # If this assertion changes, the route-gap ledger and documentation must be
    # reconciled in the same change; do not silently promote a doc-only route.
    assert DOCUMENTED_BUT_UNIMPLEMENTED_ROUTES.isdisjoint(actual)
