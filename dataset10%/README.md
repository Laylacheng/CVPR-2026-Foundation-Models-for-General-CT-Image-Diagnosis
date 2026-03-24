# Anatomy-aware Sampling Pipeline

pretty_counts.txt
        ↓
build_file_list.py
        ↓
all_files.txt
        ↓
sampling.py
        ↓
coreset_1082.txt


""
ls train_part1 train_part2 | grep ".nii" \
| sed 's/[0-9].*//' \
| sort \
| uniq -c \
| sort -nr > pretty_counts.txt 
""

# 1.pretty_counts.txt

紀錄每個 dataset 的數量（prefix + count）

用來「辨識 dataset 名稱」，後續抽樣比例的依據


# 2.build_file_list.py 整理原始資料 → 建立標準清單

掃描 train_part1、train_part2

根據 pretty_counts.txt 判斷每個檔案屬於哪個 dataset

產生統一格式


輸出：all_files.txt

內容格式：dataset_name  file_path


# 3.all_files.txt 所有資料的「索引清單」

每一行 = 一筆資料

已經整理好 dataset + path

是 sampling 的輸入


# 4.sampling.py 核心抽樣邏輯（Anatomy-aware Sampling）

dataset 正規化

合併 psma、autoPET 等子類


分成 anatomy（第一層）

Chest / Abdomen / Head / PET / Others

計算每個 anatomy 要抽多少

依比例分配

用最大餘數法補齊


在 anatomy 內再分 dataset（第二層）

保持 dataset 比例

隨機抽樣

補齊或減少 並確保總數 = 1082


# 5.coreset_1082.txt 最終抽樣結果

格式：

dataset    anatomy    file_path
