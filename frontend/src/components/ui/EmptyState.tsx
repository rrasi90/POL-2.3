import type { ReactNode } from "react";

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: ReactNode;
  action?: ReactNode;
}

export function EmptyState({ title, description, icon, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      {icon && <div className="mb-4 text-gray-300">{icon}</div>}
      <h3 className="text-lg font-semibold text-gray-800 mb-1">{title}</h3>
      {description && <p className="text-sm text-gray-500 max-w-sm mb-4">{description}</p>}
      {action}
    </div>
  );
}

export function EmptyBoxIcon({ className = "w-16 h-16" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="20" y="35" width="80" height="60" rx="8" stroke="#D1D5DB" strokeWidth="2" fill="#F9FAFB" />
      <path d="M20 50 L60 30 L100 50" stroke="#D1D5DB" strokeWidth="2" fill="none" />
      <line x1="60" y1="50" x2="60" y2="80" stroke="#E5E7EB" strokeWidth="1.5" strokeDasharray="4 4" />
      <circle cx="60" cy="65" r="8" stroke="#D1D5DB" strokeWidth="1.5" fill="none" />
      <line x1="56" y1="65" x2="64" y2="65" stroke="#D1D5DB" strokeWidth="1.5" />
    </svg>
  );
}

export function EmptyOrderIcon() {
  return <EmptyBoxIcon />;
}

export function EmptyProductIcon() {
  return (
    <svg className="w-16 h-16" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="25" y="25" width="70" height="70" rx="12" stroke="#D1D5DB" strokeWidth="2" fill="#F9FAFB" />
      <rect x="35" y="35" width="20" height="20" rx="4" stroke="#E5E7EB" strokeWidth="1.5" fill="white" />
      <rect x="65" y="35" width="20" height="8" rx="2" fill="#E5E7EB" />
      <rect x="65" y="50" width="14" height="5" rx="2" fill="#E5E7EB" />
      <rect x="35" y="65" width="50" height="5" rx="2" fill="#E5E7EB" />
      <rect x="35" y="77" width="30" height="5" rx="2" fill="#E5E7EB" />
    </svg>
  );
}
