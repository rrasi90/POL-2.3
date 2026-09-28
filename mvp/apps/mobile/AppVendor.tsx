import { AppShell, type WorkspaceProps } from "./AppShell";
import { VendorMobileScreen } from "./src/screens/VendorMobileScreen";
import type { Role } from "./src/types";

type VendorRole = Extract<Role, "VENDOR_OWNER" | "VENDOR_STAFF">;

export default function VendorApp(): React.ReactNode {
  const workspace = (props: WorkspaceProps<VendorRole>) => (
    <VendorMobileScreen role={props.role} onOpenOrder={props.onOpenOrder} />
  );
  return <AppShell<VendorRole> appName="پل بنکدار" allowedRoles={["VENDOR_OWNER", "VENDOR_STAFF"]} workspace={workspace} orderMode="vendor" />;
}
