"""
Script tự động hóa toàn bộ quy trình training cho dữ liệu thơ tiếng Việt
"""
import os
import sys
import glob
import argparse
from pathlib import Path

def find_latest_checkpoint(pattern):
    """Tìm checkpoint mới nhất"""
    files = glob.glob(pattern)
    if not files:
        return None
    # Sắp xếp theo thời gian sửa đổi
    return max(files, key=os.path.getmtime)

def update_config_file(config_path, updates):
    """Cập nhật file config YAML"""
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in updates.items():
        content = content.replace(old, new)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Đã cập nhật {config_path}")

def step_prepare_data():
    """Bước 1: Chuẩn bị dữ liệu"""
    print("\n" + "="*80)
    print("BƯỚC 1: CHUẨN BỊ DỮ LIỆU")
    print("="*80)
    
    if os.path.exists('data/vietnamese_poems'):
        print("Dữ liệu đã được chuẩn bị trước đó.")
        response = input("Bạn có muốn chuẩn bị lại? (y/N): ").strip().lower()
        if response != 'y':
            print("Bỏ qua bước chuẩn bị dữ liệu.")
            return True
    
    print("Chạy script chuẩn bị dữ liệu...")
    ret = os.system('python prepare_vietnamese_data.py')
    
    if ret == 0:
        print("✅ Chuẩn bị dữ liệu thành công!")
        return True
    else:
        print("❌ Lỗi khi chuẩn bị dữ liệu!")
        return False

def step_pretrain_damsm(gpu_id):
    """Bước 2: Pre-train DAMSM"""
    print("\n" + "="*80)
    print("BƯỚC 2: PRE-TRAIN DAMSM (TEXT ENCODER)")
    print("="*80)
    
    # Kiểm tra xem đã có checkpoint DAMSM chưa
    damsm_pattern = '../output/vietnamese_poem_DAMSM_*/Model/text_encoder*.pth'
    existing = find_latest_checkpoint(damsm_pattern)
    
    if existing:
        print(f"Đã tìm thấy checkpoint DAMSM: {existing}")
        response = input("Bạn có muốn train lại từ đầu? (y/N): ").strip().lower()
        if response != 'y':
            print("Sử dụng checkpoint có sẵn.")
            return existing
    
    print("Bắt đầu pre-train DAMSM...")
    print("Lưu ý: Quá trình này có thể mất vài giờ đến vài ngày tùy GPU!")
    print("Nhấn Ctrl+C để dừng training.\n")
    
    os.chdir('AttnGAN')
    cmd = f'python pretrain_DAMSM.py --cfg cfg/DAMSM/vietnamese_poem.yml --gpu {gpu_id}'
    print(f"Chạy lệnh: {cmd}\n")
    
    ret = os.system(cmd)
    os.chdir('..')
    
    if ret == 0 or ret == 2:  # 0 = success, 2 = Ctrl+C
        # Tìm checkpoint mới nhất
        checkpoint = find_latest_checkpoint(damsm_pattern)
        if checkpoint:
            print(f"\n✅ Pre-train DAMSM hoàn tất! Checkpoint: {checkpoint}")
            return checkpoint
    
    print("\n❌ Lỗi khi pre-train DAMSM!")
    return None

