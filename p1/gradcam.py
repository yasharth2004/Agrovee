"""
Grad-CAM Implementation for Model Explainability
Visualizes which parts of the image the model focuses on
"""

import torch
import torch.nn.functional as F
import numpy as np
import cv2
from PIL import Image

class GradCAM:
    def __init__(self, model, target_layer):
        """
        Initialize Grad-CAM
        
        Args:
            model: PyTorch model
            target_layer: Target layer for Grad-CAM (e.g., model.layer4[-1] for ResNet)
        """
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # Register hooks
        self.target_layer.register_forward_hook(self.save_activation)
        self.target_layer.register_full_backward_hook(self.save_gradient)
    
    def save_activation(self, module, input, output):
        """Hook to save forward pass activations"""
        self.activations = output.detach()
    
    def save_gradient(self, module, grad_input, grad_output):
        """Hook to save backward pass gradients"""
        self.gradients = grad_output[0].detach()
    
    def generate_cam(self, input_tensor, target_class=None):
        """
        Generate Grad-CAM heatmap
        
        Args:
            input_tensor: Input image tensor (1, C, H, W)
            target_class: Target class index (if None, uses predicted class)
            
        Returns:
            cam: Grad-CAM heatmap (H, W)
        """
        # Forward pass
        self.model.eval()
        output = self.model(input_tensor)
        
        # Get target class
        if target_class is None:
            target_class = output.argmax(dim=1).item()
        
        # Backward pass
        self.model.zero_grad()
        class_loss = output[0, target_class]
        class_loss.backward()
        
        # Generate CAM
        gradients = self.gradients[0]  # (C, H, W)
        activations = self.activations[0]  # (C, H, W)
        
        # Global average pooling of gradients
        weights = gradients.mean(dim=(1, 2), keepdim=True)  # (C, 1, 1)
        
        # Weighted combination of activation maps
        cam = (weights * activations).sum(dim=0)  # (H, W)
        
        # Apply ReLU
        cam = F.relu(cam)
        
        # Normalize to [0, 1]
        cam = cam - cam.min()
        if cam.max() > 0:
            cam = cam / cam.max()
        
        return cam.cpu().numpy()
    
    def visualize(self, image, cam, alpha=0.5, colormap=cv2.COLORMAP_JET):
        """
        Create visualization by overlaying heatmap on image
        
        Args:
            image: Original PIL Image or numpy array
            cam: Grad-CAM heatmap (H, W)
            alpha: Transparency for overlay (0-1)
            colormap: OpenCV colormap
            
        Returns:
            overlay: PIL Image with heatmap overlay
        """
        # Convert PIL Image to numpy if needed
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        # Resize CAM to match image size
        h, w = image.shape[:2]
        cam_resized = cv2.resize(cam, (w, h))
        
        # Convert to heatmap
        cam_uint8 = np.uint8(255 * cam_resized)
        heatmap = cv2.applyColorMap(cam_uint8, colormap)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        
        # Overlay heatmap on image
        overlay = (1 - alpha) * image + alpha * heatmap
        overlay = np.uint8(overlay)
        
        return Image.fromarray(overlay)
    
    def generate_visualization(self, image, input_tensor, target_class=None, alpha=0.5):
        """
        Complete pipeline: Generate CAM and create visualization
        
        Args:
            image: Original PIL Image
            input_tensor: Preprocessed input tensor
            target_class: Target class (if None, uses predicted)
            alpha: Overlay transparency
            
        Returns:
            overlay_image: PIL Image with heatmap
            cam: Raw CAM array
            predicted_class: Predicted class index
        """
        # Generate CAM
        cam = self.generate_cam(input_tensor, target_class)
        
        # Get predicted class
        with torch.no_grad():
            output = self.model(input_tensor)
            predicted_class = output.argmax(dim=1).item()
        
        # Create visualization
        overlay_image = self.visualize(image, cam, alpha)
        
        return overlay_image, cam, predicted_class


def create_gradcam_for_resnet(model, device):
    """
    Create Grad-CAM instance for ResNet models
    
    Args:
        model: ResNet model
        device: torch device
        
    Returns:
        GradCAM instance
    """
    # For ResNet, use the last convolutional layer (layer4[-1])
    target_layer = model.layer4[-1]
    return GradCAM(model, target_layer)


def create_heatmap_only(cam, size=(224, 224), colormap=cv2.COLORMAP_JET):
    """
    Create standalone heatmap visualization
    
    Args:
        cam: Grad-CAM array
        size: Output size (W, H)
        colormap: OpenCV colormap
        
    Returns:
        heatmap: PIL Image of heatmap
    """
    cam_resized = cv2.resize(cam, size)
    cam_uint8 = np.uint8(255 * cam_resized)
    heatmap = cv2.applyColorMap(cam_uint8, colormap)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    return Image.fromarray(heatmap)
