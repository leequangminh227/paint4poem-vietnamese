# Hướng dẫn chạy với dữ liệu thơ tiếng Việt

## 📊 Dữ liệu đã chuẩn bị

Dữ liệu của bạn đã được chuyển đổi thành công:
- **Tổng số bài thơ**: 903 bài (từ file `vie_poem.csv`)
- **Train set**: 722 bài thơ (80%)
- **Test set**: 181 bài thơ (20%)
- **Vị trí**: `data/vietnamese_poems/`

### Cấu trúc thư mục:
```
data/vietnamese_poems/
├── train/
│   ├── filenames.txt           # Danh sách tên file
│   └── [ImageID].txt           # File thơ (ví dụ: Gushici-0.txt)
├── test/
│   ├── filenames.txt
│   └── [ImageID].txt
├── images/
│   └── [ImageID].jpg           # Ảnh tương ứng
├── example_filenames.txt       # 10 ví dụ để test
├── class_info.pickle
└── dataset_info.txt            # Chi tiết về dataset
```

---

## 🚀 Các bước chạy

### **Bước 1: Pre-train DAMSM (Text Encoder)**

DAMSM sẽ học cách encode thơ tiếng Việt thành vector.

```bash
cd AttnGAN
python pretrain_DAMSM.py --cfg cfg/DAMSM/vietnamese_poem.yml --gpu 0
```

**Lưu ý**: 
- Nếu không có GPU, đổi `--gpu 0` thành `--gpu -1`
- Nếu bị out of memory, giảm `BATCH_SIZE` trong file `cfg/DAMSM/vietnamese_poem.yml`
- Training sẽ chạy 600 epochs, mất khoảng vài giờ đến vài ngày tùy GPU
- Model sẽ được lưu tại `../output/vietnamese_poem_DAMSM_[timestamp]/Model/`

**Theo dõi training**:
```bash
# Model checkpoint được lưu mỗi 50 epochs
# Tìm file text_encoder mới nhất:
# ../output/vietnamese_poem_DAMSM_*/Model/text_encoder550.pth (hoặc cao hơn)
```

---

### **Bước 2: Cập nhật đường dẫn pre-trained DAMSM**

Sau khi pre-train DAMSM xong, cập nhật đường dẫn trong file config:

**File**: `AttnGAN/cfg/vietnamese_poem_attn2.yml`

Tìm dòng:
```yaml
NET_E: '../output/vietnamese_poem_DAMSM_*/Model/text_encoder*.pth'
```

Đổi thành đường dẫn thực tế, ví dụ:
```yaml
NET_E: '../output/vietnamese_poem_DAMSM_2025_10_06_10_30_15/Model/text_encoder600.pth'
```

---

### **Bước 3: Train AttnGAN**

Train mô hình sinh ảnh từ thơ:

```bash
python main_poem.py --cfg cfg/vietnamese_poem_attn2.yml --gpu 0
```

**Lưu ý**:
- Training sẽ chạy 600 epochs
- Model được lưu tại `../output/vietnamese_attn_[timestamp]/Model/`
- Checkpoint được lưu mỗi 50 epochs
- Ảnh mẫu được generate trong quá trình training để theo dõi tiến trình

**Theo dõi kết quả**:
- Ảnh được tạo ra: `../output/vietnamese_attn_*/[epoch]/`
- Model checkpoint: `../output/vietnamese_attn_*/Model/netG_epoch_*.pth`

---

### **Bước 4: Generate ảnh (Evaluation)**

Sau khi train xong, generate ảnh từ thơ:

#### 4.1. Cập nhật đường dẫn model

**File**: `AttnGAN/cfg/eval_vietnamese.yml`

Cập nhật 2 dòng sau với đường dẫn thực tế:
```yaml
NET_G: '../output/vietnamese_attn_2025_10_06_15_20_30/Model/netG_epoch_600.pth'
NET_E: '../output/vietnamese_poem_DAMSM_2025_10_06_10_30_15/Model/text_encoder600.pth'
```

#### 4.2. Generate từ examples (10 bài thơ mẫu)

```bash
python main_poem.py --cfg cfg/eval_vietnamese.yml --gpu 0
```

Kết quả được lưu tại: `../output/eval_vietnamese_[timestamp]/`

#### 4.3. Generate cho toàn bộ test set (181 bài thơ)

Sửa trong file `cfg/eval_vietnamese.yml`:
```yaml
B_VALIDATION: True  # Đổi từ False sang True
```

Rồi chạy lại:
```bash
python main_poem.py --cfg cfg/eval_vietnamese.yml --gpu 0
```

---

## ⚙️ Tùy chỉnh cấu hình

### Điều chỉnh nếu bị Out of Memory:

**File**: `cfg/DAMSM/vietnamese_poem.yml`
```yaml
TRAIN:
    BATCH_SIZE: 12  # Giảm từ 24 xuống 12 hoặc 8
```

