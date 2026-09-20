"use client";

import { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/navigation";
const uuidv4 = () => crypto.randomUUID();

const STEPS = [
  { key: "address", label: "آدرس تحویل" },
  { key: "delivery", label: "زمان تحویل" },
  { key: "payment", label: "روش پردازش" },
  { key: "review", label: "بررسی و تایید" },
] as const;

const PROVINCES = [
  "تهران",
  "اصفهان",
  "فارس",
  "خراسان رضوی",
  "آذربایجان شرقی",
  "خوزستان",
  "مازندران",
  "گیلان",
  "کرمان",
  "آذربایجان غربی",
  "سیستان و بلوچستان",
  "کرمانشاه",
  "گلستان",
  "همدان",
  "یزد",
  "زنجان",
  "لرستان",
  "سمنان",
  "هرمزگان",
  "چهارمحال و بختیاری",
  "کردستان",
  "بوشهر",
  "قم",
  "مرکزی",
  "ایلام",
  "خراسان شمالی",
  "خراسان جنوبی",
  "چابهار",
] as const;

const TIME_SLOTS = [
  "۰۹:۰۰ - ۱۲:۰۰",
  "۱۲:۰۰ - ۱۵:۰۰",
  "۱۵:۰۰ - ۱۸:۰۰",
  "۱۸:۰۰ - ۲۱:۰۰",
] as const;

interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
  vendor_id: string;
  vendor_name: string;
  image_url: string;
}

interface AddressForm {
  province: string;
  city: string;
  address: string;
  postal_code: string;
  phone: string;
}

interface DeliverySlot {
  date: string;
  time: string;
}

interface PaymentMethod {
  type: "cod" | "online";
  label: string;
}

interface OrderResponse {
  id: string;
  status: string;
}

function generateDeliveryDates(): string[] {
  const dates: string[] = [];
  const now = new Date();
  for (let i = 1; i <= 7; i++) {
    const d = new Date(now);
    d.setDate(d.getDate() + i);
    dates.push(d.toLocaleDateString("fa-IR"));
  }
  return dates;
}

const toPersianDigits = (s: string) =>
  s.replace(/\d/g, (d) => "۰۱۲۳۴۵۶۷۸۹"[+d]);

const formatPrice = (n: number) =>
  toPersianDigits(n.toLocaleString("fa-IR")) + " تومان";

