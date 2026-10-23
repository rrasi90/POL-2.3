# POL API — OWASP API Security Top 10 (2023) matrix

**TODO:** `TODO-131` · **Status:** verified 2026-10-23 · **Scope:** every HTTP operation served by
`scripts/api/main.py` (157 operations / 138 paths, see [`API_SERVED_INVENTORY.md`](API_SERVED_INVENTORY.md)).

Two layers describe the same surface:

1. `API_SERVED_INVENTORY.md` — the generated endpoint list (method, path, auth column, deprecation).
2. This document — the endpoint × persona × property × action reasoning and the negative test
   that proves the control holds.

Nothing here invents a permission. Every "allowed/denied" cell is tied to a guard in
`scripts/api/dependencies.py` / the boundary and to the test named in the row.

---

## 1. Personas and authorization sources

| Persona | Token source | Guard |
| --- | --- | --- |
| `ADMIN_SUPER` / `OPS_ADMIN` | `/auth/verify-otp` (operator org) | `require_ops_actor`, `require_role(...)` in routes |
| `FIELD_ACTIVATOR` | same | `require_ops_actor` + field-task scoping |
| `VENDOR_OWNER` / `VENDOR_STAFF` | verify-otp (vendor org) | `require_vendor_actor`, `require_permission("inventory.adjust", …)` |
| `RETAILER_OWNER` / `RETAILER_STAFF` | verify-otp (retailer org) | `require_retailer_actor`, org scoping in the boundary |
| anonymous | none | every non-public route raises `INVALID_ACCESS_TOKEN` (401) |

Public allowlist: `POST /api/v1/auth/request-otp`, `POST /api/v1/auth/verify-otp`,
`POST /api/v1/auth/refresh`, `GET /healthz`, `GET /readyz`. Everything else requires a bearer token.

---

## 2. Top-10 rows

### API1 — Broken Object Level Authorization (BOLA/IDOR)

| Resource | Attack | Expected | Proof |
| --- | --- | --- | --- |
| order / timeline | retailer A reads retailer B's order | 403/404, no data | `test_http_negative_rbac_matrix.py::TestTenantIsolation` |
| invoice | any tenant reads a random/foreign invoice id | 404 `NOT_FOUND` | `test_owasp_api_top10.py::test_other_tenant_cannot_read_invoice` |
| support case | vendor reads a retailer's case | 403/404 | `test_owasp_api_top10.py::test_retailer_support_case_is_not_visible_to_vendor` |
| basket | another org mutates a basket id | 403/404 | `test_http_negative_rbac_matrix.py`, basket version conflicts |
| delivery exception / group | foreign ids | 404 for unknown, 403 for foreign org | `test_http_negative_rbac_matrix.py::TestMissingResources` |

### API2 — Broken Authentication

| Case | Expected | Proof |
| --- | --- | --- |
| missing bearer | 401 `INVALID_ACCESS_TOKEN` | `test_http_negative_rbac_matrix.py::TestAuthenticationRequired` |
| malformed JWT | 401 | same + `test_owasp_api_top10.py::test_malformed_bearer_token_is_rejected` |
| revoked / expired session | 401 | same file (`revoked`, `expired` cases) |
| refresh rotation / replay | old refresh token rejected | `test_auth_contract.py`, `test_http_auth_*` |
| OTP brute force | 429 lockout after N attempts | `test_http_auth_*` OTP lockout, `test_http_observability.py` |

### API3 — Broken Object Property Level Authorization

| Property | Attack | Expected | Proof |
| --- | --- | --- | --- |
| any request body | unknown/privileged field (`role`, `retailer_id`, `permissions`) | 422 `extra_forbidden` for all 55 request schemas | `test_owasp_api_top10.py::test_every_request_schema_forbids_additional_properties` + `test_mass_assignment_field_is_rejected_http` |
| vendor inventory | retailer sends `new_physical_quantity` | 403 `inventory.adjust` | `test_owasp_api_top10.py::test_retailer_cannot_adjust_vendor_inventory` |
| vendor product / prices | staff without the delegated permission | 403 | `test_http_admin_referrals` permission cases, `test_vendor_acceptance_contract.py` |
| status/ownership fields | client tries to set them directly | ignored or absent from the schema | inventory above + `test_schema_fuzz_boundaries.py` |

### API4 — Unrestricted Resource Consumption

Owned by **`TODO-132`** (OTP/login/search/pagination/upload rate and size caps). Existing evidence:
OTP rate limit + lockout (429), pagination caps (`limit ≤ 200`, `test_schema_fuzz_boundaries.py`),
basket/order idempotency. No new commercial limit is invented here; caps come from existing policy
constants and tests.

### API5 — Broken Function Level Authorization