**File**: `cfg/vietnamese_poem_attn2.yml`
```yaml
TRAIN:
    BATCH_SIZE: 4  # Giảm từ 8 xuống 4
```

### Điều chỉnh số epochs:

```yaml
TRAIN:
    MAX_EPOCH: 300  # Giảm từ 600 nếu muốn train nhanh hơn
```

### Chạy trên CPU (không có GPU):

Thêm `--gpu -1` vào mọi lệnh:
```bash
python pretrain_DAMSM.py --cfg cfg/DAMSM/vietnamese_poem.yml --gpu -1
python main_poem.py --cfg cfg/vietnamese_poem_attn2.yml --gpu -1
```

**Lưu ý**: Chạy trên CPU sẽ rất chậm (có thể mất vài tuần).

---

## 📝 Tạo thơ tùy chỉnh để generate ảnh

### Bước 1: Tạo file thơ mới

Tạo file `data/vietnamese_poems/my_poem.txt` với nội dung thơ:
```
Trăng sáng soi bóng cây đơn côi
Gió thu lay lá rơi rơi
Nhớ người xa cách ngàn trùng
Lòng buồn man mác tháng ngày
```

### Bước 2: Cập nhật example_filenames.txt

Thêm dòng này vào file `data/vietnamese_poems/example_filenames.txt`:
```
my_poem
```

### Bước 3: Generate ảnh

```bash
cd AttnGAN
python main_poem.py --cfg cfg/eval_vietnamese.yml --gpu 0
```

---

## 🐛 Xử lý lỗi thường gặp

### 1. FileNotFoundError: text_encoder*.pth

**Nguyên nhân**: Chưa pre-train DAMSM hoặc đường dẫn sai

**Giải pháp**: 
- Chạy Bước 1 (pre-train DAMSM) trước
- Cập nhật đường dẫn `NET_E` trong file config

### 2. CUDA out of memory

**Giải pháp**:
- Giảm `BATCH_SIZE` trong file config
- Hoặc chạy trên CPU với `--gpu -1`

### 3. RuntimeError: Expected all tensors on same device

**Nguyên nhân**: Model và data không cùng device (CPU/GPU)

**Giải pháp**: 
- Đảm bảo chạy với cùng GPU setting (`--gpu 0` hoặc `--gpu -1`)

### 4. UnicodeDecodeError khi đọc file

**Nguyên nhân**: Encoding không đúng

**Giải pháp**: 
- Đảm bảo file thơ được lưu với encoding UTF-8

---

## 📊 Đánh giá kết quả

### Inception Score (IS)

Đo chất lượng ảnh:
```bash
# TODO: Thêm script đánh giá IS
```

### FID Score

Đo sự khác biệt giữa ảnh thật và ảnh sinh:
```bash
pip install pytorch-fid
python -m pytorch_fid path/to/real/images path/to/generated/images
```

### R-precision

Đo độ tương đồng giữa thơ và ảnh (có sẵn trong code):
- Kết quả được in ra trong quá trình evaluation

---

## 💡 Tips và Tricks

### 1. Early Stopping
- Theo dõi loss và quality của ảnh được generate
- Có thể dừng sớm nếu thấy quality không cải thiện

### 2. Fine-tuning
- Sau khi train xong, có thể tiếp tục train với learning rate thấp hơn:
```yaml
TRAIN:
    NET_G: '../output/vietnamese_attn_*/Model/netG_epoch_600.pth'
    GENERATOR_LR: 0.00005  # Giảm từ 0.0002
    MAX_EPOCH: 700  # Train thêm 100 epochs
```

### 3. Augmentation
- Dữ liệu hiện tại đã có random crop và horizontal flip
- Có thể thêm augmentation khác nếu cần

### 4. Transfer Learning
- Có thể pre-train trên dataset lớn hơn trước
- Sau đó fine-tune trên dữ liệu thơ tiếng Việt

---

## 📖 Tham khảo

- Paper gốc: [AttnGAN](https://arxiv.org/abs/1711.10485)
- Dataset Paint4Poem: [Paper](https://arxiv.org/abs/2109.11682)

---

## ❓ Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra file `data/vietnamese_poems/dataset_info.txt` để xem thông tin dataset
2. Xem log chi tiết khi chạy training
3. Kiểm tra GPU memory: `nvidia-smi` (nếu có GPU)

---

## 📅 Thời gian ước tính

**Với GPU (GTX 1080 Ti hoặc tương đương)**:
- Pre-train DAMSM: 4-8 giờ
- Train AttnGAN: 12-24 giờ
- Evaluation: 5-10 phút

**Với CPU**:
- Pre-train DAMSM: 3-7 ngày
- Train AttnGAN: 7-14 ngày
- Evaluation: 30-60 phút

**Khuyến nghị**: Sử dụng GPU để training, nếu không có thể:
- Sử dụng Google Colab (free GPU)
- Sử dụng Kaggle Notebooks (free GPU)
- Thuê cloud GPU (AWS, GCP, etc.)

