# SETUP INSTRUCTIONS

## Current Status

✓ Python 3.10 configured
✓ Other dependencies installed (numpy, pandas, scikit-learn, etc.)
✗ **PyTorch installation is corrupted**

## Fix PyTorch Installation

Your PyTorch installation is corrupted. To fix it, run these commands:

### Step 1: Clean up corrupted PyTorch
```powershell
# Remove corrupted PyTorch files
Remove-Item -Recurse -Force "C:\Users\DEBANJAN\AppData\Roaming\Python\Python310\site-packages\torch*" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "C:\Users\DEBANJAN\AppData\Roaming\Python\Python310\site-packages\~orch*" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "C:\Users\DEBANJAN\AppData\Roaming\Python\Python310\site-packages\~ympy*" -ErrorAction SilentlyContinue
```

### Step 2: Free up disk space
**IMPORTANT**: The installation failed due to "No space left on device". You need to:
- Clean up your C: drive to free at least 5-10 GB
- Delete temporary files, old downloads, etc.
- Run Disk Cleanup utility

### Step 3: Install PyTorch with CUDA support
```powershell
# Install PyTorch with CUDA 11.8
&"C:/Program Files/Python310/python.exe" -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Step 4: Verify installation
```powershell
&"C:/Program Files/Python310/python.exe" e:\p1\verify_gpu.py
```

You should see:
```
✓ GPU DETECTED
  Device: [Your GPU Name]
  Memory: [X.XX GB]
```

## Alternative: Use CPU-only version

If you don't have a CUDA-compatible GPU or want to start immediately:

```powershell
# Install CPU-only PyTorch (much smaller, ~200MB)
&"C:/Program Files/Python310/python.exe" -m pip install torch torchvision torchaudio
```

**Note**: CPU training will be much slower (hours vs minutes).

## Run Training

Once PyTorch is installed correctly:

```powershell
# Start training
&"C:/Program Files/Python310/python.exe" e:\p1\train.py
```

## Project Files Created

- `train.py` - Main training script with GPU support
- `predict.py` - Inference script for single image prediction
- `verify_gpu.py` - GPU verification script
- `requirements.txt` - All dependencies
- `README.md` - Full documentation

## Next Steps

1. Fix disk space issue
2. Reinstall PyTorch with CUDA support
3. Update dataset path in train.py (line 18)
4. Run training script
