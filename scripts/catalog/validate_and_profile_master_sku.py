"""
POL Master SKU Import Validation and Profiling Utility
Profiles the raw dataset: Master SKU/backup_no_images.json
Calculates exact reproducible metrics required by POL Master Prompt.
"""

import json
import os
import re
import sys
from collections import Counter

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def normalize_persian_text(text: str) -> str:
    """Normalizes Persian characters, removes diacritics, and fixes spacing."""
    if not text:
        return ""
    # Replace Arabic letters with Persian equivalents
    text = text.replace('ي', 'ی').replace('ك', 'ک').replace('ة', 'ه')
    # Remove Arabic diacritics (fatha, damma, kasra, tanwin, sukun, shadda)
    text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
    # Convert half-space (ZWNJ) and multiple spaces to a single space
    text = text.replace('\u200c', ' ')
    text = re.sub(r'\s+', ' ', text)
    # Convert Persian/Arabic digits to Latin digits
    persian_arabic_digits = '۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩'
    latin_digits = '01234567890123456789'
    trans_table = str.maketrans(persian_arabic_digits, latin_digits)
    text = text.translate(trans_table)
    return text.strip().lower()

def profile_dataset(file_path: str):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None

    print(f"Loading dataset from: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_records = len(data)
    print(f"Total records in dataset: {total_records}")

    external_ids = Counter()
    missing_barcode = 0
    non_empty_barcode = 0
    missing_brand = 0
    missing_category = 0
    missing_subcategory = 0
    missing_net_weight = 0
    missing_packaging_unit = 0
    missing_price = 0
    missing_stock = 0
    missing_rating = 0
    missing_reviews_count = 0

    raw_titles = []
    norm_titles = []
    categories = Counter()
    subcategories = Counter()
    brands = Counter()

    for r in data:
        ext_id = r.get('dkpId')
        if ext_id is not None:
            external_ids[ext_id] += 1
        else:
            external_ids["MISSING"] += 1

        bc = r.get('barcode')
        if bc is None or str(bc).strip() == '':
            missing_barcode += 1
        else:
            non_empty_barcode += 1

        br = r.get('brand')
        if br is None or str(br).strip() == '':
            missing_brand += 1
        else:
            brands[str(br).strip()] += 1

        cat = r.get('category')
        if cat is None or str(cat).strip() == '':
            missing_category += 1
        else:
            categories[str(cat).strip()] += 1

        subcat = r.get('subcategory')
        if subcat is None or str(subcat).strip() == '':
            missing_subcategory += 1
        else:
            subcategories[str(subcat).strip()] += 1

        nw = r.get('netWeight')
        if nw is None or str(nw).strip() == '':
            missing_net_weight += 1

        pu = r.get('packagingUnit')
        if pu is None or str(pu).strip() == '':
            missing_packaging_unit += 1

        pr = r.get('priceRials')
        if pr is None or str(pr).strip() == '':
            missing_price += 1

        st = r.get('stockCount')
        if st is None or str(st).strip() == '':
            missing_stock += 1

        rt = r.get('rating')
        if rt is None or str(rt).strip() == '':
            missing_rating += 1

        rc = r.get('reviewsCount')
        if rc is None or str(rc).strip() == '':
            missing_reviews_count += 1

        raw_t = r.get('titleFa', '').strip()
        if raw_t:
            raw_titles.append(raw_t)
            norm_titles.append(normalize_persian_text(raw_t))

    unique_ext_ids = len([k for k in external_ids.keys() if k != "MISSING"])
    duplicate_ext_ids = len([k for k, v in external_ids.items() if v > 1 and k != "MISSING"])

    raw_counts = Counter(raw_titles)
    raw_dups = {k: v for k, v in raw_counts.items() if v > 1}
    raw_records_in_dups = sum(raw_dups.values())
    raw_unique_dups = len(raw_dups)

    norm_counts = Counter(norm_titles)
    norm_dups = {k: v for k, v in norm_counts.items() if v > 1}
    norm_records_in_dups = sum(norm_dups.values())
    norm_unique_dups = len(norm_dups)

    summary = {
        "dataset_name": os.path.basename(file_path),
        "total_records": total_records,
        "unique_external_ids": unique_ext_ids,
        "duplicate_external_ids": duplicate_ext_ids,
        "non_empty_barcode": non_empty_barcode,
        "empty_barcode": missing_barcode,
        "empty_barcode_pct": round(missing_barcode / total_records * 100, 2),
        "missing_brand": missing_brand,
        "missing_category": missing_category,
        "missing_subcategory": missing_subcategory,
        "missing_net_weight": missing_net_weight,
        "missing_net_weight_pct": round(missing_net_weight / total_records * 100, 2),
        "missing_packaging_unit": missing_packaging_unit,
        "missing_packaging_unit_pct": round(missing_packaging_unit / total_records * 100, 2),
        "missing_price": missing_price,
        "missing_stock": missing_stock,
        "missing_rating": missing_rating,
        "missing_reviews_count": missing_reviews_count,
        "raw_unique_titles": len(raw_counts),
        "raw_duplicate_unique_titles": raw_unique_dups,
        "raw_records_belonging_to_duplicate_titles": raw_records_in_dups,
        "normalized_unique_titles": len(norm_counts),
        "normalized_duplicate_unique_titles": norm_unique_dups,
        "normalized_records_belonging_to_duplicate_titles": norm_records_in_dups,
        "distinct_brands_count": len(brands),
        "distinct_categories_count": len(categories),
        "distinct_subcategories_count": len(subcategories),
        "category_distribution": dict(categories.most_common(10)),
        "subcategory_distribution": dict(subcategories.most_common(15)),
        "top_brands": dict(brands.most_common(15))
    }

    print("\n--- Summary Audit Report ---")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dataset_path = os.path.join(base_dir, "Master SKU", "backup_no_images.json")
    profile_dataset(dataset_path)
