# POL — flakiness, test independence and CI failure diagnosability

**TODO:** `TODO-136` · **Verified:** 2026-10-23 · **Guards:** `scripts/test_flake_policy.py`

## 1. Evidence from repeated runs (same SHA `d5c1096` tree)

| Run | Command | Result |
| --- | --- | --- |
| Python suite, run 1 | `python scripts/run_verification_suite.py` | **878 passed / 244.4 s** |
| Python suite, run 2 (earlier same tree, before TODO-132 tests) | same | **857 passed / 246.2 s** |
| Browser suite, parallel, doubled | `npx playwright test --repeat-each=2` in `mvp/apps/web` | **60 passed / 54.2 s** |
| Browser suite, fully serial | `npx playwright test --workers=1` | **30 passed / 53.4 s** |

Doubling every browser test exercises the same specs twice in one worker pool, which is
where shared cookies/localStorage/token state would corrupt the second run. Serial execution
removes worker-level isolation, so any reliance on another test's seeded data would surface.
Both passed.

Python ordering: the suite is file-ordered and DB-backed. Independence comes from each module
creating its own organizations/users with random phones/emails (`_seed_admin_vendor_retailer`,
`_seed_dispatch`, `_seed_user`), never from a shared world state. Two full runs on the same
tree produced identical pass counts with no retries.

## 2. Sleeps and fixed waits — full inventory

| Location | Kind | Verdict |
| --- | --- | --- |
| `scripts/test_http_live_transport.py:83` | 250 ms poll while waiting for uvicorn `healthz` (45 s deadline) | **allowlist** — bounded readiness poll, not a fixed wait |
| `scripts/test_http_live_transport.py:214` | 3 s socket hold to force a client read timeout | **allowlist** — the sleep *is* the condition under test |
| `scripts/notification_providers.py:76` | production backoff `delay_seconds` | production code, not a test |
| `scripts/worker_runtime.py:68` | worker poll interval | production code, not a test |
| `mvp/apps/web/tests/delivery-flow.spec.ts:86` | `test.setTimeout(240_000)` | budget for a cross-persona journey, not a sleep |

`scripts/test_flake_policy.py` fails the build if `time.sleep(` appears in any other
`scripts/test_*.py`, so a future copy-pasted sleep must be justified in this table first.

Browser specs use zero `waitForTimeout`; they rely on Playwright auto-retrying assertions
(`expect(locator).toBeVisible()` etc.) with an explicit 15 s expect timeout. Locators are
role/label based where the UI exposes them (guarded by a minimum `getByRole` count so a
regression to CSS-only selectors is visible in review).

## 3. Failure diagnosability

* `trace: "retain-on-failure"`, `screenshot: "only-on-failure"`, `video: "retain-on-failure"`
  — every failure leaves a replayable trace, a screenshot and a video under
  `mvp/apps/web/test-results/`.
* `retries: process.env.CI ? 1 : 0` — local runs never retry. In CI a retried test is reported
  as **flaky**, not passed, so the first failure stays visible in the run summary; the retained
  trace is from the failing attempt.
* Reporters: `list` + `html` + `json` (`test-results/results.json`), so a CI consumer can read
  the failure text without parsing console output.
* API server logs are piped into the Playwright output, and every request carries a
  `X-Correlation-ID` (TODO-086) that also appears in the failure output, so a browser failure
  can be matched to the exact server log line.
* Seeds are deterministic by role but unique per module (random phone/email/UUID). A failing
  run prints the identifiers it used in the assertion message.

## 4. Known order-dependence risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Shared `pol_test` database accumulates rows across modules | Every module creates fresh orgs/users; queries are scoped by those ids, never by "first row" |
| OTP rate limit is phone+IP scoped and IP is fixed (`testclient`) | Each test uses a fresh random phone; the one lockout test uses a fresh seeded user |
| Fixed calendar dates in seeds (inventory day, SLA windows) | Seeds derive dates from "today" in `Asia/Tehran`, matching the worker's configured timezone |
| Port collisions (`8001` API, `3000` web) | Config honours `POL_E2E_API_PORT`/`POL_E2E_WEB_PORT`; `reuseExistingServer` is off in CI so a stale server cannot be silently reused |

## 5. Reproduce

```powershell
cd mvp/apps/web
npx playwright test --repeat-each=2 --reporter=line
npx playwright test --workers=1 --reporter=line

cd C:\Star\pol\2.4
python -m pytest scripts/test_flake_policy.py -q
```

Debug a single failure:

```powershell
npx playwright test tests/<spec>.spec.ts --trace on --workers=1
npx playwright show-trace test-results/<trace>.zip
```
