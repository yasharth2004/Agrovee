"""
Inference script for the trained crop disease detection model
"""

import torch
import torch.nn as nn
from torchvision import models, transforms
import json
import os
from PIL import Image
import argparse

def load_model(model_path, metadata_path, device):
    """Load trained model"""
    # Load metadata
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    num_classes = metadata['num_classes']
    class_names = metadata['class_names']
    
    # Create model
    model = models.resnet50(weights=None)
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, num_classes)
    
    # Load weights
    checkpoint = torch.load(model_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    model.eval()
    
    return model, class_names, metadata

def predict(image_path, model, class_names, device, img_size=224):
    """Predict disease for a single image"""
    # Load and preprocess image
    image = Image.open(image_path).convert('RGB')
    
    transform = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    
    image_tensor = transform(image).unsqueeze(0).to(device)
    
    # Predict
    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.softmax(outputs, dim=1)
        confidence, prediction = torch.max(probabilities, 1)
    
    predicted_class = class_names[prediction.item()]
    confidence_score = confidence.item() * 100
    
    return predicted_class, confidence_score, class_names, probabilities[0].cpu().numpy()

def main():
    parser = argparse.ArgumentParser(description='Predict crop disease from image')
    parser.add_argument('--image', type=str, required=True, help='Path to image')
    parser.add_argument('--model', type=str, default='./models/best_model.pth', help='Path to model')
    parser.add_argument('--metadata', type=str, default='./models/metadata.json', help='Path to metadata')
    
    args = parser.parse_args()
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Load model
    print(f"Loading model from {args.model}...")
    model, class_names, metadata = load_model(args.model, args.metadata, device)
    
    # Predict
    print(f"Processing image: {args.image}")
    predicted_class, confidence, classes, all_probs = predict(
        args.image, model, class_names, device
    )
    
    print(f"\n{'='*50}")
    print(f"Prediction: {predicted_class}")
    print(f"Confidence: {confidence:.2f}%")
    print(f"{'='*50}")
    print(f"\nAll predictions:")
    for cls, prob in zip(class_names, all_probs):
        print(f"  {cls}: {prob*100:.2f}%")

if __name__ == "__main__":
    main()
