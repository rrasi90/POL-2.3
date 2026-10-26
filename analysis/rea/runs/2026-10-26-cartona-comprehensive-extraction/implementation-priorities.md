# Implementation Priorities — POL alignment (comprehensive run)

Carries forward the P0-P3 ladder from `runs/2026-10-26-cartona-revision-2-import-02/implementation-priorities.md` and refines it with this run's new evidence. POL code untouched in this phase.

## Refinements from new evidence
1. **J8e (multi-step business signup)** rises: Cartona's signup captures business name/type/address/landmark with per-field state — POL's single-step mock login blocks the B2B trust model. Recommend folding into the P0/P1 window after cart foundation.
2. **J8a (approval + confirmation-call step)** is a distinctive B2B trust flow; design an independent pending-approval state rather than auto-activating new retailers.
3. **J8b (supplier badges)** is cheap to add once the supplier model exists — fold into J2a supplier screens.
4. **J8d (abandoned-cart TTL as config)** shapes the J3c cart-recovery design — make the TTL server-configurable from day one.
5. **J8h (wallet copy)** strengthens the P2 wallet case; no new work until payment rails are decided.
6. **J8c/J8f/J8g** remain Phase 3 (anti-fraud, companion-app links, seasonal theming) — valuable, not MVP-blocking.

## Priority order (unchanged core, refined)
P0: cart persistence + server sync (J3a), order lifecycle statuses (J3e), push notifications (J6a).
P1: reorder (J3d), supplier catalogue + search (J2a/J2b), cart validation (J3b), favorites (J2c), **multi-step signup (J8e)**.
P2: branches (J4a), guest browsing (J1b), order tickets (J3g), service-area gate (J1c), **approval flow (J8a)**, wallet (J5a + J8h).
P3: BNPL (J5b), stories (J6c), GMV targets (J6d), sub-users (J4b), deep links (J7b), integrity (J7c + J8c), seasonal theming (J8g), companion-app links (J8f).

## Non-goals
Do not copy Cartona's vendor choices (AppsFlyer/PostHog/Freshchat) — evaluate Iranian-market equivalents (Cartona itself ships Huawei support for exactly this reason). Do not embed client API keys (Cartona's embedded AIzaSy key is a cautionary example). Do not replicate cleartext allowances — POL keeps TLS-only.
