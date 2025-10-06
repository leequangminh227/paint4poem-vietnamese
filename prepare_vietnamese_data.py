"""
Script để chuyển đổi dữ liệu thơ tiếng Việt sang định dạng AttnGAN/MirrorGAN
"""
import pandas as pd
import os
import shutil
from pathlib import Path

# Đường dẫn
SOURCE_DIR = 'data/Paint4Poem-Zikai-poem-subset-20251006T041948Z-1-001/Paint4Poem-Zikai-poem-subset'
OUTPUT_DIR = 'data/vietnamese_poems'
CSV_FILE = os.path.join(SOURCE_DIR, 'vie_poem.csv')
IMAGE_DIR = os.path.join(SOURCE_DIR, 'images')

# Tỷ lệ chia train/test
TRAIN_RATIO = 0.8

def create_directory_structure():
    """Tạo cấu trúc thư mục cần thiết"""
    dirs = [
        os.path.join(OUTPUT_DIR, 'train'),
        os.path.join(OUTPUT_DIR, 'test'),
        os.path.join(OUTPUT_DIR, 'images')
    ]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    print(f"✓ Đã tạo cấu trúc thư mục tại {OUTPUT_DIR}")

def read_data():
    """Đọc dữ liệu từ CSV"""
    print(f"Đọc dữ liệu từ {CSV_FILE}...")
    df = pd.read_csv(CSV_FILE)
    
    # Đổi tên cột cho dễ làm việc
    df.columns = ['PoemID', 'ChineseText', 'VietnameseText', 'ImageID']
    
    print(f"✓ Đã đọc {len(df)} bài thơ")
    return df

def copy_images(df):
    """Copy ảnh sang thư mục output"""
    print("\nCopy ảnh...")
    copied = 0
    missing = []
    
    for idx, row in df.iterrows():
        image_id = row['ImageID']
        
        # Tìm file ảnh (có thể là .PNG hoặc .jpg)
        source_path = None
        for ext in ['.PNG', '.jpg', '.jpeg', '.png', '.JPG', '.JPEG']:
            potential_path = os.path.join(IMAGE_DIR, f"{image_id}{ext}")
            if os.path.exists(potential_path):
                source_path = potential_path
                break
        
        if source_path:
            dest_path = os.path.join(OUTPUT_DIR, 'images', f"{image_id}.jpg")
            if not os.path.exists(dest_path):
                shutil.copy2(source_path, dest_path)
            copied += 1
            if copied % 100 == 0:
                print(f"  Đã copy {copied} ảnh...")
        else:
            missing.append(image_id)
    
    print(f"✓ Đã copy {copied} ảnh")
    if missing:
        print(f"⚠ Thiếu {len(missing)} ảnh: {missing[:5]}..." if len(missing) > 5 else f"⚠ Thiếu ảnh: {missing}")
    
    return missing

def create_text_files(df, missing_images):
    """Tạo file text cho mỗi bài thơ"""
    print("\nTạo file text...")
    
    # Loại bỏ các bài thơ không có ảnh
    df_valid = df[~df['ImageID'].isin(missing_images)].copy()
    print(f"Số bài thơ hợp lệ: {len(df_valid)}")
    
    # Shuffle và chia train/test
    df_valid = df_valid.sample(frac=1, random_state=42).reset_index(drop=True)
    train_size = int(len(df_valid) * TRAIN_RATIO)
    
    df_train = df_valid[:train_size]
    df_test = df_valid[train_size:]
    
    print(f"  Train: {len(df_train)} bài thơ")
    print(f"  Test: {len(df_test)} bài thơ")
    
    # Tạo file text cho train set
    for idx, row in df_train.iterrows():
        image_id = row['ImageID']
        poem = row['VietnameseText']
        
        text_file = os.path.join(OUTPUT_DIR, 'train', f"{image_id}.txt")
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(poem)
    
    # Tạo file text cho test set
    for idx, row in df_test.iterrows():
        image_id = row['ImageID']
        poem = row['VietnameseText']
        
        text_file = os.path.join(OUTPUT_DIR, 'test', f"{image_id}.txt")
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(poem)
    
    print(f"✓ Đã tạo file text cho train và test")
    
    return df_train, df_test

def create_filenames_list(df_train, df_test):
    """Tạo file danh sách tên file"""
    print("\nTạo file danh sách...")
    
    # Train filenames
    train_file = os.path.join(OUTPUT_DIR, 'train', 'filenames.txt')
    with open(train_file, 'w', encoding='utf-8') as f:
        for image_id in df_train['ImageID']:
            f.write(f"{image_id}\n")
    
    # Test filenames
    test_file = os.path.join(OUTPUT_DIR, 'test', 'filenames.txt')
    with open(test_file, 'w', encoding='utf-8') as f:
        for image_id in df_test['ImageID']:
            f.write(f"{image_id}\n")
    
    print(f"✓ Đã tạo filenames.txt cho train và test")

