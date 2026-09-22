import { AppShell, RequireRole } from "@/components/shell/app-shell";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <RequireRole>
      <AppShell>{children}</AppShell>
    </RequireRole>
  );
}
