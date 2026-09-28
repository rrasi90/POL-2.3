"use client";

import {
  forwardRef,
  type ButtonHTMLAttributes,
  type ReactNode,
} from "react";

export type ButtonVariant =
  | "primary"
  | "secondary"
  | "outline"
  | "ghost"
  | "danger"
  | "success";
export type ButtonSize = "sm" | "md" | "lg";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  block?: boolean;
  children: ReactNode;
}

const variantCls: Record<ButtonVariant, string> = {
  primary:
    "bg-[var(--pol-light-brand-primary)] text-white shadow-xs hover:bg-[var(--pol-light-brand-hover)] active:bg-[var(--pol-light-brand-active)] border border-transparent",
  secondary:
    "bg-[var(--pol-light-surface-default)] text-[var(--pol-light-text-primary)] border border-[var(--pol-light-border-strong)] shadow-xs hover:bg-[var(--pol-light-surface-subtle)] hover:border-[var(--pol-light-border-strong)] active:bg-[var(--pol-light-surface-subtle)]",
  outline:
    "bg-transparent text-[var(--pol-light-brand-primary)] border border-[var(--pol-light-brand-primary)] hover:bg-[var(--pol-light-brand-primary)]/10 active:bg-[var(--pol-light-brand-primary)]/20",
  ghost:
    "bg-transparent text-[var(--pol-light-text-secondary)] hover:bg-[var(--pol-light-surface-subtle)] hover:text-[var(--pol-light-text-primary)] border border-transparent",
  danger:
    "bg-[var(--pol-light-semantic-danger)] text-white shadow-xs hover:opacity-90 active:opacity-100 border border-transparent",
  success:
    "bg-[var(--pol-light-semantic-success)] text-white shadow-xs hover:opacity-90 active:opacity-100 border border-transparent",
};

const sizeCls: Record<ButtonSize, string> = {
  sm: "h-8 px-3 text-[12px] leading-[18px]",
  md: "h-10 px-4 text-[14px] leading-[22px]",
  lg: "h-12 px-5 text-[16px] leading-[24px]",
};

/**
 * Golden Button — states: default / hover / active / focus / disabled / loading.
 * Touch target min 40px on md+; sm is desktop-dense (ops) only.
 * Source: doc 39 Button contract; doc 21 §16; doc 56 motion for transitions.
 */
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  {
    variant = "primary",
    size = "md",
    loading = false,
    block = false,
    disabled,
    className = "",
    children,
    type = "button",
    ...rest
  },
  ref,
) {
  const isDisabled = disabled || loading;
  return (
    <button
      ref={ref}
      type={type}
      disabled={isDisabled}
      aria-busy={loading || undefined}
      className={[
        "inline-flex items-center justify-center gap-2 rounded-[8px] font-medium cursor-pointer",
        "transition-all duration-[160ms] ease-out select-none active:scale-[0.98]",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--pol-light-focus-ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--pol-light-surface-default)]",
        "disabled:pointer-events-none disabled:opacity-50 disabled:cursor-not-allowed",
        sizeCls[size],
        variantCls[variant],
        block ? "w-full" : "",
        className,
      ].join(" ")}
      {...rest}
    >
      {loading ? (
        <span
          aria-hidden="true"
          className="size-4 animate-spin rounded-full border-2 border-current border-t-transparent"
        />
      ) : null}
      {children}
    </button>
  );
});
