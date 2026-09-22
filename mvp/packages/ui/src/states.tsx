import type { ReactNode } from "react";
import { Button } from "./button";

export interface EmptyStateProps {
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: ReactNode;
}

/** EmptyState — required shared state (doc 22 batch 9 / doc 39). */
export function EmptyState({
  title,
  description,
  actionLabel,
  onAction,
  icon,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-[12px] border border-dashed border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] px-6 py-10 text-center">
      {icon ? <div className="text-[var(--pol-light-text-muted)]">{icon}</div> : null}
      <h3 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
        {title}
      </h3>
      {description ? (
        <p className="max-w-md text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
          {description}
        </p>
      ) : null}
      {actionLabel && onAction ? (
        <Button variant="secondary" size="sm" onClick={onAction}>
          {actionLabel}
        </Button>
      ) : null}
    </div>
  );
}

export interface ErrorStateProps {
  title?: string;
  description?: string;
  onRetry?: () => void;
  retryLabel?: string;
}

/** Error + inline recovery (doc 22 rule 11). */
export function ErrorState({
  title = "خطایی رخ داد",
  description,
  onRetry,
  retryLabel = "تلاش مجدد",
}: ErrorStateProps) {
  return (
    <div
      role="alert"
      className="flex flex-col items-start gap-2 rounded-[12px] border border-[var(--pol-light-semantic-danger)]/40 bg-[var(--pol-light-surface-default)] p-4"
    >
      <p className="text-[14px] leading-[22px] font-semibold text-[var(--pol-light-semantic-danger)]">
        {title}
      </p>
      {description ? (
        <p className="text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
          {description}
        </p>
      ) : null}
      {onRetry ? (
        <Button variant="secondary" size="sm" onClick={onRetry}>
          {retryLabel}
        </Button>
      ) : null}
    </div>
  );
}

export interface SkeletonProps {
  className?: string;
  lines?: number;
}

/** Loading skeleton — reduced-motion respected via CSS animation-play-state if needed. */
export function Skeleton({ className = "", lines = 1 }: SkeletonProps) {
  if (lines > 1) {
    return (
      <div className="flex flex-col gap-2" aria-hidden>
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className={["h-4 animate-pulse rounded bg-[var(--pol-light-surface-subtle)]", className].join(" ")}
          />
        ))}
      </div>
    );
  }
  return (
    <div
      aria-hidden
      className={["h-4 animate-pulse rounded bg-[var(--pol-light-surface-subtle)]", className].join(" ")}
    />
  );
}

export function PermissionDenied({ message = "دسترسی مجاز نیست" }: { message?: string }) {
  return (
    <div
      role="status"
      className="rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] p-6 text-center text-[14px] text-[var(--pol-light-text-secondary)]"
    >
      {message}
    </div>
  );
}
