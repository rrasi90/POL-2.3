import { useEffect, useState } from "react";
import { AccessibilityInfo } from "react-native";

// Shared singleton so every mounted primitive observes one native subscription
// instead of attaching its own listener per instance.
let currentValue = false;
let started = false;
const listeners = new Set<(value: boolean) => void>();

function publish(value: boolean): void {
  currentValue = value;
  for (const listener of listeners) listener(value);
}

function start(): void {
  if (started) return;
  started = true;
  AccessibilityInfo.isReduceMotionEnabled()
    .then((value) => publish(value === true))
    .catch(() => publish(false));
  AccessibilityInfo.addEventListener("reduceMotionChanged", publish);
}

export function useReducedMotion(): boolean {
  const [reduced, setReduced] = useState(currentValue);
  useEffect(() => {
    start();
    listeners.add(setReduced);
    setReduced(currentValue);
    return () => {
      listeners.delete(setReduced);
    };
  }, []);
  return reduced;
}
