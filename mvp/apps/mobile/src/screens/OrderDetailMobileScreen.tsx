import React, { useCallback, useEffect, useState } from "react";
import { ScrollView, StyleSheet, Text, View } from "react-native";
import { api } from "../api";
import { Btn, Card, Empty, ErrorBox, Input, Screen, StatusChip } from "../components/ui";
import { DeliveryProgress } from "../motion/DeliveryProgress";
import { FadeIn } from "../motion/FadeIn";
import { OrderProgress } from "../motion/OrderProgress";
import { Pulse } from "../motion/Pulse";
import { staggerDelay } from "../motion/motionTokens";
import { SuccessCheck } from "../motion/SuccessCheck";
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
    if (props.mode === "vendor" && props.role !== "VENDOR_OWNER") { setActionError("رد سفارش فقط برای مالک بنکداری مجاز است."); return; }
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
    if (!/^\d{4}$/.test(deliveryOtp.trim())) {
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
    if (props.mode === "vendor" && props.role !== "VENDOR_OWNER") { setActionError("پذیرش جزئی فقط برای مالک بنکداری مجاز است."); return; }
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
        <View style={styles.centerState}>
          <Pulse active size={62} style={styles.loadingDot}>
            <Text style={styles.loadingMark}>…</Text>
          </Pulse>
          <Text style={styles.title}>در حال بارگذاری سفارش</Text>
          <Text style={styles.meta}>در حال دریافت اطلاعات…</Text>
        </View>
      </Screen>
    );
  }

  if (!order) {
    return (
      <Screen>
        <View style={styles.pageHeader}>
          <Btn label="بازگشت" tone="ghost" onPress={props.onBack} />
          <Text style={styles.title}>جزئیات سفارش</Text>
        </View>
        <ErrorBox message={error || "سفارش پیدا نشد."} />
        <Btn label="تلاش مجدد" onPress={() => void load()} />
      </Screen>
    );
  }

  const status = order.order_status || "";
  const vendorMode = props.mode === "vendor";
  const vendorOwner = vendorMode && props.role === "VENDOR_OWNER";
  const deliveryAxisVisible = status === "DISPATCHED" || (status === "DELIVERED" && deliveryStatus !== null) || Boolean(deliveryStatus);

  return (
    <Screen>
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scroll}>
        <View style={styles.pageHeader}>
          <Btn label="بازگشت" tone="ghost" onPress={props.onBack} compact />
          <Text style={styles.title}>جزئیات سفارش</Text>
          <View style={styles.headerSpacer} />
        </View>

        <ErrorBox message={error || actionError} />

        <Card style={styles.summaryCard}>
          <View style={styles.summaryTop}>
            <StatusChip label={status || "—"} tone={status === "DELIVERED" ? "ok" : "info"} />
            <Text style={styles.orderNumber}>{order.order_number || order.id}</Text>
          </View>
          <Text style={styles.metric}>{money(order.total_amount_toman)}</Text>
          {order.delivery_address ? <Text style={styles.address}>📍 {order.delivery_address}</Text> : null}
        </Card>

        <Card style={styles.stepperCard}>
          <Text style={styles.sectionTitle}>وضعیت سفارش</Text>
          <OrderProgress status={status} />
        </Card>

        {deliveryAxisVisible ? (
          <Card style={styles.stepperCard}>
            <Text style={styles.sectionTitle}>مسیر تحویل</Text>
            <DeliveryProgress deliveryStatus={deliveryStatus} orderStatus={status} />
            {status === "DELIVERED" ? (
              <FadeIn>
                <View style={styles.deliveredStrip}>
                  <SuccessCheck size={40} />
                  <Text style={styles.deliveredText}>تحویل با موفقیت ثبت شد</Text>
                </View>
              </FadeIn>
            ) : null}
          </Card>
        ) : null}

        {vendorMode ? (
          <Card style={styles.actionCard}>
            <Text style={styles.sectionTitle}>اقدامات فروشنده</Text>
            {vendorOwner && ["SUBMITTED", "CREATED"].includes(status) ? <Input label="دلیل رد سفارش" value={rejectReason} onChangeText={setRejectReason} maxLength={1000} /> : null}
            {status === "READY" ? (
              <>
                <Input label="نام راننده" value={dispatchDriverName} onChangeText={setDispatchDriverName} maxLength={100} />
                <Input label="پلاک خودرو" value={dispatchVehiclePlate} onChangeText={setDispatchVehiclePlate} maxLength={20} />
                <Input label="تلفن راننده" value={dispatchDriverPhone} onChangeText={setDispatchDriverPhone} maxLength={32} />
              </>
            ) : null}
            <View style={styles.actionRow}>
              {vendorOwner && ["SUBMITTED", "CREATED"].includes(status) ? (
                <>
                  <Btn compact label="پذیرش" onPress={() => void act("accept")} loading={acting === "accept"} disabled={acting !== null} />
                  <Btn compact label="رد" tone="ghost" onPress={() => void submitReject()} loading={acting === "reject"} disabled={acting !== null || !rejectReason.trim()} />
                  <Btn compact label="پذیرش جزئی" tone="ghost" onPress={() => void submitPartial()} loading={acting === "partial"} disabled={acting !== null} />
                </>
              ) : null}
              {["ACCEPTED", "PARTIALLY_ACCEPTED"].includes(status) ? <Btn compact label="آماده‌سازی" onPress={() => void act("preparing")} loading={acting === "preparing"} disabled={acting !== null} /> : null}
              {status === "PREPARING" ? <Btn compact label="آماده ارسال" onPress={() => void act("ready")} loading={acting === "ready"} disabled={acting !== null} /> : null}
              {status === "READY" ? <Btn compact label="ثبت ارسال" onPress={() => void submitDispatch()} loading={acting === "dispatch"} disabled={acting !== null} /> : null}
              {status === "DISPATCHED" ? (
                <>
                  <Btn compact label="جمع‌آوری شد" onPress={() => void submitDeliveryStage("picked-up")} loading={acting === "picked-up"} disabled={acting !== null} />
                  <Btn compact label="در مسیر" onPress={() => void submitDeliveryStage("in-transit")} loading={acting === "in-transit"} disabled={acting !== null} />
                  <Btn compact label="رسید" onPress={() => void submitDeliveryStage("arrived")} loading={acting === "arrived"} disabled={acting !== null} />
                </>
              ) : null}
            </View>
          </Card>
        ) : null}

        <Card style={styles.itemsCard}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>اقلام سفارش</Text>
            <Text style={styles.meta}>{items.length.toLocaleString("fa-IR")} قلم</Text>
          </View>
          {items.length === 0 ? <Empty title="قلمی ثبت نشده" /> : items.map((x, index) => (
            <FadeIn key={x.id} delay={staggerDelay(index)}>
              <View style={styles.item}>
                <View style={styles.itemVisual}><Text style={styles.itemEmoji}>📦</Text></View>
                <View style={styles.itemMain}>
                  <Text style={styles.itemTitle}>{x.product_name_snapshot || x.id}</Text>
                  <Text style={styles.meta}>{x.brand_name_snapshot || ""} · {x.packaging_unit_snapshot || ""}</Text>
                  <Text style={styles.meta}>درخواست: {String(x.ordered_quantity ?? 0)} · پذیرفته: {String(x.accepted_quantity ?? "—")}</Text>
                  {vendorMode && ["SUBMITTED", "CREATED"].includes(status) ? (
                    <Input label="تعداد پیشنهادی" value={partial[x.id] || ""} onChangeText={(v) => setPartial((p) => ({ ...p, [x.id]: v }))} keyboardType="numeric" />
                  ) : null}
                </View>
                <Text style={styles.linePrice}>{money(x.total_line_amount_toman)}</Text>
              </View>
            </FadeIn>
          ))}
        </Card>

        {props.mode === "retailer" ? (
          <Card style={styles.deliveryCard}>
            <Text style={styles.sectionTitle}>تحویل، مرجوعی و اختلاف</Text>
            {status === "DISPATCHED" ? (
              <>
                <StatusChip label={"تحویل: " + (deliveryStatus || "نامشخص")} tone="info" />
                <Input label="نام تحویل‌گیرنده" value={deliveryRecipient} onChangeText={setDeliveryRecipient} maxLength={200} />
                <Input label="کد تحویل ۴ رقمی" value={deliveryOtp} onChangeText={setDeliveryOtp} keyboardType="numeric" maxLength={4} />
                <Btn label="ثبت تحویل" onPress={() => void submitDelivery()} loading={acting === "deliver"} disabled={acting !== null || deliveryStatus !== "ARRIVED" || !deliveryRecipient.trim() || !deliveryOtp.trim()} />
              </>
            ) : null}

            <Text style={styles.subTitle}>ثبت مرجوعی</Text>
            <Input label="دلیل مرجوعی" value={returnReason} onChangeText={setReturnReason} />
            {items.length > 0 ? <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.choiceRow}>{items.map((x) => <Btn key={x.id} compact label={(x.product_name_snapshot || x.id) + (returnItemId === x.id ? " ✓" : "")} tone={returnItemId === x.id ? "primary" : "ghost"} onPress={() => setReturnItemId(x.id)} />)}</ScrollView> : null}
            <Input label="تعداد مرجوعی" value={returnQuantity} onChangeText={setReturnQuantity} keyboardType="numeric" />
            <Input label="مبلغ بازپرداخت ادعایی (تومان)" value={returnClaimedRefund} onChangeText={setReturnClaimedRefund} keyboardType="numeric" />
            <Input label="توضیح مرجوعی" value={returnNote} onChangeText={setReturnNote} multiline numberOfLines={3} maxLength={500} />
            <Btn label="ثبت مرجوعی" onPress={() => void submitReturn()} loading={acting === "return"} disabled={acting !== null} />

            <Text style={styles.subTitle}>ثبت اختلاف</Text>
            <Input label="دلیل اختلاف" value={disputeReason} onChangeText={setDisputeReason} maxLength={200} />
            <Input label="مبلغ مورد ادعا (تومان)" value={disputeClaimedAmount} onChangeText={setDisputeClaimedAmount} keyboardType="numeric" />
            <Input label="شرح اختلاف" value={disputeDescription} onChangeText={setDisputeDescription} multiline numberOfLines={3} maxLength={2000} />
            <Btn label="ثبت اختلاف" tone="ghost" onPress={() => void submitDispute()} loading={acting === "dispute"} disabled={acting !== null || !disputeReason.trim() || !disputeClaimedAmount.trim()} />

            {returns.length > 0 ? (
              <View style={styles.returnList}>
                <Text style={styles.meta}>آخرین مرجوعی‌ها</Text>
                {returns.map((x) => <View key={x.id} style={styles.returnRow}><StatusChip label={x.status || "—"} tone="info" /><Text style={styles.meta}>{x.issue_type || "—"}</Text><Text style={styles.meta}>{x.created_at || "—"}</Text></View>)}
              </View>
            ) : null}
          </Card>
        ) : null}

        <Card style={styles.timelineCard}>
          <Text style={styles.sectionTitle}>خط زمانی سفارش</Text>
          {timeline.length === 0 ? <Empty title="رویدادی ثبت نشده" /> : timeline.map((x, index) => (
            <FadeIn key={x.id} delay={staggerDelay(index)}>
              <View style={styles.timelineRow}>
                <View style={styles.timelineRail}><View style={styles.timelineDot} />{index < timeline.length - 1 ? <View style={styles.timelineLine} /> : null}</View>
                <View style={styles.timelineBody}>
                  <Text style={styles.itemTitle}>{x.event_type || "رویداد"}</Text>
                  <Text style={styles.meta}>{(x.from_status || "∅") + " → " + (x.to_status || "∅")}</Text>
                  <Text style={styles.meta}>{x.created_at || "—"}</Text>
                </View>
              </View>
            </FadeIn>
          ))}
        </Card>
      </ScrollView>
    </Screen>
  );
}
function makeStyles(colors: Palette) {
  return StyleSheet.create({
    scroll: { paddingBottom: spacing.xl },
    pageHeader: { flexDirection: "row", alignItems: "center", marginBottom: spacing.md, gap: spacing.sm },
    headerSpacer: { width: 74 },
    centerState: { flex: 1, minHeight: 420, alignItems: "center", justifyContent: "center" },
    loadingDot: { width: 62, height: 62, borderRadius: 31, backgroundColor: colors.brandSoft, alignItems: "center", justifyContent: "center", marginBottom: spacing.md },
    loadingMark: { color: colors.brand, fontSize: 28, fontWeight: "900" },
    title: { flex: 1, color: colors.text, fontSize: 21, fontWeight: "900", textAlign: "right" },
    summaryCard: { paddingVertical: spacing.lg },
    summaryTop: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", gap: spacing.sm },
    orderNumber: { flex: 1, color: colors.text, fontSize: 15, fontWeight: "900", textAlign: "right" },
    metric: { color: colors.text, fontSize: 24, fontWeight: "900", textAlign: "right", marginTop: spacing.sm },
    address: { color: colors.textSecondary, fontSize: 12, lineHeight: 19, textAlign: "right", marginTop: spacing.sm },
    stepperCard: { paddingVertical: spacing.lg },
    deliveredStrip: { flexDirection: "row", alignItems: "center", gap: spacing.md, borderTopWidth: 1, borderTopColor: colors.border, paddingTop: spacing.md, marginTop: spacing.sm },
    deliveredText: { color: colors.success, fontSize: 13, fontWeight: "800", textAlign: "right" },
    sectionHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.sm },
    sectionTitle: { color: colors.text, fontSize: 15, fontWeight: "900", textAlign: "right", marginBottom: spacing.sm },
    actionCard: { borderColor: colors.brand + "44" },
    actionRow: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm },
    itemsCard: { paddingBottom: spacing.sm },
    item: { flexDirection: "row", alignItems: "center", gap: spacing.sm, borderTopWidth: 1, borderTopColor: colors.border, paddingTop: spacing.md, marginTop: spacing.sm },
    itemVisual: { width: 58, height: 66, borderRadius: 14, backgroundColor: colors.neutralBg, alignItems: "center", justifyContent: "center" },
    itemEmoji: { fontSize: 26 },
    itemMain: { flex: 1, minWidth: 0 },
    itemTitle: { color: colors.text, fontSize: 13, fontWeight: "900", textAlign: "right" },
    linePrice: { color: colors.text, fontSize: 12, fontWeight: "900", minWidth: 72, textAlign: "left" },
    deliveryCard: { borderColor: colors.border },
    subTitle: { color: colors.text, fontSize: 13, fontWeight: "800", textAlign: "right", marginTop: spacing.md, marginBottom: spacing.sm },
    choiceRow: { gap: spacing.sm, paddingBottom: spacing.sm },
    returnList: { marginTop: spacing.md },
    returnRow: { flexDirection: "row", alignItems: "center", gap: spacing.sm, borderTopWidth: 1, borderTopColor: colors.border, paddingTop: spacing.sm, marginTop: spacing.sm },
    timelineCard: { paddingBottom: spacing.md },
    timelineRow: { flexDirection: "row", alignItems: "stretch", gap: spacing.md, minHeight: 72 },
    timelineRail: { width: 16, alignItems: "center" },
    timelineDot: { width: 10, height: 10, borderRadius: 5, backgroundColor: colors.brand, marginTop: 4 },
    timelineLine: { flex: 1, width: 2, backgroundColor: colors.brand + "55", marginTop: 4 },
    timelineBody: { flex: 1, borderBottomWidth: 1, borderBottomColor: colors.border, paddingBottom: spacing.sm, marginBottom: spacing.sm },
    meta: { color: colors.textSecondary, fontSize: 11, lineHeight: 18, textAlign: "right" },
    body: { color: colors.text, fontSize: 13, lineHeight: 21, textAlign: "right" },
  });
}
