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
  | { name: "assisted" };
