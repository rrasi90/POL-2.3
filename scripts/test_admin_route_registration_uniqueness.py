"""Regression gate for duplicate registrations across admin routers.

The production app mounts the guarded admin router before the management router.
A duplicate method/path can silently shadow a later handler in OpenAPI/runtime.
Keep the shared admin surface registered in exactly one router.
"""
from fastapi.routing import APIRoute

from scripts.api.routes.admin import router as guarded_admin_router
from scripts.api.routes.management import admin_router as management_admin_router


PROTECTED_SHARED_ADMIN_ROUTES = {
    ("POST", "/admin/broadcasts"),
    ("POST", "/admin/broadcasts/{broadcast_id}/dispatch"),
    ("POST", "/admin/categories"),
    ("PATCH", "/admin/categories/{category_id}"),
}


def _route_keys(router) -> set[tuple[str, str]]:
    return {
        (method.upper(), route.path)
        for route in router.routes
        if isinstance(route, APIRoute)
        for method in (route.methods or set())
        if method.upper() not in {"HEAD", "OPTIONS"}
    }


def test_shared_admin_routes_have_one_canonical_registration():
    guarded = _route_keys(guarded_admin_router)
    management = _route_keys(management_admin_router)

    assert PROTECTED_SHARED_ADMIN_ROUTES <= guarded
    assert not (PROTECTED_SHARED_ADMIN_ROUTES & management)
    assert not (guarded & management), (
        "Admin routers have duplicate method/path registrations; "
        "a later route may be shadowed by registration order."
    )


if __name__ == "__main__":
    test_shared_admin_routes_have_one_canonical_registration()
    print("[ADMIN ROUTE UNIQUENESS PASS] Shared admin routes have one guarded registration.")
