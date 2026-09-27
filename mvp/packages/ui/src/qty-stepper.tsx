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
      "flex h-10 w-10 items-center justify-center rounded-[8px] border border-[var(--pol-light-border-strong)] bg-[var(--pol-light-surface-default)] text-[16px] font-bold text-[var(--pol-light-text-primary)] shadow-2xs transition-all duration-[160ms] cursor-pointer hover:bg-[var(--pol-light-surface-subtle)] active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--pol-light-focus-ring)] disabled:opacity-40 disabled:cursor-not-allowed disabled:active:scale-100 select-none";

    return (
      <div
        ref={ref}
        role="group"
        aria-label={label}
        className={["inline-flex items-center gap-1.5", className].join(" ")}
      >
        <button
          type="button"
          className={btn}
          disabled={disabled || value <= min}
          aria-label="کاهش تعداد"
          onClick={() => onChange(dec)}
          {...btnRest}
        >
          −
        </button>
        <span
          className="min-w-10 text-center text-[15px] font-semibold tabular-nums text-[var(--pol-light-text-primary)] select-none"
          aria-live="polite"
        >
          {value.toLocaleString("fa-IR")}
        </span>
        <button
          type="button"
          className={btn}
          disabled={disabled || (max !== undefined && value >= max)}
          aria-label="افزایش تعداد"
          onClick={() => onChange(inc)}
        >
          +
        </button>
      </div>
    );
  },
);
