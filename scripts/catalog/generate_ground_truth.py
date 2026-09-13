"""
Generate Master SKU Ground Truth Machine-Readable JSON
Source: Master SKU/backup_no_images.json
Target: 08_DATA/Master_SKU_Ground_Truth.json
"""

import json
import os
import re
import sys
from collections import Counter

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATASET_PATH = os.path.join(REPO_ROOT, 'Master SKU', 'backup_no_images.json')
OUTPUT_PATH = os.path.join(REPO_ROOT, '08_DATA', 'Master_SKU_Ground_Truth.json')

def normalize_title(t):
    if not t:
        return ""
    t = t.replace('ي', 'ی').replace('ك', 'ک').replace('ة', 'ه')
    t = re.sub(r'[\u064B-\u065F\u0670]', '', t)
    t = t.replace('\u200c', ' ')
    t = re.sub(r'\s+', ' ', t)
    persian_arabic_digits = '۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩'
    latin_digits = '01234567890123456789'
    t = t.translate(str.maketrans(persian_arabic_digits, latin_digits))
    return t.strip().lower()

def main():
    print(f"Reading dataset: {DATASET_PATH}")
    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        records = json.load(f)

    total_records = len(records)
    print(f"Total records parsed: {total_records}")

    dkp_ids = Counter()
    empty_barcodes = 0
    non_empty_barcodes = 0
    missing_brand = 0
    missing_category = 0
    missing_subcategory = 0
    missing_net_weight = 0
    missing_packaging_unit = 0
    missing_price = 0
    missing_stock = 0
    missing_rating = 0
    missing_reviews = 0

    raw_titles = []
    norm_titles = []
    brands = Counter()
    categories = Counter()
    subcategories = Counter()

    for r in records:
        dkp = r.get('dkpId')
        if dkp is not None:
            dkp_ids[dkp] += 1

        bc = str(r.get('barcode', '')).strip()
        if not bc or bc == 'None' or bc == '0':
            empty_barcodes += 1
        else:
            non_empty_barcodes += 1

        br = str(r.get('brand', '')).strip()
        if not br or br == 'None':
            missing_brand += 1
        else:
            brands[br] += 1

        cat = str(r.get('category', '')).strip()
        if not cat or cat == 'None':
            missing_category += 1
        else:
            categories[cat] += 1

        subcat = str(r.get('subcategory', '')).strip()
        if not subcat or subcat == 'None':
            missing_subcategory += 1
        else:
            subcategories[subcat] += 1

        nw = r.get('netWeight')
        if nw is None or str(nw).strip() == '' or str(nw).strip() == 'None':
            missing_net_weight += 1

        pu = r.get('packagingUnit')
        if pu is None or str(pu).strip() == '' or str(pu).strip() == 'None':
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
            missing_reviews += 1

        t = r.get('titleFa', '').strip()
        if t:
            raw_titles.append(t)
            norm_titles.append(normalize_title(t))

    raw_counts = Counter(raw_titles)
    raw_dups = {k: v for k, v in raw_counts.items() if v > 1}
    raw_records_in_dups = sum(raw_dups.values())
    raw_unique_dups = len(raw_dups)

    norm_counts = Counter(norm_titles)
    norm_dups = {k: v for k, v in norm_counts.items() if v > 1}
    norm_records_in_dups = sum(norm_dups.values())
    norm_unique_dups = len(norm_dups)

    ground_truth = {
        "dataset_metadata": {
            "source_file": "Master SKU/backup_no_images.json",
            "classification": "Imported Reference / Identity Dataset",
            "not_operational_inventory": True,
            "not_operational_price": True,
            "not_pol_reputation": True,
            "generated_at": "2026-09-11T21:15:00Z",
            "generator_script": "scripts/catalog/generate_ground_truth.py"
        },
        "metrics": {
            "total_records": total_records,
            "unique_dkp_id": len(dkp_ids),
            "duplicate_dkp_id": sum(1 for v in dkp_ids.values() if v > 1),
            "empty_barcode": empty_barcodes,
            "empty_barcode_percentage": round(empty_barcodes / total_records * 100, 2),
            "non_empty_barcode": non_empty_barcodes,
            "missing_brand": missing_brand,
            "missing_category": missing_category,
            "missing_subcategory": missing_subcategory,
            "missing_net_weight": missing_net_weight,
            "missing_net_weight_percentage": round(missing_net_weight / total_records * 100, 2),
            "missing_packaging_unit": missing_packaging_unit,
            "missing_packaging_unit_percentage": round(missing_packaging_unit / total_records * 100, 2),
            "missing_price": missing_price,
            "missing_stock": missing_stock,
            "missing_rating": missing_rating,
            "missing_reviews_count": missing_reviews,
            "raw_unique_titles": len(raw_counts),
            "raw_duplicate_unique_titles": raw_unique_dups,
            "raw_duplicate_records": raw_records_in_dups,
            "normalized_unique_titles": len(norm_counts),
            "normalized_duplicate_unique_titles": norm_unique_dups,
            "normalized_duplicate_records": norm_records_in_dups,
            "distinct_brands_count": len(brands),
            "distinct_categories_count": len(categories),
            "distinct_subcategories_count": len(subcategories)
        },
        "top_categories": dict(categories.most_common(10)),
        "top_brands": dict(brands.most_common(15))
    }

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(ground_truth, f, indent=2, ensure_ascii=False)

    print(f"Ground Truth successfully written to: {OUTPUT_PATH}")
    print(f"Verified Records: {total_records}")
    print(f"Verified Empty Barcodes: {empty_barcodes}")
    print(f"Verified Raw Unique Titles: {len(raw_counts)}")
    print(f"Verified Normalized Unique Titles: {len(norm_counts)}")

if __name__ == '__main__':
    main()
