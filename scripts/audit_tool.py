import os
import sys
import json
import re
from collections import Counter

REPO_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def inventory_repo():
    exts = Counter()
    dirs = Counter()
    total_files = 0
    total_bytes = 0
    file_list = []

    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        rel_dir = os.path.relpath(dirpath, REPO_ROOT)
        parts = rel_dir.split(os.sep)
        top = parts[0] if parts and parts[0] != '.' else 'root'
        if any(p.startswith('.') for p in parts):
            continue
        for f in filenames:
            total_files += 1
            fp = os.path.join(dirpath, f)
            sz = os.path.getsize(fp)
            total_bytes += sz
            _, ext = os.path.splitext(f)
            exts[ext.lower()] += 1
            dirs[top] += 1
            file_list.append((os.path.relpath(fp, REPO_ROOT).replace('\\', '/'), sz))

    print(f"Total files: {total_files}")
    print(f"Total size: {total_bytes:,} bytes")
    print("\nBy Extension:")
    for ext, cnt in exts.most_common():
        print(f"  {ext or '[none]':12}: {cnt}")
    print("\nBy Top-level Dir:")
    for d, cnt in sorted(dirs.items()):
        print(f"  {d:32}: {cnt}")
    return file_list

if __name__ == '__main__':
    inventory_repo()
