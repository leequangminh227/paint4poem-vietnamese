# 🚀 Quick Start - Thơ Tiếng Việt

## ✅ Đã hoàn thành

- ✓ Đã chuẩn bị **903 bài thơ tiếng Việt** với ảnh tương ứng
- ✓ Chia thành: **722 train** / **181 test**
- ✓ Tạo file config cho AttnGAN
- ✓ Dữ liệu tại: `data/vietnamese_poems/`

---

## 🎯 Chạy toàn bộ pipeline (Cách đơn giản nhất)

### Tự động (Khuyên dùng):
```bash
# Chạy toàn bộ: chuẩn bị dữ liệu → train DAMSM → train AttnGAN → generate ảnh
python run_vietnamese_training.py --gpu 0 --step all

# Hoặc chạy từng bước:
python run_vietnamese_training.py --gpu 0 --step prepare  # Chuẩn bị dữ liệu
python run_vietnamese_training.py --gpu 0 --step damsm    # Pre-train DAMSM
python run_vietnamese_training.py --gpu 0 --step attngan  # Train AttnGAN
python run_vietnamese_training.py --gpu 0 --step eval     # Generate ảnh
```

### Thủ công (Từng bước):

#### 1️⃣ Pre-train DAMSM (4-8 giờ với GPU)
```bash
cd AttnGAN
python pretrain_DAMSM.py --cfg cfg/DAMSM/vietnamese_poem.yml --gpu 0
```

#### 2️⃣ Cập nhật đường dẫn DAMSM
Mở file `AttnGAN/cfg/vietnamese_poem_attn2.yml`, tìm dòng:
```yaml
NET_E: '../output/vietnamese_poem_DAMSM_*/Model/text_encoder*.pth'
```
Đổi thành đường dẫn thực tế, ví dụ:
```yaml
NET_E: '../output/vietnamese_poem_DAMSM_2025_10_06_10_30_15/Model/text_encoder600.pth'
```

#### 3️⃣ Train AttnGAN (12-24 giờ với GPU)
```bash
cd AttnGAN
python main_poem.py --cfg cfg/vietnamese_poem_attn2.yml --gpu 0
```

#### 4️⃣ Generate ảnh từ thơ
Mở file `AttnGAN/cfg/eval_vietnamese.yml`, cập nhật 2 dòng:
```yaml
NET_G: '../output/vietnamese_attn_[timestamp]/Model/netG_epoch_600.pth'
NET_E: '../output/vietnamese_poem_DAMSM_[timestamp]/Model/text_encoder600.pth'
```

Rồi chạy:
```bash
cd AttnGAN
python main_poem.py --cfg cfg/eval_vietnamese.yml --gpu 0
```

---

## 💻 Nếu không có GPU (chạy trên CPU)

Thêm `--gpu -1` vào mọi lệnh:
```bash
python run_vietnamese_training.py --gpu -1 --step all
```
**Lưu ý**: Sẽ chậm hơn rất nhiều (có thể mất vài tuần)

---

## 📁 Kết quả

- **Model checkpoints**: `output/vietnamese_*/Model/`
- **Ảnh được generate**: `output/eval_vietnamese_*/`
- **Training logs**: In ra console

---

## 🎨 Tạo ảnh từ thơ tùy chỉnh

1. Tạo file thơ: `data/vietnamese_poems/my_poem.txt`
   ```
   Trăng sáng soi bóng cây đơn côi
   Gió thu lay lá rơi rơi
   ```

2. Thêm vào `data/vietnamese_poems/example_filenames.txt`:
   ```
   my_poem
   ```

3. Chạy evaluation:
   ```bash
   cd AttnGAN
   python main_poem.py --cfg cfg/eval_vietnamese.yml --gpu 0
   ```

---

## 🐛 Lỗi thường gặp

### Out of Memory
Giảm batch size trong file config:
- `cfg/DAMSM/vietnamese_poem.yml`: `BATCH_SIZE: 12` (thay vì 24)
- `cfg/vietnamese_poem_attn2.yml`: `BATCH_SIZE: 4` (thay vì 8)

### File not found
Kiểm tra đường dẫn trong file `.yml` có đúng không

### Checkpoint không tìm thấy
Chạy lại bước pre-train DAMSM trước khi train AttnGAN

---

## 📖 Tài liệu chi tiết

- 📄 **Hướng dẫn đầy đủ**: Xem file `HUONG_DAN_THO_TIENG_VIET.md`
- 📄 **Hướng dẫn chung**: Xem file `HUONG_DAN_CHAY.md`

---

## ⏱️ Thời gian ước tính

| Bước | GPU (GTX 1080 Ti) | CPU |
|------|-------------------|-----|
| Pre-train DAMSM | 4-8 giờ | 3-7 ngày |
| Train AttnGAN | 12-24 giờ | 7-14 ngày |
| Evaluation | 5-10 phút | 30-60 phút |

---

## ✨ Ví dụ output

Sau khi chạy xong, bạn sẽ có:
- Ảnh được tạo từ 10 bài thơ mẫu
- Model đã train có thể tạo ảnh từ bất kỳ bài thơ tiếng Việt nào
- Có thể tiếp tục fine-tune hoặc generate thêm

**Chúc bạn thành công! 🎉**
