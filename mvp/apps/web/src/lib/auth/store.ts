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
  user: AuthUser | null;
  role: Role | null;
  setSession: (p: {
    accessToken: string;
    user?: AuthUser | null;
    role?: Role | null;
  }) => void;
  clear: () => void;
}

const LS = "pol.auth.profile" as const;

function loadInitial(): Pick<AuthState, "accessToken" | "user" | "role"> {
  if (typeof window === "undefined") {
    return { accessToken: null, user: null, role: null };
  }
  try {
    const raw = window.localStorage.getItem(LS);
    if (!raw) return { accessToken: null, user: null, role: null };
    const p = JSON.parse(raw) as Pick<AuthState, "user" | "role">;
    return {
      accessToken: null,
      user: p.user ?? null,
      role: p.role ?? null,
    };
  } catch {
    return { accessToken: null, user: null, role: null };
  }
}

function persistProfile(user: AuthUser | null, role: Role | null) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(LS, JSON.stringify({ user, role }));
}

export const useAuthStore = create<AuthState>((set) => ({
  ...loadInitial(),
  setSession: ({ accessToken, user, role }) => {
    persistProfile(user ?? null, role ?? null);
    set({
      accessToken,
      user: user ?? null,
      role: role ?? null,
    });
  },
  clear: () => {
    const next = { accessToken: null, user: null, role: null };
    if (typeof window !== "undefined") {
      window.localStorage.removeItem(LS);
    }
    set(next);
  },
}));
