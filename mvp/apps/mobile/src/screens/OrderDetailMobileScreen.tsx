import React, { useCallback, useEffect, useState } from "react";
import { ScrollView, StyleSheet, Text, View } from "react-native";
import { api } from "../api";
import { Btn, Card, Empty, ErrorBox, Input, Screen, StatusChip, Title } from "../components/ui";
import { spacing, useThemedStyles, type Palette } from "../theme";
import type { Role } from "../types";

type Mode = "retailer" | "vendor";
type Order = {
  id: string;
  order_number?: string | null;
  order_status?: string | null;
  dispute_status?: string | null;
  total_amount_toman?: number | string | null;
  retailer_id?: string | null;
  created_at?: string | null;
  delivery_address?: string | null;
};
type Item = {
  id: string;
  product_name_snapshot?: string | null;
  brand_name_snapshot?: string | null;
  packaging_unit_snapshot?: string | null;
  pack_quantity_snapshot?: number | null;
  ordered_quantity?: number | null;
  accepted_quantity?: number | null;
  delivered_quantity?: number | null;
  total_line_amount_toman?: number | string | null;
};
type Timeline = {
  id: string;
  event_type?: string | null;
  from_status?: string | null;
  to_status?: string | null;
  created_at?: string | null;
};
type ReturnRow = {
  id: string;
  status?: string | null;
  issue_type?: string | null;
  created_at?: string | null;
};

function rows<T>(data: unknown, keys: string[]): T[] {
  if (Array.isArray(data)) return data as T[];
  if (!data || typeof data !== "object") return [];
  const o = data as Record<string, unknown>;
  for (const k of keys) {
    if (Array.isArray(o[k])) return o[k] as T[];
    if (o[k] && typeof o[k] === "object") {
      const n = o[k] as Record<string, unknown>;
      for (const k2 of ["items", "data", "events", "returns", "proposals"]) {
        if (Array.isArray(n[k2])) return n[k2] as T[];
      }
    }
  }
  return [];
}
function money(v: number | string | null | undefined): string {
  const n = Number(v);
  return Number.isFinite(n) ? n.toLocaleString("fa-IR") + " تومان" : "—";
}

