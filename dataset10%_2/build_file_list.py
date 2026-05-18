import os

ROOTS = ["train_part1", "train_part2"]
OUTPUT = "all_files.txt"
PREFIX_FILE = "pretty_counts.txt"

# 讀取 pretty_counts.txt 裡的標準 prefix
prefixes = []#空list
with open(PREFIX_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()#把每一行前後空白、換行拿掉。
        if not line:
            continue #空白跳過
        parts = line.split()  #2350 amos_ 會變成：["2350", "amos_"]
        if len(parts) < 2:
            continue
        prefix = parts[1]
        if prefix == "train_part":
            continue
        prefixes.append(prefix)#加進list

# 最長的 prefix 要先比對(避免KiTS被Ki之類的吃掉)
prefixes = sorted(prefixes, key=len, reverse=True)

all_items = [] #(dataset, full_path)
unknowns = []

#os.listdir(root)  列出這個資料夾下所有檔名。
for root in ROOTS:
    for fname in sorted(os.listdir(root)):
        ###################用 pretty_counts.txt 裡的每個 prefix，一個一個去比對目前這個檔名開頭是不是符合。
        #exfname = "MSD_colon_003.nii.gz",,, fname.startswith("amos_") → 否, fname.startswith("MSD_colon_") → 是
        dataset = None
        for p in prefixes:
            if fname.startswith(p):
                dataset = p
                break

        #轉成絕對路徑        
        full_path = os.path.abspath(os.path.join(root, fname))

        #找不到對應 prefix 就丟到 UNKNOWN
        if dataset is None:
            dataset = "UNKNOWN"
            unknowns.append(full_path)

        all_items.append((dataset, full_path))

#這裡是把剛剛整理好的 (dataset, path) 寫到檔案(txt)裡。
#每一行會變成：dataset path
with open(OUTPUT, "w", encoding="utf-8") as f:
    for dataset, path in all_items:
        f.write(f"{dataset} {path}\n")

print(f"Saved {len(all_items)} entries to {OUTPUT}")

if unknowns:
    print(f"UNKNOWN files: {len(unknowns)}")
    for x in unknowns[:30]:
        print(x)
else:
    print("No UNKNOWN files found.")
