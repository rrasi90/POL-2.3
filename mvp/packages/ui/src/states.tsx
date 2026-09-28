import type { ReactNode } from "react";
import { Button } from "./button";

export interface EmptyStateProps {
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: ReactNode;
  className?: string;
}

/** EmptyState — required shared state (doc 22 batch 9 / doc 39). */
export function EmptyState({
  title,
  description,
  actionLabel,
  onAction,
  icon,
  className = "",
}: EmptyStateProps) {
  return (
    <div
      className={[
        "flex flex-col items-center justify-center gap-3 rounded-[12px] border border-dashed border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-subtle)]/60 px-6 py-12 text-center",
        className,
      ].join(" ")}
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-full border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] text-[22px] shadow-xs">
        {icon ?? "📦"}
      </div>
      <div className="space-y-1">
        <h3 className="text-[16px] leading-[24px] font-semibold text-[var(--pol-light-text-primary)]">
          {title}
        </h3>
        {description ? (
          <p className="max-w-md text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)]">
            {description}
          </p>
        ) : null}
      </div>
      {actionLabel && onAction ? (
        <div className="pt-2">
          <Button variant="secondary" size="sm" onClick={onAction}>
            {actionLabel}
          </Button>
        </div>
      ) : null}
    </div>
  );
}

export interface ErrorStateProps {
  title?: string;
  description?: string;
  onRetry?: () => void;
  retryLabel?: string;
  className?: string;
}

/** Error + inline recovery (doc 22 rule 11). */
export function ErrorState({
  title = "خطایی رخ داد",
  description,
  onRetry,
  retryLabel = "تلاش مجدد",
  className = "",
}: ErrorStateProps) {
  return (
    <div
      role="alert"
      className={[
        "flex flex-col items-start gap-2.5 rounded-[12px] border border-[var(--pol-light-semantic-danger)]/30 border-r-4 border-r-[var(--pol-light-semantic-danger)] bg-[var(--pol-light-surface-default)] p-4 shadow-xs",
        className,
      ].join(" ")}
    >
      <div className="flex items-center gap-2">
        <span className="text-[16px]" aria-hidden="true">
          ⚠️
        </span>
        <p className="text-[14px] leading-[22px] font-bold text-[var(--pol-light-semantic-danger)]">
          {title}
        </p>
      </div>
      {description ? (
        <p className="text-[13px] leading-[20px] text-[var(--pol-light-text-secondary)] ps-6">
          {description}
        </p>
      ) : null}
      {onRetry ? (
        <div className="pt-1 ps-6">
          <Button variant="outline" size="sm" onClick={onRetry}>
            {retryLabel}
          </Button>
        </div>
      ) : null}
    </div>
  );
}

export interface SkeletonProps {
  className?: string;
  lines?: number;
  variant?: "text" | "card" | "circle";
}

/** Loading skeleton — reduced-motion respected via CSS animation-play-state if needed. */
export function Skeleton({
  className = "",
  lines = 1,
  variant = "text",
}: SkeletonProps) {
  if (variant === "circle") {
    return (
      <div
        aria-hidden="true"
        className={["animate-pulse rounded-full bg-[var(--pol-light-surface-subtle)]", className].join(" ")}
      />
    );
  }

  if (variant === "card") {
    return (
      <div
        aria-hidden="true"
        className={[
          "animate-pulse rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)]",
          className,
        ].join(" ")}
      />
    );
  }

  if (lines > 1) {
    return (
      <div className="flex flex-col gap-2 w-full" aria-hidden="true">
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className={[
              "h-4 animate-pulse rounded-[4px] bg-[var(--pol-light-surface-subtle)]",
              i === lines - 1 ? "w-3/4" : "w-full",
              className,
            ].join(" ")}
          />
        ))}
      </div>
    );
  }

  return (
    <div
      aria-hidden="true"
      className={["h-4 animate-pulse rounded-[4px] bg-[var(--pol-light-surface-subtle)]", className].join(" ")}
    />
  );
}

export function PermissionDenied({ message = "دسترسی به این بخش برای نقش کاربری شما مجاز نیست" }: { message?: string }) {
  return (
    <div
      role="status"
      className="flex flex-col items-center justify-center gap-2 rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] p-8 text-center shadow-xs"
    >
      <span className="text-[24px]" aria-hidden="true">
        🔒
      </span>
      <p className="text-[14px] font-semibold text-[var(--pol-light-text-primary)]">
        محدودیت دسترسی
      </p>
      <p className="text-[13px] text-[var(--pol-light-text-secondary)]">
        {message}
      </p>
    </div>
  );
}
