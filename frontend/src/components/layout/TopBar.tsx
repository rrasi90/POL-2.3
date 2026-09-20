"use client";

import { useState, useRef, useEffect } from "react";
import { useAuthStore, useUIStore } from "@/store";
import NavIcon from "@/components/ui/NavIcon";
import type { UserRole } from "@/lib/types";

interface TopBarProps {
  onToggleSidebar: () => void;
}

const roleLabels: Record<UserRole, string> = {
  ADMIN_SUPER: "مدیر ارشد",
  OPS_AGENT: "کارشناس عملیات",
  FIELD_ACTIVATOR: "فعال‌ساز میدانی",
  VENDOR_OWNER: "مالک فروشنده",
  VENDOR_STAFF: "کارمند فروشنده",
  RETAILER_OWNER: "مالک خرده‌فروش",
  RETAILER_STAFF: "کارمند خرده‌فروش",
};

export function TopBar({ onToggleSidebar }: TopBarProps) {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const notifications = useUIStore((s) => s.notifications);
  const unreadCount = notifications.filter((n) => !n.read).length;

  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center px-4 gap-4">
      {/* Right side (RTL): hamburger menu */}
      <button
        onClick={onToggleSidebar}
        className="p-2 rounded-md text-gray-500 hover:bg-gray-100 transition-colors"
        aria-label="Toggle sidebar"
      >
        <NavIcon name="menu" className="h-5 w-5" />
      </button>

      {/* Center: search */}
      <div className="flex-1 max-w-md mx-auto">
        <div className="relative">
          <input
            type="text"
            placeholder="جستجو..."
            className="w-full h-9 px-4 pr-9 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <NavIcon
            name="search"
            className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 pointer-events-none"
          />
        </div>
      </div>

      {/* Left side (RTL): notifications + user */}
      <div className="flex items-center gap-2">
        {/* Notification bell */}
        <button className="relative p-2 rounded-md text-gray-500 hover:bg-gray-100 transition-colors">
          <NavIcon name="bell" className="h-5 w-5" />
          {unreadCount > 0 && (
            <span className="absolute -top-0.5 -left-0.5 flex items-center justify-center min-w-[18px] h-[18px] px-1 text-[10px] font-bold text-white bg-danger-500 rounded-full">
              {unreadCount > 99 ? "99+" : unreadCount}
            </span>
          )}
        </button>

        {/* User dropdown */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2 p-1.5 rounded-md hover:bg-gray-100 transition-colors"
          >
            <div className="h-8 w-8 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-sm font-semibold">
              {user?.full_name?.charAt(0) || "?"}
            </div>
            <div className="hidden sm:flex flex-col items-end leading-tight">
              <span className="text-sm font-medium text-gray-800">
                {user?.full_name || "کاربر"}
              </span>
              <span className="text-[11px] text-gray-500">
                {user?.role ? roleLabels[user.role] : ""}
              </span>
            </div>
            <NavIcon name="chevron-down" className="h-4 w-4 text-gray-400 hidden sm:block" />
          </button>

          {dropdownOpen && (
            <div className="absolute left-0 top-full mt-1 w-56 bg-white border border-gray-200 rounded-lg shadow-lg py-1 z-50">
              <div className="px-4 py-3 border-b border-gray-100">
                <p className="text-sm font-medium text-gray-800">{user?.full_name || "کاربر"}</p>
                <p className="text-xs text-gray-500 mt-0.5">
                  {user?.role ? roleLabels[user.role] : ""}
                </p>
              </div>
              <button
                onClick={logout}
                className="w-full text-right px-4 py-2.5 text-sm text-danger-600 hover:bg-gray-50 transition-colors flex items-center gap-2"
              >
                <NavIcon name="logout" className="h-4 w-4" />
                خروج
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
