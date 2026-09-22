/** Shared domain types — derive from authoritative API contract + API_MAP. */

export type Role =
  | "ADMIN_SUPER"
  | "OPS_AGENT"
  | "FIELD_ACTIVATOR"
  | "VENDOR_OWNER"
  | "VENDOR_STAFF"
  | "RETAILER_OWNER"
  | "RETAILER_STAFF";

export type ScreenStatus =
  | "IMPLEMENTED"
  | "VERIFIED"
  | "BLOCKED_EXTERNAL"
  | "GAP"
  | "NOT_APPLICABLE"
  | "PENDING";

export interface ApiSuccess<T> {
  success: true;
  data: T;
}

export interface ApiErrorBody {
  success: false;
  error: {
    code: string;
    message: string;
    details: Record<string, unknown>;
    timestamp: string;
  };
}

export type ApiResponse<T> = ApiSuccess<T> | ApiErrorBody;