export function OrderDetailMobileScreen(props: {
  mode: Mode;
  role: Role;
  orderId: string;
  onBack: () => void;
}): React.ReactNode {
  const styles = useThemedStyles(makeStyles);
  const [order, setOrder] = useState<Order | null>(null);
  const [items, setItems] = useState<Item[]>([]);
  const [timeline, setTimeline] = useState<Timeline[]>([]);
  const [returns, setReturns] = useState<ReturnRow[]>([]);
  const [partial, setPartial] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [acting, setActing] = useState<string | null>(null);
  const [returnReason, setReturnReason] = useState("DAMAGED");
  const [returnQuantity, setReturnQuantity] = useState("1");
  const [returnNote, setReturnNote] = useState("");
  const [disputeReason, setDisputeReason] = useState("");
  const [disputeClaimedAmount, setDisputeClaimedAmount] = useState("");
  const [returnClaimedRefund, setReturnClaimedRefund] = useState("");
  const [returnItemId, setReturnItemId] = useState("");
  const [rejectReason, setRejectReason] = useState("");
  const [dispatchDriverName, setDispatchDriverName] = useState("");
  const [dispatchVehiclePlate, setDispatchVehiclePlate] = useState("");
  const [dispatchDriverPhone, setDispatchDriverPhone] = useState("");
  const [deliveryRecipient, setDeliveryRecipient] = useState("");
  const [deliveryOtp, setDeliveryOtp] = useState("");
  const [deliveryStatus, setDeliveryStatus] = useState<string | null>(null);
  const [disputeDescription, setDisputeDescription] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    setActionError(null);
    try {
      const [o, it, tl] = await Promise.all([
        api.get<Order>("/api/v1/orders/" + props.orderId),
        api.get<unknown>("/api/v1/orders/" + props.orderId + "/items"),
        api.get<unknown>("/api/v1/orders/" + props.orderId + "/timeline"),
      ]);
      setOrder(o);
      const nextItems = rows<Item>(it, ["items", "data"]);
      setItems(nextItems);
      setReturnItemId((current) => current || nextItems[0]?.id || "");
      if (props.mode === "retailer") {
        try {
          const delivery = await api.get<{ delivery_status?: string | null }>("/api/v1/orders/" + props.orderId + "/delivery");
          setDeliveryStatus(delivery.delivery_status || null);
        } catch {
          setDeliveryStatus(null);
        }
      }
      setTimeline(rows<Timeline>(tl, ["events", "items", "data"]));
      const next: Record<string, string> = {};
      nextItems.forEach((x) => {
        next[x.id] = String(x.accepted_quantity ?? x.ordered_quantity ?? 0);
      });
      setPartial(next);
      if (props.mode === "retailer") {
        try {
          const rr = await api.get<unknown>("/api/v1/orders/" + props.orderId + "/returns");
          setReturns(rows<ReturnRow>(rr, ["returns", "items", "data"]));
        } catch {
          setReturns([]);
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "دریافت جزئیات سفارش ناموفق بود");
    } finally {
      setLoading(false);
    }
  }, [props.orderId, props.mode]);

  useEffect(() => {
    void load();
  }, [load]);

  async function act(name: "accept" | "preparing" | "ready"): Promise<void> {
    if (props.mode === "vendor" && name === "accept" && props.role !== "VENDOR_OWNER") {
      setActionError("پذیرش سفارش فقط برای مالک بنکداری مجاز است.");
      return;
    }
    setActing(name);
    setActionError(null);
    try {
      await api.post("/api/v1/orders/" + props.orderId + "/" + name, {});
      await load();
    } catch (e) {
      setActionError(e instanceof Error ? e.message : "عملیات سفارش ناموفق بود");
    } finally {
      setActing(null);
    }
  }

  function keyV4(): string {
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (ch) => {
      const r = (Math.random() * 16) | 0;
      const n = ch === "x" ? r : (r & 3) | 8;
      return n.toString(16);
    });
  }

  async function submitReject(): Promise<void> {
    if (props.mode === "vendor" && props.role !== "VENDOR_OWNER") {
      setActionError("رد سفارش فقط برای مالک بنکداری مجاز است.");
      return;
    }
    if (!rejectReason.trim()) {
      setActionError("دلیل رد سفارش الزامی است.");
      return;
    }
    setActing("reject");
    setActionError(null);
    try {
      await api.post("/api/v1/orders/" + props.orderId + "/reject", { reason: rejectReason.trim() });
      setRejectReason("");
      await load();
    } catch (e) {
      setActionError(e instanceof Error ? e.message : "رد سفارش ناموفق بود");
    } finally {
      setActing(null);
    }
  }

  async function submitDispatch(): Promise<void> {
    if (!dispatchDriverName.trim() || !dispatchVehiclePlate.trim() || !dispatchDriverPhone.trim()) {
      setActionError("نام راننده، پلاک و تلفن راننده الزامی است.");
      return;
    }
    setActing("dispatch");
    setActionError(null);
    try {
      await api.post("/api/v1/orders/" + props.orderId + "/dispatch", {
        driver_name: dispatchDriverName.trim(),
        vehicle_plate: dispatchVehiclePlate.trim(),
        driver_phone: dispatchDriverPhone.trim(),
      });
      await load();
    } catch (e) {
      setActionError(e instanceof Error ? e.message : "ثبت ارسال ناموفق بود");
    } finally {
      setActing(null);
    }
  }

  async function submitDeliveryStage(target: "picked-up" | "in-transit" | "arrived"): Promise<void> {
    setActing(target);
    setActionError(null);
    try {
      await api.post("/api/v1/orders/" + props.orderId + "/delivery/" + target, {});
      await load();
    } catch (e) {
      setActionError(e instanceof Error ? e.message : "تغییر وضعیت تحویل ناموفق بود");
    } finally {
      setActing(null);
    }
  }

  async function submitDelivery(): Promise<void> {
    if (!deliveryRecipient.trim()) {
      setActionError("نام تحویل‌گیرنده الزامی است.");
      return;
    }
    if (!/^\\d{4}$/.test(deliveryOtp.trim())) {
      setActionError("کد تحویل باید ۴ رقم باشد.");
      return;
    }
    setActing("deliver");
    setActionError(null);
    try {
      await api.post("/api/v1/orders/" + props.orderId + "/deliver", {
        recipient_name: deliveryRecipient.trim(),
        otp_code: deliveryOtp.trim(),
        proof_type: "OTP_CODE",
      });
      setDeliveryRecipient("");
      setDeliveryOtp("");
      await load();
    } catch (e) {
      setActionError(e instanceof Error ? e.message : "ثبت تحویل ناموفق بود");
    } finally {
      setActing(null);
    }
  }

  async function submitReturn(): Promise<void> {
    const quantity = Number(returnQuantity);
    const claimedRefund = Number(returnClaimedRefund);
    if (!returnItemId) {
      setActionError("یک قلم برای مرجوعی انتخاب کنید.");
      return;
    }
    if (!Number.isFinite(quantity) || quantity < 1) {
      setActionError("تعداد مرجوعی باید حداقل ۱ باشد.");
      return;
    }
    if (!Number.isFinite(claimedRefund) || claimedRefund < 0) {
      setActionError("مبلغ بازپرداخت ادعایی نامعتبر است.");
      return;
    }
    setActing("return");
    setActionError(null);
    try {
      const key = keyV4();
      await api.post("/api/v1/orders/" + props.orderId + "/returns", {
        items: [{ order_item_id: returnItemId, quantity, reason_code: returnReason }],
        reason: returnNote.trim() || returnReason,
        idempotency_key: key,
        claimed_refund_amount_toman: claimedRefund,
      }, { headers: { "Idempotency-Key": key } });
      await load();
    } catch (e) {
      setActionError(e instanceof Error ? e.message : "ثبت مرجوعی ناموفق بود");
    } finally {
      setActing(null);
    }
  }

  async function submitDispute(): Promise<void> {
    if (!disputeReason.trim()) {
      setActionError("دلیل اختلاف الزامی است.");
      return;
    }
    const claimedAmount = Number(disputeClaimedAmount);
    if (!Number.isFinite(claimedAmount) || claimedAmount <= 0) {
      setActionError("مبلغ مورد ادعا باید بیشتر از صفر باشد.");
      return;
    }
    setActing("dispute");
    setActionError(null);
    try {
      const description = disputeDescription.trim()
        ? disputeReason.trim() + ": " + disputeDescription.trim()
        : disputeReason.trim();
      const body: Record<string, unknown> = {
        claimed_amount_toman: claimedAmount,
        description,
      };
      await api.post("/api/v1/orders/" + props.orderId + "/disputes", body);
      setDisputeReason("");
      setDisputeClaimedAmount("");
      setDisputeDescription("");
      await load();
    } catch (e) {
      setActionError(e instanceof Error ? e.message : "ثبت اختلاف ناموفق بود");
    } finally {
      setActing(null);
    }
  }

  async function submitPartial(): Promise<void> {
    if (props.mode === "vendor" && props.role !== "VENDOR_OWNER") {
      setActionError("پذیرش جزئی فقط برای مالک بنکداری مجاز است.");
      return;
    }
    setActing("partial");
    setActionError(null);
    try {
      const lines = items.map((x) => ({
        order_item_id: x.id,
        accepted_quantity: Number(partial[x.id] ?? x.ordered_quantity ?? 0),
      }));
      await api.post("/api/v1/orders/" + props.orderId + "/partial-acceptance-proposals", { items: lines }, {
        headers: { "Idempotency-Key": keyV4() },
      });
      await load();
    } catch (e) {
      setActionError(e instanceof Error ? e.message : "ثبت پذیرش جزئی ناموفق بود");
    } finally {
      setActing(null);
    }
  }

  if (loading) {
    return (
      <Screen>
        <Title badge={props.mode}>در حال بارگذاری سفارش</Title>
        <Card><Text style={styles.meta}>در حال دریافت اطلاعات…</Text></Card>
      </Screen>
    );
  }
  if (!order) {
    return (
      <Screen>
        <Title badge={props.mode}>جزئیات سفارش</Title>
        <ErrorBox message={error || "سفارش پیدا نشد."} />
        <Btn label="تلاش مجدد" onPress={() => void load()} />
        <Btn label="بازگشت" tone="ghost" onPress={props.onBack} />
      </Screen>
    );
  }

  const status = order.order_status || "";
  const vendorMode = props.mode === "vendor";
  const vendorOwner = vendorMode && props.role === "VENDOR_OWNER";

  return (
    <Screen>
      <ScrollView>
        <View style={styles.header}>
          <Title badge={props.role}>جزئیات سفارش</Title>
          <Btn label="بازگشت" tone="ghost" onPress={props.onBack} />
        </View>
        <ErrorBox message={error || actionError} />
        <Card>
          <StatusChip label={status || "—"} tone={status === "DELIVERED" ? "ok" : "info"} />
          <Text style={styles.h2}>{order.order_number || order.id}</Text>
          <Text style={styles.metric}>{money(order.total_amount_toman)}</Text>
          {order.delivery_address ? <Text style={styles.body}>آدرس تحویل: {order.delivery_address}</Text> : null}
        </Card>

        {vendorMode ? (
          <Card>
            <Text style={styles.h2}>اقدامات فروشنده</Text>
            {vendorOwner && ["SUBMITTED", "CREATED"].includes(status) ? <Input label="دلیل رد سفارش" value={rejectReason} onChangeText={setRejectReason} maxLength={1000} /> : null}
            {status === "READY" ? <><Input label="نام راننده" value={dispatchDriverName} onChangeText={setDispatchDriverName} maxLength={100} /><Input label="پلاک خودرو" value={dispatchVehiclePlate} onChangeText={setDispatchVehiclePlate} maxLength={20} /><Input label="تلفن راننده" value={dispatchDriverPhone} onChangeText={setDispatchDriverPhone} maxLength={32} /></> : null}
            <View style={styles.row}>
              {vendorOwner && ["SUBMITTED", "CREATED"].includes(status) ? (
                <>
                  <Btn label="پذیرش" onPress={() => void act("accept")} loading={acting === "accept"} disabled={acting !== null} />
                  <Btn label="رد" tone="ghost" onPress={() => void submitReject()} loading={acting === "reject"} disabled={acting !== null || !rejectReason.trim()} />
                  <Btn label="پذیرش جزئی" tone="ghost" onPress={() => void submitPartial()} loading={acting === "partial"} disabled={acting !== null} />
                </>
              ) : null}
              {["ACCEPTED", "PARTIALLY_ACCEPTED"].includes(status) ? <Btn label="آماده‌سازی" onPress={() => void act("preparing")} loading={acting === "preparing"} disabled={acting !== null} /> : null}
              {status === "PREPARING" ? <Btn label="آماده ارسال" onPress={() => void act("ready")} loading={acting === "ready"} disabled={acting !== null} /> : null}
              {status === "READY" ? <Btn label="ثبت ارسال" onPress={() => void submitDispatch()} loading={acting === "dispatch"} disabled={acting !== null} /> : null}
              {status === "DISPATCHED" ? (
                <>
                  <Btn label="جمع‌آوری شد" onPress={() => void submitDeliveryStage("picked-up")} loading={acting === "picked-up"} disabled={acting !== null} />
                  <Btn label="در مسیر" onPress={() => void submitDeliveryStage("in-transit")} loading={acting === "in-transit"} disabled={acting !== null} />
                  <Btn label="رسید" onPress={() => void submitDeliveryStage("arrived")} loading={acting === "arrived"} disabled={acting !== null} />
                </>
              ) : null}
            </View>
          </Card>
        ) : null}

        <Card>
          <Text style={styles.h2}>اقلام</Text>
          {items.length === 0 ? <Empty title="قلمی ثبت نشده" /> : items.map((x) => (
            <View key={x.id} style={styles.item}>
              <Text style={styles.h2}>{x.product_name_snapshot || x.id}</Text>
              <Text style={styles.meta}>درخواست: {String(x.ordered_quantity ?? 0)} · پذیرفته: {String(x.accepted_quantity ?? "—")}</Text>
              <Text style={styles.meta}>{money(x.total_line_amount_toman)}</Text>
              {vendorOwner && ["SUBMITTED", "CREATED"].includes(status) ? (
                <Input label="تعداد پیشنهادی" value={partial[x.id] || ""} onChangeText={(v) => setPartial((p) => ({ ...p, [x.id]: v }))} keyboardType="numeric" />
              ) : null}
            </View>
          ))}
        </Card>

        {props.mode === "retailer" ? (
          <Card>
            {status === "DISPATCHED" ? (
              <>
                <Text style={styles.meta}>وضعیت تحویل: {deliveryStatus || "نامشخص"}؛ پس از رسیدن محموله به وضعیت ARRIVED، کد تحویل را ثبت کنید.</Text>
                <Input label="نام تحویل‌گیرنده" value={deliveryRecipient} onChangeText={setDeliveryRecipient} maxLength={200} />
                <Input label="کد تحویل ۴ رقمی" value={deliveryOtp} onChangeText={setDeliveryOtp} keyboardType="numeric" maxLength={4} />
                <Btn label="ثبت تحویل" tone="ghost" onPress={() => void submitDelivery()} loading={acting === "deliver"} disabled={acting !== null || deliveryStatus !== "ARRIVED" || !deliveryRecipient.trim() || !deliveryOtp.trim()} />
              </>
            ) : null}
            <Text style={styles.h2}>بازگشت / اختلاف</Text>
            <Input label="دلیل مرجوعی" value={returnReason} onChangeText={setReturnReason} />
            {items.length > 0 ? <View style={styles.row}>{items.map((x) => <Btn key={x.id} label={(x.product_name_snapshot || x.id) + (returnItemId === x.id ? " ✓" : "")} tone={returnItemId === x.id ? "primary" : "ghost"} onPress={() => setReturnItemId(x.id)} />)}</View> : null}
            <Input label="تعداد مرجوعی" value={returnQuantity} onChangeText={setReturnQuantity} keyboardType="numeric" />
            <Input label="مبلغ بازپرداخت ادعایی (تومان)" value={returnClaimedRefund} onChangeText={setReturnClaimedRefund} keyboardType="numeric" />
            <Input label="توضیح مرجوعی" value={returnNote} onChangeText={setReturnNote} multiline numberOfLines={3} maxLength={500} />
            <Btn label="ثبت مرجوعی" onPress={() => void submitReturn()} loading={acting === "return"} disabled={acting !== null} />
            <Text style={styles.meta}>کدهای قراردادی نمونه: DAMAGED، WRONG_ITEM، MISSING_ITEMS، QUALITY، EXPIRED، OTHER</Text>
            <Input label="دلیل اختلاف" value={disputeReason} onChangeText={setDisputeReason} maxLength={200} />
            <Input label="مبلغ مورد ادعا (تومان)" value={disputeClaimedAmount} onChangeText={setDisputeClaimedAmount} keyboardType="numeric" />
            <Input label="شرح اختلاف" value={disputeDescription} onChangeText={setDisputeDescription} multiline numberOfLines={3} maxLength={2000} />
            <Btn label="ثبت اختلاف" tone="ghost" onPress={() => void submitDispute()} loading={acting === "dispute"} disabled={acting !== null || !disputeReason.trim() || !disputeClaimedAmount.trim()} />
            {returns.length === 0 ? <Empty title="مرجوعی ثبت نشده" description="برای این سفارش مورد بازگشتی از API دریافت نشد." /> : returns.map((x) => (
              <View key={x.id} style={styles.item}>
                <StatusChip label={x.status || "—"} tone="info" />
                <Text style={styles.meta}>{x.issue_type || "—"}</Text>
                <Text style={styles.meta}>{x.created_at || "—"}</Text>
              </View>
            ))}
          </Card>
        ) : null}

        <Card>
          <Text style={styles.h2}>خط زمانی</Text>
          {timeline.length === 0 ? <Empty title="رویدادی ثبت نشده" /> : timeline.map((x) => (
            <View key={x.id} style={styles.item}>
              <Text style={styles.h2}>{x.event_type || "رویداد"}</Text>
              <Text style={styles.meta}>{(x.from_status || "∅") + " → " + (x.to_status || "∅")}</Text>
              <Text style={styles.meta}>{x.created_at || "—"}</Text>
            </View>
          ))}
        </Card>
      </ScrollView>
    </Screen>
  );
}

function makeStyles(colors: Palette) {
  return StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", gap: spacing.sm },
  row: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm },
  item: { borderTopWidth: 1, borderTopColor: colors.border, paddingTop: spacing.sm, marginTop: spacing.sm },
  h2: { color: colors.text, fontSize: 15, fontWeight: "700", marginBottom: 4 },
  body: { color: colors.textSecondary, fontSize: 13, lineHeight: 20 },
  meta: { color: colors.textSecondary, fontSize: 11, lineHeight: 18 },
  metric: { color: colors.text, fontSize: 20, fontWeight: "700", marginVertical: spacing.sm },
  });
}
