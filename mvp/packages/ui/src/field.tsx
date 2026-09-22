"use client";

import { forwardRef, useId, type InputHTMLAttributes, type ReactNode } from "react";

export interface FieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string | null;
  hint?: string;
  required?: boolean;
  trailing?: ReactNode;
}

/**
 * TextField — default / focus / error / disabled / RTL.
 * Constraints shown before failure where known (doc 22 rule 7).
 * Source: doc 39 TextField; GOV.UK error pattern (specific message, keep values).
 */
export const Field = forwardRef<HTMLInputElement, FieldProps>(function Field(
  { label, error, hint, required, trailing, id, className = "", ...rest },
  ref,
) {
  const auto = useId();
  const fieldId = id ?? auto;
  const errId = `${fieldId}-err`;
  const hintId = `${fieldId}-hint`;

  return (
    <div className={["flex flex-col gap-1.5", className].join(" ")}>
      <label
        htmlFor={fieldId}
        className="text-[12px] leading-[18px] font-medium text-[var(--pol-light-text-secondary)]"
      >
        {label}
        {required ? (
          <span className="text-[var(--pol-light-semantic-danger)]" aria-hidden>
            *
          </span>
        ) : null}
      </label>
      <div className="relative">
        <input
          ref={ref}
          id={fieldId}
          required={required}
          aria-invalid={error ? true : undefined}
          aria-describedby={[error ? errId : null, hint ? hintId : null]
            .filter(Boolean)
            .join(" ") || undefined}
          className={[
            "h-10 w-full rounded-[8px] border bg-[var(--pol-light-surface-default)] px-3",
            "text-[14px] leading-[22px] text-[var(--pol-light-text-primary)]",
            "placeholder:text-[var(--pol-light-text-muted)]",
            "transition-[border-color,box-shadow] duration-[160ms]",
            "focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)] focus:border-transparent",
            "disabled:opacity-50 disabled:bg-[var(--pol-light-surface-subtle)]",
            error
              ? "border-[var(--pol-light-semantic-danger)]"
              : "border-[var(--pol-light-border-strong)]",
          ].join(" ")}
          {...rest}
        />
        {trailing ? (
          <span className="absolute inset-y-0 end-3 flex items-center text-[var(--pol-light-text-muted)]">
            {trailing}
          </span>
        ) : null}
      </div>
      {hint && !error ? (
        <p id={hintId} className="text-[11px] leading-[16px] text-[var(--pol-light-text-muted)]">
          {hint}
        </p>
      ) : null}
      {error ? (
        <p
          id={errId}
          role="alert"
          className="text-[12px] leading-[18px] text-[var(--pol-light-semantic-danger)]"
        >
          {error}
        </p>
      ) : null}
    </div>
  );
});
