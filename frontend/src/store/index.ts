import { create } from "zustand";
import type { User, UserRole } from "@/lib/types";

interface AuthStore {
  user: User | null;
  access_token: string | null;
  refresh_token: string | null;
  organization_id: string | null;
  isAuthenticated: boolean;
  setAuth: (user: User, access_token: string, refresh_token?: string) => void;
  setOrganization: (org_id: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  access_token: typeof window !== "undefined" ? localStorage.getItem("access_token") : null,
  refresh_token: typeof window !== "undefined" ? localStorage.getItem("refresh_token") : null,
  organization_id: typeof window !== "undefined" ? localStorage.getItem("organization_id") : null,
  isAuthenticated: typeof window !== "undefined" ? !!localStorage.getItem("access_token") : false,

  setAuth: (user, access_token, refresh_token) => {
    localStorage.setItem("access_token", access_token);
    if (refresh_token) localStorage.setItem("refresh_token", refresh_token);
    localStorage.setItem("user", JSON.stringify(user));
    set({ user, access_token, refresh_token, isAuthenticated: true });
  },

  setOrganization: (org_id) => {
    localStorage.setItem("organization_id", org_id);
    set({ organization_id: org_id });
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("organization_id");
    localStorage.removeItem("user");
    set({ user: null, access_token: null, refresh_token: null, organization_id: null, isAuthenticated: false });
    window.location.href = "/auth";
  },
}));

interface UIStore {
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
  notifications: Notification[];
  addNotification: (n: Notification) => void;
  markRead: (id: string) => void;
  toasts: Toast[];
  addToast: (toast: Omit<Toast, "id">) => void;
  removeToast: (id: string) => void;
}

interface Notification {
  id: string;
  title: string;
  body: string;
  priority: string;
  read: boolean;
  created_at: string;
}

interface Toast {
  id: string;
  type: "success" | "error" | "warning" | "info";
  message: string;
}

let toastId = 0;

export const useUIStore = create<UIStore>((set) => ({
  sidebarCollapsed: false,
  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  notifications: [],
  addNotification: (n) => set((s) => ({ notifications: [n, ...s.notifications] })),
  markRead: (id) =>
    set((s) => ({
      notifications: s.notifications.map((n) => (n.id === id ? { ...n, read: true } : n)),
    })),
  toasts: [],
  addToast: (toast) => {
    const id = String(++toastId);
    set((s) => ({ toasts: [...s.toasts, { ...toast, id }] }));
    setTimeout(() => {
      set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }));
    }, 5000);
  },
  removeToast: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}));
