# 🖥️ Hướng dẫn cho Windows ARM64 (Qualcomm Snapdragon)

## 📊 Thông tin hệ thống của bạn

- **Kiến trúc**: ARM64 (ARMv8)
- **Chip**: Qualcomm Snapdragon
- **Hệ điều hành**: Windows ARM64
- **PyTorch**: 2.8.0+cpu (CPU only, không có CUDA)

---

## ⚠️ Thách thức với ARM64

### **1. Không có GPU hỗ trợ**
- Windows ARM64 hiện tại **không hỗ trợ CUDA/GPU** cho deep learning
- Chỉ có thể chạy trên CPU

### **2. Hiệu suất CPU ARM**
- CPU ARM tốt cho tiêu thụ điện năng
- Nhưng **chậm hơn nhiều** cho deep learning so với CPU x86 hoặc GPU
- Training có thể mất **rất lâu** (tuần đến tháng)

### **3. Khả năng tương thích**
- PyTorch trên ARM64 vẫn đang phát triển
- Một số thư viện có thể chưa tối ưu

---

## 🎯 Khuyến nghị giải pháp

### **✅ Giải pháp 1: Google Colab (TỐT NHẤT)**

Sử dụng Google Colab để chạy training trên GPU miễn phí:

#### **Ưu điểm:**
- ✅ GPU Tesla T4 miễn phí
- ✅ Nhanh gấp 100-200 lần máy ARM64 của bạn
- ✅ Hoàn thành trong 1-2 ngày thay vì vài tuần/tháng
- ✅ Không tốn điện máy local

#### **Hướng dẫn chi tiết:**

**Bước 1: Chuẩn bị dữ liệu**

Nén dữ liệu để upload lên Google Drive:

```powershell
# Trên máy Windows ARM64
Compress-Archive -Path data\vietnamese_poems -DestinationPath vietnamese_poems.zip
Compress-Archive -Path AttnGAN -DestinationPath attngan_code.zip
```

**Bước 2: Upload lên Google Drive**

1. Truy cập https://drive.google.com
2. Tạo thư mục mới: `paint4poem`
3. Upload 2 file zip vào thư mục đó

**Bước 3: Setup Google Colab**

1. Truy cập: https://colab.research.google.com
2. Tạo notebook mới
3. Runtime > Change runtime type > **Hardware accelerator: GPU** > Save

**Bước 4: Chạy code trong Colab**

```python
# Cell 1: Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Cell 2: Extract data
!cd /content
!unzip -q /content/drive/MyDrive/paint4poem/vietnamese_poems.zip
!unzip -q /content/drive/MyDrive/paint4poem/attngan_code.zip

# Cell 3: Install dependencies
!pip install easydict nltk pyyaml python-dateutil pandas openpyxl

# Cell 4: Check GPU
import torch
print('CUDA available:', torch.cuda.is_available())
print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')

# Cell 5: Pre-train DAMSM
%cd /content/AttnGAN
!python pretrain_DAMSM.py --cfg cfg/DAMSM/vietnamese_poem.yml --gpu 0

# Cell 6: Train AttnGAN (sau khi pre-train xong)
# Cập nhật đường dẫn NET_E trong cfg/vietnamese_poem_attn2.yml trước
!python main_poem.py --cfg cfg/vietnamese_poem_attn2.yml --gpu 0

# Cell 7: Evaluation
!python main_poem.py --cfg cfg/eval_vietnamese.yml --gpu 0

# Cell 8: Download kết quả
from google.colab import files
!zip -r results.zip ../output/
files.download('results.zip')
```

**Lưu ý về giới hạn 12 giờ:**

Colab miễn phí giới hạn 12 giờ/session. Để xử lý:

1. Checkpoint được lưu tự động mỗi 50 epochs
2. Khi session timeout, tạo notebook mới
3. Load checkpoint cuối cùng và tiếp tục:

```yaml
# Trong file config
NET_E: '/content/drive/MyDrive/paint4poem/output/.../text_encoder_last.pth'
```

---

### **✅ Giải pháp 2: Kaggle Notebooks**

