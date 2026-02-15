"""
LIME (Local Interpretable Model-agnostic Explanations) for Images
Explains predictions by showing which image regions contribute to the decision
"""

import numpy as np
from PIL import Image
import torch
from skimage.segmentation import mark_boundaries
from lime import lime_image
import warnings
warnings.filterwarnings('ignore')

class LIMEExplainer:
    def __init__(self, model, device, transform, class_names):
        """
        Initialize LIME explainer for images
        
        Args:
            model: PyTorch model
            device: torch device
            transform: Image preprocessing transform
            class_names: List of class names
        """
        self.model = model
        self.device = device
        self.transform = transform
        self.class_names = class_names
        self.explainer = lime_image.LimeImageExplainer()
        
    def predict_fn(self, images):
        """
        Prediction function for LIME
        
        Args:
            images: numpy array of images (batch_size, H, W, C)
            
        Returns:
            probabilities: numpy array of predictions (batch_size, num_classes)
        """
        self.model.eval()
        batch_preds = []
        
        for img in images:
            # Convert numpy to PIL
            pil_img = Image.fromarray(img.astype('uint8'))
            
            # Apply transform
            img_tensor = self.transform(pil_img).unsqueeze(0).to(self.device)
            
            # Get prediction
            with torch.no_grad():
                output = self.model(img_tensor)
                probs = torch.nn.functional.softmax(output, dim=1)
                batch_preds.append(probs.cpu().numpy()[0])
        
        return np.array(batch_preds)
    
    def explain_instance(self, image, top_labels=1, num_samples=1000, num_features=10):
        """
        Generate LIME explanation for an image
        
        Args:
            image: PIL Image or numpy array
            top_labels: Number of top predictions to explain
            num_samples: Number of samples for LIME
            num_features: Number of superpixels to show
            
        Returns:
            explanation: LIME explanation object
            predicted_class: Predicted class index
        """
        # Convert PIL to numpy if needed
        if isinstance(image, Image.Image):
            img_array = np.array(image)
        else:
            img_array = image
        
        # Get prediction first
        pil_img = Image.fromarray(img_array.astype('uint8')) if not isinstance(image, Image.Image) else image
        img_tensor = self.transform(pil_img).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            output = self.model(img_tensor)
            predicted_class = output.argmax(dim=1).item()
        
        # Generate explanation
        explanation = self.explainer.explain_instance(
            img_array,
            self.predict_fn,
            top_labels=top_labels,
            hide_color=0,
            num_samples=num_samples,
            batch_size=10
        )
        
        return explanation, predicted_class
    
    def visualize_explanation(self, image, explanation, predicted_class, 
                             num_features=10, positive_only=True):
        """
        Create visualization showing important regions
        
        Args:
            image: Original PIL Image
            explanation: LIME explanation object
            predicted_class: Predicted class index
            num_features: Number of features to show
            positive_only: Show only positive contributions
            
        Returns:
            visualization: PIL Image with highlighted regions
            feature_importance: Dict with region contributions
        """
        # Convert to numpy
        if isinstance(image, Image.Image):
            img_array = np.array(image)
        else:
            img_array = image
        
        # Get explanation for predicted class
        temp, mask = explanation.get_image_and_mask(
            predicted_class,
            positive_only=positive_only,
            num_features=num_features,
            hide_rest=False
        )
        
        # Create visualization with boundaries
        img_with_boundary = mark_boundaries(temp / 255.0, mask)
        img_with_boundary = (img_with_boundary * 255).astype(np.uint8)
        
        # Get feature importance scores
        feature_weights = explanation.local_exp[predicted_class]
        
        # Calculate contribution percentages
        total_abs_weight = sum(abs(w) for _, w in feature_weights)
        feature_importance = {}
        
        if total_abs_weight > 0:
            for idx, (segment, weight) in enumerate(feature_weights[:num_features]):
                contribution_pct = (abs(weight) / total_abs_weight) * 100
                feature_importance[f"Region {idx+1}"] = {
                    'weight': weight,
                    'contribution': contribution_pct,
                    'sign': 'positive' if weight > 0 else 'negative'
                }
        
        return Image.fromarray(img_with_boundary), feature_importance
    
    def get_text_explanation(self, feature_importance, predicted_class, confidence):
        """
        Generate human-readable text explanation
        
        Args:
            feature_importance: Dict with region contributions
            predicted_class: Predicted class name
            confidence: Prediction confidence
            
        Returns:
            explanation_text: Human-readable explanation
        """
        lines = []
        lines.append(f"Prediction: {predicted_class} ({confidence:.1f}% confidence)\n")
        lines.append("Feature Attribution Analysis:")
        lines.append("-" * 50)
        
        # Sort by contribution
        sorted_features = sorted(
            feature_importance.items(),
            key=lambda x: x[1]['contribution'],
            reverse=True
        )
        
        for region_name, info in sorted_features[:5]:  # Top 5
            contrib = info['contribution']
            sign = "increased" if info['sign'] == 'positive' else "decreased"
            lines.append(f"{region_name}: {sign} probability by {contrib:.1f}%")
        
        return "\n".join(lines)
    
    def create_heatmap_overlay(self, image, explanation, predicted_class, num_features=10):
        """
        Create a heatmap-style overlay showing region importance
        
        Args:
            image: Original PIL Image
            explanation: LIME explanation object
            predicted_class: Predicted class index
            num_features: Number of features to visualize
            
        Returns:
            heatmap_image: PIL Image with heatmap overlay
        """
        import cv2
        
        # Convert to numpy
        if isinstance(image, Image.Image):
            img_array = np.array(image)
        else:
            img_array = image
        
        # Get mask
        _, mask = explanation.get_image_and_mask(
            predicted_class,
            positive_only=True,
            num_features=num_features,
            hide_rest=False
        )
        
        # Create heatmap from mask
        heatmap = np.zeros(mask.shape, dtype=np.float32)
        feature_weights = dict(explanation.local_exp[predicted_class])
        
        # Map segment IDs to weights
        for segment_id, weight in feature_weights.items():
            if weight > 0:  # Only positive contributions
                heatmap[mask == segment_id] = weight
        
        # Normalize heatmap
        if heatmap.max() > 0:
            heatmap = heatmap / heatmap.max()
        
        # Resize to image size
        h, w = img_array.shape[:2]
        heatmap_resized = cv2.resize(heatmap, (w, h))
        
        # Apply colormap
        heatmap_colored = cv2.applyColorMap(
            np.uint8(255 * heatmap_resized),
            cv2.COLORMAP_JET
        )
        heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
        
        # Overlay on original image
        alpha = 0.4
        overlay = (1 - alpha) * img_array + alpha * heatmap_colored
        overlay = np.uint8(overlay)
        
        return Image.fromarray(overlay)


def create_lime_explainer(model, device, transform, class_names):
    """
    Factory function to create LIME explainer
    
    Args:
        model: PyTorch model
        device: torch device
        transform: preprocessing transform
        class_names: list of class names
        
    Returns:
        LIMEExplainer instance
    """
    return LIMEExplainer(model, device, transform, class_names)
