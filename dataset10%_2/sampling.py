import random
import csv
from collections import defaultdict, Counter

# =========================================================
# 0. 基本設定
# =========================================================

random.seed(42)

INPUT_LIST = "all_files.txt"
OUTPUT_LIST = "coreset_1082_equal_dataset.txt"
SUMMARY_CSV = "coreset_1082_equal_dataset_summary.csv"

TARGET_TOTAL = 1082

# =========================================================
# 1. 手動指定五大 anatomy 抽樣數量
# =========================================================

ANATOMY_TARGETS = {
    "Abdomen": 532,
    "Chest": 250,
    "Head": 100,
    "PET": 100,
    "Others": 100,
}

assert sum(ANATOMY_TARGETS.values()) == TARGET_TOTAL, (
    f"ANATOMY_TARGETS sum = {sum(ANATOMY_TARGETS.values())}, "
    f"but TARGET_TOTAL = {TARGET_TOTAL}"
)

# =========================================================
# 2. dataset 正規化
# =========================================================

def normalize_dataset(name):
    """
    將同系列 dataset 統一命名，避免同一來源被切太細。
    """
    if name.startswith("psma_"):
        return "psma_"

    if name.startswith("autoPET_fdg"):
        return "autoPET_fdg_"

    return name


# =========================================================
# 3. anatomy mapping
# =========================================================

ANATOMY_MAP = {
    "Chest": [
        "Chest_LIDC-IDRI-",
        "Chest_NSCLC-Radiomics_",
        "Chest_volume-covid",
        "Chest_NSCLC-Radiogenomics_R",
        "Chest_NSCLCPleuralEffusion_",
        "Chest_MSD_lung_",
        "MSD_lung_",
        "Chest_coronacases_",
        "NIH-LYMPH-MED-",
    ],

    "Abdomen": [
        "amos_",
        "KiTS",
        "MSD_hepaticvessel_",
        "MSD_pancreas_",
        "MSD_colon_",
        "MSD_liver_",
        "NIH-LYMPH-ABD-",
        "HCC_",
        "WAWTACE_Arterial_",
        "WAWTACE_Portal_",
        "WAWTACE_Delayed_",
        "WAWTACE_Naive_",
        "MSD_spleen_",
        "Adrenal_Ki",
    ],

    "Head": [
        "IntracranialHemorrhage_INSTANCE",
    ],

    "PET": [
        "psma_",
        "autoPET_fdg_",
    ],

    "Others": [
        "Panorama_",
        "mela_",
        "lnq",
    ],
}


def get_anatomy(dataset):
    """
    根據 dataset prefix 判斷 anatomy 大類。
    """
    for anatomy, prefixes in ANATOMY_MAP.items():
        for p in prefixes:
            if dataset.startswith(p):
                return anatomy

    return "Others"


# =========================================================
# 4. 讀取 all_files.txt
# =========================================================

