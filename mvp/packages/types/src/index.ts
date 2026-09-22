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

export type NotificationPriority = "LOW" | "NORMAL" | "HIGH" | "CRITICAL";

export interface NotificationItem {
  id: string;
  event_name: string;
  title: string;
  body: string;
  priority: NotificationPriority;
  created_at: string;
  read?: boolean;
  is_read?: boolean;
}

export interface NotificationPreference {
  user_id: string;
  category: string;
  push_enabled: boolean;
  sms_enabled: boolean;
}

export interface NotificationPreferenceUpdate {
  event_name: string;
  channel: "PUSH" | "SMS";
  is_enabled: boolean;
}

export interface UserProfileRecord {
  id?: string;
  user_id: string;
  display_name: string;
  avatar_media_asset_id?: string | null;
  email?: string | null;
  preferred_language?: string;
  timezone?: string;
  bio?: string | null;
  profile_status?: string;
  phone_number?: string | null;
  is_active?: boolean;
  last_login_at?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface MembershipContext {
  id?: string;
  user_id?: string;
  organization_id: string;
  role: string;
  status?: string;
  organization_name?: string | null;
  org_type?: string | null;
  organization_status?: string | null;
}

export interface ProfileContextResponse {
  user_profile: UserProfileRecord;
  membership?: MembershipContext | null;
  membership_profile?: Record<string, unknown> | null;
  persona_profile?: Record<string, unknown> | null;
}

export interface ProfileUpdateRequest {
  display_name?: string | null;
  email?: string | null;
  preferred_language?: string | null;
  timezone?: string | null;
  bio?: string | null;
  avatar_media_asset_id?: string | null;
}

export interface RefreshRequest {
  refresh_token: string;
}

export interface RefreshResponse {
  access_token: string;
  token_type?: string;
  expires_in?: number;
}
