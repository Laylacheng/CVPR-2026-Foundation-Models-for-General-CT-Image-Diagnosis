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
# 1. pretty_counts.txt

Records the number of each dataset (prefix + count)

Used to "identify dataset names", the basis for subsequent sampling ratios

# 2. build_file_list.py Organizes raw data → Creates a standard list

Scans train_part1, train_part2

Determines which file belongs to each file based on pretty_counts.txt Dataset

Generates a unified format

Output: all_files.txt

Content format: dataset_name file_path

# 3. all_files.txt An "index list" of all data

Each line = one data entry

The dataset + path has been organized

It is the input for sampling

# 4. sampling.py Core sampling logic (Anatomy-aware Sampling)

Dataset normalization

Merge subclasses such as psma and autoPET

Divide into anatomy (first level)

Chest / Abdomen / Head / PET / Others

Calculate how many samples to take from each anatomy

Distribute proportionally

Patch using the maximum remainder method

Re-divide into datasets within the anatomy (second level)

Maintain dataset proportions

Random sampling

Patch or reduce and ensure total = 1082

# 5. coreset_1082.txt Final sampling result

Format:

dataset anatomy    file_path

<img width="821" height="333" alt="image" src="https://github.com/user-attachments/assets/d52a6aa5-132e-4baf-8aed-808e43d1bf74" />