def step_train_attngan(gpu_id, damsm_checkpoint):
    """Bước 3: Train AttnGAN"""
    print("\n" + "="*80)
    print("BƯỚC 3: TRAIN ATTNGAN")
    print("="*80)
    
    # Cập nhật config với checkpoint DAMSM
    config_path = 'AttnGAN/cfg/vietnamese_poem_attn2.yml'
    print(f"Cập nhật đường dẫn DAMSM checkpoint trong {config_path}...")
    
    # Đọc và tìm dòng NET_E
    with open(config_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    with open(config_path, 'w', encoding='utf-8') as f:
        for line in lines:
            if 'NET_E:' in line and 'vietnamese_poem_DAMSM' in line:
                # Thay thế bằng đường dẫn thực tế
                indent = len(line) - len(line.lstrip())
                f.write(' ' * indent + f"NET_E: '{damsm_checkpoint}'\n")
                print(f"  Cập nhật NET_E: {damsm_checkpoint}")
            else:
                f.write(line)
    
    print("\nBắt đầu train AttnGAN...")
    print("Lưu ý: Quá trình này có thể mất vài giờ đến vài ngày tùy GPU!")
    print("Nhấn Ctrl+C để dừng training.\n")
    
    os.chdir('AttnGAN')
    cmd = f'python main_poem.py --cfg cfg/vietnamese_poem_attn2.yml --gpu {gpu_id}'
    print(f"Chạy lệnh: {cmd}\n")
    
    ret = os.system(cmd)
    os.chdir('..')
    
    if ret == 0 or ret == 2:  # 0 = success, 2 = Ctrl+C
        # Tìm checkpoint mới nhất
        pattern = '../output/vietnamese_attn_*/Model/netG_epoch_*.pth'
        checkpoint = find_latest_checkpoint(pattern)
        if checkpoint:
            print(f"\n✅ Train AttnGAN hoàn tất! Checkpoint: {checkpoint}")
            return checkpoint
    
    print("\n❌ Lỗi khi train AttnGAN!")
    return None

def step_evaluate(gpu_id, attngan_checkpoint, damsm_checkpoint):
    """Bước 4: Evaluation"""
    print("\n" + "="*80)
    print("BƯỚC 4: GENERATE ẢNH TỪ THƠ")
    print("="*80)
    
    if not attngan_checkpoint or not damsm_checkpoint:
        print("❌ Cần có checkpoint AttnGAN và DAMSM để evaluate!")
        return False
    
    # Cập nhật config
    config_path = 'AttnGAN/cfg/eval_vietnamese.yml'
    print(f"Cập nhật đường dẫn checkpoint trong {config_path}...")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    with open(config_path, 'w', encoding='utf-8') as f:
        for line in lines:
            if 'NET_G:' in line and 'vietnamese_attn' in line:
                indent = len(line) - len(line.lstrip())
                f.write(' ' * indent + f"NET_G: '{attngan_checkpoint}'\n")
                print(f"  Cập nhật NET_G: {attngan_checkpoint}")
            elif 'NET_E:' in line and 'vietnamese_poem_DAMSM' in line:
                indent = len(line) - len(line.lstrip())
                f.write(' ' * indent + f"NET_E: '{damsm_checkpoint}'\n")
                print(f"  Cập nhật NET_E: {damsm_checkpoint}")
            else:
                f.write(line)
    
    print("\nGenerate ảnh từ examples...")
    
    os.chdir('AttnGAN')
    cmd = f'python main_poem.py --cfg cfg/eval_vietnamese.yml --gpu {gpu_id}'
    print(f"Chạy lệnh: {cmd}\n")
    
    ret = os.system(cmd)
    os.chdir('..')
    
    if ret == 0:
        print("\n✅ Evaluation hoàn tất!")
        print("Kiểm tra kết quả tại: ../output/eval_vietnamese_*/")
        return True
    
    print("\n❌ Lỗi khi evaluate!")
    return False

def main():
    parser = argparse.ArgumentParser(description='Training pipeline cho thơ tiếng Việt')
    parser.add_argument('--gpu', type=int, default=0, 
                        help='GPU ID (sử dụng -1 cho CPU)')
    parser.add_argument('--step', type=str, default='all',
                        choices=['all', 'prepare', 'damsm', 'attngan', 'eval'],
                        help='Bước cần chạy')
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("PIPELINE TRAINING THƠ TIẾNG VIỆT - ATTNGAN")
    print("="*80)
    print(f"GPU: {'CPU' if args.gpu == -1 else f'GPU {args.gpu}'}")
    print(f"Bước: {args.step}")
    print("="*80)
    
    damsm_checkpoint = None
    attngan_checkpoint = None
    
    # Bước 1: Chuẩn bị dữ liệu
    if args.step in ['all', 'prepare']:
        if not step_prepare_data():
            print("\n❌ Pipeline dừng do lỗi ở bước chuẩn bị dữ liệu!")
            return
    
    # Bước 2: Pre-train DAMSM
    if args.step in ['all', 'damsm']:
        damsm_checkpoint = step_pretrain_damsm(args.gpu)
        if not damsm_checkpoint and args.step == 'all':
            print("\n❌ Pipeline dừng do lỗi ở bước pre-train DAMSM!")
            return
    
    # Nếu chỉ chạy bước sau, tìm checkpoint có sẵn
    if args.step in ['attngan', 'eval'] and not damsm_checkpoint:
        pattern = '../output/vietnamese_poem_DAMSM_*/Model/text_encoder*.pth'
        damsm_checkpoint = find_latest_checkpoint(pattern)
        if not damsm_checkpoint:
            print("❌ Không tìm thấy DAMSM checkpoint! Chạy bước 'damsm' trước.")
            return
        print(f"Sử dụng DAMSM checkpoint: {damsm_checkpoint}")
    
    # Bước 3: Train AttnGAN
    if args.step in ['all', 'attngan']:
        attngan_checkpoint = step_train_attngan(args.gpu, damsm_checkpoint)
        if not attngan_checkpoint and args.step == 'all':
            print("\n❌ Pipeline dừng do lỗi ở bước train AttnGAN!")
            return
    
    # Nếu chỉ chạy eval, tìm checkpoint có sẵn
    if args.step == 'eval' and not attngan_checkpoint:
        pattern = '../output/vietnamese_attn_*/Model/netG_epoch_*.pth'
        attngan_checkpoint = find_latest_checkpoint(pattern)
        if not attngan_checkpoint:
            print("❌ Không tìm thấy AttnGAN checkpoint! Chạy bước 'attngan' trước.")
            return
        print(f"Sử dụng AttnGAN checkpoint: {attngan_checkpoint}")
    
    # Bước 4: Evaluation
    if args.step in ['all', 'eval']:
        step_evaluate(args.gpu, attngan_checkpoint, damsm_checkpoint)
    
    print("\n" + "="*80)
    print("✅ HOÀN TẤT PIPELINE!")
    print("="*80)
    print("\nTóm tắt checkpoint:")
    if damsm_checkpoint:
        print(f"  DAMSM: {damsm_checkpoint}")
    if attngan_checkpoint:
        print(f"  AttnGAN: {attngan_checkpoint}")
    print("\nKiểm tra kết quả tại thư mục ../output/")

if __name__ == '__main__':
    main()

