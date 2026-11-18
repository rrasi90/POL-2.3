import { useEffect, useState } from "react";
import { AccessibilityInfo } from "react-native";

// Shared singleton so every mounted primitive observes one native subscription
// instead of attaching its own listener per instance.
let currentValue = false;
let started = false;
let changeVersion = 0;
const listeners = new Set<(value: boolean) => void>();

function publish(value: boolean): void {
  currentValue = value;
  for (const listener of listeners) listener(value);
}

function start(): void {
  if (started) return;
  started = true;

  // The initial native query is asynchronous. Ignore its result if a newer
  // reduceMotionChanged event arrived while the query was in flight.
  const queryVersion = changeVersion;
  AccessibilityInfo.isReduceMotionEnabled()
    .then((value) => {
      if (queryVersion === changeVersion) publish(value === true);
    })
    .catch(() => {
      if (queryVersion === changeVersion) publish(false);
    });

  AccessibilityInfo.addEventListener("reduceMotionChanged", (value) => {
    changeVersion += 1;
    publish(value === true);
  });
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
