#!/usr/bin/env python3
"""Live basket -> allocation -> checkout -> order lifecycle e2e against FastAPI :8000."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
import uuid

BASE = "http://127.0.0.1:8000"
PHONE = "+989160007777"
OTP = "123456"
RESULTS: list[dict] = []


def req(method: str, path: str, token: str | None = None, body: dict | None = None, headers: dict | None = None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    if headers:
        h.update(headers)
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=20) as resp:
            raw = resp.read().decode()
            try:
                parsed = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                parsed = {"_raw": raw[:500]}
            return resp.status, parsed
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            parsed = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            parsed = {"_raw": raw[:800]}
        return e.code, parsed


def step(name: str, status: int, ok: bool, detail: str = ""):
    RESULTS.append({"name": name, "status": status, "ok": ok, "detail": detail})
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] {name} status={status} {detail}")


def main() -> int:
    # health
    st, body = req("GET", "/healthz")
    step("healthz", st, st == 200)
    if st != 200:
        return 1

    # auth
    st, body = req("POST", "/api/v1/auth/request-otp", body={"mobile_number": PHONE})
    step("request_otp", st, st == 200 and body.get("success") is True)
    st, body = req(
        "POST",
        "/api/v1/auth/verify-otp",
        body={"mobile_number": PHONE, "otp_code": OTP},
    )
    token = (body.get("data") or {}).get("access_token") if isinstance(body, dict) else None
    step("verify_otp", st, st == 200 and bool(token), f"token_len={len(token or '')}")
    if not token:
        print(json.dumps(body, indent=2)[:800])
        return 1

    # profile context (confirm retailer org)
    st, body = req("GET", "/api/v1/profile/context", token=token)
    ctx = body.get("data") or {}
    step("profile_context", st, st == 200, f"org={ctx.get('organization',{}).get('org_type') if isinstance(ctx.get('organization'), dict) else ctx.get('org_type')}")

    # catalog product (q required)
    st, body = req("GET", "/api/v1/catalog/search?q=a&limit=10", token=token)
    data = body.get("data") or body
    items = data.get("items") or data.get("products") or []
    step("catalog_search", st, st == 200 and len(items or []) > 0, f"n={len(items or [])}")
    if not items:
        st, body = req("GET", "/api/v1/search?q=a&type=product&page_size=10", token=token)
        data = body.get("data") or body
        items = (data.get("products") or data.get("items") or []) if isinstance(data, dict) else (data or [])
        step("unified_search", st, st == 200 and len(items) > 0, f"n={len(items)}")
    if not items:
        print("NO_PRODUCTS", json.dumps(body)[:500])
        return 1

    product = items[0]
    product_id = product.get("id") or product.get("product_id")
    step("pick_product", 200, bool(product_id), f"product_id={product_id}")

    # create basket
    st, body = req("POST", "/api/v1/baskets", token=token)
    basket = body.get("data") or {}
    basket_id = basket.get("basket_id") or basket.get("id")
    version = basket.get("version", 1)
    step("basket_create", st, st in (200, 201) and bool(basket_id), f"basket={basket_id} v={version}")

    # add item
    st, body = req(
        "POST",
        f"/api/v1/baskets/{basket_id}/items",
        token=token,
        body={
            "product_id": product_id,
            "requested_quantity": 2,
            "pack_quantity": 1,
            "expected_version": version,
        },
    )
    added = body.get("data") or {}
    version = added.get("version", version + 1)
    step("basket_add_item", st, st == 200, f"v={version} {str(body.get('error') or '')[:120]}")

    # allocation preview
    st, body = req("POST", f"/api/v1/baskets/{basket_id}/allocation-preview", token=token)
    preview = body.get("data") or {}
    plan_id = preview.get("allocation_plan_id") or preview.get("plan_id")
    vendors = preview.get("allocated_vendors") or []
    summary = preview.get("summary") or {}
    step(
        "allocation_preview",
        st,
        st == 200 and bool(plan_id),
        f"plan={plan_id} vendors={len(vendors)} total={summary.get('total_amount_toman')}",
    )
    if not plan_id:
        print(json.dumps(body, indent=2)[:1200])
        return 1

    # checkout
    st, body = req(
        "POST",
        "/api/v1/orders",
        token=token,
        headers={"Idempotency-Key": str(uuid.uuid4())},
        body={
            "allocation_plan_id": plan_id,
            "delivery_address": "Ahvaz, Naderi, Live E2E Street 1",
            "preferred_payment_method": "CASH_ON_DELIVERY",
        },
    )
    checkout = body.get("data") or {}
    group_id = checkout.get("order_group_id")
    child_orders = checkout.get("child_orders") or []
    step(
        "checkout",
        st,
        st == 201 and bool(group_id) and len(child_orders) > 0,
        f"group={group_id} children={len(child_orders)}",
    )
    if st != 201:
        print(json.dumps(body, indent=2)[:1200])
        return 1

    order_id = child_orders[0].get("order_id") or child_orders[0].get("id")

    # order group read
    st, body = req("GET", f"/api/v1/orders/group/{group_id}", token=token)
    step("order_group_get", st, st == 200, f"status={(body.get('data') or {}).get('status') or (body.get('data') or {}).get('group_status')}")

    # child orders list
    st, body = req("GET", f"/api/v1/orders/group/{group_id}/orders", token=token)
    listed = body.get("data") or []
    step("order_group_children", st, st == 200 and len(listed or []) > 0, f"n={len(listed or [])}")

    # order detail
    st, body = req("GET", f"/api/v1/orders/{order_id}", token=token)
    detail = body.get("data") or {}
    step("order_detail", st, st == 200, f"status={detail.get('status') or detail.get('order_status')}")

    # order items
    st, body = req("GET", f"/api/v1/orders/{order_id}/items", token=token)
    oitems = body.get("data") or []
    step("order_items", st, st == 200 and len(oitems or []) > 0, f"n={len(oitems or [])}")

    # timeline
    st, body = req("GET", f"/api/v1/orders/{order_id}/timeline", token=token)
    events = body.get("data") or []
    step("order_timeline", st, st == 200 and len(events or []) > 0, f"events={len(events or [])}")

    # orders list for retailer
    st, body = req("GET", "/api/v1/orders?limit=5", token=token)
    orders = body.get("data") or []
    step("orders_list", st, st == 200, f"n={len(orders or []) if isinstance(orders, list) else 'obj'}")

    out = r"C:\Star\pol\2.4\artifacts\live_basket_checkout_e2e.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(
            {
                "passed": sum(1 for r in RESULTS if r["ok"]),
                "failed": sum(1 for r in RESULTS if not r["ok"]),
                "results": RESULTS,
                "order_id": order_id,
                "group_id": group_id,
                "plan_id": plan_id,
                "basket_id": basket_id,
            },
            f,
            indent=2,
        )
    failed = [r for r in RESULTS if not r["ok"]]
    print(f"\nSUMMARY passed={len(RESULTS)-len(failed)} failed={len(failed)} out={out}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
