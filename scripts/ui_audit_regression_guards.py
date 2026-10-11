#!/usr/bin/env python3
"""Source-level regression guards for high-risk POL web/mobile UI fixes.

These checks are intentionally labeled source-contract checks. They do not replace
browser E2E, API integration tests, emulator tests, or physical-device QA.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
BASKET_PATH = ROOT / "mvp/apps/web/src/app/(dashboard)/retailer/basket/page.tsx"
ORDER_PATH = ROOT / "mvp/apps/mobile/src/screens/OrderDetailMobileScreen.tsx"
BASKET_STORE_PATH = ROOT / "mvp/apps/web/src/lib/basket.ts"


def read(path: Path) -> str:
    if not path.is_file():
        raise AssertionError(f"Required source file is missing: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def between(source: str, start: str, end: str) -> str:
    a = source.find(start)
    if a < 0:
        raise AssertionError(f"Start marker not found: {start}")
    b = source.find(end, a + len(start))
    if b < 0:
        raise AssertionError(f"End marker not found: {end}")
    return source[a:b]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check(name: str, fn) -> bool:
    try:
        fn()
    except Exception as exc:
        print(f"FAIL | {name} | {exc}")
        return False
    print(f"PASS | {name}")
    return True


def main() -> int:
    basket = read(BASKET_PATH)
    store = read(BASKET_STORE_PATH)
    order = read(ORDER_PATH)
    push_fn = between(
        basket,
        "async function pushToServer(): Promise<boolean>",
        "  async function reviewAndCheckout()",
    )
    checkout_fn = between(
        basket,
        "  async function reviewAndCheckout()",
        "  if (lines.length === 0)",
    )
    load_fn = between(
        order,
        "  const load = useCallback(async () => {",
        "  }, [props.orderId, props.mode]);",
    )
    action_block = between(
        order,
        '              {status === "DISPATCHED" ? (',
        "              ) : null}",
    )

    checks = [
        (
            "Basket sync is explicitly success/failure typed",
            lambda: require(
                "async function pushToServer(): Promise<boolean>" in basket,
                "pushToServer must return Promise<boolean> so checkout can gate navigation.",
            ),
        ),
        (
            "A previously synchronized basket is reused before creating a new server basket",
            lambda: require(
                re.search(
                    r"if \(serverBasketId\)\s*\{\s*setSyncError\(null\);\s*setSynced\(true\);\s*return true;\s*\}",
                    push_fn,
                ) is not None
                and push_fn.find("if (serverBasketId)")
                < push_fn.find('getApi().post<BasketCreateResult>("/api/v1/baskets")'),
                "Repeat checkout actions must reuse the existing server basket rather than create another OPEN basket.",
            ),
        ),
        (
            "Local basket edits invalidate the previously synchronized server basket id",
            lambda: require(
                all(
                    re.search(
                        rf"{method}:[\s\S]*?const next = \{{ lines, serverBasketId: null \}};",
                        store,
                    ) is not None
                    for method in (
                        r"addLine",
                        r"setQuantity",
                        r"removeLine",
                    )
                ),
                "Adding, editing, or removing a local line must clear serverBasketId before resynchronization.",
            ),
        ),
        (
            "Retry after basket-sync failure follows the checkout navigation path",
            lambda: require(
                'onRetry={() => void reviewAndCheckout()}' in basket,
                "A successful retry from the sync error must navigate to checkout instead of only resyncing.",
            ),
        ),
        (
            "Empty retailer basket cannot be treated as synchronized",
            lambda: require(
                re.search(r"if \(lines\.length === 0\)\s*\{[^}]*return false;", push_fn, re.S) is not None,
                "The empty-basket branch must fail closed with return false.",
            ),
        ),
        (
            "Basket sync must await both basket creation and each item write",
            lambda: require(
                "await getApi().post<BasketCreateResult>(\"/api/v1/baskets\")" in push_fn
                and "await getApi().post<BasketItemResult>(" in push_fn
                and "expected_version: version" in push_fn,
                "Basket and item writes must remain awaited and version-aware.",
            ),
        ),
        (
            "Basket sync only returns success after server basket is recorded",
            lambda: require(
                re.search(r"setServerBasket\(basketId\);\s*setSynced\(true\);\s*return true;", push_fn) is not None,
                "Successful return must follow setServerBasket and setSynced.",
            ),
        ),
        (
            "Basket sync errors fail closed and clear syncing state",
            lambda: require(
                "catch (err)" in push_fn
                and "setSyncError(" in push_fn
                and "return false;" in push_fn
                and re.search(r"finally\s*\{\s*setSyncing\(false\);", push_fn) is not None,
                "The catch must report failure and return false; finally must clear syncing.",
            ),
        ),
        (
            "Retailer checkout navigation is gated by the sync result",
            lambda: require(
                re.search(
                    r"const syncedSuccessfully = await pushToServer\(\);\s*if \(syncedSuccessfully\)\s*router\.push\(\"/retailer/checkout\"\);",
                    checkout_fn,
                ) is not None
                and checkout_fn.count('router.push("/retailer/checkout")') == 1,
                "Checkout route must be navigated to only inside the success guard.",
            ),
        ),
        (
            "Delivery state is fetched in the shared order-load path for both roles",
            lambda: require(
                'api.get<{ delivery_status?: string | null }>(\"/api/v1/orders/\" + props.orderId + \"/delivery\")' in load_fn
                and load_fn.find('/delivery\")') < load_fn.find('if (props.mode === "retailer")')
                and "setDeliveryStatus(delivery.delivery_status || null)" in load_fn,
                "The delivery endpoint must be fetched before the retailer-only returns branch.",
            ),
        ),
        (
            "Delivery-state fetch failure is non-fatal and clears stale state",
            lambda: require(
                re.search(r"api\.get<\{ delivery_status\?: string \| null \}>\([\s\S]*?catch\s*\{\s*setDeliveryStatus\(null\);\s*\}", load_fn) is not None,
                "A delivery API failure must be caught and reset the displayed delivery state.",
            ),
        ),
        (
            "Vendor delivery buttons only offer the next valid transition",
            lambda: require(
                'deliveryStatus === "ASSIGNED"' in action_block
                and 'submitDeliveryStage("picked-up")' in action_block
                and 'deliveryStatus === "PICKED_UP"' in action_block
                and 'submitDeliveryStage("in-transit")' in action_block
                and 'deliveryStatus === "IN_TRANSIT"' in action_block
                and 'submitDeliveryStage("arrived")' in action_block,
                "Expected ASSIGNED→PICKED_UP→IN_TRANSIT→ARRIVED progression is incomplete.",
            ),
        ),
        (
            "Failed delivery displays an explicit operational recovery message",
            lambda: require(
                'deliveryStatus === "FAILED"' in action_block
                and "به رسیدگی عملیاتی نیاز دارد" in action_block,
                "FAILED delivery must not be presented as a normal next-step transition.",
            ),
        ),
        (
            "Retailer delivery confirmation requires ARRIVED, recipient, and OTP",
            lambda: require(
                'deliveryStatus !== "ARRIVED"' in order
                and "!deliveryRecipient.trim()" in order
                and "!deliveryOtp.trim()" in order,
                "Delivery confirmation must remain gated until arrival and required fields are present.",
            ),
        ),
    ]

    passed = 0
    for name, fn in checks:
        passed += int(check(name, fn))
    total = len(checks)
    print(f"\nPOL UI audit regression source guards: {passed}/{total} passed.")
    print("Note: These are source-contract guards, not browser/device E2E certification.")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
