"""
Crop Disease Detection Model Training
Trains a ResNet50 model on GPU to detect crop diseases
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms, models
import os
import json
from pathlib import Path
from tqdm import tqdm
import numpy as np
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    'dataset_path': r'E:\PlantVillage 2 Dataset\plantvillage dataset\color',
    'model_save_dir': './models',
    'logs_dir': './logs',
    'batch_size': 32,
    'num_epochs': 100,  # Increased for reaching >99% accuracy
    'learning_rate': 0.0005,  # Lower LR for better convergence
    'weight_decay': 1e-4,
    'num_workers': 0,  # Set to 0 for Windows compatibility
    'train_split': 0.8,
    'val_split': 0.1,
    'test_split': 0.1,
    'img_size': 224,
    'model_name': 'resnet50',
    'target_accuracy': 99.0,  # Target validation accuracy
    'early_stop_patience': 20,  # Stop if no improvement for 20 epochs
    'force_gpu': True,  # Force GPU usage only
}

# ============================================================================
# DEVICE SETUP
# ============================================================================

def setup_device():
    """Setup GPU device (force GPU only)"""
    if CONFIG['force_gpu']:
        if not torch.cuda.is_available():
            print("✗ ERROR: GPU/CUDA not available but force_gpu=True")
            print("  Please ensure CUDA is properly installed and GPU is available")
            exit(1)
        
        device = torch.device("cuda")
        print(f"✓ GPU Available: {torch.cuda.get_device_name(0)}")
        print(f"  CUDA Version: {torch.version.cuda}")
        print(f"  GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    else:
        if torch.cuda.is_available():
            device = torch.device("cuda")
            print(f"✓ GPU Available: {torch.cuda.get_device_name(0)}")
        else:
            device = torch.device("cpu")
            print("✗ GPU Not Available - Using CPU (Training will be slower)")
    
    return device

# ============================================================================
# DATA LOADING
# ============================================================================

def get_data_transforms():
    """Define data augmentation and normalization transforms"""
    train_transform = transforms.Compose([
        transforms.Resize((CONFIG['img_size'], CONFIG['img_size'])),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    
    val_test_transform = transforms.Compose([
        transforms.Resize((CONFIG['img_size'], CONFIG['img_size'])),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    
    return train_transform, val_test_transform

def load_data():
    """Load dataset and create train/val/test splits"""
    print("\n" + "="*70)
    print("LOADING DATA")
    print("="*70)
    
    dataset_path = CONFIG['dataset_path']
    
    if not os.path.exists(dataset_path):
        print(f"✗ Dataset not found at: {dataset_path}")
        print("Please update CONFIG['dataset_path'] with the correct path")
        return None, None, None, None, None
    
    train_transform, val_test_transform = get_data_transforms()
    
    # Load full dataset
    full_dataset = datasets.ImageFolder(root=dataset_path, transform=train_transform)
    class_names = full_dataset.classes
    num_classes = len(class_names)
    
    print(f"✓ Dataset loaded: {len(full_dataset)} images")
    print(f"✓ Number of classes: {num_classes}")
    print(f"✓ Classes: {', '.join(class_names)}")
    
    # Calculate split sizes
    train_size = int(len(full_dataset) * CONFIG['train_split'])
    val_size = int(len(full_dataset) * CONFIG['val_split'])
    test_size = len(full_dataset) - train_size - val_size
    
    # Create splits
    train_dataset, val_dataset, test_dataset = random_split(
        full_dataset, [train_size, val_size, test_size]
    )
    
    # Apply appropriate transforms to each split
    val_dataset.dataset.transform = val_test_transform
    test_dataset.dataset.transform = val_test_transform
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=CONFIG['batch_size'],
        shuffle=True,
        num_workers=CONFIG['num_workers'],
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=CONFIG['batch_size'],
        shuffle=False,
        num_workers=CONFIG['num_workers'],
        pin_memory=True
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=CONFIG['batch_size'],
        shuffle=False,
        num_workers=CONFIG['num_workers'],
        pin_memory=True
    )
    
    print(f"✓ Train samples: {len(train_dataset)}")
    print(f"✓ Val samples: {len(val_dataset)}")
    print(f"✓ Test samples: {len(test_dataset)}")
    
    return train_loader, val_loader, test_loader, class_names, num_classes

# ============================================================================
# MODEL
# ============================================================================

def create_model(num_classes, device):
    """Create ResNet50 model with transfer learning"""
    print("\n" + "="*70)
    print("CREATING MODEL")
    print("="*70)
    
    # Load pretrained ResNet50
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
    
    # Replace final fully connected layer
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, num_classes)
    
    model = model.to(device)
    
    print(f"✓ Model: {CONFIG['model_name'].upper()}")
    print(f"✓ Transfer Learning: Pretrained on ImageNet")
    print(f"✓ Output classes: {num_classes}")
    
    return model

# ============================================================================
# TRAINING
# ============================================================================

def train_epoch(model, train_loader, criterion, optimizer, device, epoch, total_epochs):
    """Train for one epoch"""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    progress_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{total_epochs}", unit="batch")
    
    for batch_idx, (images, labels) in enumerate(progress_bar):
        images, labels = images.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        
        progress_bar.set_postfix({
            'loss': f'{running_loss / (batch_idx + 1):.4f}',
            'acc': f'{100 * correct / total:.2f}%'
        })
    
    epoch_loss = running_loss / len(train_loader)
    epoch_acc = 100 * correct / total
    
    return epoch_loss, epoch_acc

def validate(model, val_loader, criterion, device):
    """Validate model"""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    epoch_loss = running_loss / len(val_loader)
    epoch_acc = 100 * correct / total
    
    return epoch_loss, epoch_acc

def train_model(model, train_loader, val_loader, device, num_classes):
    """Full training loop with target accuracy and early stopping"""
    print("\n" + "="*70)
    print("TRAINING")
    print("="*70)
    print(f"Target: {CONFIG['target_accuracy']}% validation accuracy")
    print(f"Max epochs: {CONFIG['num_epochs']}")
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), 
                          lr=CONFIG['learning_rate'],
                          weight_decay=CONFIG['weight_decay'])
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=5
    )
    
    # Create save directory
    os.makedirs(CONFIG['model_save_dir'], exist_ok=True)
    
    best_val_acc = 0.0
    best_epoch = 0
    epochs_no_improve = 0
    target_reached = False
    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
    
    for epoch in range(CONFIG['num_epochs']):
        train_loss, train_acc = train_epoch(
            model, train_loader, criterion, optimizer, device, epoch, CONFIG['num_epochs']
        )
        
        val_loss, val_acc = validate(model, val_loader, criterion, device)
        
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        
        print(f"\nEpoch {epoch+1}/{CONFIG['num_epochs']}")
        print(f"  Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"  Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.2f}%")
        print(f"  Learning Rate: {optimizer.param_groups[0]['lr']:.6f}")
        
        scheduler.step(val_loss)
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_epoch = epoch
            epochs_no_improve = 0
            checkpoint = {
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
                'history': history,
            }
            model_path = os.path.join(CONFIG['model_save_dir'], f'best_model.pth')
            torch.save(checkpoint, model_path)
            print(f"  ✓ Best model saved! (Epoch {best_epoch+1})")
            
            # Check if target reached
            if val_acc > CONFIG['target_accuracy']:
                if not target_reached:
                    print(f"  \n🎯 TARGET REACHED! Validation accuracy: {val_acc:.2f}% > {CONFIG['target_accuracy']}%")
                    target_reached = True
        else:
            epochs_no_improve += 1
        
        # Early stopping if target reached and no improvement
        if target_reached and epochs_no_improve >= 10:
            print(f"\n✓ Early stopping: Target reached and no improvement for {epochs_no_improve} epochs")
            break
        
        # Early stopping if no improvement for patience epochs
        if epochs_no_improve >= CONFIG['early_stop_patience']:
            print(f"\n✓ Early stopping: No improvement for {CONFIG['early_stop_patience']} epochs")
            break
    
    print(f"\n✓ Training completed!")
    print(f"✓ Best validation accuracy: {best_val_acc:.2f}% (Epoch {best_epoch+1})")
    if best_val_acc > CONFIG['target_accuracy']:
        print(f"✓ Target accuracy {CONFIG['target_accuracy']}% ACHIEVED!")
    else:
        print(f"⚠ Target accuracy {CONFIG['target_accuracy']}% not reached. Best: {best_val_acc:.2f}%")
    
    return best_val_acc, history

# ============================================================================
# TESTING & EVALUATION
# ============================================================================

def test_model(model, test_loader, device, class_names):
    """Test model and compute metrics"""
    print("\n" + "="*70)
    print("TESTING")
    print("="*70)
    
    model.eval()
    correct = 0
    total = 0
    class_correct = [0] * len(class_names)
    class_total = [0] * len(class_names)
    
    with torch.no_grad():
        for images, labels in tqdm(test_loader, desc="Testing"):
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
            for i in range(len(class_names)):
                mask = labels == i
                class_correct[i] += (predicted[mask] == labels[mask]).sum().item()
                class_total[i] += mask.sum().item()
    
    overall_acc = 100 * correct / total
    
    print(f"\n✓ Overall Test Accuracy: {overall_acc:.2f}%")
    print(f"\nPer-class accuracy:")
    for i, class_name in enumerate(class_names):
        if class_total[i] > 0:
            acc = 100 * class_correct[i] / class_total[i]
            print(f"  {class_name}: {acc:.2f}% ({class_correct[i]}/{class_total[i]})")
    
    return overall_acc

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*70)
    print("CROP DISEASE DETECTION - GPU TRAINING")
    print("="*70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Setup
    device = setup_device()
    
    # Load data
    train_loader, val_loader, test_loader, class_names, num_classes = load_data()
    if train_loader is None:
        return
    
    # Create model
    model = create_model(num_classes, device)
    
    # Train model
    best_val_acc, history = train_model(model, train_loader, val_loader, device, num_classes)
    
    # Load best model
    checkpoint = torch.load(os.path.join(CONFIG['model_save_dir'], 'best_model.pth'))
    model.load_state_dict(checkpoint['model_state_dict'])
    
    # Test model
    test_acc = test_model(model, test_loader, device, class_names)
    
    # Save metadata
    metadata = {
        'model_name': CONFIG['model_name'],
        'num_classes': num_classes,
        'class_names': class_names,
        'img_size': CONFIG['img_size'],
        'best_val_acc': best_val_acc,
        'test_acc': test_acc,
        'device': str(device),
        'timestamp': datetime.now().isoformat(),
    }
    
    metadata_path = os.path.join(CONFIG['model_save_dir'], 'metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n" + "="*70)
    print("TRAINING COMPLETE")
    print("="*70)
    print(f"✓ Model saved to: {os.path.abspath(CONFIG['model_save_dir'])}")
    print(f"✓ Validation Accuracy: {best_val_acc:.2f}%")
    print(f"✓ Test Accuracy: {test_acc:.2f}%")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
