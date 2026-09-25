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

  async function act(name: "accept" | "reject" | "preparing" | "ready" | "dispatch" | "deliver"): Promise<void> {
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

  async function submitReturn(): Promise<void> {
    const quantity = Number(returnQuantity);
    if (!Number.isFinite(quantity) || quantity < 1) {
      setActionError("تعداد مرجوعی باید حداقل ۱ باشد.");
      return;
    }
    setActing("return");
    setActionError(null);
    try {
      const body: Record<string, unknown> = { reason_code: returnReason, quantity };
      if (returnNote.trim()) body.reason = returnNote.trim();
      await api.post("/api/v1/orders/" + props.orderId + "/returns", body);
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
    setActing("partial");
    setActionError(null);
    try {
      const lines = items.map((x) => ({
        item_id: x.id,
        quantity: Number(partial[x.id] ?? x.ordered_quantity ?? 0),
      }));
      await api.post("/api/v1/orders/" + props.orderId + "/partial-acceptance-proposals", { items: lines });
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
            <View style={styles.row}>
              {["SUBMITTED", "CREATED"].includes(status) ? (
                <>
                  <Btn label="پذیرش" onPress={() => void act("accept")} loading={acting === "accept"} disabled={acting !== null} />
                  <Btn label="رد" tone="ghost" onPress={() => void act("reject")} loading={acting === "reject"} disabled={acting !== null} />
                  <Btn label="پذیرش جزئی" tone="ghost" onPress={() => void submitPartial()} loading={acting === "partial"} disabled={acting !== null} />
                </>
              ) : null}
              {["ACCEPTED", "PARTIALLY_ACCEPTED"].includes(status) ? <Btn label="آماده‌سازی" onPress={() => void act("preparing")} loading={acting === "preparing"} disabled={acting !== null} /> : null}
              {status === "PREPARING" ? <Btn label="آماده ارسال" onPress={() => void act("ready")} loading={acting === "ready"} disabled={acting !== null} /> : null}
              {status === "READY" ? <Btn label="ارسال" onPress={() => void act("dispatch")} loading={acting === "dispatch"} disabled={acting !== null} /> : null}
              {status === "DISPATCHED" ? <Btn label="تحویل" onPress={() => void act("deliver")} loading={acting === "deliver"} disabled={acting !== null} /> : null}
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
              {vendorMode && ["SUBMITTED", "CREATED"].includes(status) ? (
                <Input label="تعداد پیشنهادی" value={partial[x.id] || ""} onChangeText={(v) => setPartial((p) => ({ ...p, [x.id]: v }))} keyboardType="numeric" />
              ) : null}
            </View>
          ))}
        </Card>

        {props.mode === "retailer" ? (
          <Card>
            <Text style={styles.h2}>بازگشت / اختلاف</Text>
            <Input label="دلیل مرجوعی" value={returnReason} onChangeText={setReturnReason} />
            <Input label="تعداد مرجوعی" value={returnQuantity} onChangeText={setReturnQuantity} keyboardType="numeric" />
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
