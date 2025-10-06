# ⚠️ LƯU Ý QUAN TRỌNG

## 🖥️ Máy tính của bạn KHÔNG có GPU CUDA

Tôi phát hiện máy bạn không có GPU NVIDIA hoặc chưa cài đặt CUDA. 

### **Tác động:**
- ❌ Training trên CPU sẽ **CỰC KỲ CHẬM**
- ⏰ Pre-train DAMSM: ~3-7 ngày (thay vì 4-8 giờ)
- ⏰ Train AttnGAN: ~7-14 ngày (thay vì 12-24 giờ)
- 💻 CPU sẽ chạy ở 100% trong thời gian dài

---

## 🚀 Giải pháp được khuyến nghị

### **Tùy chọn 1: Google Colab (MIỄN PHÍ - KHUYÊN DÙNG)**

Google Colab cung cấp GPU miễn phí:

1. Truy cập: https://colab.research.google.com
2. Tạo notebook mới
3. Chọn Runtime > Change runtime type > GPU (T4 hoặc V100)
4. Upload code và data lên Google Drive
5. Chạy training trên Colab

**Ưu điểm:**
- ✅ Hoàn toàn miễn phí
- ✅ GPU Tesla T4 (nhanh gấp 50-100 lần CPU)
- ✅ Không cần cài đặt gì

**Nhược điểm:**
- ⚠️ Giới hạn 12 giờ/session liên tục
- ⚠️ Cần reconnect và tiếp tục training

### **Tùy chọn 2: Kaggle Notebooks (MIỄN PHÍ)**

Tương tự Colab nhưng cho phép 30 giờ GPU/tuần:

1. Truy cập: https://www.kaggle.com
2. Tạo account và notebook mới
3. Bật GPU trong Settings
4. Upload data và chạy code

### **Tùy chọn 3: Cloud GPU có trả phí**

- AWS EC2 (p2/p3 instances)
- Google Cloud Platform
- Paperspace
- Lambda Labs

**Chi phí:** ~$0.50-2.00/giờ

### **Tùy chọn 4: Giảm quy mô (Training trên CPU nhưng nhanh hơn)**

Nếu bạn vẫn muốn thử trên máy local:

1. **Giảm số epochs** - Từ 600 xuống 100-200
2. **Giảm batch size** - Từ 24 xuống 4-8
3. **Giảm kích thước model** - Sửa trong config
4. **Giảm số bài thơ** - Chỉ dùng 100-200 bài thay vì 903

---

## 📝 Nếu bạn vẫn muốn chạy trên CPU

### **Bước 1: Giảm quy mô training**

**File: `AttnGAN/cfg/DAMSM/vietnamese_poem.yml`**
```yaml
TRAIN:
    BATCH_SIZE: 4        # Giảm từ 24
    MAX_EPOCH: 100       # Giảm từ 600
    SNAPSHOT_INTERVAL: 10  # Giảm từ 50
```

**File: `AttnGAN/cfg/vietnamese_poem_attn2.yml`**
```yaml
TRAIN:
    BATCH_SIZE: 2        # Giảm từ 8
    MAX_EPOCH: 100       # Giảm từ 600
    SNAPSHOT_INTERVAL: 10  # Giảm từ 50
```

### **Bước 2: Giảm số dữ liệu**

Tạo script để chỉ dùng 100 bài thơ:

```python
# create_small_dataset.py
import os
import shutil

src = 'data/vietnamese_poems'
dst = 'data/vietnamese_poems_small'

os.makedirs(dst, exist_ok=True)
os.makedirs(f'{dst}/train', exist_ok=True)
os.makedirs(f'{dst}/test', exist_ok=True)
os.makedirs(f'{dst}/images', exist_ok=True)

# Copy chỉ 80 bài train và 20 bài test
with open(f'{src}/train/filenames.txt') as f:
    train_files = f.readlines()[:80]

with open(f'{src}/test/filenames.txt') as f:
    test_files = f.readlines()[:20]

# Copy files...
# (Chi tiết xem script prepare_vietnamese_data.py)
```

### **Bước 3: Chạy với CPU**

```bash
python run_vietnamese_training.py --gpu -1 --step damsm
```

**Thời gian ước tính với config giảm:**
- Pre-train DAMSM: 1-2 ngày
- Train AttnGAN: 2-3 ngày
- Chất lượng kết quả: Trung bình đến thấp

---

## 🎯 Khuyến nghị của tôi

**Cho bạn:**

1. ✅ **Sử dụng Google Colab** (miễn phí, nhanh nhất)
2. ✅ Upload code + data lên Google Drive
3. ✅ Chạy training trên Colab GPU
4. ✅ Download model về sau khi train xong

**Hoặc:**

1. ✅ Giảm quy mô training (100 epochs, 100 bài thơ)
2. ✅ Chạy overnight trên CPU để xem kết quả demo
3. ⚠️ Kỳ vọng chất lượng thấp hơn

---

## 📚 Hướng dẫn sử dụng Google Colab

### **Bước 1: Chuẩn bị**

1. Tải dữ liệu và code lên Google Drive
2. Truy cập https://colab.research.google.com
3. Tạo notebook mới

### **Bước 2: Setup trong Colab**

```python
# Cell 1: Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Cell 2: Install dependencies
!pip install torch torchvision easydict nltk pyyaml python-dateutil

# Cell 3: Copy data
!cp -r /content/drive/MyDrive/paint4poem /content/
%cd /content/paint4poem

# Cell 4: Run training
!python run_vietnamese_training.py --gpu 0 --step damsm
```

### **Bước 3: Xử lý timeout 12 giờ**

- Sau 12 giờ, session sẽ disconnect
- Checkpoint đã được lưu mỗi 50 epochs
- Cập nhật config để load checkpoint và tiếp tục:

```yaml
NET_E: 'path/to/text_encoder_last_checkpoint.pth'
```

---

## ❓ Câu hỏi thường gặp

**Q: Tôi có thể chạy overnight trên laptop không?**
A: Có, nhưng laptop sẽ nóng và tốn điện. Đảm bảo tản nhiệt tốt.

**Q: Training bị gián đoạn, có mất hết không?**
A: Không. Checkpoint được lưu định kỳ, bạn có thể tiếp tục từ checkpoint cuối.

**Q: Colab free có đủ không?**
A: Có, nhưng cần chia nhỏ thành nhiều session 12 giờ.

**Q: Làm sao biết training có đang tiến triển tốt không?**
A: Xem loss giảm dần và quality ảnh được generate cải thiện.

---

## 🆘 Cần hỗ trợ?

Nếu cần giúp setup Colab hoặc có câu hỏi, hãy cho tôi biết!

**Bạn muốn:**
- [ ] Hướng dẫn chi tiết setup Google Colab
- [ ] Script giảm quy mô dữ liệu để chạy nhanh trên CPU
- [ ] Tiếp tục chạy trên CPU với config hiện tại
- [ ] Hướng dẫn khác

