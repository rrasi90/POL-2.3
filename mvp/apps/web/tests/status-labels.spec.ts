import { expect, test } from "@playwright/test";
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
