// Semantic motion directions — primitives map these to concrete translateX/Y
// (RTL-aware); screens never pass raw pixel offsets.
export type MotionDirection = "forward" | "back" | "up" | "down";