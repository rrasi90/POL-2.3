const PACKAGING_UNIT_LABELS: Readonly<Record<string, string>> = {
  CARTON: "کارتن",
  CASE: "کارتن",
  BOX: "جعبه",
  PACK: "بسته",
  PIECE: "عدد",
  UNIT: "واحد",
  KG: "کیلوگرم",
  GRAM: "گرم",
  LITER: "لیتر",
  L: "لیتر",
  ML: "میلی‌لیتر",
  G: "گرم",
  EA: "عدد",
  PC: "عدد",
  BUNDLE: "دسته",
  BAG: "کیسه",
  BOTTLE: "بطری",
  CAN: "قوطی",
  METER: "متر",
  M: "متر",
  DOZEN: "دوجین",
  PAIR: "جفت",
  ROLL: "رول",
  SET: "ست",
  CRATE: "سبد",
  SACK: "گونی",
  PALLET: "پالت",
};

export function formatPackagingUnit(value: string | null | undefined): string {
  if (!value || !value.trim()) return "واحد نامشخص";
  const unit = value.trim();
  const normalized = unit.toUpperCase();
  if (PACKAGING_UNIT_LABELS[normalized]) return PACKAGING_UNIT_LABELS[normalized];
  if (/[\u0600-\u06FF]/.test(unit)) return unit;
  return "واحد دیگر";
}

const FRESHNESS_LABELS: Readonly<Record<string, string>> = {
  FRESH: "تازه",
  STALE: "نیازمند بررسی",
  EXPIRED: "منقضی‌شده",
};

export function formatFreshnessStatus(value: string | null | undefined): string {
  if (!value) return "نامشخص";
  return FRESHNESS_LABELS[value.toUpperCase()] ?? "وضعیت تازگی نامشخص";
}
