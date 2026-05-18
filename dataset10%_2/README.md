# Anatomy-aware Sampling Pipeline
python count_groups.py  (統計每個資料集 prefix 數量)

        ↓
        
pretty_counts.txt (用途: 之後 build_file_list.py 會用這些 prefix 判斷每個 .nii.gz 檔案屬於哪個 dataset。)

        ↓
        
build_file_list.py

        ↓
        
all_files.txt

        ↓
        
sampling.py (第一層：手動指定五大 anatomy 數量 ， 第二層：每個 anatomy 裡面的 dataset 平均抽樣)

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

第一層：手動指定五大 anatomy 數量

ANATOMY_TARGETS = {
    "Abdomen": 532,
    "Chest": 250,
    "Head": 100,
    "PET": 100,
    "Others": 100,
}

第二層：每個 anatomy 裡面的 dataset 平均抽樣


