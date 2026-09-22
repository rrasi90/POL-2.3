import type { ReactNode } from "react";

export type StatusTone = "success" | "warning" | "danger" | "info" | "neutral";

const toneCls: Record<StatusTone, string> = {
  success:
    "bg-[var(--pol-light-surface-subtle)] text-[var(--pol-light-semantic-success)] border-[var(--pol-light-semantic-success)]/30",
  warning:
    "bg-[var(--pol-light-surface-subtle)] text-[var(--pol-light-semantic-warning)] border-[var(--pol-light-semantic-warning)]/30",
  danger:
    "bg-[var(--pol-light-surface-subtle)] text-[var(--pol-light-semantic-danger)] border-[var(--pol-light-semantic-danger)]/30",
  info:
    "bg-[var(--pol-light-surface-subtle)] text-[var(--pol-light-semantic-info)] border-[var(--pol-light-semantic-info)]/30",
  neutral:
    "bg-[var(--pol-light-surface-subtle)] text-[var(--pol-light-text-secondary)] border-[var(--pol-light-border-subtle)]",
};

export interface StatusChipProps {
  tone?: StatusTone;
  children: ReactNode;
  /** Optional machine state for aria-label */
  title?: string;
}

/** Pill status — radius.pill only for chips (doc 56). */
export function StatusChip({ tone = "neutral", children, title }: StatusChipProps) {
  return (
    <span
      title={title}
      className={[
        "inline-flex items-center rounded-full border px-2 py-0.5",
        "text-[11px] leading-[16px] font-medium",
        toneCls[tone],
      ].join(" ")}
    >
      {children}
    </span>
  );
}
