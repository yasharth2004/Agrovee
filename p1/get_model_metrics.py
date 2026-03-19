"""
Script to extract metrics from the saved best_model.pth checkpoint
"""

import torch
import json
import os

def get_model_metrics(model_path):
    """Extract metrics from saved model checkpoint"""
    
    if not os.path.exists(model_path):
        print(f"✗ Model not found at: {model_path}")
        return None
    
    # Load checkpoint
    print(f"Loading model checkpoint from: {model_path}")
    checkpoint = torch.load(model_path, map_location='cpu')
    
    print("\n" + "="*70)
    print("MODEL CHECKPOINT INFORMATION")
    print("="*70)
    
    # Extract metrics
    epoch = checkpoint.get('epoch', 'N/A')
    val_acc = checkpoint.get('val_acc', 'N/A')
    history = checkpoint.get('history', {})
    
    print(f"\n✓ Best Model saved at Epoch: {epoch + 1 if isinstance(epoch, int) else epoch}")
    print(f"✓ Validation Accuracy: {val_acc:.2f}%" if isinstance(val_acc, (int, float)) else f"✓ Validation Accuracy: {val_acc}")
    
    if history:
        print(f"\n{'='*70}")
        print("TRAINING HISTORY")
        print("="*70)
        
        train_loss = history.get('train_loss', [])
        train_acc = history.get('train_acc', [])
        val_loss = history.get('val_loss', [])
        val_acc_history = history.get('val_acc', [])
        
        print(f"\n{'Epoch':<10} {'Train Loss':<15} {'Train Acc':<15} {'Val Loss':<15} {'Val Acc':<15}")
        print("-" * 70)
        
        for i in range(len(train_loss)):
            print(f"{i+1:<10} {train_loss[i]:<15.4f} {train_acc[i]:<15.2f} {val_loss[i]:<15.4f} {val_acc_history[i]:<15.2f}")
        
        # Summary statistics
        if train_acc and val_acc_history:
            print(f"\n{'='*70}")
            print("SUMMARY")
            print("="*70)
            print(f"Best Training Accuracy: {max(train_acc):.2f}%")
            print(f"Best Validation Accuracy: {max(val_acc_history):.2f}%")
            print(f"Final Training Loss: {train_loss[-1]:.4f}")
            print(f"Final Validation Loss: {val_loss[-1]:.4f}")
    
    # Check for metadata file
    model_dir = os.path.dirname(model_path)
    metadata_path = os.path.join(model_dir, 'metadata.json')
    
    if os.path.exists(metadata_path):
        print(f"\n{'='*70}")
        print("METADATA")
        print("="*70)
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        print(f"\nModel Name: {metadata.get('model_name', 'N/A')}")
        print(f"Number of Classes: {metadata.get('num_classes', 'N/A')}")
        print(f"Image Size: {metadata.get('img_size', 'N/A')}")
        print(f"Best Val Accuracy: {metadata.get('best_val_acc', 'N/A'):.2f}%")
        if 'test_acc' in metadata:
            print(f"Test Accuracy: {metadata.get('test_acc', 'N/A'):.2f}%")
        print(f"Training Device: {metadata.get('device', 'N/A')}")
        print(f"Timestamp: {metadata.get('timestamp', 'N/A')}")
        
        if 'class_names' in metadata:
            print(f"\nClass Names ({len(metadata['class_names'])}):")
            for cls_name in metadata['class_names'][:10]:  # Show first 10
                print(f"  - {cls_name}")
            if len(metadata['class_names']) > 10:
                print(f"  ... and {len(metadata['class_names']) - 10} more")
    
    print("\n" + "="*70 + "\n")
    
    return {
        'epoch': epoch,
        'val_acc': val_acc,
        'history': history,
    }

if __name__ == "__main__":
    model_path = './models/best_model.pth'
    metrics = get_model_metrics(model_path)
