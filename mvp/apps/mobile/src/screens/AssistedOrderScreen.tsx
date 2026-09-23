import React, { useCallback, useEffect, useState } from "react";
import { FlatList, StyleSheet, Text, View } from "react-native";
import { api } from "../api";
import { OfflineBanner } from "../components/OfflineBanner";
import { Btn, Card, Empty, ErrorBox, Input, Screen, StatusChip, Title } from "../components/ui";
import { colors, spacing } from "../theme";
import { getToken } from "../api";

interface CatalogItem {
  id?: string;
  sku?: string;
  name?: string;
  title?: string;
  price_toman?: number;
}

function itemsOf(data: unknown): CatalogItem[] {
  if (Array.isArray(data)) return data as CatalogItem[];
  if (data && typeof data === "object") {
    const rec = data as Record<string, unknown>;
    if (Array.isArray(rec.items)) return rec.items as CatalogItem[];
    if (Array.isArray(rec.products)) return rec.products as CatalogItem[];
    if (Array.isArray(rec.results)) return rec.results as CatalogItem[];
  }
  return [];
}

/**
 * F-03 assisted order — Field embeds retailer catalog browse (RETAILER_CTX).
 * Basket/checkout remains retailer web flows (D-014 multi-vendor).
 */
export function AssistedOrderScreen(props: { onBack: () => void }): React.ReactNode {
  const [items, setItems] = useState<CatalogItem[]>([]);
  const [query, setQuery] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const authed = Boolean(getToken());

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const q = query.trim();
      const path = q
        ? `/api/v1/catalog/search?q=${encodeURIComponent(q)}&limit=40`
        : "/api/v1/catalog/search?limit=40";
      const data = await api.get<unknown>(path);
      setItems(itemsOf(data));
    } catch (err) {
      setError(err instanceof Error ? err.message : "دریافت کاتالوگ ناموفق بود");
    } finally {
      setLoading(false);
    }
  }, [query]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <Screen>
      <OfflineBanner />
      <Title badge="F-03">سفارش کمکی (F-03)</Title>
      <ErrorBox message={error} />
      <Btn label="بازگشت" tone="ghost" onPress={props.onBack} disabled={loading} />
      {!authed ? (
        <Card>
          <Text style={styles.note}>
            برای ثبت سفارش واقعی، ورود با نقش خرده‌فروش لازم است. مرور کاتالوگ عمومی در دسترس است.
          </Text>
        </Card>
      ) : null}
      <Input
        label="جستجوی کاتالوگ"
        placeholder="نام یا SKU…"
        value={query}
        onChangeText={setQuery}
        autoCapitalize="none"
      />
      <View style={styles.actions}>
        <Btn label="جستجو" onPress={() => void load()} loading={loading} />
      </View>
      {items.length === 0 ? (
        <Empty title="کالایی یافت نشد" description="عبارت دیگری امتحان کنید یا آفلاین را بررسی کنید." />
      ) : (
        <FlatList
          data={items}
          keyExtractor={(item, index) => item.id ?? item.sku ?? String(index)}
          renderItem={({ item }) => (
            <Card>
              <View style={styles.row}>
                <Text style={styles.name} numberOfLines={2}>
                  {item.name ?? item.title ?? item.sku ?? "—"}
                </Text>
                {item.price_toman != null ? (
                  <StatusChip label={`${item.price_toman.toLocaleString("fa-IR")} تومان`} tone="info" />
                ) : null}
              </View>
              {item.sku ? (
                <Text style={styles.sku} numberOfLines={1}>
                  {item.sku}
                </Text>
              ) : null}
            </Card>
          )}
        />
      )}
    </Screen>
  );
}

const styles = StyleSheet.create({
  actions: { marginBottom: spacing.md },
  note: { fontSize: 13, color: colors.textSecondary, lineHeight: 20 },
  row: { flexDirection: "row", gap: spacing.sm, alignItems: "flex-start", justifyContent: "space-between" },
  name: { flex: 1, fontSize: 14, color: colors.text, fontWeight: "500" },
  sku: { fontSize: 11, color: colors.textMuted, marginTop: 4, direction: "ltr" },
});
