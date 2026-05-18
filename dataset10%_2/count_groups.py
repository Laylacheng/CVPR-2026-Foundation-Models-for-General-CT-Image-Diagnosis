from pathlib import Path
from collections import Counter
import re

root = Path("/data/workspace/m1461010/datasets/data_668")
files = list(root.glob("train_part1/*.nii.gz")) + list(root.glob("train_part2/*.nii.gz"))

def extract_group(name: str) -> str:
    # 去掉副檔名
    name = name.replace(".nii.gz", "")

    # 去掉常見影像通道尾碼，例如 _0000
    name = re.sub(r"_\d{4}$", "", name)

    # 去掉尾端純數字編號：支援 _123 或 -123
    name = re.sub(r"([_-])\d+$", "", name)

    return name

counter = Counter()

for f in files:
    group = extract_group(f.name)
    counter[group] += 1

for group, count in counter.most_common():
    print(f"{count:5d}  {group}")
