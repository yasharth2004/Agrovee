# Crop Disease Detection Model

A deep learning model for detecting crop diseases using GPU acceleration with PyTorch and CUDA.

## Features

- **ResNet50 Architecture**: Transfer learning with ImageNet pretrained weights
- **GPU Acceleration**: CUDA support for fast training
- **Data Augmentation**: Comprehensive augmentation for robust predictions
- **Multi-class Classification**: Detect crop type and disease status
- **Model Evaluation**: Per-class accuracy metrics and detailed statistics

## Dataset

Download the PlantVillage dataset and update the path in `train.py`:

```python
CONFIG['dataset_path'] = r'E:\PlantVillage 2 Dataset\plantvillage dataset\color'
```

The dataset should have the following structure:
```
color/
├── Apple_Black_rot/
├── Apple_Healthy/
├── Corn_Rust/
├── Corn_Healthy/
└── ... (other classes)
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Verify CUDA is working:
```python
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

## Usage

### Training

Run the training script:
```bash
python train.py
```

The script will:
- Load and augment the dataset
- Create train/validation/test splits (80/10/10)
- Train ResNet50 for 50 epochs on GPU
- Save the best model to `./models/best_model.pth`
- Output metrics and per-class accuracy

### Configuration

Edit `CONFIG` in `train.py` to customize:
- `batch_size`: Batch size (default: 32)
- `num_epochs`: Number of training epochs (default: 50)
- `learning_rate`: Learning rate (default: 0.001)
- `img_size`: Input image size (default: 224)

### Inference

Predict on a single image:
```bash
python predict.py --image path/to/image.jpg --model ./models/best_model.pth
```

## Model Output

The training script saves:
- `best_model.pth`: Best model weights and optimizer state
- `metadata.json`: Model metadata (class names, accuracy, device info)

## Performance Metrics

After training, you'll get:
- **Overall Test Accuracy**: Accuracy across all test samples
- **Per-class Accuracy**: Accuracy for each crop/disease class
- **Validation Accuracy**: Best validation accuracy during training

## GPU Requirements

- NVIDIA GPU with CUDA compute capability 3.5+
- CUDA 11.8+ installed
- cuDNN 8.0+ installed
- Minimum 4GB GPU memory (8GB+ recommended)

## Hyperparameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| Model | ResNet50 | Pretrained on ImageNet |
| Optimizer | Adam | weight_decay=1e-4 |
| Learning Rate | 0.001 | Reduced on plateau |
| Batch Size | 32 | Adjust based on GPU memory |
| Epochs | 50 | Early stopping via LR scheduling |
| Image Size | 224x224 | Standard for ResNet50 |

## Troubleshooting

### CUDA Not Available
```
✗ GPU Not Available - Using CPU (Training will be slower)
```
- Verify NVIDIA GPU is installed
- Install CUDA Toolkit and cuDNN
- Reinstall PyTorch with CUDA support: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`

### Out of Memory (OOM)
- Reduce batch size in CONFIG: `'batch_size': 16`
- Use gradient accumulation
- Enable mixed precision training

### Dataset Not Found
Update the dataset path in `train.py`:
```python
CONFIG['dataset_path'] = r'your/path/to/dataset'
```

## Future Improvements

- [ ] Ensemble models for better accuracy
- [ ] Grad-CAM visualization of predictions
- [ ] Model pruning for inference optimization
- [ ] ONNX export for cross-platform deployment
- [ ] Web API with FastAPI
- [ ] Mobile deployment with TensorFlow Lite

## License

MIT License - Feel free to use and modify for your projects.
