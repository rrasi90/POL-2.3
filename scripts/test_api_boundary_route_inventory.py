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
    ("POST", "/api/v1/orders"),
    ("POST", "/api/v1/orders/{order_id}/accept"),
    ("POST", "/api/v1/orders/{order_id}/reject"),
    ("POST", "/api/v1/orders/{order_id}/partial-acceptance-proposals"),
    ("POST", "/api/v1/orders/{order_id}/partial-acceptance-proposals/{proposal_id}/approve"),
    ("POST", "/api/v1/orders/{order_id}/partial-acceptance-proposals/{proposal_id}/decline"),
    ("GET", "/api/v1/profile"),
    ("GET", "/api/v1/profile/completion"),
    ("GET", "/api/v1/profile/context"),
    ("PUT", "/api/v1/profile"),
    ("GET", "/api/v1/membership/profile"),
    ("PUT", "/api/v1/membership/profile"),
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
