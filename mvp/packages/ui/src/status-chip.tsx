import type { ReactNode } from "react";

export type StatusTone = "success" | "warning" | "danger" | "info" | "neutral";

const toneCls: Record<StatusTone, { container: string; dot: string }> = {
  success: {
    container:
      "bg-[var(--pol-light-semantic-success)]/10 text-[var(--pol-light-semantic-success)] border-[var(--pol-light-semantic-success)]/30",
    dot: "bg-[var(--pol-light-semantic-success)]",
  },
  warning: {
    container:
      "bg-[var(--pol-light-semantic-warning)]/10 text-[var(--pol-light-semantic-warning)] border-[var(--pol-light-semantic-warning)]/30",
    dot: "bg-[var(--pol-light-semantic-warning)]",
  },
  danger: {
    container:
      "bg-[var(--pol-light-semantic-danger)]/10 text-[var(--pol-light-semantic-danger)] border-[var(--pol-light-semantic-danger)]/30",
    dot: "bg-[var(--pol-light-semantic-danger)]",
  },
  info: {
    container:
      "bg-[var(--pol-light-semantic-info)]/10 text-[var(--pol-light-semantic-info)] border-[var(--pol-light-semantic-info)]/30",
    dot: "bg-[var(--pol-light-semantic-info)]",
  },
  neutral: {
    container:
      "bg-[var(--pol-light-surface-subtle)] text-[var(--pol-light-text-secondary)] border-[var(--pol-light-border-subtle)]",
    dot: "bg-[var(--pol-light-text-muted)]",
  },
};

export interface StatusChipProps {
  tone?: StatusTone;
  children: ReactNode;
  /** Optional machine state for aria-label */
  title?: string;
  /** Show visual indicator dot */
  dot?: boolean;
  className?: string;
}

/** Pill status — radius.pill only for chips (doc 56). */
export function StatusChip({
  tone = "neutral",
  children,
  title,
  dot = true,
  className = "",
}: StatusChipProps) {
  const currentTone = toneCls[tone] ?? toneCls.neutral;

  return (
    <span
      title={title}
      className={[
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5",
        "text-[11px] leading-[16px] font-semibold tracking-wide select-none shadow-2xs",
        currentTone.container,
        className,
      ].join(" ")}
    >
      {dot ? (
        <span
          aria-hidden="true"
          className={["size-1.5 rounded-full shrink-0", currentTone.dot].join(" ")}
        />
      ) : null}
      <span>{children}</span>
    </span>
  );
}
