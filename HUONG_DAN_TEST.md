# 🧪 Hướng Dẫn Test Model Vietnamese Poem

## 📋 Tổng Quan

Hệ thống test giúp bạn:
- ✅ Kiểm tra model đã học được gì sau mỗi epoch
- ✅ So sánh embeddings giữa các checkpoint
- ✅ Quyết định khi nào bắt đầu train AttnGAN
- ✅ Lưu lại lịch sử training để phân tích

---

## 🚀 1. Test Model Hiện Tại

### Chạy test:
```bash
python test_generation_early.py
```

### Script sẽ:
1. Tự động tìm model epoch cao nhất
2. Test với 5 câu thơ tiếng Việt
3. Tính cosine similarity
4. Hiển thị progress bar
5. **Lưu kết quả vào `test_results/test_epoch_TIMESTAMP.txt`**

### Kết quả hiển thị:
```
============================================================
LOADING TRAINED DAMSM MODELS...
============================================================
📂 Model directory: output/vietnamese_poem_DAMSM_.../Model
📄 Found 4 model files:
   - text_encoder0.pth (2.60 MB)
   - text_encoder50.pth (2.60 MB)    ← EPOCH 50

✅ Loading: text_encoder50.pth (Epoch 50)

📊 Training Progress:
   Current Epoch: 50/600 (8.3%)
   [████░░░░░░░░░░░░░░░░░░░░░░░] 8.3%

💡 Next steps:
   🔄 Model is learning (epoch 50-200)
   → Embeddings starting to differentiate
   → Test again every 50 epochs

💾 Results saved to: test_results/test_epoch_20251006_153544.txt
```

---

## 📊 2. So Sánh Giữa Các Epochs

### Chạy so sánh:
```bash
python compare_test_results.py
```

### Script sẽ:
1. Hiển thị danh sách tất cả test results
2. Yêu cầu chọn 2 files để so sánh
3. Tính toán sự thay đổi:
   - Embedding mean/std
   - Similarity matrix statistics
   - Range của similarities
4. Đưa ra nhận xét

### Ví dụ output:
```
AVAILABLE TEST RESULTS
============================================================
 1. test_epoch_20251006_130000.txt  Epoch   0  (4.2 KB)
 2. test_epoch_20251007_120000.txt  Epoch  50  (4.3 KB)
 3. test_epoch_20251010_140000.txt  Epoch 200  (4.4 KB)

SELECT FILES TO COMPARE
============================================================
Enter the number of the FIRST file (older epoch):
> 1
Enter the number of the SECOND file (newer epoch):
> 2

============================================================
          📊 COMPARISON OF TEST RESULTS
============================================================

Metric                         Epoch 0              Epoch 50             Change         
---------------------------------------------------------------------------------
Off-diagonal Average          0.9980               0.7850               -0.2130
Off-diagonal Min              0.9950               0.6200               -0.3750
Off-diagonal Max              1.0000               0.9100               -0.0900
Off-diagonal Range            0.0050               0.2900               +0.2850

💡 Interpretation:
   ✅ Similarity decreased (good!)
   → Model is learning to differentiate poems
   
   ✅ Range increased significantly
   → Model shows more varied responses to different poems
```

---

## 📈 3. Lịch Trình Test Khuyến Nghị

### Giai đoạn Early Training (Epoch 0-50)
**Tần suất:** Mỗi 10 epochs
```bash
python test_generation_early.py
```
**Mục đích:** Theo dõi model có bắt đầu học chưa

### Giai đoạn Learning (Epoch 50-200)
**Tần suất:** Mỗi 25 epochs
```bash
python test_generation_early.py
python compare_test_results.py  # So sánh với epoch trước
```
**Mục đích:** Xem embeddings có differentiate không

### Giai đoạn Converging (Epoch 200-400)
**Tần suất:** Mỗi 50 epochs
```bash
python test_generation_early.py
python compare_test_results.py
```
**Mục đích:** Theo dõi sự ổn định của embeddings

### Giai đoạn Final (Epoch 400-600)
**Tần suất:** Mỗi 100 epochs
```bash
python test_generation_early.py
```
**Mục đích:** Xác nhận model đã converge

---

## 🎯 4. Cách Đánh Giá Kết Quả

### A. Similarity Matrix

#### ❌ CHƯA TỐT (Epoch 0-50)
```
     P1    P2    P3    P4    P5
P1  1.000 0.998 0.999 0.997 0.998
P2  0.998 1.000 0.999 0.998 0.999
...
```
- **Vấn đề:** Tất cả similarities > 0.99
- **Nguyên nhân:** Model chưa học được gì
- **Giải pháp:** Đợi thêm epochs

#### ⚠️ ĐANG HỌC (Epoch 50-200)
```
     P1    P2    P3    P4    P5
P1  1.000 0.850 0.820 0.780 0.810
P2  0.850 1.000 0.860 0.830 0.840
...
```
- **Tình trạng:** Similarities trong khoảng 0.75-0.90
- **Ý nghĩa:** Model bắt đầu phân biệt
- **Hành động:** Tiếp tục training, test định kỳ

#### ✅ TỐT (Epoch 200-400)
```
     P1    P2    P3    P4    P5
P1  1.000 0.620 0.580 0.450 0.530
P2  0.620 1.000 0.650 0.680 0.600  ← Mưa & Biển (nước)
P3  0.580 0.650 1.000 0.520 0.650  ← Núi & Mây
P4  0.450 0.680 0.520 1.000 0.480
P5  0.530 0.600 0.650 0.480 1.000
```
- **Đặc điểm:**
  - Similarities trong khoảng 0.40-0.70
  - Các câu tương tự có similarity cao hơn
  - Các câu khác biệt có similarity thấp hơn
