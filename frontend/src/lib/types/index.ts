export interface User {
  id: string;
  phone_number: string;
  full_name: string | null;
  role: UserRole;
  is_active: boolean;
}

export type UserRole =
  | "ADMIN_SUPER"
  | "OPS_AGENT"
  | "FIELD_ACTIVATOR"
  | "VENDOR_OWNER"
  | "VENDOR_STAFF"
  | "RETAILER_OWNER"
  | "RETAILER_STAFF";

export interface Organization {
  id: string;
  name: string;
  org_type: "VENDOR" | "RETAILER" | "BRAND";
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
  switchOrganization: (orgId: string) => Promise<void>;
}

export interface Product {
  id: string;
  name: string;
  brand: string;
  category: string;
  unit: string;
  pack_size: number;
  unit_price_toman: number;
  image_url: string | null;
  vendor_id?: string;
  vendor_name?: string;
  vendor_logo_url?: string;
  stock_quantity?: number;
}

export interface BasketItem {
  id: string;
  product_id: string;
  product_name: string;
  vendor_id: string;
  vendor_name: string;
  quantity: number;
  unit_price_toman: number;
  pack_size: number;
  unit: string;
}

export interface Order {
  id: string;
  order_number: string;
  order_status: OrderStatus;
  total_amount_toman: number;
  created_at: string;
  vendor_count?: number;
  items?: OrderItem[];
  timeline?: OrderEvent[];
}

export type OrderStatus =
  | "CREATED"
  | "SUBMITTED"
  | "ACCEPTED"
  | "PARTIALLY_ACCEPTED"
  | "PREPARING"
  | "DISPATCHED"
  | "DELIVERED"
  | "CANCELLED"
  | "RETURN_REQUESTED"
  | "DISPUTED";

export interface OrderItem {
  id: string;
  product_name: string;
  quantity: number;
  unit_price_toman: number;
  pack_size: number;
  unit: string;
  vendor_name: string;
}

export interface OrderEvent {
  id: string;
  event_type: string;
  description: string;
  created_at: string;
  actor_name?: string;
}

export interface VendorOrder {
  id: string;
  order_number: string;
  retailer_name: string;
  total_amount_toman: number;
  order_status: OrderStatus;
  created_at: string;
  items_count: number;
}

export interface Settlement {
  id: string;
  settlement_batch_id: string;
  order_id: string;
  order_number?: string;
  gross_amount_toman: number;
  commission_amount_toman: number;
  net_vendor_amount_toman: number;
  status: "PENDING" | "SETTLED" | "FAILED";
  settled_at: string | null;
}

export interface InventoryItem {
  id: string;
  product_id: string;
  product_name: string;
  quantity: number;
  unit: string;
  last_confirmed_at: string | null;
}

export interface Notification {
  id: string;
  event_name: string;
  title: string;
  body: string;
  priority: "LOW" | "NORMAL" | "HIGH" | "CRITICAL";
  created_at: string;
  read: boolean;
}

export interface FieldTask {
  id: string;
  task_type: FieldTaskType;
  status: FieldTaskStatus;
  notes: string | null;
  created_at: string;
  retailer_name?: string;
  vendor_name?: string;
  location?: string;
}

export type FieldTaskType =
  | "ONBOARD_RETAILER"
  | "TRAIN_RETAILER"
  | "FIRST_ORDER_ASSIST"
  | "FOLLOW_UP"
  | "VENDOR_VISIT"
  | "DISPUTE_VISIT"
  | "VENDOR_TIMEOUT";

export type FieldTaskStatus =
  | "ASSIGNED"
  | "IN_PROGRESS"
  | "COMPLETED"
  | "FAILED"
  | "CANCELLED";

export interface SupportCase {
  id: string;
  subject: string;
  status: SupportCaseStatus;
  priority: "LOW" | "NORMAL" | "HIGH" | "CRITICAL";
  created_at: string;
  messages?: SupportMessage[];
}

export type SupportCaseStatus =
  | "OPEN"
  | "IN_PROGRESS"
  | "WAITING_ON_VENDOR"
  | "WAITING_ON_USER"
  | "RESOLVED"
  | "CLOSED";

export interface SupportMessage {
  id: string;
  content: string;
  sender_name: string;
  sender_role: string;
  created_at: string;
}

export interface DashboardKPI {
  title: string;
  value: string | number;
  trend?: "up" | "down" | "neutral";
  trend_value?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  offset: number;
  limit: number;
}

export interface ApiError {
  detail: string;
  error_code: string;
  details?: Record<string, unknown>;
}