def create_example_filenames(df_test):
    """Tạo file example_filenames.txt với một vài ví dụ từ test set"""
    example_file = os.path.join(OUTPUT_DIR, 'example_filenames.txt')
    
    # Lấy 10 ví dụ ngẫu nhiên
    examples = df_test.sample(n=min(10, len(df_test)), random_state=42)
    
    with open(example_file, 'w', encoding='utf-8') as f:
        for image_id in examples['ImageID']:
            f.write(f"test/{image_id}\n")
    
    print(f"✓ Đã tạo example_filenames.txt với {len(examples)} ví dụ")

def create_class_info():
    """Tạo file class_info.pickle (đơn giản, chỉ 1 class)"""
    import pickle
    
    class_info_file = os.path.join(OUTPUT_DIR, 'class_info.pickle')
    
    # Tạo class_info đơn giản với 1 class "poem"
    class_info = {
        0: ['poem']  # class_id: [class_name]
    }
    
    with open(class_info_file, 'wb') as f:
        pickle.dump(class_info, f)
    
    print(f"✓ Đã tạo class_info.pickle")

def create_summary(df, df_train, df_test):
    """Tạo file tóm tắt thông tin dataset"""
    summary_file = os.path.join(OUTPUT_DIR, 'dataset_info.txt')
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("=== THÔNG TIN DATASET THƠ TIẾNG VIỆT ===\n\n")
        f.write(f"Tổng số bài thơ: {len(df)}\n")
        f.write(f"Số bài thơ train: {len(df_train)}\n")
        f.write(f"Số bài thơ test: {len(df_test)}\n")
        f.write(f"Tỷ lệ train/test: {TRAIN_RATIO:.1%} / {1-TRAIN_RATIO:.1%}\n\n")
        
        f.write("Cấu trúc thư mục:\n")
        f.write(f"  {OUTPUT_DIR}/\n")
        f.write(f"    ├── train/\n")
        f.write(f"    │   ├── filenames.txt\n")
        f.write(f"    │   └── [ImageID].txt (các file thơ)\n")
        f.write(f"    ├── test/\n")
        f.write(f"    │   ├── filenames.txt\n")
        f.write(f"    │   └── [ImageID].txt (các file thơ)\n")
        f.write(f"    ├── images/\n")
        f.write(f"    │   └── [ImageID].jpg (các file ảnh)\n")
        f.write(f"    ├── example_filenames.txt\n")
        f.write(f"    ├── class_info.pickle\n")
        f.write(f"    └── dataset_info.txt (file này)\n\n")
        
        # Thống kê độ dài thơ
        poem_lengths = df['VietnameseText'].str.len()
        f.write(f"Thống kê độ dài thơ (ký tự):\n")
        f.write(f"  Trung bình: {poem_lengths.mean():.0f}\n")
        f.write(f"  Min: {poem_lengths.min()}\n")
        f.write(f"  Max: {poem_lengths.max()}\n")
        f.write(f"  Median: {poem_lengths.median():.0f}\n\n")
        
        # Ví dụ
        f.write("Ví dụ 3 bài thơ đầu tiên:\n\n")
        for idx in range(min(3, len(df_test))):
            row = df_test.iloc[idx]
            f.write(f"--- {row['ImageID']} ---\n")
            f.write(f"{row['VietnameseText'][:200]}...\n\n")
    
    print(f"✓ Đã tạo dataset_info.txt")

def main():
    print("=" * 80)
    print("CHUẨN BỊ DỮ LIỆU THƠ TIẾNG VIỆT CHO ATTNGAN/MIRRORGAN")
    print("=" * 80)
    
    # Kiểm tra file input tồn tại
    if not os.path.exists(CSV_FILE):
        print(f"❌ Lỗi: Không tìm thấy file {CSV_FILE}")
        return
    
    if not os.path.exists(IMAGE_DIR):
        print(f"❌ Lỗi: Không tìm thấy thư mục {IMAGE_DIR}")
        return
    
    # Thực hiện các bước
    create_directory_structure()
    df = read_data()
    missing_images = copy_images(df)
    df_train, df_test = create_text_files(df, missing_images)
    create_filenames_list(df_train, df_test)
    create_example_filenames(df_test)
    create_class_info()
    create_summary(df, df_train, df_test)
    
    print("\n" + "=" * 80)
    print("✅ HOÀN TẤT!")
    print("=" * 80)
    print(f"\nDữ liệu đã được chuẩn bị tại: {OUTPUT_DIR}")
    print(f"  - Train set: {len(df_train)} bài thơ")
    print(f"  - Test set: {len(df_test)} bài thơ")
    print(f"\nBước tiếp theo:")
    print(f"  1. Kiểm tra file config tại: AttnGAN/cfg/DAMSM/vietnamese_poem.yml")
    print(f"  2. Chạy pre-train DAMSM: python pretrain_DAMSM.py --cfg cfg/DAMSM/vietnamese_poem.yml --gpu 0")

if __name__ == '__main__':
    main()

