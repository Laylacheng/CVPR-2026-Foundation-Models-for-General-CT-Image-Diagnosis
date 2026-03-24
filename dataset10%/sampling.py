import random
from collections import defaultdict

random.seed(42)

INPUT_LIST = "all_files.txt"
OUTPUT_LIST = "coreset_1082.txt"
TARGET_TOTAL = 1082

#dataset 正規化 
def normalize_dataset(name):
    if name.startswith("psma_"):
        return "psma_"
    if name.startswith("autoPET_fdg"):
        return "autoPET_fdg_"
    return name

#anatomy mapping 
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
        "NIH-LYMPH-MED-"
        #肺結節, 非小細胞肺癌, 肺炎, 
        #肺癌, 肺積水, 肺部腫瘤分割, 
        #COVID-19 確診, 縱隔 (Mediastinum) 淋巴結影像
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
        "Adrenal_Ki"
        #腹部器官, 腎臟分割, 肝臟血管
        #胰臟, 結腸癌, 肝臟
        #腹部淋巴結, 肝細胞癌, 
        #TACE（經導管動脈化療栓塞術）
        #動脈期, 門靜脈, 延遲期, 未接受過肝動脈栓塞化學療法
        #脾臟, 腎上腺
    ],
    "Head": [
        "IntracranialHemorrhage_INSTANCE"
        #顱內出血
    ],
    "PET": [
        "psma_",
        "autoPET_fdg_"
    #核醫(攝護腺癌), 腫瘤、炎症、淋巴瘤
    ],
    "Others": [
        "Panorama_",
        "mela_",
        "lnq"
    #全景 X 光, 黑色素瘤, 淋巴結量化
    ]
}

#給出一個dataset名稱，回傳他屬於哪個anatomy
#先從檔名識別 dataset，
#再將 dataset 對應到 anatomy，最後在兩層結構下進行分層抽樣。

def get_anatomy(dataset):
    for anatomy, prefixes in ANATOMY_MAP.items():
        for p in prefixes:
            if dataset.startswith(p):
                return anatomy
    return "Others"

#讀資料
#Adrenal_Ki /data/workspace/m1461010/datasets/data_668/train_part1/Adrenal_Ki67_Seg_001_0000.nii.gz
#這段執行完 #會是資料名稱配上路徑
data = []
with open(INPUT_LIST, "r") as f:
    for line in f:
        #strip()去掉前後空白與換行符號（\n）,split 切成 dataset + path
        #dataset = "Adrenal_Ki", path = "/data/workspace/.../Adrenal_Ki67_Seg_001_0000.nii.gz"
        dataset, path = line.strip().split(maxsplit=1)

        dataset = normalize_dataset(dataset)
        data.append((dataset, path))#存入

total = len(data)
print(f"Total files: {total}")#印出總數

# ===== 分 anatomy =====
#先把全部資料依 anatomy 分成 Chest / Abdomen / Head / PET / Others
anatomy_groups = defaultdict(list)
for dataset, path in data:
    anatomy = get_anatomy(dataset)
    anatomy_groups[anatomy].append((dataset, path))
#ex:
#("MSD_colon_", "/path/xxx.nii.gz")
#get_anatomy("MSD_colon_")得到:
#"Abdomen"

'''
anatomy_groups
{
    "Chest": [(dataset1, path1), (dataset2, path2), ...],
    "Abdomen": [...],
    "Head": [...],
    "PET": [...],
    "Others": [...]
}
'''

# 計算每個 anatomy 應該抽幾筆
anatomy_targets = {}#存每個 anatomy 的目標抽樣數
remainders = []#存小數點

#直接放一個舉例:
#Abdomen 有 4571 筆 (全部總數是 10820, 目標抽 1082)
#exact = 4571 / 10820 * 1082 ~= 457.1
for anatomy, items in anatomy_groups.items():
    exact = len(items) / total * TARGET_TOTAL
    base = int(exact) #取整數457.1 -> 457
    anatomy_targets[anatomy] = base
    remainders.append((exact - base, anatomy))#這邊會把小數點記錄下來

#補足因四捨五入損失的名額
assigned = sum(anatomy_targets.values())
need = TARGET_TOTAL - assigned

#最大餘數
#把剩下的名額優先分給小數點部分最大的 anatomy
remainders.sort(reverse=True)
for i in range(need):
    anatomy_targets[remainders[i][1]] += 1
    #假設大類有三個小類，然後我們分配完數量後有少那這時就會取出小數點
    #由多到少排序，看缺多少依序補足
    #anatomy_targets[remainders[i][1]] += 1  
    #i=0就會是小數點最高的，後面的1是remainders的第二個值也就是remainders
    #這樣就會在小數點最高的類別加一

print("\n[Anatomy allocation]")
for a in anatomy_targets:
    print(f"{a}: {len(anatomy_groups[a])} → {anatomy_targets[a]}")

#執行完前面就會先分配好每一類要取多少資料
#開始抽樣 (sampling)

selected = []#存最後被選中的樣本
selected_set = set()#selected_set

#對每個 anatomy，一次處理一類。
for anatomy, items in anatomy_groups.items():
    target_n = anatomy_targets[anatomy]

#做第二層分組：在同一個 anatomy 裡，再依不同 dataset 分開 
#(Chest 類：Chest_LIDC-IDRI-, Chest_NSCLC-Radiomics_, Chest_volume-covid)
    dataset_groups = defaultdict(list)
    for dataset, path in items:
        dataset_groups[dataset].append(path)

    #這邊會計算這個anatomy裡面每個dataset要抽幾筆
    #邏輯跟前面依樣計算數量存小數點，等計算完有差額就會從小數點最大的開始取
    dataset_targets = {}
    remainders = []

    total_a = len(items)
    #開始抽
    #len(files)這個 dataset 實際有幾筆
    for d, files in dataset_groups.items():
        exact = len(files) / total_a * target_n
        base = int(exact)
        dataset_targets[d] = base#這個 dataset 應該要抽幾筆
        remainders.append((exact - base, d))

    assigned = sum(dataset_targets.values())
    need = target_n - assigned

    remainders.sort(reverse=True)
    for i in range(need):
        dataset_targets[remainders[i][1]] += 1

    # 抽樣
    #把每一筆被選中的資料記錄下來
    for d, files in dataset_groups.items():
        k = min(dataset_targets[d], len(files))
        sampled = random.sample(files, k)
        for s in sampled:
            if s not in selected_set:
                selected.append((d, anatomy, s))
                selected_set.add(s)

# 做一個最後補齊的動作(以防沒有滿10%)
if len(selected) < TARGET_TOTAL:
    remaining = [(d, get_anatomy(d), p) for d, p in data if p not in selected_set]
    selected += random.sample(remaining, TARGET_TOTAL - len(selected))

#如果超過就隨機刪掉
if len(selected) > TARGET_TOTAL:
    selected = random.sample(selected, TARGET_TOTAL)

# 結果寫進出檔案
#dataset    anatomy    path
with open(OUTPUT_LIST, "w") as f:
    for d, a, p in selected:
        f.write(f"{d}\t{a}\t{p}\n")

print(f"\nFinal selected: {len(selected)}")
print(f"Saved to {OUTPUT_LIST}")
