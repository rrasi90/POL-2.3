"use client";

import { forwardRef, type InputHTMLAttributes } from "react";

export interface SearchFieldProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, "type"> {
  label?: string;
  onClear?: () => void;
}

/** Search entry — web: type + focus; clear affordance; RTL-first layout. */
export const SearchField = forwardRef<HTMLInputElement, SearchFieldProps>(
  function SearchField(
    { label = "جستجو", onClear, className = "", value, ...rest },
    ref,
  ) {
    const hasValue = typeof value === "string" ? value.length > 0 : Boolean(value);

    return (
      <div className={["relative w-full", className].join(" ")}>
        <label htmlFor={rest.id ?? "pol-search"} className="sr-only">
          {label}
        </label>
        <span
          aria-hidden="true"
          className="absolute inset-y-0 start-3 flex items-center pointer-events-none text-[var(--pol-light-text-muted)] text-[14px]"
        >
          🔍
        </span>
        <input
          ref={ref}
          id={rest.id ?? "pol-search"}
          type="search"
          value={value}
          placeholder={rest.placeholder ?? "جستجو در کاتالوگ یا کد کالا…"}
          className={[
            "h-10 w-full rounded-[8px] border border-[var(--pol-light-border-strong)]",
            "bg-[var(--pol-light-surface-default)] ps-9 pe-8 text-[14px]",
            "text-[var(--pol-light-text-primary)] placeholder:text-[var(--pol-light-text-muted)]",
            "shadow-2xs transition-all duration-[160ms]",
            "focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)] focus:border-transparent",
          ].join(" ")}
          {...rest}
        />
        {hasValue && onClear ? (
          <button
            type="button"
            onClick={onClear}
            className="absolute inset-y-0 end-2.5 flex items-center text-[var(--pol-light-text-muted)] hover:text-[var(--pol-light-text-primary)]"
            aria-label="پاک کردن جستجو"
          >
            ✕
          </button>
        ) : null}
      </div>
    );
  },
);
