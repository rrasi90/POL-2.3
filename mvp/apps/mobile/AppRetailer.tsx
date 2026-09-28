import { AppShell, type WorkspaceProps } from "./AppShell";
import { RetailerMobileScreen } from "./src/screens/RetailerMobileScreen";
import type { Role } from "./src/types";

type RetailerRole = Extract<Role, "RETAILER_OWNER" | "RETAILER_STAFF">;

export default function RetailerApp(): React.ReactNode {
  const workspace = (props: WorkspaceProps<RetailerRole>) => (
    <RetailerMobileScreen role={props.role} onOpenOrder={props.onOpenOrder} />
  );
  return <AppShell<RetailerRole> appName="پل بازار" allowedRoles={["RETAILER_OWNER", "RETAILER_STAFF"]} workspace={workspace} orderMode="retailer" />;
}
