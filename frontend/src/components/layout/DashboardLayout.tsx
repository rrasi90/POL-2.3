"use client";

import { useEffect, useState, type ReactNode } from "react";
import { useRequireAuth } from "@/lib/hooks/useAuth";
import { useDirection } from "@/lib/hooks/useDirection";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import { useUIStore } from "@/store";

const SIDEBAR_WIDTH = 256;
const SIDEBAR_COLLAPSED_WIDTH = 64;

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useRequireAuth();
  const dir = useDirection();
  const sidebarCollapsed = useUIStore((s) => s.sidebarCollapsed);
  const toggleSidebar = useUIStore((s) => s.toggleSidebar);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted || !isAuthenticated) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    );
  }

  const sidebarWidth = sidebarCollapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH;
  const isRtl = dir === "rtl";

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div
        className="flex flex-1 flex-col overflow-hidden transition-[margin] duration-200"
        style={{
          marginLeft: isRtl ? 0 : sidebarWidth,
          marginRight: isRtl ? sidebarWidth : 0,
        }}
      >
        <TopBar onToggleSidebar={toggleSidebar} />
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
}
