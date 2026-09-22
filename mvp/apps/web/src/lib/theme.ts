"use client";

import { useCallback, useEffect, useState } from "react";

export type ThemeMode = "light" | "night";

function read(): ThemeMode {
  if (typeof window === "undefined") return "light";
  const t = window.localStorage.getItem("pol.theme");
  return t === "night" ? "night" : "light";
}

export function useTheme() {
  const [theme, setTheme] = useState<ThemeMode>("light");

  useEffect(() => {
    setTheme(read());
  }, []);

  const toggle = useCallback(() => {
    setTheme((prev) => {
      const next: ThemeMode = prev === "light" ? "night" : "light";
      window.localStorage.setItem("pol.theme", next);
      document.documentElement.dataset.theme = next;
      document.documentElement.style.colorScheme = next;
      return next;
    });
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.colorScheme = theme;
  }, [theme]);

  return { theme, toggle };
}