| Surface | Attack | Expected | Proof |
| --- | --- | --- | --- |
| `/admin/*` | retailer token | 403 `FORBIDDEN` | `test_http_negative_rbac_matrix.py::TestRoleBoundaries`, `test_owasp_api_top10.py::test_retailer_cannot_reach_admin_user_management` |
| `/ops/analytics` | vendor token | 403 | `test_owasp_api_top10.py::test_vendor_cannot_reach_ops_analytics` |
| order dispatch/accept | retailer token | 403 | `test_http_negative_rbac_matrix.py` |
| worker-style surfaces | non-operator token | 403 | `test_owasp_api_top10.py::test_retailer_cannot_reach_admin_user_management` (worker message), `test_http_admin_authorization.py` |

### API6 — Unrestricted Access to Sensitive Business Flows

| Flow | Control | Proof |
| --- | --- | --- |
| OTP request | per-mobile rate limit + lockout | `test_http_auth_*`, `test_http_observability.py` |
| checkout | idempotency key + request fingerprint, stale plan → 409 | `test_checkout_fingerprint.py`, `test_canonical_runtime_regressions.py` |
| payment evidence / verify | single-use transitions, role-scoped | `test_http_payment_evidence.py` |
| refunds / RMA | state machine + role gates | `test_batch3_contract_matrix.py`, `test_http_*refund*` |

### API7 — Server Side Request Forgery

**Not applicable today.** No endpoint accepts a URL that the server fetches; `icon_url` on category
schemas is persisted metadata, not fetched. Guard test:
`test_owasp_api_top10.py::test_no_request_model_accepts_a_server_side_fetch_url`.
If a webhook/callback/fetch feature is added, this row must gain a negative test first.

### API8 — Security Misconfiguration

| Check | Expected | Proof |
| --- | --- | --- |
| CORS in production | explicit allowlist required, wildcard rejected | `test_api_config_exposure.py::test_production_requires_explicit_cors_origins`, `test_production_rejects_wildcard_cors` |
| dev CORS | loopback only, `*` dropped | `test_default_development_origins_are_loopback_only`, `test_development_drops_wildcard_and_keeps_allowlist` |
| transport headers | nosniff, frame-deny, referrer, permissions; HSTS in prod only | `test_security_headers_are_present_in_every_environment`, `test_production_adds_hsts_and_disables_docs` |
| docs/schema in production | `/docs`, `/redoc`, `/openapi.json` disabled | `test_production_adds_hsts_and_disables_docs` |
| client configuration | base URLs only from env, loopback defaults, no hardcoded credentials | `test_client_base_urls_come_from_environment_and_default_to_loopback`, `test_no_hardcoded_credentials_in_shipped_client_sources` |

### API9 — Improper Inventory Management

| Check | Proof |
| --- | --- |
| every served operation is inventoried (method/path/auth/deprecated) | `test_api_inventory.py::test_served_inventory_matches_openapi` |
| no deprecated operations served | `test_api_inventory.py::test_inventory_has_no_deprecated_operations` |
| unique operation ids and summaries | `test_api_inventory.py::test_every_operation_has_a_unique_operation_id_and_summary` |
| curated map matches the runtime schema (method + path) | `test_api_contract_drift.py::test_api_map_rows_exist_in_openapi` |
| clients only call served paths | `test_api_contract_drift.py::test_client_call_sites_resolve_to_openapi_paths` |
| contract fingerprint (status codes, required fields, enums) | `test_api_contract_drift.py::test_openapi_fingerprint_matches_committed_snapshot` |

### API10 — Unsafe Consumption of Third-Party APIs

| Control | Proof |
| --- | --- |
| explicit endpoint/credential configuration, never silent | `test_route_hardening.py::test_external_provider_configuration_is_explicit` |
| timeout and transient/permanent classification | `test_provider_adapter_contract.py` |
| unverifiable 2xx body is never reported as delivered | `test_provider_adapter_contract.py::test_unverifiable_2xx_is_not_reported_as_success` |
| no raw third-party payload persisted as success evidence | `metadata["response"]` only for dict bodies with a provider id |
| SSRF/URL-fetch surface | see API7 (none) |

---

## 3. Known residual risks

| Risk | Owner / decision |
| --- | --- |
| `POST /baskets` declares no body, so a body is ignored rather than rejected | cosmetic; basket creation is scoped to the authenticated org |
| Permission/validation ordering: an invalid query string returns 422 before 403 on some ops routes | standard FastAPI ordering; no data disclosed |
| Admin broadcast `priority` accepts `URGENT` even though `admin_broadcasts` DB legacy row shows `CRITICAL` in one migration | schema now enforces the `broadcast_messages` constraint; DB is the authority |
| API4 numeric caps for OTP/search/upload | `TODO-132` |
| Live provider credentials and webhook signature verification | blocked on procurement (`TODO-077`, `TODO-125`) |

---

## 4. Reproduce

```powershell
$env:ENVIRONMENT='test'; $env:POL_API_DB_NAME='pol_test'
python -m pytest scripts/test_owasp_api_top10.py scripts/test_api_config_exposure.py `
  scripts/test_api_inventory.py scripts/test_api_contract_drift.py `
  scripts/test_provider_adapter_contract.py scripts/test_http_negative_rbac_matrix.py -q
```
