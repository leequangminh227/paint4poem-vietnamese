# 📊 Test Results - Vietnamese Poem Embeddings

## 📁 Vị trí kết quả test

Tất cả kết quả test được lưu trong thư mục:
```
test_results/
└── test_epoch_YYYYMMDD_HHMMSS.txt
```

## 🚀 Cách chạy test

```bash
python test_generation_early.py
```

Script sẽ:
1. ✅ Load model DAMSM mới nhất (epoch cao nhất)
2. ✅ Test với 5 câu thơ tiếng Việt
3. ✅ Tính cosine similarity giữa các embeddings
4. ✅ Hiển thị progress và khuyến nghị
5. ✅ **Lưu kết quả vào file** trong `test_results/`

## 📄 Nội dung file kết quả

Mỗi file test chứa:

### 1. Thông tin test
```
📝 Test time: 2025-10-06 15:35:44
✅ Loading: text_encoder50.pth (Epoch 50)
```

### 2. Vocabulary statistics
```
📚 Total vocabulary: 804 words
🔤 Sample words from vocabulary
🇻🇳 Vietnamese words with diacritics
```

### 3. Embedding analysis
```
🎨 Testing 5 Vietnamese poems:
   - Tokens extracted
   - Embedding shape: [1, 256]
   - Statistics: mean, std
   - First 5 values
```

### 4. Similarity matrix
```
📊 Cosine Similarity Matrix:
     P1    P2    P3    P4    P5
P1  1.000 0.850 0.720 0.650 0.700
P2  0.850 1.000 0.780 0.600 0.720
...
```

### 5. Training progress
```
📊 Training Progress:
   Current Epoch: 50/600 (8.3%)
   [████░░░░░░░░...] 8.3%
```

### 6. Recommendations
- Khuyến nghị dựa trên epoch hiện tại
- Action items tiếp theo
- Estimated time remaining

## 📈 So sánh kết quả qua các epoch

Bạn có thể so sánh các file test để thấy model học như thế nào:

```bash
# Epoch 0
test_results/test_epoch_20251006_135000.txt
→ Similarity matrix: tất cả = 1.000 (chưa học được gì)

# Epoch 50
test_results/test_epoch_20251007_120000.txt
→ Similarity matrix: 0.85-0.95 (bắt đầu khác biệt)

# Epoch 200
test_results/test_epoch_20251010_140000.txt
→ Similarity matrix: 0.60-0.85 (khác biệt rõ ràng)

# Epoch 400+
test_results/test_epoch_20251015_100000.txt
→ Similarity matrix: 0.40-0.75 (ổn định, sẵn sàng)
```

## 🎯 Cách đọc Similarity Matrix

### Giá trị gần 1.0 (0.9-1.0)
- **Rất giống nhau**
- Model chưa phân biệt được
- Ví dụ: Epoch 0-20

### Giá trị trung bình (0.6-0.8)
- **Tương đồng nhưng khác biệt**
- Model đang học
- Ví dụ: Epoch 50-200

### Giá trị thấp (0.4-0.6)
- **Rõ ràng khác nhau**
- Model đã học tốt
- Ví dụ: Epoch 400+

### Giá trị rất thấp (< 0.4)
- **Hoàn toàn khác biệt**
- Các câu thơ về chủ đề rất khác nhau

## 📊 Ví dụ Similarity Matrix tốt (Epoch 400+)

```
         P1(Trăng) P2(Mưa) P3(Núi) P4(Biển) P5(Gió)
P1(Trăng)  1.000    0.520    0.480    0.350    0.450
P2(Mưa)    0.520    1.000    0.550    0.680    0.600  ← Mưa & Biển (nước)
P3(Núi)    0.480    0.550    1.000    0.420    0.650  ← Núi & Gió (tự nhiên)
P4(Biển)   0.350    0.680    0.420    1.000    0.400
P5(Gió)    0.450    0.600    0.650    0.400    1.000
```

**Nhận xét:**
- Mưa & Biển có similarity cao (0.680) → cùng chủ đề nước ✅
- Núi & Gió có similarity cao (0.650) → cùng chủ đề tự nhiên ✅
- Trăng & Biển khác biệt (0.350) → chủ đề khác nhau ✅

## 🔄 Lịch test khuyến nghị

- **Epoch 0-50**: Test mỗi 10 epochs
- **Epoch 50-200**: Test mỗi 25 epochs  
- **Epoch 200-400**: Test mỗi 50 epochs
- **Epoch 400-600**: Test mỗi 100 epochs

## 💡 Tips

1. **Backup kết quả quan trọng**
   ```bash
   cp test_results/test_epoch_BEST.txt test_results/BACKUP_epoch400.txt
   ```

2. **So sánh 2 epochs**
   ```bash
   # Windows
   fc test_results\test_epoch_A.txt test_results\test_epoch_B.txt
   
   # Linux/Mac
   diff test_results/test_epoch_A.txt test_results/test_epoch_B.txt
   ```

3. **Tìm epoch tốt nhất**
   - Xem similarity matrix
   - Similarity trong khoảng 0.4-0.7 là tốt
   - Quá cao (>0.9): model chưa học
   - Quá thấp (<0.3): model overfit hoặc embeddings không ổn định

## 📋 Checklist sử dụng

- [ ] Chạy test sau mỗi 50 epochs
- [ ] So sánh similarity matrix với epoch trước
- [ ] Backup file kết quả quan trọng
- [ ] Khi similarity ổn định (0.4-0.7), bắt đầu train AttnGAN
- [ ] Giữ file test của epoch 0, 50, 100, 200, 400, 600 để so sánh

## 🎯 Mục tiêu

**Similarity matrix lý tưởng:**
- Diagonal = 1.0 (câu với chính nó)
- Off-diagonal = 0.4-0.7 (câu khác nhau)
- Các câu tương đồng có similarity cao hơn (0.6-0.7)
- Các câu khác biệt có similarity thấp hơn (0.4-0.5)

Khi đạt được điều này ở epoch 400+, model đã sẵn sàng cho AttnGAN! ✅

