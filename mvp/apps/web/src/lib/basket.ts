"use client";

import { create } from "zustand";

export interface BasketLine {
  product_id: string;
  name: string;
  master_sku?: string | null;
  unit?: string | null;
  quantity: number;
  pack_quantity: number;
}

const LS = "pol.basket" as const;

interface Persisted {
  lines: BasketLine[];
  serverBasketId: string | null;
}

interface BasketState extends Persisted {
  addLine: (line: BasketLine) => void;
  setQuantity: (productId: string, quantity: number) => void;
  removeLine: (productId: string) => void;
  clear: () => void;
  setServerBasket: (id: string | null) => void;
}

function loadInitial(): Persisted {
  if (typeof window === "undefined") return { lines: [], serverBasketId: null };
  try {
    const raw = window.localStorage.getItem(LS);
    if (!raw) return { lines: [], serverBasketId: null };
    const p = JSON.parse(raw) as Partial<Persisted>;
    return {
      lines: Array.isArray(p.lines) ? p.lines : [],
      serverBasketId: typeof p.serverBasketId === "string" ? p.serverBasketId : null,
    };
  } catch {
    return { lines: [], serverBasketId: null };
  }
}

function persist(state: Persisted) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(LS, JSON.stringify(state));
}

/** Client-side basket (G-012): presentation cache only — no business rules. */
export const useBasketStore = create<BasketState>((set, get) => ({
  ...loadInitial(),
  addLine: (line) => {
    const lines = [...get().lines];
    const idx = lines.findIndex((l) => l.product_id === line.product_id);
    if (idx >= 0) {
      lines[idx] = {
        ...lines[idx],
        quantity: lines[idx].quantity + line.quantity,
        name: line.name || lines[idx].name,
        pack_quantity: line.pack_quantity || lines[idx].pack_quantity,
        unit: line.unit ?? lines[idx].unit,
        master_sku: line.master_sku ?? lines[idx].master_sku,
      };
    } else {
      lines.push(line);
    }
    const next = { lines, serverBasketId: null };
    persist(next);
    set(next);
  },
  setQuantity: (productId, quantity) => {
    if (quantity < 1) return;
    const lines = get().lines.map((l) =>
      l.product_id === productId ? { ...l, quantity } : l,
    );
    const next = { lines, serverBasketId: null };
    persist(next);
    set(next);
  },
  removeLine: (productId) => {
    const lines = get().lines.filter((l) => l.product_id !== productId);
    const next = { lines, serverBasketId: null };
    persist(next);
    set(next);
  },
  clear: () => {
    const next = { lines: [], serverBasketId: null };
    persist(next);
    set(next);
  },
  setServerBasket: (id) => {
    const next = { lines: get().lines, serverBasketId: id };
    persist(next);
    set(next);
  },
}));