Tương tự Colab nhưng cho phép **30 giờ GPU/tuần**:

1. Truy cập: https://www.kaggle.com
2. Tạo account (miễn phí)
3. New Notebook > Settings > GPU ON
4. Upload data và chạy code tương tự Colab

**Ưu điểm so với Colab:**
- Cho phép 30 giờ GPU liên tục/tuần
- Có thể chạy xong pre-train DAMSM trong 1 session

---

### **⚙️ Giải pháp 3: Chạy trên ARM64 local (Không khuyến nghị)**

Nếu bạn **thực sự muốn** chạy local trên ARM64:

#### **A. Giảm quy mô training nghiêm trọng**

**File: `AttnGAN/cfg/DAMSM/vietnamese_poem_tiny.yml`** (tạo mới)

```yaml
CONFIG_NAME: 'DAMSM_tiny'
DATASET_NAME: 'vietnamese_poem'
DATA_DIR: '../../data/vietnamese_poems_tiny'  # Chỉ 50 bài thơ
GPU_ID: 0
WORKERS: 1

TREE:
    BRANCH_NUM: 1
    BASE_SIZE: 64  # Giảm từ 299

TRAIN:
    FLAG: True
    NET_E: ''
    BATCH_SIZE: 2  # Giảm từ 24
    MAX_EPOCH: 50  # Giảm từ 600
    SNAPSHOT_INTERVAL: 10
    ENCODER_LR: 0.002
    RNN_GRAD_CLIP: 0.25
    SMOOTH:
        GAMMA1: 4.0
        GAMMA2: 5.0
        GAMMA3: 10.0

TEXT:
    EMBEDDING_DIM: 128  # Giảm từ 256
    CAPTIONS_PER_IMAGE: 1
    WORDS_NUM: 32  # Giảm từ 64
```

#### **B. Tạo dataset nhỏ**

```python
# create_tiny_dataset.py
import os
import shutil
from pathlib import Path

src_dir = 'data/vietnamese_poems'
dst_dir = 'data/vietnamese_poems_tiny'

# Tạo thư mục
os.makedirs(f'{dst_dir}/train', exist_ok=True)
os.makedirs(f'{dst_dir}/test', exist_ok=True)
os.makedirs(f'{dst_dir}/images', exist_ok=True)

# Lấy 40 bài train, 10 bài test
with open(f'{src_dir}/train/filenames.txt') as f:
    train_files = [line.strip() for line in f.readlines()[:40]]

with open(f'{src_dir}/test/filenames.txt') as f:
    test_files = [line.strip() for line in f.readlines()[:10]]

# Copy files
for fname in train_files:
    shutil.copy2(f'{src_dir}/train/{fname}.txt', f'{dst_dir}/train/')
    # Copy image
    if os.path.exists(f'{src_dir}/images/{fname}.jpg'):
        shutil.copy2(f'{src_dir}/images/{fname}.jpg', f'{dst_dir}/images/')

for fname in test_files:
    shutil.copy2(f'{src_dir}/test/{fname}.txt', f'{dst_dir}/test/')
    if os.path.exists(f'{src_dir}/images/{fname}.jpg'):
        shutil.copy2(f'{src_dir}/images/{fname}.jpg', f'{dst_dir}/images/')

# Tạo filenames.txt
with open(f'{dst_dir}/train/filenames.txt', 'w') as f:
    f.write('\n'.join(train_files))

with open(f'{dst_dir}/test/filenames.txt', 'w') as f:
    f.write('\n'.join(test_files))

# Copy class_info
shutil.copy2(f'{src_dir}/class_info.pickle', f'{dst_dir}/')

print(f'✓ Đã tạo dataset nhỏ: 40 train + 10 test')
```

#### **C. Chạy training**

```bash
# Tạo dataset nhỏ
python create_tiny_dataset.py

# Chạy training
cd AttnGAN
python pretrain_DAMSM.py --cfg cfg/DAMSM/vietnamese_poem_tiny.yml --gpu -1
```

**Thời gian ước tính:**
- Pre-train DAMSM: 2-4 ngày
- Train AttnGAN: 4-7 ngày  
- **Chất lượng kết quả: RẤT THẤP** (do giảm quy mô quá nhiều)

