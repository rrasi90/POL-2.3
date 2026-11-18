import { expect, test } from "@playwright/test";
import { postLoginDestination } from "../src/lib/auth/routes";
import type { Role } from "@pol/types";

test.describe("post-login destination validation", () => {
  test("allows an authorized same-origin deep link", () => {
    expect(postLoginDestination("RETAILER_OWNER", "/retailer/orders")).toBe("/retailer/orders");
    expect(postLoginDestination("VENDOR_STAFF", "/vendor/inventory")).toBe("/vendor/inventory");
  });

  test("falls back when the role cannot access the requested route", () => {
    expect(postLoginDestination("RETAILER_OWNER", "/admin/users")).toBe("/retailer");
    expect(postLoginDestination("VENDOR_OWNER", "/ops/analytics")).toBe("/vendor");
  });

  test("rejects normalized path traversal into another role's route", () => {
    expect(postLoginDestination("RETAILER_OWNER", "/retailer/../admin/users")).toBe("/retailer");
    expect(postLoginDestination("VENDOR_OWNER", "/vendor/../../ops")).toBe("/vendor");
  });

  test("preserves safe query and fragment components", () => {
    expect(postLoginDestination("RETAILER_OWNER", "/retailer/orders?tab=open#latest")).toBe(
      "/retailer/orders?tab=open#latest",
    );
  });

  test("rejects protocol-relative and external destinations", () => {
    expect(postLoginDestination("RETAILER_OWNER", "//evil.example")).toBe("/retailer");
    expect(postLoginDestination("RETAILER_OWNER", "https://evil.example")).toBe("/retailer");
  });

  test("rejects backslash-based and malformed destinations", () => {
    expect(postLoginDestination("RETAILER_OWNER", "/\\\\evil.example")).toBe("/retailer");
    expect(postLoginDestination("RETAILER_OWNER", "\\evil.example")).toBe("/retailer");
  });

  test("uses the role home when no destination is supplied", () => {
    const roles: Array<[Role, string]> = [
      ["ADMIN_SUPER", "/admin"],
      ["OPS_AGENT", "/ops"],
      ["FIELD_ACTIVATOR", "/field"],
      ["VENDOR_OWNER", "/vendor"],
      ["VENDOR_STAFF", "/vendor"],
      ["RETAILER_OWNER", "/retailer"],
      ["RETAILER_STAFF", "/retailer"],
    ];
    for (const [role, home] of roles) {
      expect(postLoginDestination(role, null)).toBe(home);
    }
  });
});
