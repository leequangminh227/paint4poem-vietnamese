"""
Script so sánh kết quả test giữa các epochs
Hiển thị sự thay đổi của embeddings và similarity matrix
"""
import os
import re
from datetime import datetime

def extract_info_from_file(filepath):
    """Extract thông tin quan trọng từ file test"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    info = {}
    
    # Extract test time
    time_match = re.search(r'Test time: (.+)', content)
    info['time'] = time_match.group(1) if time_match else 'Unknown'
    
    # Extract epoch
    epoch_match = re.search(r'Loading: text_encoder(\d+)\.pth \(Epoch (\d+)\)', content)
    info['epoch'] = int(epoch_match.group(2)) if epoch_match else 0
    
    # Extract progress
    progress_match = re.search(r'Current Epoch: (\d+)/(\d+) \((.+?)%\)', content)
    if progress_match:
        info['current_epoch'] = int(progress_match.group(1))
        info['max_epoch'] = int(progress_match.group(2))
        info['progress'] = float(progress_match.group(3))
    
    # Extract embedding stats (first poem)
    emb_match = re.search(r'Embedding stats: mean=([-\d.]+), std=([-\d.]+)', content)
    if emb_match:
        info['mean'] = float(emb_match.group(1))
        info['std'] = float(emb_match.group(2))
    
    # Extract similarity matrix
    sim_section = re.search(r'Cosine Similarity Matrix:\s+.+?\n((?:P\d+.+?\n)+)', content, re.DOTALL)
    if sim_section:
        sim_lines = sim_section.group(1).strip().split('\n')
        info['similarity_matrix'] = []
        for line in sim_lines:
            values = re.findall(r'(\d+\.\d+)', line)
            if values:
                info['similarity_matrix'].append([float(v) for v in values])
    
    return info

def compare_epochs(file1, file2):
    """So sánh 2 epochs"""
    print("\n" + "=" * 70)
    print(" " * 15 + "📊 COMPARISON OF TEST RESULTS")
    print("=" * 70)
    
    info1 = extract_info_from_file(file1)
    info2 = extract_info_from_file(file2)
    
    print(f"\n{'Item':<30} {'Epoch {}'.format(info1.get('epoch', 0)):<20} {'Epoch {}'.format(info2.get('epoch', 0)):<20}")
    print("-" * 70)
    
    # Time
    print(f"{'Test Time':<30} {info1.get('time', 'N/A'):<20} {info2.get('time', 'N/A'):<20}")
    
    # Progress
    prog1 = f"{info1.get('progress', 0):.1f}%" if 'progress' in info1 else 'N/A'
    prog2 = f"{info2.get('progress', 0):.1f}%" if 'progress' in info2 else 'N/A'
    print(f"{'Progress':<30} {prog1:<20} {prog2:<20}")
    
    # Embedding stats
    if 'mean' in info1 and 'mean' in info2:
        mean1 = f"{info1['mean']:.4f}"
        mean2 = f"{info2['mean']:.4f}"
        mean_diff = info2['mean'] - info1['mean']
        mean_change = f"({mean_diff:+.4f})"
        print(f"{'Embedding Mean':<30} {mean1:<20} {mean2 + ' ' + mean_change}")
        
        std1 = f"{info1['std']:.4f}"
        std2 = f"{info2['std']:.4f}"
        std_diff = info2['std'] - info1['std']
        std_change = f"({std_diff:+.4f})"
        print(f"{'Embedding Std':<30} {std1:<20} {std2 + ' ' + std_change}")
    
    # Similarity matrix comparison
    if 'similarity_matrix' in info1 and 'similarity_matrix' in info2:
        print("\n" + "=" * 70)
        print("SIMILARITY MATRIX COMPARISON")
        print("=" * 70)
        
        matrix1 = info1['similarity_matrix']
        matrix2 = info2['similarity_matrix']
        
        if len(matrix1) == len(matrix2) and len(matrix1[0]) == len(matrix2[0]):
            n = len(matrix1)
            
            # Calculate statistics
            off_diag_vals1 = []
            off_diag_vals2 = []
            
            for i in range(n):
                for j in range(n):
                    if i != j:
                        off_diag_vals1.append(matrix1[i][j])
                        off_diag_vals2.append(matrix2[i][j])
            
            avg1 = sum(off_diag_vals1) / len(off_diag_vals1) if off_diag_vals1 else 0
            avg2 = sum(off_diag_vals2) / len(off_diag_vals2) if off_diag_vals2 else 0
            
            min1 = min(off_diag_vals1) if off_diag_vals1 else 0
            min2 = min(off_diag_vals2) if off_diag_vals2 else 0
            
            max1 = max(off_diag_vals1) if off_diag_vals1 else 0
            max2 = max(off_diag_vals2) if off_diag_vals2 else 0
            
            print(f"\n{'Metric':<30} {'Epoch {}'.format(info1.get('epoch', 0)):<20} {'Epoch {}'.format(info2.get('epoch', 0)):<20} {'Change':<15}")
            print("-" * 85)
            print(f"{'Off-diagonal Average':<30} {avg1:.4f}{' '*16} {avg2:.4f}{' '*16} {avg2-avg1:+.4f}")
            print(f"{'Off-diagonal Min':<30} {min1:.4f}{' '*16} {min2:.4f}{' '*16} {min2-min1:+.4f}")
            print(f"{'Off-diagonal Max':<30} {max1:.4f}{' '*16} {max2:.4f}{' '*16} {max2-max1:+.4f}")
            print(f"{'Off-diagonal Range':<30} {max1-min1:.4f}{' '*16} {max2-min2:.4f}{' '*16} {(max2-min2)-(max1-min1):+.4f}")
            
            # Interpretation
            print("\n💡 Interpretation:")
            if avg1 > 0.95 and avg2 > 0.95:
                print("   ⚠️  Both epochs show very high similarity (>0.95)")
                print("   → Model hasn't learned to differentiate yet")
            elif avg1 > 0.95 and avg2 < 0.90:
                print("   ✅ Significant improvement!")
                print("   → Model is starting to learn differences")
            elif avg2 < avg1:
                print("   ✅ Similarity decreased (good!)")
                print("   → Model is learning to differentiate poems")
            else:
                print("   ⚠️  Similarity increased")
                print("   → May need more training or check for issues")
            
            # Range analysis
            range_diff = (max2-min2) - (max1-min1)
            if range_diff > 0.1:
                print("\n   ✅ Range increased significantly")
                print("   → Model shows more varied responses to different poems")
            elif range_diff < -0.05:
                print("\n   ⚠️  Range decreased")
                print("   → Embeddings becoming more uniform (may be an issue)")
        else:
            print("⚠️  Matrix dimensions don't match, can't compare")
    
    print("\n" + "=" * 70)

def list_available_tests():
    """List tất cả test results"""
    if not os.path.exists('test_results'):
        print("❌ No test_results directory found!")
        return []
    
    files = sorted([f for f in os.listdir('test_results') if f.endswith('.txt')])
    
    if not files:
        print("❌ No test result files found!")
        return []
    
    print("\n" + "=" * 70)
    print("AVAILABLE TEST RESULTS")
    print("=" * 70)
    
    for i, f in enumerate(files, 1):
        filepath = f'test_results/{f}'
        info = extract_info_from_file(filepath)
        epoch = info.get('epoch', 0)
        time = info.get('time', 'Unknown')
        size_kb = os.path.getsize(filepath) / 1024
        print(f"{i:2d}. {f:<40} Epoch {epoch:3d}  {time}  ({size_kb:.1f} KB)")
    
    return files

def main():
    """Main function"""
    print("\n" + "=" * 70)
    print(" " * 10 + "🔍 COMPARE TEST RESULTS - Vietnamese Poems")
    print("=" * 70)
    
    files = list_available_tests()
    
    if len(files) < 2:
        print("\n⚠️  Need at least 2 test result files to compare!")
        print("   Run: python test_generation_early.py")
        return
    
    print("\n" + "=" * 70)
    print("SELECT FILES TO COMPARE")
    print("=" * 70)
    
    try:
        print("\nEnter the number of the FIRST file (older epoch):")
        idx1 = int(input("> ")) - 1
        
        print("\nEnter the number of the SECOND file (newer epoch):")
        idx2 = int(input("> ")) - 1
        
        if idx1 < 0 or idx1 >= len(files) or idx2 < 0 or idx2 >= len(files):
            print("❌ Invalid selection!")
            return
        
        file1 = f'test_results/{files[idx1]}'
        file2 = f'test_results/{files[idx2]}'
        
        compare_epochs(file1, file2)
        
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

