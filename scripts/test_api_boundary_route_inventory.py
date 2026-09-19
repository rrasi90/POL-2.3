"""Static API/boundary route inventory gate for POL Stage 07."""

from scripts.api.main import create_app


EXPECTED_BUSINESS_ROUTES = {
    ("POST", "/api/v1/auth/request-otp"),
    ("POST", "/api/v1/auth/verify-otp"),
    ("POST", "/api/v1/auth/refresh"),
    ("POST", "/api/v1/auth/switch-organization"),
    ("DELETE", "/api/v1/auth/sessions/current"),
    ("DELETE", "/api/v1/auth/sessions/{session_id}"),
    ("POST", "/api/v1/auth/logout-all"),
    ("POST", "/api/v1/baskets"),
    ("POST", "/api/v1/baskets/{basket_id}/items"),
    ("POST", "/api/v1/baskets/{basket_id}/allocation-preview"),
    ("GET", "/api/v1/catalog/search"),
    ("GET", "/api/v1/catalog/categories"),
    ("GET", "/api/v1/catalog/products/{product_id}"),
    ("GET", "/api/v1/catalog/products/{product_id}/vendors"),
    ("GET", "/api/v1/catalog/products/{product_id}/compare-prices"),
    ("GET", "/api/v1/catalog/products/{product_id}/compare-inventory"),
    ("GET", "/api/v1/catalog/vendors/products"),
    ("POST", "/api/v1/catalog/vendors/products"),
    ("PATCH", "/api/v1/catalog/vendors/products/{vendor_product_id}"),
    ("GET", "/api/v1/catalog/vendors/products/{vendor_product_id}/prices"),
    ("GET", "/api/v1/catalog/vendors/products/{vendor_product_id}/prices/current"),
    ("POST", "/api/v1/catalog/vendors/products/{vendor_product_id}/prices"),
    ("GET", "/api/v1/catalog/vendors/products/{vendor_product_id}/inventory"),
    ("PATCH", "/api/v1/catalog/vendors/products/{vendor_product_id}/inventory"),
    ("GET", "/api/v1/inventory/daily/{confirmation_date}"),
    ("POST", "/api/v1/inventory/daily/{confirmation_date}/confirm"),
    ("POST", "/api/v1/inventory/daily/{confirmation_date}/confirm-with-changes"),
    ("POST", "/api/v1/orders"),
    ("POST", "/api/v1/orders/{order_id}/accept"),
    ("POST", "/api/v1/orders/{order_id}/reject"),
    ("POST", "/api/v1/orders/{order_id}/partial-acceptance-proposals"),
    ("POST", "/api/v1/orders/{order_id}/partial-acceptance-proposals/{proposal_id}/approve"),
    ("POST", "/api/v1/orders/{order_id}/partial-acceptance-proposals/{proposal_id}/decline"),
    ("GET", "/api/v1/orders"),
    ("GET", "/api/v1/orders/{order_id}"),
    ("GET", "/api/v1/orders/{order_id}/items"),
    ("GET", "/api/v1/orders/{order_id}/timeline"),
    ("GET", "/api/v1/orders/group/{order_group_id}"),
    ("GET", "/api/v1/orders/group/{order_group_id}/orders"),
    ("POST", "/api/v1/orders/{order_id}/preparing"),
    ("POST", "/api/v1/orders/{order_id}/ready"),
    ("POST", "/api/v1/orders/{order_id}/dispatch"),
    ("POST", "/api/v1/orders/{order_id}/deliver"),
    ("GET", "/api/v1/orders/{order_id}/delivery"),
    ("GET", "/api/v1/orders/{order_id}/delivery/proof"),
    ("POST", "/api/v1/orders/{order_id}/delivery-exceptions"),
    ("GET", "/api/v1/orders/{order_id}/delivery-exceptions"),
    ("GET", "/api/v1/orders/delivery-exceptions/{exception_id}"),
    ("PATCH", "/api/v1/orders/delivery-exceptions/{exception_id}/resolve"),
    ("PATCH", "/api/v1/orders/delivery-exceptions/{exception_id}/escalate"),
    ("POST", "/api/v1/orders/{order_id}/returns"),
    ("GET", "/api/v1/orders/{order_id}/returns"),
    ("GET", "/api/v1/returns/{return_id}"),
    ("PATCH", "/api/v1/returns/{return_id}"),
    ("POST", "/api/v1/orders/{order_id}/disputes"),
    ("GET", "/api/v1/orders/{order_id}/disputes"),
    ("GET", "/api/v1/disputes/{dispute_id}"),
    ("POST", "/api/v1/orders/{order_id}/payments/evidence"),
    ("GET", "/api/v1/orders/{order_id}/payments/evidence"),
    ("POST", "/api/v1/orders/{order_id}/payments/verify"),
    ("GET", "/api/v1/profile"),
    ("GET", "/api/v1/profile/completion"),
    ("GET", "/api/v1/profile/context"),
    ("PUT", "/api/v1/profile"),
    ("GET", "/api/v1/membership/profile"),
    ("PUT", "/api/v1/membership/profile"),
    ("POST", "/api/v1/support/cases"),
    ("GET", "/api/v1/support/cases"),
    ("GET", "/api/v1/support/cases/{case_id}"),
    ("POST", "/api/v1/support/cases/{case_id}/messages"),
    ("PATCH", "/api/v1/support/cases/{case_id}"),
    ("GET", "/api/v1/finance/reconciliation"),
    ("GET", "/api/v1/finance/reconciliation/{case_id}"),
    ("PATCH", "/api/v1/finance/reconciliation/{case_id}/resolve"),
    ("GET", "/api/v1/invoices"),
    ("GET", "/api/v1/invoices/{invoice_id}"),
    ("GET", "/api/v1/orders/{order_id}/invoice"),
    ("GET", "/api/v1/vendors/settlements"),
    ("GET", "/api/v1/settlements/{settlement_id}"),
    ("GET", "/api/v1/admin/audit-logs"),
    ("GET", "/api/v1/admin/exceptions/dashboard"),
    ("POST", "/api/v1/referrals"),
    ("GET", "/api/v1/referrals"),
    ("GET", "/api/v1/referrals/{referral_id}"),
    ("POST", "/api/v1/referrals/{referral_id}/redeem"),
}

EXPECTED_OPERATIONAL_ROUTES = {
    ("GET", "/healthz"),
    ("GET", "/readyz"),
}


def test_fastapi_runtime_route_inventory_is_explicit():
    app = create_app()
    # FastAPI may expose nested _IncludedRouter wrappers in app.routes. OpenAPI is
    # the normalized transport surface after router inclusion and prefix composition.
    actual = {
        (method.upper(), path)
        for path, operations in app.openapi()["paths"].items()
        for method in operations
        if method.lower() in {"get", "post", "put", "patch", "delete", "options", "head"}
    }

    assert actual == EXPECTED_BUSINESS_ROUTES | EXPECTED_OPERATIONAL_ROUTES
