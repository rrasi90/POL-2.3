export type Role =
  | "ADMIN_SUPER"
  | "OPS_AGENT"
  | "FIELD_ACTIVATOR"
  | "VENDOR_OWNER"
  | "VENDOR_STAFF"
  | "RETAILER_OWNER"
  | "RETAILER_STAFF";

export interface FieldTask {
  id: string;
  task_type?: string | null;
  assigned_to_user_id?: string | null;
  target_organization_id?: string | null;
  status?: string | null;
  notes?: string | null;
  due_date?: string | null;
  completed_at?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface OtpRequest {
  otp_request_id: string;
  expires_in_seconds: number;
  resend_interval_seconds: number;
}

export interface VerifyResult {
  access_token: string;
  refresh_token?: string;
  role?: string;
  current_organization?: { id?: string; role?: string } | null;
}

export type Route =
  | { name: "login" }
  | { name: "field" }
  | { name: "task"; taskId: string }
  | { name: "assisted" }
  | { name: "workspace"; role: Role };

export const ALL_ROLES: Role[] = [
  "ADMIN_SUPER",
  "OPS_AGENT",
  "FIELD_ACTIVATOR",
  "VENDOR_OWNER",
  "VENDOR_STAFF",
  "RETAILER_OWNER",
  "RETAILER_STAFF",
];

export function normalizeRole(value: string | undefined | null): Role | null {
  return value && (ALL_ROLES as string[]).includes(value) ? (value as Role) : null;
}
