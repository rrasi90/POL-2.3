"""POL production FastAPI transport entrypoint.

FastAPI is intentionally thin:
HTTP → authentication/session → ApplicationContext → POLApplicationBoundary
→ canonical service → PostgreSQL transaction → outbox/worker.
"""

from __future__ import annotations

import os
import re
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from scripts.api.errors import (
    auth_error_handler,
    generic_error_handler,
    http_exception_handler,
    key_error_handler,
    otp_lockout_handler,
    otp_rate_limit_handler,
    permission_handler,
    request_validation_handler,
    value_error_handler,
)
from scripts.api.routes.auth import router as auth_router
from scripts.api.routes.baskets import router as baskets_router
from scripts.api.routes.catalog import router as catalog_router
from scripts.api.routes.profile import membership_router, router as profile_router
from scripts.api.routes.orders import router as orders_router
from scripts.api.routes.returns import router as returns_order_router
from scripts.api.routes.returns import returns_router
from scripts.api.routes.disputes import router as disputes_order_router
from scripts.api.routes.disputes import disputes_router
from scripts.api.routes.vendor_catalog import router as vendor_catalog_router
from scripts.api.routes.daily_inventory import router as daily_inventory_router
from scripts.api.routes.reconciliation import router as reconciliation_router
from scripts.api.routes.support import router as support_router
from scripts.api.routes.admin import router as admin_router
from scripts.api.routes.referrals import router as referrals_router
from scripts.api.routes.notifications import router as notifications_router
from scripts.api.routes.field import router as field_router
from scripts.api.routes.vendor_storefront import router as vendor_storefront_router
from scripts.api.routes.catalog_search import router as catalog_search_router
from scripts.api.routes.finance import (
    invoices_router as finance_invoices_router,
    order_invoice_router as finance_order_invoice_router,
    settlements_router as finance_settlements_router,
    settlement_detail_router as finance_settlement_detail_router,
)
from starlette.exceptions import HTTPException as StarletteHTTPException

from scripts.auth_boundary import (
    AuthError,
    InvalidRefreshTokenError,
    OTPRateLimitError,
    OTPLockoutError,
    SessionExpiredError,
    SessionRevokedError,
)

_CORRELATION_ID_RE = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


def create_app() -> FastAPI:
    app = FastAPI(
        title="POL API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    environment = os.getenv("ENVIRONMENT", "").lower()
    configured_origins = [
        origin.strip()
        for origin in os.getenv("POL_CORS_ORIGINS", "").split(",")
        if origin.strip()
    ]
    if configured_origins:
        cors_origins = configured_origins
    elif environment in {"prod", "production"}:
        raise RuntimeError("POL_CORS_ORIGINS must be configured in production.")
    else:
        cors_origins = [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
        ]

    if "*" in cors_origins:
        if environment in {"prod", "production"}:
            raise RuntimeError("Wildcard CORS is forbidden in production.")
        cors_origins = [o for o in cors_origins if o != "*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Correlation-ID"],
        expose_headers=["X-Correlation-ID"],
    )
    @app.middleware("http")
    async def correlation_middleware(request: Request, call_next):
        supplied = request.headers.get("X-Correlation-ID", "").strip()
        correlation_id = supplied if _CORRELATION_ID_RE.fullmatch(supplied) else str(uuid4())
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response

    @app.get("/healthz", tags=["ops"])
    def healthz():
        return {"status": "ok"}

    @app.get("/readyz", tags=["ops"])
    def readyz():
        from scripts.api.db import get_runtime_connection

        conn = get_runtime_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
            return {"status": "ready"}
        finally:
            conn.close()

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(baskets_router, prefix="/api/v1")
    app.include_router(catalog_router, prefix="/api/v1")
    app.include_router(vendor_catalog_router, prefix="/api/v1")
    app.include_router(daily_inventory_router, prefix="/api/v1")
    app.include_router(profile_router, prefix="/api/v1")
    app.include_router(membership_router, prefix="/api/v1")
    app.include_router(orders_router, prefix="/api/v1")
    app.include_router(returns_order_router, prefix="/api/v1")
    app.include_router(returns_router, prefix="/api/v1")
    app.include_router(disputes_order_router, prefix="/api/v1")
    app.include_router(disputes_router, prefix="/api/v1")
    app.include_router(support_router, prefix="/api/v1")
    app.include_router(finance_invoices_router, prefix="/api/v1")
    app.include_router(finance_order_invoice_router, prefix="/api/v1")
    app.include_router(finance_settlements_router, prefix="/api/v1")
    app.include_router(finance_settlement_detail_router, prefix="/api/v1")
    app.include_router(reconciliation_router, prefix="/api/v1")
    app.include_router(admin_router, prefix="/api/v1")
    app.include_router(referrals_router, prefix="/api/v1")
    app.include_router(notifications_router, prefix="/api/v1")
    app.include_router(field_router, prefix="/api/v1")
    app.include_router(vendor_storefront_router, prefix="/api/v1")
    app.include_router(catalog_search_router, prefix="/api/v1")

    app.add_exception_handler(RequestValidationError, request_validation_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(InvalidRefreshTokenError, auth_error_handler)
    app.add_exception_handler(SessionExpiredError, auth_error_handler)
    app.add_exception_handler(SessionRevokedError, auth_error_handler)
    app.add_exception_handler(AuthError, auth_error_handler)
    app.add_exception_handler(OTPRateLimitError, otp_rate_limit_handler)
    app.add_exception_handler(OTPLockoutError, otp_lockout_handler)
    app.add_exception_handler(PermissionError, permission_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(KeyError, key_error_handler)
    app.add_exception_handler(Exception, generic_error_handler)

    return app


app = create_app()
