import type { HTMLAttributes, TdHTMLAttributes, ThHTMLAttributes } from "react";

export function Table({
  className = "",
  children,
  ...rest
}: HTMLAttributes<HTMLTableElement>) {
  return (
    <div className="w-full overflow-x-auto rounded-[12px] border border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-default)] shadow-xs">
      <table className={["w-full border-collapse text-start text-[13px]", className].join(" ")} {...rest}>
        {children}
      </table>
    </div>
  );
}

export function TableHeader({
  className = "",
  children,
  ...rest
}: HTMLAttributes<HTMLTableSectionElement>) {
  return (
    <thead
      className={["border-b border-[var(--pol-light-border-subtle)] bg-[var(--pol-light-surface-subtle)] text-[12px] font-semibold text-[var(--pol-light-text-secondary)]", className].join(" ")}
      {...rest}
    >
      {children}
    </thead>
  );
}

export function TableBody({
  className = "",
  children,
  ...rest
}: HTMLAttributes<HTMLTableSectionElement>) {
  return (
    <tbody
      className={["divide-y divide-[var(--pol-light-border-subtle)] text-[var(--pol-light-text-primary)]", className].join(" ")}
      {...rest}
    >
      {children}
    </tbody>
  );
}

export function TableRow({
  className = "",
  children,
  ...rest
}: HTMLAttributes<HTMLTableRowElement>) {
  return (
    <tr
      className={["transition-colors duration-[160ms] hover:bg-[var(--pol-light-surface-subtle)]/70", className].join(" ")}
      {...rest}
    >
      {children}
    </tr>
  );
}

export function TableHead({
  className = "",
  children,
  ...rest
}: ThHTMLAttributes<HTMLTableCellElement>) {
  return (
    <th
      className={["px-3.5 py-3 text-start font-semibold text-[var(--pol-light-text-secondary)] select-none", className].join(" ")}
      {...rest}
    >
      {children}
    </th>
  );
}

export function TableCell({
  className = "",
  children,
  ...rest
}: TdHTMLAttributes<HTMLTableCellElement>) {
  return (
    <td
      className={["px-3.5 py-3 align-middle text-[var(--pol-light-text-primary)]", className].join(" ")}
      {...rest}
    >
      {children}
    </td>
  );
}
