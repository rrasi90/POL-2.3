# Historical verification evidence archive

**Snapshot date:** 2026-10-23  
**Source PR:** [#47 — test: fix POD proof media isolation and record journey/security evidence](https://github.com/rrasi90/POL-2.3/pull/47)  
**Observed PR head:** `c700232c80cf78dd471ec5b8ca55fcad2b13c414`  
**Archived by:** integration branch `integration/pol-2.3-mainline-consolidation-2026-11`

These documents are retained as historical engineering evidence, not current certification. Some underlying rows refer to older source SHAs such as `d5c1096` or `c65c282`. The data is useful as a starting point for audits and test recreation, but must be regenerated/revalidated against the exact target SHA before release or current-state claims.

## Archived documents

- [API served endpoint inventory](API_SERVED_INVENTORY.md) — generated endpoint list from the historical OpenAPI tree.
- [API/UI/test traceability matrix](API_UI_TRACEABILITY_MATRIX.md) — static route and HTTP scenario matching snapshot.
- [Bug reproduction log](BUG_REPRODUCTION_LOG.md) — historical issue register; status claims remain tied to each recorded SHA.
- [Flakiness audit](FLAKE_AUDIT.md) — historical repeated-run measurements.
- [OWASP API security matrix](OWASP_API_SECURITY_MATRIX.md) — historical route/persona/security coverage assessment.
- [Resource limits](RESOURCE_LIMITS.md) — historical API limits and test references; not a load-test report.
- [Screen/test parity](SCREEN_TEST_PARITY.md) — historical generated screen/API/browser coverage matrix.

## Rules for reuse

1. Do not replace current `mvp/MVP_SCREEN_MATRIX.md`, `TODO_LIST.md`, or current API inventory with these snapshots.
2. Do not copy `PASS`, `VERIFIED`, or `CLOSED` values into current tracking without fresh execution evidence.
3. Regenerate generated matrices using their documented generator only after confirming the generator and inputs on the target SHA.
4. Keep each original source SHA and run date when reproducing a result.
5. Compare endpoint inventory and security assertions with the consolidated route tree, including current support-message history and duplicate-admin-route removals.