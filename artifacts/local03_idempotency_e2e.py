#!/usr/bin/env python3
"""LOCAL-03 idempotency replay + conflict test against live FastAPI :8000 on DB pol."""
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


def req(method, path, token=None, body=None, headers=None):
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


def step(name, status, ok, detail=""):
    RESULTS.append({"name": name, "status": status, "ok": ok, "detail": detail})
    print(f"[{'PASS' if ok else 'FAIL'}] {name} status={status} {detail}")


def db_query(sql, params=()):
    import psycopg2

    conn = psycopg2.connect(dbname="pol", user="postgres", host="127.0.0.1", port=5432)
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        conn.commit()
        return rows
    finally:
        conn.close()


def main() -> int:
    st, body = req("GET", "/healthz")
    step("healthz", st, st == 200)
    if st != 200:
        return 1

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

    # build basket -> plan (fresh plan per run)
    st, body = req(
        "GET",
        "/api/v1/catalog/search?q=a&limit=10",
        token=token,
    )
    items = (body.get("data") or {}).get("items") or (body.get("data") or {}).get("products") or []
    step("catalog_search", st, st == 200 and len(items) > 0, f"n={len(items)}")
    if not items:
        return 1
    product_id = items[0].get("id") or items[0].get("product_id")

    st, body = req("POST", "/api/v1/baskets", token=token)
    basket = body.get("data") or {}
    basket_id = basket.get("basket_id") or basket.get("id")
    version = basket.get("version", 1)
    step("basket_create", st, st in (200, 201) and bool(basket_id), f"basket={basket_id}")

    st, body = req(
        "POST",
        f"/api/v1/baskets/{basket_id}/items",
        token=token,
        body={
            "product_id": product_id,
            "requested_quantity": 1,
            "pack_quantity": 1,
            "expected_version": version,
        },
    )
    added = body.get("data") or {}
    version = added.get("version", version + 1)
    step("basket_add_item", st, st == 200, f"v={version}")

    st, body = req(
        "POST",
        f"/api/v1/baskets/{basket_id}/allocation-preview",
        token=token,
    )
    preview = body.get("data") or {}
    plan_id = preview.get("allocation_plan_id") or preview.get("plan_id")
    step("allocation_preview", st, st == 200 and bool(plan_id), f"plan={plan_id}")
    if not plan_id:
        print(json.dumps(body, indent=2)[:1200])
        return 1

    idem_key = str(uuid.uuid4())
    address = "Ahvaz, Naderi, LOCAL-03 Street"
    payload = {
        "allocation_plan_id": plan_id,
        "delivery_address": address,
        "preferred_payment_method": "CASH_ON_DELIVERY",
    }

    # Request 1
    st1, body1 = req(
        "POST",
        "/api/v1/orders",
        token=token,
        headers={"Idempotency-Key": idem_key},
        body=payload,
    )
    data1 = body1.get("data") or {}
    group1 = data1.get("order_group_id")
    replay_flag1 = data1.get("idempotent_replay")
    children1 = data1.get("child_orders") or []
    step(
        "first_request",
        st1,
        st1 == 201 and bool(group1) and not replay_flag1,
        f"group={group1} children={len(children1)} idempotent_replay={replay_flag1}",
    )
    if not group1:
        print(json.dumps(body1, indent=2)[:1500])
        return 1

    # Request 2 — exact replay
    st2, body2 = req(
        "POST",
        "/api/v1/orders",
        token=token,
        headers={"Idempotency-Key": idem_key},
        body=payload,
    )
    data2 = body2.get("data") or {}
    group2 = data2.get("order_group_id")
    replay_flag2 = data2.get("idempotent_replay")
    step(
        "exact_replay",
        st2,
        st2 in (200, 201) and group2 == group1 and replay_flag2 is True,
        f"group={group2} idempotent_replay={replay_flag2}",
    )

    # Request 3 — same key, different payload
    payload_conflict = dict(payload)
    payload_conflict["delivery_address"] = "Ahvaz, DIFFERENT address for conflict test"
    st3, body3 = req(
        "POST",
        "/api/v1/orders",
        token=token,
        headers={"Idempotency-Key": idem_key},
        body=payload_conflict,
    )
    conflict_rejected = st3 >= 400 and st3 not in (200, 201)
    data3 = body3.get("data") or {}
    group3 = data3.get("order_group_id")
    step(
        "different_payload_same_key",
        st3,
        conflict_rejected and (group3 is None or group3 == group1),
        f"rejected={conflict_rejected} group={group3} err={(body3.get('error') or {}).get('code') if isinstance(body3.get('error'), dict) else body3.get('error')}",
    )

    # DB checks
    rows = db_query(
        "SELECT count(*) FROM order_groups WHERE checkout_idempotency_key = %s;",
        (idem_key,),
    )
    dup_groups = rows[0][0] if rows else -1
    step("duplicate_db_check", 200, dup_groups == 1, f"order_groups_with_key={dup_groups}")

    rows_all = db_query(
        "SELECT count(*) FROM order_groups WHERE checkout_idempotency_key = %s;",
        (idem_key,),
    )
    # total groups created by this basket plan should be 1 even after conflict attempt
    rows_plan = db_query(
        "SELECT count(*) FROM order_groups og "
        "JOIN orders o ON o.order_group_id = og.id "
        "WHERE og.checkout_idempotency_key = %s;",
        (idem_key,),
    )
    step(
        "no_new_group_after_conflict",
        200,
        (rows_plan[0][0] if rows_plan else -1) >= 1 and dup_groups == 1,
        f"groups={dup_groups}",
    )

    # capture ids for report
    child_ids = [c.get("order_id") or c.get("id") for c in children1]
    vendor_ids = []
    for oid in child_ids:
        r = db_query("SELECT vendor_id FROM orders WHERE id = %s;", (oid,))
        if r and r[0][0]:
            vendor_ids.append(str(r[0][0]))

    out = r"C:\Star\pol\2.4\artifacts\local03_idempotency_e2e.json"
    summary = {
        "passed": sum(1 for r in RESULTS if r["ok"]),
        "failed": sum(1 for r in RESULTS if not r["ok"]),
        "results": RESULTS,
        "basket_id": basket_id,
        "allocation_plan_id": plan_id,
        "order_group_id": group1,
        "child_order_ids": child_ids,
        "vendor_ids": vendor_ids,
        "idempotency_key": idem_key,
        "FIRST REQUEST": "PASS" if RESULTS[7]["ok"] else "FAIL",
        "EXACT REPLAY": "PASS" if RESULTS[8]["ok"] else "FAIL",
        "DIFFERENT PAYLOAD SAME KEY": "PASS" if RESULTS[9]["ok"] else "FAIL",
        "DUPLICATE DB CHECK": "PASS" if RESULTS[10]["ok"] else "FAIL",
        "NO NEW GROUP AFTER CONFLICT": "PASS" if RESULTS[11]["ok"] else "FAIL",
    }
    with open(out, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    failed = [r for r in RESULTS if not r["ok"]]
    print(f"\nSUMMARY passed={len(RESULTS) - len(failed)} failed={len(failed)} out={out}")
    print(json.dumps({k: summary[k] for k in (
        "FIRST REQUEST", "EXACT REPLAY", "DUPLICATE DB CHECK",
        "DIFFERENT PAYLOAD SAME KEY", "basket_id", "allocation_plan_id",
        "order_group_id", "child_order_ids", "vendor_ids")}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
