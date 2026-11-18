import { expect, test } from "@playwright/test";
import { formatPackagingUnit, formatFreshnessStatus } from "../src/lib/format-labels";
import { vendorProductDisplayName } from "../src/app/(dashboard)/vendor/_shared";
import {
  formatDeliveryStatus as formatOpsDeliveryStatus,
  formatFulfillmentStatus as formatOpsFulfillmentStatus,
  formatOperationalStatus as formatOpsStatus,
  formatTimelineEventLabel as formatOpsEvent,
} from "../src/app/(dashboard)/ops/_shared";
import {
  formatDeliveryStatus as formatRetailDeliveryStatus,
  formatFulfillmentStatus as formatRetailFulfillmentStatus,
  formatOperationalStatus as formatRetailStatus,
  formatTimelineEventLabel as formatRetailEvent,
} from "../src/app/(dashboard)/retailer/shared";

test.describe("Persian operational status labels", () => {
  test("operations order, group and reconciliation states are localized", () => {
    expect(formatOpsStatus("SUBMITTED")).toBe("ثبت‌شده");
    expect(formatOpsStatus("ACTIVE")).toBe("فعال");
    expect(formatOpsStatus("PARTIALLY_MATCHED")).toBe("مطابق جزئی");
    expect(formatOpsStatus("IN_TRANSIT")).toBe("در مسیر");
  });

  test("resource-specific return status is preserved in its own label map", () => {
    expect(formatOpsStatus("REFUNDED")).toBe("بازپرداخت‌شده");
    expect(formatRetailStatus("REQUESTED")).toBe("درخواست‌شده");
  });

  test("delivery and fulfillment states avoid raw enum labels", () => {
    expect(formatOpsDeliveryStatus("ASSIGNED")).toBe("راننده تعیین‌شده");
    expect(formatOpsDeliveryStatus("ARRIVED")).toBe("رسیده به مقصد");
    expect(formatOpsFulfillmentStatus("PARTIALLY_FULFILLED")).toBe("تکمیل جزئی");
    expect(formatRetailDeliveryStatus("PICKED_UP")).toBe("جمع‌آوری‌شده");
    expect(formatRetailFulfillmentStatus("FULFILLED")).toBe("تکمیل‌شده");
  });

  test("timeline events use Persian copy with a safe fallback", () => {
    expect(formatOpsEvent("DELIVERY_COMPLETED")).toBe("تحویل ثبت شد");
    expect(formatRetailEvent("ORDER_PARTIAL_ACCEPTANCE_PROPOSED")).toBe("پیشنهاد پذیرش جزئی ثبت شد");
    expect(formatOpsEvent("UNKNOWN_SYSTEM_EVENT")).toBe("رویداد ثبت‌شده");
  });
});

test.describe("Persian packaging and enum fallbacks", () => {
  test("common packaging units are Persian-first and preserve custom Persian names", () => {
    expect(formatPackagingUnit("CARTON")).toBe("کارتن");
    expect(formatPackagingUnit("PACK")).toBe("بسته");
    expect(formatPackagingUnit("KG")).toBe("کیلوگرم");
    expect(formatPackagingUnit("لیتر")).toBe("لیتر");
    expect(formatPackagingUnit("UNLISTED_UNIT")).toBe("واحد دیگر");
    expect(formatPackagingUnit(null)).toBe("واحد نامشخص");
  });

  test("unknown internal status enums do not leak raw identifiers", () => {
    expect(formatOpsStatus("UNKNOWN_INTERNAL_STATUS")).toBe("وضعیت نامشخص");
    expect(formatRetailStatus("UNKNOWN_INTERNAL_STATUS")).toBe("وضعیت نامشخص");
  });

  test("freshness values use stable Persian labels", () => {
    expect(formatFreshnessStatus("FRESH")).toBe("تازه");
    expect(formatFreshnessStatus("STALE")).toBe("نیازمند بررسی");
    expect(formatFreshnessStatus("EXPIRED")).toBe("منقضی‌شده");
    expect(formatFreshnessStatus(null)).toBe("نامشخص");
  });

  test("vendor product display prefers canonical names and rejects placeholders", () => {
    expect(vendorProductDisplayName("کالای بدون نام", "نام محصول اصلی", "fallback")).toBe("نام محصول اصلی");
    expect(vendorProductDisplayName("unknown product", "  ", null)).toBeNull();
  });
});