def read_all_files(input_list):
    """
    讀取 all_files.txt。
    每一行格式：
    dataset path
    """
    data = []

    with open(input_list, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            dataset, path = line.split(maxsplit=1)
            dataset = normalize_dataset(dataset)

            data.append((dataset, path))

    return data


# =========================================================
# 5. 平均分配函式
# =========================================================

def allocate_equal_with_capacity(dataset_groups, target_n):
    """
    在某個 anatomy 裡面，將 target_n 盡量平均分給每個 dataset。

    1. 每個子 dataset 先盡量平均拿名額。
    2. 如果某個 dataset 數量不足，就抽它全部。
    3. 剩下的名額再平均分給其他還有資料的 dataset。
    """

    datasets = sorted(dataset_groups.keys())
    capacities = {d: len(dataset_groups[d]) for d in datasets}

    total_available = sum(capacities.values())

    if total_available < target_n:
        raise ValueError(
            f"Available files = {total_available}, "
            f"but target_n = {target_n}. Not enough files."
        )

    allocation = {d: 0 for d in datasets}
    remaining_target = target_n
    active = set(datasets)

    while remaining_target > 0 and active:
        active_list = sorted(active)
        n_active = len(active_list)

        base = remaining_target // n_active
        remainder = remaining_target % n_active

        if base == 0:
            for d in active_list:
                if remaining_target == 0:
                    break

                if allocation[d] < capacities[d]:
                    allocation[d] += 1
                    remaining_target -= 1

            break

        used_this_round = 0
        full_datasets = []

        for idx, d in enumerate(active_list):
            extra = 1 if idx < remainder else 0
            want = base + extra

            available_room = capacities[d] - allocation[d]
            give = min(want, available_room)

            allocation[d] += give
            used_this_round += give

            if allocation[d] >= capacities[d]:
                full_datasets.append(d)

        remaining_target -= used_this_round

        for d in full_datasets:
            active.remove(d)

        if used_this_round == 0:
            break

    if sum(allocation.values()) != target_n:
        raise RuntimeError(
            f"Allocation failed. "
            f"Got {sum(allocation.values())}, expected {target_n}."
        )

    return allocation


# =========================================================
# 6. 主要 sampling 流程
# =========================================================

def main():
    data = read_all_files(INPUT_LIST)

    total = len(data)
    print(f"Total files: {total}")

    # -----------------------------------------------------
    # 第一層：依 anatomy 分組
    # -----------------------------------------------------
    anatomy_groups = defaultdict(list)

    for dataset, path in data:
        anatomy = get_anatomy(dataset)
        anatomy_groups[anatomy].append((dataset, path))

    print("\n[Available files by anatomy]")
    for anatomy in ["Abdomen", "Chest", "Head", "PET", "Others"]:
        print(f"{anatomy}: {len(anatomy_groups[anatomy])}")

    # -----------------------------------------------------
    # 檢查每個 anatomy 是否足夠抽
    # -----------------------------------------------------
    for anatomy, target_n in ANATOMY_TARGETS.items():
        available_n = len(anatomy_groups[anatomy])

        if available_n < target_n:
            raise ValueError(
                f"{anatomy} only has {available_n} files, "
                f"but target is {target_n}."
            )

    print("\n[Anatomy target allocation]")
    for anatomy, target_n in ANATOMY_TARGETS.items():
        print(f"{anatomy}: {len(anatomy_groups[anatomy])} → {target_n}")

    # -----------------------------------------------------
    # 第二層：每個 anatomy 裡面，dataset 平均抽
    # -----------------------------------------------------
    selected = []
    selected_set = set()
    summary_rows = []

    for anatomy, target_n in ANATOMY_TARGETS.items():
        items = anatomy_groups[anatomy]

        dataset_groups = defaultdict(list)

        for dataset, path in items:
            dataset_groups[dataset].append(path)

        dataset_targets = allocate_equal_with_capacity(
            dataset_groups=dataset_groups,
            target_n=target_n
        )

        print(f"\n[{anatomy}] Dataset equal allocation")
        for dataset in sorted(dataset_targets.keys()):
            available = len(dataset_groups[dataset])
            target = dataset_targets[dataset]
            print(f"{dataset}: {available} → {target}")

        for dataset in sorted(dataset_groups.keys()):
            files = dataset_groups[dataset]
            k = dataset_targets[dataset]

            sampled = random.sample(files, k)

            for path in sampled:
                if path not in selected_set:
                    selected.append((dataset, anatomy, path))
                    selected_set.add(path)

            summary_rows.append({
                "anatomy": anatomy,
                "dataset": dataset,
                "available_count": len(files),
                "sampled_count": k,
            })

    # -----------------------------------------------------
    # 最後檢查
    # -----------------------------------------------------
    if len(selected) != TARGET_TOTAL:
        raise RuntimeError(
            f"Final selected count = {len(selected)}, "
            f"but expected {TARGET_TOTAL}."
        )

    # -----------------------------------------------------
    # 輸出 coreset txt
    # -----------------------------------------------------
    with open(OUTPUT_LIST, "w", encoding="utf-8") as f:
        for dataset, anatomy, path in selected:
            f.write(f"{dataset}\t{anatomy}\t{path}\n")

    # -----------------------------------------------------
    # 輸出 summary csv
    # -----------------------------------------------------
    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "anatomy",
            "dataset",
            "available_count",
            "sampled_count",
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in summary_rows:
            writer.writerow(row)

    # -----------------------------------------------------
    # 印出 final summary
    # -----------------------------------------------------
    print("\n[Final summary]")
    print(f"Final selected: {len(selected)}")
    print(f"Saved to: {OUTPUT_LIST}")
    print(f"Saved summary to: {SUMMARY_CSV}")

    anatomy_counter = Counter([a for _, a, _ in selected])

    print("\n[Selected count by anatomy]")
    for anatomy in ["Abdomen", "Chest", "Head", "PET", "Others"]:
        print(f"{anatomy}: {anatomy_counter[anatomy]}")

    dataset_counter = Counter([(a, d) for d, a, _ in selected])

    print("\n[Selected count by dataset]")
    for anatomy in ["Abdomen", "Chest", "Head", "PET", "Others"]:
        print(f"\n{anatomy}")
        for (a, d), count in sorted(dataset_counter.items()):
            if a == anatomy:
                print(f"  {d}: {count}")


if __name__ == "__main__":
    main()