export default function CheckoutPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [address, setAddress] = useState<AddressForm>({
    province: "",
    city: "",
    address: "",
    postal_code: "",
    phone: "",
  });
  const [deliverySlot, setDeliverySlot] = useState<DeliverySlot>({
    date: "",
    time: "",
  });
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const deliveryDates = useMemo(() => generateDeliveryDates(), []);

  useEffect(() => {
    const stored = localStorage.getItem("cart");
    if (stored) {
      try {
        setCart(JSON.parse(stored));
      } catch {
        setCart([]);
      }
    }
  }, []);

  const groupedByVendor = useMemo(() => {
    const groups: Record<string, CartItem[]> = {};
    cart.forEach((item) => {
      if (!groups[item.vendor_id]) groups[item.vendor_id] = [];
      groups[item.vendor_id].push(item);
    });
    return groups;
  }, [cart]);

  const subtotal = useMemo(
    () => cart.reduce((sum, item) => sum + item.price * item.quantity, 0),
    [cart]
  );

  const deliveryFee = 50000;
  const grandTotal = subtotal + deliveryFee;

  const canProceed = (): boolean => {
    switch (step) {
      case 0:
        return (
          address.province !== "" &&
          address.city !== "" &&
          address.address.trim().length > 5 &&
          address.postal_code.length === 10 &&
          address.phone.length >= 10
        );
      case 1:
        return deliverySlot.date !== "" && deliverySlot.time !== "";
      case 2:
        return paymentMethod !== null;
      default:
        return true;
    }
  };

  const handleSubmit = async () => {
    if (submitting) return;
    setSubmitting(true);
    setError("");
    try {
      const idempotencyKey = uuidv4();
      const payload = {
        items: cart.map((item) => ({
          product_id: item.id,
          quantity: item.quantity,
          vendor_id: item.vendor_id,
        })),
        delivery_address: address,
        delivery_slot: deliverySlot,
        payment_method: paymentMethod?.type ?? "cod",
        idempotency_key: idempotencyKey,
      };
      const res = await fetch("/api/v1/orders", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Idempotency-Key": idempotencyKey,
        },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || "خطا در ثبت سفارش");
      }
      const data: OrderResponse = await res.json();
      localStorage.removeItem("cart");
      router.push(
        `/retailer/orders/${data.id}?message=سفارش شما با موفقیت ثبت شد`
      );
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "خطای غیرمنتظره");
    } finally {
      setSubmitting(false);
    }
  };

  const updateAddress = (field: keyof AddressForm, value: string) => {
    setAddress((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold mb-6 text-gray-900">تسویه حساب</h1>

        {/* Stepper */}
        <div className="flex items-center mb-8 gap-0">
          {STEPS.map((s, i) => (
            <div key={s.key} className="flex items-center flex-1 last:flex-none">
              <div className="flex flex-col items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold transition-colors ${
                    i < step
                      ? "bg-green-500 text-white"
                      : i === step
                      ? "bg-blue-600 text-white"
                      : "bg-gray-200 text-gray-500"
                  }`}
                >
                  {i < step ? "✓" : toPersianDigits(String(i + 1))}
                </div>
                <span className="text-xs mt-1 text-gray-600 text-center whitespace-nowrap">
                  {s.label}
                </span>
              </div>
              {i < STEPS.length - 1 && (
                <div
                  className={`flex-1 h-1 mx-1 rounded ${
                    i < step ? "bg-green-500" : "bg-gray-200"
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-300 text-red-700 rounded-lg p-3 mb-4 text-sm">
            {error}
          </div>
        )}

        {/* Step Content */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          {/* Step 1: Address */}
          {step === 0 && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold mb-4">آدرس تحویل</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    استان
                  </label>
                  <select
                    value={address.province}
                    onChange={(e) => {
                      updateAddress("province", e.target.value);
                      updateAddress("city", "");
                    }}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">انتخاب استان</option>
                    {PROVINCES.map((p) => (
                      <option key={p} value={p}>
                        {p}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    شهر
                  </label>
                  <input
                    type="text"
                    value={address.city}
                    onChange={(e) => updateAddress("city", e.target.value)}
                    placeholder="نام شهر"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  آدرس کامل
                </label>
                <textarea
                  value={address.address}
                  onChange={(e) => updateAddress("address", e.target.value)}
                  rows={3}
                  placeholder="خیابان، کوچه، پلاک، واحد..."
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    کد پستی
                  </label>
                  <input
                    type="text"
                    value={address.postal_code}
                    onChange={(e) =>
                      updateAddress(
                        "postal_code",
                        e.target.value.replace(/\D/g, "").slice(0, 10)
                      )
                    }
                    placeholder="۱۲۳۴۵۶۷۸۹۰"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    dir="ltr"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    شماره تماس
                  </label>
                  <input
                    type="tel"
                    value={address.phone}
                    onChange={(e) =>
                      updateAddress(
                        "phone",
                        e.target.value.replace(/\D/g, "").slice(0, 11)
                      )
                    }
                    placeholder="۰۹۱۲۱۲۳۴۵۶۷"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    dir="ltr"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Delivery Time */}
          {step === 1 && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold mb-4">زمان تحویل</h2>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  تاریخ تحویل
                </label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {deliveryDates.map((date) => (
                    <button
                      key={date}
                      onClick={() =>
                        setDeliverySlot((prev) => ({ ...prev, date }))
                      }
                      className={`border rounded-lg px-3 py-2 text-sm transition-colors ${
                        deliverySlot.date === date
                          ? "bg-blue-600 text-white border-blue-600"
                          : "border-gray-300 hover:border-blue-400 text-gray-700"
                      }`}
                    >
                      {date}
                    </button>
                  ))}
                </div>
              </div>

              {deliverySlot.date && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    بازه زمانی
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    {TIME_SLOTS.map((slot) => (
                      <button
                        key={slot}
                        onClick={() =>
                          setDeliverySlot((prev) => ({ ...prev, time: slot }))
                        }
                        className={`border rounded-lg px-4 py-3 text-sm transition-colors ${
                          deliverySlot.time === slot
                            ? "bg-blue-600 text-white border-blue-600"
                            : "border-gray-300 hover:border-blue-400 text-gray-700"
                        }`}
                      >
                        {slot}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Step 3: Payment Method */}
          {step === 2 && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold mb-4">روش پردازش</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button
                  onClick={() =>
                    setPaymentMethod({ type: "cod", label: "پرداخت در محل" })
                  }
                  className={`border-2 rounded-xl p-6 text-center transition-all ${
                    paymentMethod?.type === "cod"
                      ? "border-blue-600 bg-blue-50"
                      : "border-gray-200 hover:border-blue-300"
                  }`}
                >
                  <div className="text-3xl mb-2">💵</div>
                  <div className="font-semibold text-gray-900">
                    پرداخت در محل
                  </div>
                  <div className="text-sm text-gray-500 mt-1">
                    هنگام تحویل سفارش وجه نقد پرداخت کنید
                  </div>
                </button>

                <button
                  onClick={() =>
                    setPaymentMethod({ type: "online", label: "پرداخت آنلاین" })
                  }
                  className={`border-2 rounded-xl p-6 text-center transition-all ${
                    paymentMethod?.type === "online"
                      ? "border-blue-600 bg-blue-50"
                      : "border-gray-200 hover:border-blue-300"
                  }`}
                >
                  <div className="text-3xl mb-2">💳</div>
                  <div className="font-semibold text-gray-900">
                    پرداخت آنلاین
                  </div>
                  <div className="text-sm text-gray-500 mt-1">
                    پرداخت از طریق درگاه بانکی
                  </div>
                </button>
              </div>
            </div>
          )}

          {/* Step 4: Review */}
          {step === 3 && (
            <div className="space-y-6">
              <h2 className="text-lg font-semibold mb-4">بررسی و تایید سفارش</h2>

              {/* Items grouped by vendor */}
              {Object.entries(groupedByVendor).map(([vendorId, items]) => (
                <div
                  key={vendorId}
                  className="border border-gray-200 rounded-lg p-4"
                >
                  <h3 className="font-medium text-gray-800 mb-3 border-b pb-2">
                    {items[0].vendor_name}
                  </h3>
                  <div className="space-y-2">
                    {items.map((item) => (
                      <div
                        key={item.id}
                        className="flex justify-between text-sm"
                      >
                        <span>
                          {item.name} × {toPersianDigits(String(item.quantity))}
                        </span>
                        <span className="font-medium">
                          {formatPrice(item.price * item.quantity)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}

              {/* Totals */}
              <div className="border-t pt-4 space-y-2">
                <div className="flex justify-between text-sm text-gray-600">
                  <span>جمع کل</span>
                  <span>{formatPrice(subtotal)}</span>
                </div>
                <div className="flex justify-between text-sm text-gray-600">
                  <span>هزینه ارسال</span>
                  <span>{formatPrice(deliveryFee)}</span>
                </div>
                <div className="flex justify-between text-base font-bold text-gray-900 border-t pt-2">
                  <span>مبلغ قابل پرداخت</span>
                  <span>{formatPrice(grandTotal)}</span>
                </div>
              </div>

              {/* Delivery Info */}
              <div className="bg-gray-50 rounded-lg p-4 text-sm space-y-1">
                <div className="font-medium text-gray-800 mb-2">
                  اطلاعات تحویل
                </div>
                <div>
                  آدرس: {address.address}، {address.city}، {address.province}
                </div>
                <div>کد پستی: {toPersianDigits(address.postal_code)}</div>
                <div>تلفن: {toPersianDigits(address.phone)}</div>
                <div>
                  زمان تحویل: {deliverySlot.date} — {deliverySlot.time}
                </div>
              </div>

              {/* Payment */}
              <div className="bg-gray-50 rounded-lg p-4 text-sm">
                <div className="font-medium text-gray-800 mb-1">
                  روش پرداخت
                </div>
                <div>{paymentMethod?.label}</div>
              </div>
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="flex justify-between mt-6">
          {step > 0 ? (
            <button
              onClick={() => setStep((s) => s - 1)}
              className="px-6 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-100 transition-colors text-sm font-medium"
            >
              بازگشت
            </button>
          ) : (
            <div />
          )}

          {step < 3 ? (
            <button
              onClick={() => setStep((s) => s + 1)}
              disabled={!canProceed()}
              className="px-6 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors text-sm font-medium"
            >
              ادامه
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={submitting || cart.length === 0}
              className="px-8 py-2.5 rounded-lg bg-green-600 text-white hover:bg-green-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors text-sm font-bold"
            >
              {submitting ? "در حال ثبت..." : "ثبت سفارش"}
            </button>
          )}
        </div>

        {cart.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            سبد خرید شما خالی است
          </div>
        )}
      </div>
    </div>
  );
}
