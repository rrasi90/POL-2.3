"use client";

import { useEffect, useState } from "react";

export function useDirection(): "ltr" | "rtl" {
  const [dir, setDir] = useState<"ltr" | "rtl">("rtl");

  useEffect(() => {
    const stored = localStorage.getItem("ui_direction");
    if (stored === "rtl" || stored === "ltr") {
      setDir(stored);
    }
  }, []);

  useEffect(() => {
    document.documentElement.dir = dir;
    document.documentElement.lang = dir === "rtl" ? "fa" : "en";
  }, [dir]);

  return dir;
}