- **Ý nghĩa:** Model đã học tốt!
- **Hành động:** Sẵn sàng train AttnGAN

### B. Embedding Statistics

#### Epoch 0 (Chưa học)
```
Embedding stats: mean=-0.0040, std=0.0747
First 5 values: [-0.0110, -0.0379, 0.0221, -0.0054, 0.0142]
```
- Tất cả embeddings giống nhau

#### Epoch 50+ (Đang học)
```
Embedding stats: mean=-0.0120, std=0.1250
First 5 values: [-0.0850, -0.1220, 0.0680, -0.0320, 0.0950]
```
- Mean và std thay đổi
- First 5 values khác biệt giữa các câu thơ

#### Epoch 200+ (Học tốt)
```
Poem 1: mean=0.0250, std=0.1850
Poem 2: mean=-0.0380, std=0.1620
Poem 3: mean=0.0520, std=0.2100
```
- Mỗi câu thơ có mean/std riêng biệt
- Phạm vi giá trị rộng hơn

---

## 🔍 5. Troubleshooting

### Vấn đề 1: Similarity vẫn > 0.95 sau epoch 100
**Nguyên nhân:**
- Learning rate quá thấp
- Batch size quá nhỏ
- Training bị stuck

**Giải pháp:**
```bash
# Kiểm tra training có đang chạy không
# Xem log file hoặc training output
cd AttnGAN
# Kiểm tra loss có giảm không
```

### Vấn đề 2: Similarity dao động mạnh
**Nguyên nhân:**
- Model chưa ổn định
- Learning rate quá cao

**Giải pháp:**
- Đợi thêm epochs (đến 400-600)
- So sánh nhiều checkpoints

### Vấn đề 3: Không tìm thấy model files
**Lỗi:**
```
❌ Không tìm thấy model đã train!
```

**Giải pháp:**
```bash
# Kiểm tra thư mục output
ls output/vietnamese_poem_DAMSM_*/Model/

# Đảm bảo đã train ít nhất 1 epoch
```

---

## 📁 6. Cấu Trúc Files

```
paint4poem/
├── test_generation_early.py        # Script test chính
├── compare_test_results.py         # Script so sánh
├── TEST_RESULTS_README.md          # Hướng dẫn đọc kết quả
├── HUONG_DAN_TEST.md               # File này
│
├── test_results/                   # Thư mục lưu kết quả
│   ├── test_epoch_20251006_130000.txt  # Epoch 0
│   ├── test_epoch_20251007_120000.txt  # Epoch 50
│   └── test_epoch_20251010_140000.txt  # Epoch 200
│
└── output/
    └── vietnamese_poem_DAMSM_.../
        └── Model/
            ├── text_encoder0.pth
            ├── text_encoder50.pth
            └── ...
```

---

## 🎓 7. Best Practices

### ✅ DO:
- Test mỗi 50 epochs
- Backup file test quan trọng (epoch 0, 50, 100, 200, 400, 600)
- So sánh với epoch trước để thấy tiến triển
- Đọc similarity matrix để hiểu model học gì

### ❌ DON'T:
- Test quá thường xuyên (tốn thời gian)
- Xóa file test cũ (mất lịch sử)
- Bỏ qua similarity matrix
- Train AttnGAN khi similarity > 0.85

---

## 🚀 8. Workflow Hoàn Chỉnh

### Bước 1: Training DAMSM
```bash
cd AttnGAN
python pretrain_DAMSM.py --cfg cfg/DAMSM/vietnamese_poem.yml --gpu -1
```

### Bước 2: Test định kỳ (Terminal riêng)
```bash
# Mỗi 50 epochs, chạy:
python test_generation_early.py
```

### Bước 3: So sánh tiến triển
```bash
# Sau mỗi lần test, so sánh:
python compare_test_results.py
```

### Bước 4: Quyết định tiếp theo
```
IF similarity < 0.70 AND epoch >= 400:
    → ✅ Sẵn sàng train AttnGAN!
    → python run_vietnamese_training.py --gpu -1 --step attngan
ELSE:
    → ⏳ Tiếp tục training DAMSM
```

---

## 📞 9. Tham Khảo Nhanh

### Lệnh thường dùng:
```bash
# Test model hiện tại
python test_generation_early.py

# So sánh 2 epochs
python compare_test_results.py

# Xem danh sách test results
ls test_results/

# Xem nội dung file test
cat test_results/test_epoch_TIMESTAMP.txt

# Xem model đã train
ls output/vietnamese_poem_DAMSM_*/Model/
```

### Target Metrics:
```
Epoch 0-50:   Similarity 0.95-1.00   (Chưa học)
Epoch 50-200: Similarity 0.75-0.90   (Đang học)
Epoch 200+:   Similarity 0.40-0.70   (Học tốt) ✅
```

---

## ✅ Checklist

Trước khi train AttnGAN, đảm bảo:
- [ ] Đã train DAMSM ít nhất 400 epochs
- [ ] Similarity matrix có range 0.40-0.70
- [ ] Đã test ít nhất 5 checkpoints khác nhau
- [ ] Đã so sánh và thấy sự tiến triển rõ ràng
- [ ] Embeddings của các câu thơ khác nhau rõ rệt
- [ ] Đã backup file test quan trọng

Khi tất cả ✅, bạn sẵn sàng! 🚀

```bash
python run_vietnamese_training.py --gpu -1 --step attngan
```

