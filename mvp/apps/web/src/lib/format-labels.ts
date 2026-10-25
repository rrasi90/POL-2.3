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
  BUNDLE: "دسته",
  BAG: "کیسه",
  BOTTLE: "بطری",
  CAN: "قوطی",
};

export function formatPackagingUnit(value: string | null | undefined): string {
  if (!value) return "واحد نامشخص";
  return PACKAGING_UNIT_LABELS[value.toUpperCase()] ?? "واحد دیگر";
}
