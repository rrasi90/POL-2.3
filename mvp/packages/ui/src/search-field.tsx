"use client";

import { forwardRef, type InputHTMLAttributes } from "react";

export interface SearchFieldProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, "type"> {
  label?: string;
}

/** Search entry — web: type + focus; clear affordance; RTL-first layout. */
export const SearchField = forwardRef<HTMLInputElement, SearchFieldProps>(
  function SearchField({ label = "جستجو", className = "", ...rest }, ref) {
    return (
      <div className={["relative w-full", className].join(" ")}>
        <label htmlFor={rest.id ?? "pol-search"} className="sr-only">
          {label}
        </label>
        <input
          ref={ref}
          id={rest.id ?? "pol-search"}
          type="search"
          placeholder={rest.placeholder ?? "جستجو…"}
          className={[
            "h-10 w-full rounded-[8px] border border-[var(--pol-light-border-strong)]",
            "bg-[var(--pol-light-surface-default)] px-3 text-[14px]",
            "text-[var(--pol-light-text-primary)] placeholder:text-[var(--pol-light-text-muted)]",
            "focus:outline-none focus:ring-2 focus:ring-[var(--pol-light-focus-ring)]",
          ].join(" ")}
          {...rest}
        />
      </div>
    );
  },
);
