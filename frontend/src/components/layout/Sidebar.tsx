"use client";

import { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { useAuthStore, useUIStore } from "@/store";
import { useNavItems } from "@/lib/navigation";
import NavIcon from "@/components/ui/NavIcon";

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();
  const { sidebarCollapsed, toggleSidebar } = useUIStore();
  const navItems = useNavItems();
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  const collapsed = sidebarCollapsed;

  const sidebarWidth = collapsed ? "w-16" : "w-64";

  return (
    <>
      <button
        type="button"
        className="fixed top-4 z-50 rounded-md bg-gray-900 p-2 text-gray-400 hover:text-white lg:hidden"
        style={{ [process.env.NEXT_PUBLIC_DIR === "rtl" ? "right" : "left"]: "1rem" }}
        onClick={() => setMobileOpen((o) => !o)}
        aria-label="Toggle menu"
      >
        <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          {mobileOpen ? (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          ) : (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          )}
        </svg>
      </button>

      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <aside
        className={`fixed top-0 z-40 flex h-screen flex-col bg-gray-900 text-gray-300 transition-all duration-200
          ${sidebarWidth}
          ${mobileOpen ? "translate-x-0" : "max-lg:-translate-x-full"}
          lg:translate-x-0`}
      >
        <div className="flex h-16 items-center gap-3 border-b border-gray-800 px-4">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded bg-primary-800 text-sm font-bold text-white">
            P
          </div>
          {!collapsed && (
            <span className="text-lg font-semibold text-white">POL</span>
          )}
        </div>

        <nav className="flex-1 overflow-y-auto py-3">
          <ul className="space-y-1 px-2">
            {navItems.map((item) => {
              const active = pathname === item.href || pathname.startsWith(item.href + "/");
              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors
                      ${active ? "bg-primary-800 text-white" : "text-gray-400 hover:bg-gray-800 hover:text-white"}
                      ${collapsed ? "justify-center" : ""}`}
                    title={collapsed ? item.label : undefined}
                  >
                    <NavIcon name={item.icon} className="h-5 w-5 shrink-0" />
                    {!collapsed && <span>{item.label}</span>}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        <div className="border-t border-gray-800 p-2">
          {!collapsed && user && (
            <div className="mb-2 truncate px-3 text-xs text-gray-500">
              {user.full_name ?? user.phone_number}
            </div>
          )}

          <button
            type="button"
            onClick={toggleSidebar}
            className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-gray-400 transition-colors hover:bg-gray-800 hover:text-white max-lg:hidden"
            title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            <svg
              className={`h-5 w-5 shrink-0 transition-transform ${collapsed ? "rotate-180" : ""}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
            </svg>
            {!collapsed && <span>Collapse</span>}
          </button>

          <button
            type="button"
            onClick={logout}
            className={`flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-gray-400 transition-colors hover:bg-gray-800 hover:text-white
              ${collapsed ? "justify-center" : ""}`}
            title={collapsed ? "Logout" : undefined}
          >
            <svg className="h-5 w-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
              />
            </svg>
            {!collapsed && <span>Logout</span>}
          </button>
        </div>
      </aside>
    </>
  );
}
