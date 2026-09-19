export interface User {
  id: string;
  phone_number: string;
  full_name: string;
  role: string;
}

export interface AuthState {
  user: User | null;
  access_token: string | null;
  refresh_token: string | null;
  organization_id: string | null;
  isAuthenticated: boolean;
  login: (phoneNumber: string) => Promise<void>;
  verifyOtp: (phoneNumber: string, code: string) => Promise<void>;
  logout: () => void;
}

export interface Order {
  id: string;
  order_number: string;
  order_status: string;
  total_amount_toman: number;
  created_at: string;
}

export interface FieldTask {
  id: string;
  task_type: string;
  status: string;
  notes: string | null;
  created_at: string;
}

export interface Notification {
  id: string;
  event_name: string;
  title: string;
  body: string;
  priority: string;
  created_at: string;
}

export interface NotificationPreference {
  event_name: string;
  push_enabled: boolean;
  sms_enabled: boolean;
}

export interface SupportCase {
  id: string;
  subject: string;
  status: string;
  priority: string;
  created_at: string;
}

export interface DeliveryException {
  id: string;
  exception_type: string;
  status: string;
  description: string;
  created_at: string;
}
