"use client";

import { useAuthStore } from "@/store";
import type { UserRole } from "@/lib/types";

interface NavItem {
  href: string;
  label: string;
  icon: string;
  roles: UserRole[];
}

export const navItems: NavItem[] = [
  { href: "/admin", label: "داشبورد", icon: "grid", roles: ["ADMIN_SUPER"] },
  { href: "/admin/users", label: "کاربران", icon: "users", roles: ["ADMIN_SUPER"] },
  { href: "/admin/orgs", label: "سازمان‌ها", icon: "building", roles: ["ADMIN_SUPER"] },
  { href: "/ops", label: "داشبورد", icon: "grid", roles: ["OPS_AGENT"] },
  { href: "/ops/support", label: "پشتیبانی", icon: "headset", roles: ["OPS_AGENT", "ADMIN_SUPER"] },
  { href: "/ops/finance", label: "مالی", icon: "wallet", roles: ["OPS_AGENT", "VENDOR_OWNER", "ADMIN_SUPER"] },
  { href: "/ops/reconciliation", label: "تطبیق", icon: "check-circle", roles: ["OPS_AGENT"] },
  { href: "/field", label: "تسک‌ها", icon: "clipboard", roles: ["FIELD_ACTIVATOR", "OPS_AGENT"] },
  { href: "/vendor", label: "داشبورد", icon: "grid", roles: ["VENDOR_OWNER"] },
  { href: "/vendor/catalog", label: "کاتالوگ", icon: "package", roles: ["VENDOR_OWNER", "VENDOR_STAFF"] },
  { href: "/vendor/orders", label: "سفارشات", icon: "cart", roles: ["VENDOR_OWNER", "VENDOR_STAFF"] },
  { href: "/vendor/inventory", label: "انبار", icon: "box", roles: ["VENDOR_OWNER", "VENDOR_STAFF"] },
  { href: "/vendor/settlements", label: "تسویه", icon: "banknotes", roles: ["VENDOR_OWNER"] },
  { href: "/retailer", label: "کاتالوگ", icon: "search", roles: ["RETAILER_OWNER", "RETAILER_STAFF"] },
  { href: "/retailer/basket", label: "سبد خرید", icon: "bag", roles: ["RETAILER_OWNER", "RETAILER_STAFF"] },
  { href: "/retailer/orders", label: "سفارشات", icon: "list", roles: ["RETAILER_OWNER", "RETAILER_STAFF"] },
  { href: "/retailer/returns", label: "برگشت", icon: "return", roles: ["RETAILER_OWNER"] },
];

export function useNavItems() {
  const user = useAuthStore((s) => s.user);
  if (!user) return [];
  return navItems.filter((item) => item.roles.includes(user.role as UserRole));
}
