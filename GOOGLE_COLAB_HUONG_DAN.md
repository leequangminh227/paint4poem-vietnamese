# ☁️ Hướng Dẫn Train Trên Google Colab

## 🎯 Mục tiêu
- Tận dụng GPU miễn phí của Google Colab để train nhanh hơn (600 epoch DAMSM + 300 epoch AttnGAN trong 1-3 ngày)
- Tránh giới hạn CPU ARM64 chậm trên máy local (21-36 ngày)
- Lưu checkpoint + kết quả về Google Drive để tải xuống dùng sau

---

## ✅ Chuẩn Bị Trước Khi Lên Colab
- Tài khoản Google Drive với ít nhất 15 GB trống
- Bộ dữ liệu `vie_poem.csv` + thư mục `images/` (giống như trên máy local)
- Toàn bộ source code `paint4poem/` (khuyến nghị push lên GitHub để clone trực tiếp)
- Kết nối mạng ổn định (Colab session có thể timeout sau 90 phút nếu không tương tác)

---

## 🚀 Bắt Đầu Với Colab

### 1. Mở Colab
- Truy cập https://colab.research.google.com
- `File → New Notebook`

### 2. Chạy các cell sau (copy từng khối vào Colab):

```python
#@title 🚗 Kết nối Google Drive
from google.colab import drive

# Mount Google Drive (sẽ yêu cầu cấp quyền lần đầu)
drive.mount('/content/drive')
```

```python
#@title ⚙️ Kiểm tra GPU và tạo thư mục làm việc
import os
!nvidia-smi

# Tạo thư mục chính trong Drive để lưu mọi thứ
BASE_DIR = '/content/drive/MyDrive/paint4poem-colab'
os.makedirs(BASE_DIR, exist_ok=True)
%cd $BASE_DIR
```

---

### 3. Tải Source Code

#### Cách A (khuyến nghị): Clone từ GitHub
```python
#@title 🧬 Clone repository từ GitHub
REPO_URL = "https://github.com/leequangminh227/paint4poem-vietnamese.git"  # thay bằng repo của bạn
!git clone $REPO_URL
%cd paint4poem-vietnamese
```

#### Cách B: Upload ZIP thủ công
- Nén thư mục `paint4poem/` thành `paint4poem.zip`
- Upload lên Google Drive (ví dụ: `MyDrive/paint4poem.zip`)
- Giải nén:
```python
#@title 📦 Giải nén source code từ Google Drive
ZIP_PATH = '/content/drive/MyDrive/paint4poem.zip'  # cập nhật đường dẫn nếu khác
!unzip -q $ZIP_PATH -d .
%cd paint4poem
```

---

### 4. Chuẩn Bị Dữ Liệu Thơ + Ảnh

#### 4.1 Upload dữ liệu lên Drive
- Tạo thư mục trong Drive: `MyDrive/paint4poem-data/`
- Copy các file:
  - `vie_poem.csv`
  - Thư mục `images/`

#### 4.2 Liên kết dữ liệu vào Colab
```python
#@title 🔗 Liên kết dữ liệu từ Drive vào thư mục dự án
DATA_SRC = '/content/drive/MyDrive/paint4poem-data'
DATA_DST = 'data/Paint4Poem-Zikai-poem-subset'
!mkdir -p $DATA_DST
!ln -sfn $DATA_SRC/vie_poem.csv $DATA_DST/vie_poem.csv
!ln -sfn $DATA_SRC/images $DATA_DST/images
```

#### 4.3 (Tuỳ chọn) Re-run script chuẩn hoá dữ liệu
```python
#@title 🛠️ Chuẩn hoá dữ liệu thơ tiếng Việt (chạy 1 lần)
!python prepare_vietnamese_data.py
```

Kết quả sẽ nằm ở `data/vietnamese_poems/` với cấu trúc train/test hoàn chỉnh.

---

### 5. Cài Đặt Môi Trường
```python
#@title 📦 Cài đặt thư viện cần thiết
!pip install --upgrade pip
!pip install -r requirements.txt

# Các gói bổ sung (nếu cần)
!pip install easydict nltk scikit-image Pillow==9.5.0
```

Kiểm tra phiên bản PyTorch (Colab GPU mặc định đã có sẵn):
```python
import torch
print('Torch version:', torch.__version__)
print('CUDA available:', torch.cuda.is_available())
```

---

### 6. Thiết Lập Biến Môi Trường
```python
#@title 🌱 Thiết lập đường dẫn & GPU
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ['PYTHONPATH'] = '/content/drive/MyDrive/paint4poem-colab/paint4poem-vietnamese/AttnGAN'

%cd /content/drive/MyDrive/paint4poem-colab/paint4poem-vietnamese/AttnGAN
```

---

### 7. Train DAMSM Trên GPU
```python
#@title 🚀 Train DAMSM (Text Encoder)
!python pretrain_DAMSM.py --cfg cfg/DAMSM/vietnamese_poem.yml --gpu 0
```

