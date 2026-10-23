# POL API — resource limits and abuse guards

**TODO:** `TODO-132` · **Verified:** 2026-10-23 · **Tests:** `scripts/test_resource_limits.py` (20)

This is the answer to "what stops one caller from spending our money or our database?"
Every cap below is either a **policy value** that already exists in
`scripts/operational_config.py` (D-018, media policy) or a **technical payload guard**
explicitly labelled as such. No commercial number was invented for this task, and no
load test was run — load/stress belongs to `TODO-147` on an isolated environment.

## 1. Limits enforced inside the API

| Surface | Cap | Source | Enforcement | Proof |
| --- | --- | --- | --- | --- |
| OTP request | 3 per phone+IP per 5 min | `OTP_RATE_LIMIT_COUNT` / `OTP_RATE_LIMIT_WINDOW_MINUTES` (D-018) | `AuthService.request_otp`, advisory lock per phone+IP | `test_rate_limit_stops_provider_sends_at_the_policy_count`, `test_http_auth_matrix.py::test_request_otp_rate_limit_after_three_requests` |
| OTP verify | 5 wrong attempts → 10 min phone lock | `OTP_MAX_ATTEMPTS` / `OTP_LOCKOUT_MINUTES` (D-018) | `AuthService.verify_otp`, committed on failure | `test_wrong_otp_attempts_lock_the_phone` |
| OTP resend cadence | 60 s | `OTP_RESEND_INTERVAL_SECONDS` (D-018) | `AuthService.request_otp` | `test_auth_contract.py` RL series |
| SMS spend | at most 3 provider sends per phone+IP window; the 4th request raises **before** the adapter is built | D-018 + adapter call ordering | `request_otp` | `test_rate_limit_stops_provider_sends_at_the_policy_count` (counting adapter: exactly 3 sends) |
| List pagination | every `limit`/`page_size` has a hard `maximum` ≤ 500 (defaults ≤ 200); `offset` ≥ 0 | route `Query(le=…)` declarations | FastAPI validation → 422 | `test_every_page_size_query_has_a_hard_maximum`, `test_oversized_page_requests_are_rejected` (6 endpoints) |
| Bulk arrays | 500 rows per request array | `MAX_BULK_ITEMS` (technical guard) | Pydantic `max_length` on `items`/`changes` | `test_bulk_arrays_declare_the_shared_cap`, `test_oversized_dispute_item_list_is_rejected` |
| JSON body size | 1 MiB | `MAX_JSON_BODY_BYTES` (technical guard) | `body_size_middleware` → 413 `PAYLOAD_TOO_LARGE` (checks `Content-Length` **and** measures chunked bodies) | `test_oversized_json_body_is_413_with_envelope`, `test_chunked_body_without_content_length_is_still_bounded` |
| Multipart uploads | refused at the API | media is presigned/direct-to-storage | `body_size_middleware` | `test_multipart_uploads_are_not_accepted_through_the_api` |
| Upload size | 5 MiB declared size; image mime allowlist | `MAX_UPLOAD_BYTES` / `media_service` | schema `file_size_bytes ≤ 5 MiB` → 422 before a URL is issued; storage re-checks the real object | `test_declared_upload_size_over_cap_is_rejected` (presign + resumable init) |
| Provider calls | one attempt per send, 10 s timeout, no retry storm | `provider_adapters` | adapter unit contract | `test_provider_adapter_contract.py` |
| Notification retries | 3 attempts with 30/120/600 s backoff | `NOTIFICATION_MAX_RETRIES` / `NOTIFICATION_BACKOFF_SECONDS` | worker | worker tests (`test_worker_*`) |
| Checkout / refund replay | idempotency key + fingerprint, stale plan → 409 | route-level idempotency | boundary | `test_checkout_fingerprint.py`, `test_batch3_contract_matrix.py` |

## 2. What the API does **not** do (and who must)

| Gap | Why it is not in the app | Where it belongs | Owner / TODO |
| --- | --- | --- | --- |
| Per-IP request-rate limiting for search, catalog and other read-heavy endpoints | Needs a shared counter; in-process limits are wrong behind multiple workers | Edge gateway / ingress (e.g. `limit_req`, WAF) with the same 429 envelope | deployment config + `TODO-084` release checklist |
| Connection/TLS limits, slowloris, max header size | Transport concerns, not application concerns | Reverse proxy | deployment config |
| Global request rate per token | Same shared-counter problem | Gateway | deployment config |
| Deep `offset` cost (`offset=10^6`) | Valid but slow; capping it would be a product decision | Query optimisation + monitoring | `TODO-147` load test |
| `page × page_size` multiplication on paged searches | `page` is unbounded by design (page numbers are meaningful) | Monitor; add a max page only if measurements demand it | `TODO-147` |
| SMS cost budget per day/tenant | Commercial policy — not invented here | `DECISION_REGISTER.md` | product owner |
| Seeded/automated account abuse | Pilot uses operator-created accounts | Ops process | `TODO-118` (if applicable) |

The gateway rules must return the same contract as the API (`429` + `{success:false,error.code}`),
so clients do not need a second error path. That requirement is recorded here and repeated
in the release checklist (`TODO-084`).

## 3. Reproduce

```powershell
$env:ENVIRONMENT='test'; $env:POL_API_DB_NAME='pol_test'
python -m pytest scripts/test_resource_limits.py scripts/test_http_auth_matrix.py -q
```
