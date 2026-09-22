import { forwardRef, type ButtonHTMLAttributes } from "react";

export interface QtyStepperProps
  extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, "onChange" | "value"> {
  value: number;
  min?: number;
  max?: number;
  onChange: (next: number) => void;
  label?: string;
  disabled?: boolean;
}

/**
 * Quantity stepper — min/max = MOQ/MOV display only; real enforcement is server-side.
 * Mobile: large hit targets (≥40px). Web: keyboard ± via buttons.
 */
export const QtyStepper = forwardRef<HTMLDivElement, QtyStepperProps>(
  function QtyStepper(
    { value, min = 0, max, onChange, label = "تعداد", disabled, className = "", ...btnRest },
    ref,
  ) {
    const dec = Math.max(min, value - 1);
    const inc = max === undefined ? value + 1 : Math.min(max, value + 1);
    const btn =
      "flex h-10 w-10 items-center justify-center rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] text-[16px] text-[var(--pol-light-text-primary)] transition-colors duration-[160ms] hover:bg-[var(--pol-light-surface-subtle)] focus-visible:outline-2 focus-visible:outline-[var(--pol-light-focus-ring)] disabled:opacity-40";

    return (
      <div
        ref={ref}
        role="group"
        aria-label={label}
        className={["inline-flex items-center gap-1", className].join(" ")}
      >
        <button
          type="button"
          className={btn}
          disabled={disabled || value <= min}
          aria-label="کاهش"
          onClick={() => onChange(dec)}
          {...btnRest}
        >
          −
        </button>
        <span
          className="min-w-10 text-center text-[14px] tabular-nums text-[var(--pol-light-text-primary)]"
          aria-live="polite"
        >
          {value}
        </span>
        <button
          type="button"
          className={btn}
          disabled={disabled || (max !== undefined && value >= max)}
          aria-label="افزایش"
          onClick={() => onChange(inc)}
        >
          +
        </button>
      </div>
    );
  },
);