**Ghi chú:**
- Với GPU T4: 600 epoch ≈ 18-24 giờ
- Checkpoint lưu trong `output/vietnamese_poem_DAMSM_*/Model/`
- Nên để session chạy liên tục (đừng đóng tab)
- Nếu bị ngắt kết nối, có thể resume:
```python
#@title 🔄 Resume DAMSM từ checkpoint gần nhất
CHECKPOINT_EPOCH = 300  # thay bằng epoch đã có
!python pretrain_DAMSM.py --cfg cfg/DAMSM/vietnamese_poem.yml --gpu 0 \
    --resume output/vietnamese_poem_DAMSM_*/Model/text_encoder{CHECKPOINT_EPOCH}.pth
```

---

### 8. Theo Dõi Training
```python
#@title 📈 Quan sát log training
!tail -n 50 output/vietnamese_poem_DAMSM_*/log.txt
```

Tuỳ chọn bật TensorBoard:
```python
#@title 📊 TensorBoard (tuỳ chọn)
%load_ext tensorboard
%tensorboard --logdir output/vietnamese_poem_DAMSM_*
```

---

### 9. Kiểm Tra DAMSM Đã Học Đủ Chưa
```python
#@title 🧪 Test embeddings (option)
%cd /content/drive/MyDrive/paint4poem-colab/paint4poem-vietnamese
!python test_generation_early.py
```

Logs lưu tại `test_results/`, có thể tải về Drive.

---

### 10. Train AttnGAN (Sau Khi DAMSM Xong)
```python
#@title 🎨 Train AttnGAN
%cd AttnGAN
!python main.py --cfg cfg/vietnamese_poem_attn2.yml --gpu 0
```

**Ghi chú:**
- Chắc chắn file `cfg/vietnamese_poem_attn2.yml` đã cập nhật đường dẫn `NET_E` tới text encoder tốt nhất (ví dụ epoch 600)
- Training 300 epoch ≈ 8-12 giờ trên T4
- Checkpoint lưu ở `output/vietnamese_poem_attn2_*/Model/`

Resume nếu session bị ngắt:
```python
#@title 🔄 Resume AttnGAN
CHECKPOINT = 'netG_epoch_150.pth'  # thay bằng checkpoint của bạn
!python main.py --cfg cfg/vietnamese_poem_attn2.yml --gpu 0 \
    --netG output/vietnamese_poem_attn2_*/Model/$CHECKPOINT
```

---

### 11. Generate Ảnh Từ Thơ
```python
#@title 🖼️ Generate ảnh từ thơ tiếng Việt
%cd AttnGAN
!python main.py --cfg cfg/eval_vietnamese.yml --gpu 0
```

Trước khi chạy, cập nhật file `cfg/eval_vietnamese.yml`:
- `TRAIN: NET_G`: đường dẫn đến generator tốt nhất (`netG_epoch_300.pth`)
- `TRAIN: NET_E`: đường dẫn đến text encoder (`text_encoder600.pth`)
- `B_VALIDATION`: 
  - `False`: dùng `example_filenames.txt`
  - `True`: generate toàn bộ test set

Ảnh output nằm tại: `AttnGAN/output/vietnamese_poem_attn2_*/Image/`

---

### 12. Tải Về Checkpoint & Ảnh
```python
#@title 💾 Nén và tải về checkpoints + ảnh
%cd /content/drive/MyDrive/paint4poem-colab
!zip -r outputs_vietnamese.zip paint4poem-vietnamese/output
!zip -r generated_images.zip paint4poem-vietnamese/AttnGAN/output/*/Image
```

Sau khi zip xong, vào Google Drive tải về máy local.

---

## 🛟 Lưu Ý Quan Trọng
- **Mất kết nối Colab:** mở tab devtools → Console nhập `function ClickConnect(){...}` để tự động bấm “Reconnect”
- **Hết thời gian free GPU:** chờ ~12h hoặc nâng cấp Colab Pro
- **Tiết kiệm dung lượng:** định kỳ xoá checkpoint cũ trong thư mục `output/`
- **Giảm rủi ro mất progress:** 
  - Dùng Drive để lưu trực tiếp output
  - Chia training thành nhiều cell nhỏ (DAMSM 300 epoch × 2 lần...)

---

## 🎁 Mẹo Tăng Tốc
- Giảm `SNAPSHOT_INTERVAL` (ví dụ 25) để coi training nhanh hơn
- Giảm `BATCH_SIZE` nếu GPU báo OOM (ví dụ từ 24 → 16)
- Dùng `%env` set `CUDA_LAUNCH_BLOCKING=1` khi cần debug
- Lưu `pip freeze > requirements-colab.txt` để tái tạo môi trường dễ dàng

---

## 🔚 Kết Thúc
- ✅ Đã có pipeline train DAMSM + AttnGAN trên Colab
- ✅ Ảnh generated lưu ở `AttnGAN/output/.../Image`
- ✅ Checkpoint lưu ở `output/.../Model`

Chúc bạn train vui vẻ và ra nhiều bức tranh thơ Việt đẹp! 🎨🇻🇳
