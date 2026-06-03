# Anatomy-aware Sampling Pipeline

```
python count_groups.py  (count the number of files per dataset prefix)

↓

pretty_counts.txt  (used by build_file_list.py to identify which dataset each .nii.gz file belongs to, based on prefix)

↓

build_file_list.py

↓

all_files.txt

↓

sampling.py  (Layer 1: manually specify target counts for five anatomy groups; Layer 2: uniform sampling across datasets within each anatomy group)

↓

coreset_1082.txt
```

```bash
ls train_part1 train_part2 | grep ".nii" \
| sed 's/[0-9].*//' \
| sort \
| uniq -c \
| sort -nr > pretty_counts.txt
```

---

## 1. pretty_counts.txt

Records the file count per dataset (prefix + count).

Used to **identify dataset names** and serves as the basis for determining sampling proportions.

---

## 2. build_file_[list.py](http://list.py) — Organize raw data → Build a standardized file list

- Scans `train_part1` and `train_part2`
- Uses `pretty_counts.txt` to determine which dataset each file belongs to
- Produces a unified format

**Output:** `all_files.txt`

**Format:** `dataset_name  file_path`

---

## 3. all_files.txt — Index list of all data

- Each line = one data entry
- Already organized with dataset name and file path
- Serves as the input to the sampling step

---

## 4. [sampling.py](http://sampling.py) — Core sampling logic (Anatomy-aware Sampling)

**Layer 1:** Manually specify target counts for five anatomy groups

```python
ANATOMY_TARGETS = {
    "Abdomen": 532,
    "Chest": 250,
    "Head": 100,
    "PET": 100,
    "Others": 100,
}
```

**Layer 2:** Uniform sampling across datasets within each anatomy group
