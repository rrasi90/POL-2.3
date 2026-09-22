"use client";

import { create } from "zustand";
import type { Role } from "@pol/types";

export interface AuthUser {
  user_id: string;
  mobile_number?: string;
  organization_id?: string | null;
  role?: Role | null;
}

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: AuthUser | null;
  role: Role | null;
  setSession: (p: {
    accessToken: string;
    refreshToken?: string | null;
    user?: AuthUser | null;
    role?: Role | null;
  }) => void;
  clear: () => void;
}

const LS = "pol.auth" as const;

function loadInitial(): Pick<AuthState, "accessToken" | "refreshToken" | "user" | "role"> {
  if (typeof window === "undefined") {
    return { accessToken: null, refreshToken: null, user: null, role: null };
  }
  try {
    const raw = window.localStorage.getItem(LS);
    if (!raw) return { accessToken: null, refreshToken: null, user: null, role: null };
    const p = JSON.parse(raw) as Pick<AuthState, "accessToken" | "refreshToken" | "user" | "role">;
    return {
      accessToken: p.accessToken ?? null,
      refreshToken: p.refreshToken ?? null,
      user: p.user ?? null,
      role: p.role ?? null,
    };
  } catch {
    return { accessToken: null, refreshToken: null, user: null, role: null };
  }
}

function persist(s: Pick<AuthState, "accessToken" | "refreshToken" | "user" | "role">) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(LS, JSON.stringify(s));
}

export const useAuthStore = create<AuthState>((set, get) => ({
  ...loadInitial(),
  setSession: ({ accessToken, refreshToken, user, role }) => {
    const next = {
      accessToken,
      refreshToken: refreshToken ?? get().refreshToken,
      user: user ?? get().user,
      role: role ?? get().role,
    };
    persist(next);
    set(next);
  },
  clear: () => {
    const next = { accessToken: null, refreshToken: null, user: null, role: null };
    persist(next);
    set(next);
  },
}));
