import { forwardRef, type HTMLAttributes, type ReactNode } from "react";

export type CardVariant = "default" | "subtle" | "interactive" | "elevated";

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant;
  children: ReactNode;
}

const variantCls: Record<CardVariant, string> = {
  default:
    "bg-[var(--pol-light-surface-default)] border border-[var(--pol-light-border-subtle)] shadow-xs",
  subtle:
    "bg-[var(--pol-light-surface-subtle)] border border-[var(--pol-light-border-subtle)]",
  interactive:
    "bg-[var(--pol-light-surface-default)] border border-[var(--pol-light-border-subtle)] shadow-xs hover:border-[var(--pol-light-border-strong)] hover:shadow-sm active:scale-[0.99] cursor-pointer transition-all duration-[160ms]",
  elevated:
    "bg-[var(--pol-light-surface-elevated)] border border-[var(--pol-light-border-subtle)] shadow-md",
};

export const Card = forwardRef<HTMLDivElement, CardProps>(function Card(
  { variant = "default", className = "", children, ...rest },
  ref,
) {
  return (
    <div
      ref={ref}
      className={[
        "rounded-[12px] p-4 text-[var(--pol-light-text-primary)]",
        variantCls[variant],
        className,
      ].join(" ")}
      {...rest}
    >
      {children}
    </div>
  );
});

export function CardHeader({
  className = "",
  children,
}: {
  className?: string;
  children: ReactNode;
}) {
  return (
    <div className={["flex flex-col gap-1 pb-3", className].join(" ")}>
      {children}
    </div>
  );
}

export function CardTitle({
  className = "",
  children,
}: {
  className?: string;
  children: ReactNode;
}) {
  return (
    <h3
      className={[
        "text-[16px] leading-[24px] font-bold text-[var(--pol-light-text-primary)]",
        className,
      ].join(" ")}
    >
      {children}
    </h3>
  );
}

export function CardDescription({
  className = "",
  children,
}: {
  className?: string;
  children: ReactNode;
}) {
  return (
    <p
      className={[
        "text-[12px] leading-[18px] text-[var(--pol-light-text-secondary)]",
        className,
      ].join(" ")}
    >
      {children}
    </p>
  );
}

export function CardContent({
  className = "",
  children,
}: {
  className?: string;
  children: ReactNode;
}) {
  return <div className={className}>{children}</div>;
}

export function CardFooter({
  className = "",
  children,
}: {
  className?: string;
  children: ReactNode;
}) {
  return (
    <div
      className={[
        "flex items-center justify-between pt-3 border-t border-[var(--pol-light-border-subtle)] mt-3",
        className,
      ].join(" ")}
    >
      {children}
    </div>
  );
}