---

## 📊 So sánh các giải pháp

| Giải pháp | Thời gian | Chi phí | Chất lượng | Độ khó |
|-----------|-----------|---------|------------|---------|
| **Google Colab** | 1-2 ngày | Miễn phí | Cao | Dễ ⭐⭐ |
| **Kaggle** | 1-2 ngày | Miễn phí | Cao | Dễ ⭐⭐ |
| **ARM64 Full** | 3-8 tuần | Điện (~$20) | Cao | Khó ⭐⭐⭐⭐ |
| **ARM64 Tiny** | 1-2 tuần | Điện (~$10) | Rất thấp | Trung bình ⭐⭐⭐ |

---

## 🔧 Fix đã áp dụng

Tôi đã sửa code để tương thích với CPU-only mode:

✅ **File đã sửa:**
- `AttnGAN/pretrain_DAMSM.py` - Thêm check `if cfg.CUDA` trước `torch.cuda.set_device()`
- `AttnGAN/trainer.py` - Tương tự
- `AttnGAN/GlobalAttention.py` - Sửa docstring escape sequence
- `AttnGAN/miscc/config.py` - Thêm `Loader=yaml.FullLoader`

✅ **Bây giờ code có thể chạy với `--gpu -1`** (CPU mode) mà không bị crash

---

## 🚀 Khuyến nghị cuối cùng

**Cho máy ARM64 của bạn:**

### **Lựa chọn tốt nhất: Google Colab**

1. ✅ Upload data lên Google Drive (làm 1 lần)
2. ✅ Chạy training trên Colab GPU (1-2 ngày)
3. ✅ Download model về máy ARM64
4. ✅ Có thể chạy inference/evaluation trên ARM64 local (nhanh hơn training nhiều)

### **Lựa chọn thay thế: ARM64 Tiny**

1. Chạy với dataset tiny (50 bài thơ)
2. Chỉ để thử nghiệm/demo
3. Kỳ vọng chất lượng thấp

### **KHÔNG khuyến nghị:**

- ❌ Training full dataset trên ARM64 (mất quá lâu)
- ❌ Mua cloud GPU (tốn kém hơn dùng Colab free)

---

## 📝 Các bước tiếp theo

**Bạn muốn:**

### **A. Hướng dẫn chi tiết setup Google Colab** ⭐ KHUYẾN NGHỊ
→ Tôi sẽ tạo notebook Colab sẵn cho bạn

### **B. Tạo dataset tiny để test trên ARM64**
→ Tôi sẽ tạo script và config tiny

### **C. Thử chạy inference với pre-trained model**
→ Tôi sẽ hướng dẫn download và sử dụng model có sẵn

### **D. Hướng dẫn khác**
→ Cho tôi biết bạn cần gì

---

## 💡 Tips cho Windows ARM64

1. **Pin và Nhiệt độ**: ARM64 tiêu thụ điện ít hơn, nhưng training vẫn khiến máy nóng
2. **Background tasks**: Tắt các app khác khi training
3. **Checkpoint**: Luôn lưu checkpoint thường xuyên
4. **Cloud first**: Ưu tiên dùng cloud GPU cho training, local cho inference

---

## ❓ Câu hỏi thường gặp

**Q: ARM64 có nhanh hơn x86 CPU không?**
A: Cho workload thông thường thì có, nhưng cho deep learning thì chậm hơn vì thiếu tối ưu hóa.

**Q: Có thể dùng NPU trên Snapdragon không?**
A: Hiện tại PyTorch chưa hỗ trợ NPU trên Qualcomm Snapdragon cho training.

**Q: Google Colab có an toàn không?**
A: Có, nhưng đừng upload dữ liệu nhạy cảm. Dữ liệu thơ của bạn không vấn đề gì.

**Q: Sau khi train trên Colab, có chạy được trên ARM64 không?**
A: Có! Model PyTorch tương thích cross-platform. Train trên GPU/x86, chạy inference trên ARM64 không vấn đề.

---

Bạn muốn tôi giúp gì tiếp theo? 🎯

