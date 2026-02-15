"""
Verify GPU and CUDA setup for PyTorch
"""

import torch
import sys

print("="*70)
print("GPU & CUDA VERIFICATION")
print("="*70)

print(f"\nPyTorch Version: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"\n✓ GPU DETECTED")
    print(f"  Device: {torch.cuda.get_device_name(0)}")
    print(f"  Capability: {torch.cuda.get_device_capability(0)}")
    print(f"  Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    print(f"  CUDA Version: {torch.version.cuda}")
    print(f"  cuDNN Version: {torch.backends.cudnn.version()}")
    
    # Test GPU
    print(f"\n  Testing GPU...")
    x = torch.randn(1000, 1000).cuda()
    y = torch.randn(1000, 1000).cuda()
    z = torch.mm(x, y)
    print(f"  ✓ GPU computation successful!")
else:
    print(f"\n✗ GPU NOT DETECTED - Using CPU")
    print(f"  Training will be significantly slower")
    print(f"  CPU: {torch.get_num_threads()} threads available")
    sys.exit(1)

print("\n" + "="*70)
