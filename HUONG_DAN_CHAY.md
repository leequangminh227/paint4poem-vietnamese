# Hướng dẫn chạy dự án Paint4Poem

## 1. Cài đặt môi trường

### Cài đặt dependencies:
```bash
pip install --user -r requirements.txt
```

### Tải NLTK data (chạy một lần):
```python
import nltk
nltk.download('punkt')
```

## 2. Chuẩn bị dữ liệu

### Tải dữ liệu:
- [Bộ dữ liệu đầy đủ](https://drive.google.com/drive/folders/1ySx3xTq1Lzay6N-2qvqkar9TUkV2eR8q?usp=sharing)
- [Bộ mẫu nhỏ](https://drive.google.com/file/d/1iJ8WApTiVGznkU2qXcdycZjrQGYxUoOT/view?usp=sharing)

### Cấu trúc thư mục:
```
paint4poem/
├── AttnGAN/
├── MirrorGAN/
├── data/
│   └── Paint4Poem-Zikai-poem-subset/
│       ├── poem_image/
│       │   ├── train/
│       │   ├── test/
│       │   └── example_filenames.txt
│       └── ...
└── output/
```

## 3. Chạy AttnGAN

### Bước 1: Pre-train DAMSM (Text Encoder)
```bash
cd AttnGAN

# Cho dataset poem
python pretrain_DAMSM.py --cfg cfg/DAMSM/zikai_poem.yml --gpu 0

# Cho dataset caption
python pretrain_DAMSM.py --cfg cfg/DAMSM/zikai_title.yml --gpu 0
```

**Lưu ý**: Nếu không có GPU, thay `--gpu 0` bằng `--gpu -1`

### Bước 2: Train AttnGAN
```bash
# Cho dataset poem
python main_poem.py --cfg cfg/zikai_poem_attn2_.yml --gpu 0

# Cho dataset caption
python main_poem.py --cfg cfg/zikai_title_attn2_.yml --gpu 0
```

### Bước 3: Tạo ảnh (Evaluation)
```bash
# Tạo ảnh từ examples
python main_poem.py --cfg cfg/eval_try.yml --gpu 0

# Tạo ảnh cho toàn bộ validation set
# (Sửa B_VALIDATION: True trong cfg/eval_try.yml)
python main_poem.py --cfg cfg/eval_try.yml --gpu 0
```

## 4. Chạy MirrorGAN

### Bước 1: Pre-train
```bash
cd MirrorGAN

# Pre-train attention
python main_chi.py --cfg cfg/pretrain_attn/famous_poem.yml --gpu 0

# Hoặc pre-train cycle
python pretrain_chi_cycle.py --cfg cfg/pretrain_cycle/famous_poem.yml --gpu 0
```

### Bước 2: Train MirrorGAN
```bash
python main_chi.py --cfg cfg/train/lambda50/famous_poem/famous_poem_cycle.yml --gpu 0
```

### Bước 3: Evaluation
```bash
python main_chi_eval.py --cfg cfg/eval/eval_famous_poem_cycle.yml --gpu 0
```

## 5. Cấu hình quan trọng

### Sửa đường dẫn dữ liệu trong file .yml:
```yaml
DATA_DIR: '../data/Paint4Poem-Zikai-poem-subset/poem_image'
```

### Sửa GPU settings:
```yaml
GPU_ID: 0  # Đổi thành -1 nếu không có GPU
```

### Sửa đường dẫn pre-trained model:
```yaml
NET_E: '../output/zikai_poem_DAMSM_2021_04_11_22_57_32/Model/text_encoder600.pth'
```

## 6. Kết quả

- Kết quả training: `../output/`
- Ảnh được tạo ra: `../output/[tên_config]/[timestamp]/`
- Model checkpoints: `../output/[tên_config]/Model/`

## 7. Lỗi thường gặp

### Permission denied khi cài đặt:
```bash
pip install --user -r requirements.txt
```

### CUDA out of memory:
- Giảm `BATCH_SIZE` trong file .yml
- Hoặc chạy với CPU: `--gpu -1`

### Module not found:
```bash
# Đảm bảo đang ở đúng thư mục
cd AttnGAN  # hoặc cd MirrorGAN
```

### File not found (data):
- Kiểm tra đường dẫn `DATA_DIR` trong file .yml
- Đảm bảo đã tải và giải nén dữ liệu đúng vị trí

## 8. Tham khảo

Paper: [Paint4Poem: A Dataset for Artistic Visualization of Classical Chinese Poems](https://arxiv.org/abs/2109.11682)

Liên hệ:
- Dan Li: teelada520@gmail.com
- Shuai Wang: shuai.wang@student.uva.nl
