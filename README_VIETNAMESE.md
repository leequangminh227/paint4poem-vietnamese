# 🎨 Paint4Poem - Thơ Tiếng Việt

Dự án tạo tranh nghệ thuật từ thơ tiếng Việt sử dụng AttnGAN.

## ✅ Đã hoàn thành

- ✓ **903 bài thơ tiếng Việt** đã được chuẩn bị (722 train / 181 test)
- ✓ Script chuyển đổi dữ liệu tự động
- ✓ File config đầy đủ cho AttnGAN
- ✓ Script training tự động
- ✓ Fix lỗi tương thích với ARM64 và CPU-only mode
- ✓ Hướng dẫn chi tiết cho nhiều platform

## 📁 Các file quan trọng

### 🚀 Để bắt đầu nhanh:
- **`QUICK_START_VIETNAMESE.md`** - Hướng dẫn nhanh nhất

### 🖥️ Cho máy ARM64 của bạn:
- **`HUONG_DAN_ARM64.md`** - Hướng dẫn đặc biệt cho Windows ARM64
- **`LUU_Y_QUAN_TRONG.md`** - Lưu ý về GPU và CPU

### 📚 Hướng dẫn chi tiết:
- **`HUONG_DAN_THO_TIENG_VIET.md`** - Hướng dẫn đầy đủ
- **`HUONG_DAN_CHAY.md`** - Hướng dẫn chung cho dự án

### 🛠️ Scripts:
- **`prepare_vietnamese_data.py`** - Chuyển đổi CSV thành định dạng AttnGAN
- **`run_vietnamese_training.py`** - Training pipeline tự động

### ⚙️ Configs:
- `AttnGAN/cfg/DAMSM/vietnamese_poem.yml` - Pre-train DAMSM
- `AttnGAN/cfg/vietnamese_poem_attn2.yml` - Train AttnGAN
- `AttnGAN/cfg/eval_vietnamese.yml` - Generate ảnh

## 🎯 Khuyến nghị cho bạn (Windows ARM64)

### ⭐ Lựa chọn TỐT NHẤT: Google Colab

Máy ARM64 của bạn không có GPU → Training rất chậm.

**Giải pháp: Sử dụng Google Colab (GPU miễn phí)**

📖 **Xem hướng dẫn chi tiết tại: `HUONG_DAN_ARM64.md`**

```
Thời gian:
- Trên Colab (GPU): 1-2 ngày ✅
- Trên ARM64 (CPU): 3-8 tuần ❌
```

## 🚀 Quick Start

### Cách 1: Google Colab (Khuyên dùng)

1. Đọc file `HUONG_DAN_ARM64.md`
2. Upload data lên Google Drive
3. Chạy notebook trên Colab với GPU

### Cách 2: Chạy local trên ARM64 (Chậm)

```bash
# Đã fix lỗi, có thể chạy với CPU
python run_vietnamese_training.py --gpu -1 --step all
```

⚠️ **Lưu ý**: Sẽ mất vài tuần để hoàn thành!

## 📊 Dữ liệu

```
data/vietnamese_poems/
├── train/          # 722 bài thơ
├── test/           # 181 bài thơ
└── images/         # 903 ảnh
```

Nguồn: File `vie_poem.csv` (cột C: thơ tiếng Việt, cột D: tên ảnh)

## 🔧 Đã fix

- ✅ Lỗi `easydict` module not found
- ✅ Lỗi `yaml.load()` missing Loader
- ✅ Lỗi `torch.cuda.set_device()` trên CPU
- ✅ SyntaxWarning trong GlobalAttention.py
- ✅ Tương thích với ARM64 CPU-only mode

## 📖 Tài liệu

| File | Mô tả | Dành cho |
|------|-------|----------|
| `QUICK_START_VIETNAMESE.md` | Hướng dẫn nhanh | Mọi người |
| `HUONG_DAN_ARM64.md` | Hướng dẫn ARM64 + Colab | **Bạn - đọc đầu tiên** ⭐ |
| `LUU_Y_QUAN_TRONG.md` | Lưu ý về hardware | Không có GPU |
| `HUONG_DAN_THO_TIENG_VIET.md` | Chi tiết đầy đủ | Đọc sau |

## 🎨 Kết quả mong đợi

Sau khi train xong, bạn sẽ có:
- Model có thể tạo tranh từ thơ tiếng Việt
- Ảnh được generate từ 181 bài thơ test
- Có thể tạo ảnh từ thơ tùy chỉnh

## 💡 Tips

1. **Training**: Dùng Google Colab (GPU miễn phí)
2. **Inference**: Có thể chạy trên ARM64 local (nhanh hơn training)
3. **Checkpoint**: Luôn được lưu tự động mỗi 50 epochs
4. **Restart**: Có thể tiếp tục từ checkpoint nếu bị gián đoạn

## ❓ Hỗ trợ

Nếu cần giúp:
1. Đọc file `HUONG_DAN_ARM64.md` trước
2. Thử Google Colab theo hướng dẫn
3. Hỏi tôi nếu cần clarification

## 📊 Yêu cầu hệ thống

### Minimum (local):
- RAM: 8GB
- Disk: 5GB free space
- CPU: Bất kỳ (ARM64 OK)

### Recommended (Colab):
- Google account
- Internet connection
- Google Drive có 2GB free

## 🎯 Bước tiếp theo

1. **Đọc**: `HUONG_DAN_ARM64.md`
2. **Chọn**: Colab (nhanh) hoặc Local (chậm)
3. **Chạy**: Theo hướng dẫn tương ứng

---

**Chúc bạn thành công! 🚀🎨**

