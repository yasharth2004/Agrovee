"""
Vision Model Service
Loads and runs inference with the trained ResNet50 model
"""

import numpy as np
import json
import os
from typing import Dict, List, Tuple, Optional
import logging

from app.core.config import settings

# Try to import torch - run in demo mode if unavailable
try:
    import torch
    import torch.nn as nn
    from torchvision import models, transforms
    from PIL import Image
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️ PyTorch not available - VisionModelService running in DEMO mode")

logger = logging.getLogger(__name__)


class VisionModelService:
    """
    Service for crop disease detection using ResNet50
    Loads trained model and provides inference capabilities
    """
    
    def __init__(self):
        self.model = None
        self.class_names = []
        self.num_classes = 0
        self.device = None
        self.transform = None
        self.metadata = {}
        self._load_model()
    
    def _load_model(self):
        """Load trained model and metadata"""
        if not TORCH_AVAILABLE:
            logger.warning("⚠️ PyTorch not available - running in DEMO mode")
            self._init_demo_mode()
            return
            
        try:
            # Set device
            self.device = torch.device(settings.DEVICE if torch.cuda.is_available() else "cpu")
            logger.info(f"Using device: {self.device}")
            
            # Load metadata
            metadata_path = settings.MODEL_METADATA_PATH
            if not os.path.exists(metadata_path):
                # Try relative path from backend
                metadata_path = os.path.join(os.path.dirname(__file__), "../../..", settings.MODEL_METADATA_PATH)
            
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                    self.class_names = self.metadata['class_names']
                    self.num_classes = self.metadata['num_classes']
                    logger.info(f"Loaded metadata: {self.num_classes} classes")
            else:
                logger.warning(f"Metadata file not found at {metadata_path}")
                raise FileNotFoundError(f"Model metadata not found: {metadata_path}")
            
            # Create model architecture
            self.model = models.resnet50(weights=None)
            num_features = self.model.fc.in_features
            self.model.fc = nn.Linear(num_features, self.num_classes)
            
            # Load trained weights
            model_path = settings.MODEL_PATH
            if not os.path.exists(model_path):
                # Try relative path
                model_path = os.path.join(os.path.dirname(__file__), "../../..", settings.MODEL_PATH)
            
            if os.path.exists(model_path):
                checkpoint = torch.load(model_path, map_location=self.device)
                self.model.load_state_dict(checkpoint['model_state_dict'])
                self.model.to(self.device)
                self.model.eval()
                logger.info(f"✓ Model loaded successfully from {model_path}")
            else:
                logger.warning(f"Model file not found at {model_path}")
                raise FileNotFoundError(f"Model weights not found: {model_path}")
            
            # Define image transforms
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                   std=[0.229, 0.224, 0.225])
            ])
            
            logger.info("✓ Vision model service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self._init_demo_mode()
    
    def _init_demo_mode(self):
        """
        Initialize demo mode.
        If PyTorch is available, loads a pre-trained MobileNetV2 (ImageNet)
        for real crop identification. Otherwise falls back to heuristics.
        """
        self.device = "cpu"
        self.num_classes = 38
        self.class_names = [
            "Tomato___Early_Blight", "Tomato___Late_Blight", "Tomato___Healthy",
            "Potato___Early_Blight", "Potato___Late_Blight", "Potato___Healthy",
            "Pepper___Bacterial_Spot", "Pepper___Healthy",
            "Apple___Apple_Scab", "Apple___Black_Rot", "Apple___Healthy",
            "Cherry___Powdery_Mildew", "Cherry___Healthy",
            "Corn___Common_Rust", "Corn___Gray_Leaf_Spot", "Corn___Healthy",
            "Grape___Black_Rot", "Grape___Esca", "Grape___Healthy",
            "Wheat___Brown_Rust", "Wheat___Yellow_Rust", "Wheat___Healthy",
            "Rice___Brown_Spot", "Rice___Leaf_Blast", "Rice___Healthy",
            "Peach___Bacterial_Spot", "Peach___Healthy",
            "Strawberry___Leaf_Scorch", "Strawberry___Healthy",
            "Sugarcane___Red_Rot", "Sugarcane___Healthy",
            "Cotton___Bacterial_Blight", "Cotton___Healthy",
            "Soybean___Frog_Eye_Spot", "Soybean___Healthy",
            "Mango___Anthracnose", "Mango___Healthy",
            "Banana___Black_Sigatoka", "Banana___Healthy",
        ]
        self.class_names = self.class_names[:38]
        
        # Map ImageNet class indices → our crop names
        self._imagenet_crop_map = {
            987: "Corn",       # corn (ear of corn)
            998: "Wheat",      # ear, spike, capitulum → grain head
            958: "Wheat",      # hay → dried grain
            984: "Wheat",      # rapeseed → grain crop
            954: "Banana",     # banana
            949: "Strawberry", # strawberry
            945: "Pepper",     # bell pepper
            948: "Apple",      # Granny Smith apple
            957: "Apple",      # pomegranate → tree fruit
            950: "Tomato",     # orange → round fruit (closest)
            951: "Tomato",     # lemon → closest
            952: "Mango",      # fig → tropical fruit
            953: "Mango",      # pineapple → tropical
            956: "Mango",      # custard apple → tropical
            943: "Potato",     # cucumber → vegetable
            936: "Potato",     # head cabbage → vegetable
            937: "Potato",     # broccoli → vegetable
            938: "Potato",     # cauliflower → vegetable
            935: "Potato",     # mashed potato
            947: "Soybean",    # mushroom → ground crop
            944: "Soybean",    # artichoke → similar leaf pattern
            946: "Cotton",     # cardoon → plant stalk
            580: "Tomato",     # greenhouse
            595: "Wheat",      # harvester → grain field
            979: "Rice",       # valley → paddy fields
            970: "Rice",       # alp → terraced fields
            985: "Cotton",     # daisy → field plant
        }
        
        # Try loading MobileNetV2 for real crop identification
        self._crop_classifier = None
        self._crop_transform = None
        
        if TORCH_AVAILABLE:
            try:
                from torchvision.models import mobilenet_v2, MobileNet_V2_Weights
                
                weights = MobileNet_V2_Weights.IMAGENET1K_V2
                self._crop_classifier = mobilenet_v2(weights=weights)
                self._crop_classifier.eval()
                self._crop_transform = weights.transforms()
                self._imagenet_categories = weights.meta["categories"]
                
                logger.info("✓ Loaded MobileNetV2 pretrained model for crop identification")
            except Exception as e:
                logger.warning(f"Could not load MobileNetV2: {e}")
                self._crop_classifier = None
        
        if self._crop_classifier:
            logger.warning("⚠️ Running in DEMO mode with pretrained crop classifier (no disease-specific model)")
        else:
            logger.warning("⚠️ Running in DEMO mode with heuristics only")
    
    def predict(self, image_path: str, original_filename: str = "") -> Dict:
        """
        Predict disease from image
        
        Args:
            image_path: Path to image file
            original_filename: Original uploaded filename (for demo mode hints)
            
        Returns:
            Dictionary with predictions, confidence, and top-5 results
        """
        if not TORCH_AVAILABLE or self.model is None:
            return self._demo_predict(image_path, original_filename)
            
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                
                # Get top prediction
                confidence, prediction = torch.max(probabilities, 1)
                predicted_class = self.class_names[prediction.item()]
                confidence_score = confidence.item() * 100
                
                # Get top 5 predictions
                top5_prob, top5_idx = torch.topk(probabilities[0], k=min(5, self.num_classes))
                top5_predictions = [
                    {
                        "disease": self.class_names[idx.item()],
                        "probability": prob.item() * 100,
                        "crop": self._extract_crop_type(self.class_names[idx.item()])
                    }
                    for prob, idx in zip(top5_prob, top5_idx)
                ]
            
            # Extract crop type from disease name
            crop_type = self._extract_crop_type(predicted_class)
            
            return {
                "predicted_disease": predicted_class,
                "confidence": confidence_score,
                "crop_type": crop_type,
                "top_predictions": top5_predictions,
                "model_version": self.metadata.get("model_name", "resnet50"),
                "device": str(self.device)
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return self._demo_predict(image_path)
    
    def _classify_crop_with_model(self, image_path: str) -> Optional[str]:
        """
        Use the pretrained MobileNetV2 to classify the image via ImageNet,
        then map the top-K ImageNet labels to one of our crop categories.
        Returns the crop name (e.g. "Corn") or None if nothing maps.
        """
        if self._crop_classifier is None:
            return None
        try:
            from PIL import Image as PILImage
            img = PILImage.open(image_path).convert("RGB")
            tensor = self._crop_transform(img).unsqueeze(0)
            
            with torch.no_grad():
                logits = self._crop_classifier(tensor)
                probs = torch.softmax(logits, dim=1)
                top20_prob, top20_idx = torch.topk(probs[0], 20)
            
            # Walk through top-20 ImageNet predictions
            for prob, idx in zip(top20_prob, top20_idx):
                class_idx = idx.item()
                class_name = self._imagenet_categories[class_idx]
                confidence = prob.item()
                
                # Direct index mapping
                if class_idx in self._imagenet_crop_map:
                    crop = self._imagenet_crop_map[class_idx]
                    logger.info(
                        f"MobileNetV2 → ImageNet '{class_name}' ({confidence:.1%}) → crop '{crop}'"
                    )
                    return crop
                
                # Fuzzy keyword matching in class name
                kw_map = {
                    "corn": "Corn", "maize": "Corn", "wheat": "Wheat",
                    "rice": "Rice", "paddy": "Rice", "banana": "Banana",
                    "tomato": "Tomato", "potato": "Potato", "apple": "Apple",
                    "grape": "Grape", "cherry": "Cherry", "peach": "Peach",
                    "pepper": "Pepper", "strawberry": "Strawberry",
                    "mango": "Mango", "cotton": "Cotton", "soy": "Soybean",
                    "sugarcane": "Sugarcane", "cane": "Sugarcane",
                    "leaf": "Potato",  # very generic fallback
                }
                lower_name = class_name.lower().replace("_", " ")
                for kw, crop in kw_map.items():
                    if kw in lower_name:
                        logger.info(
                            f"MobileNetV2 → ImageNet '{class_name}' ({confidence:.1%}) "
                            f"keyword '{kw}' → crop '{crop}'"
                        )
                        return crop
            
            # Log what the model actually saw (for debugging)
            top3_names = [self._imagenet_categories[i.item()] for i in top20_idx[:3]]
            logger.info(f"MobileNetV2 top-3 (no crop mapping): {top3_names}")
            return None
            
        except Exception as e:
            logger.warning(f"Pretrained crop classification failed: {e}")
            return None

    def _demo_predict(self, image_path: str, original_filename: str = "") -> Dict:
        """
        Demo prediction.
        Priority: 1) MobileNetV2 real classification, 2) filename hints, 3) color heuristics.
        """
        import random
        import os
        from PIL import Image as PILImage
        
        filename = (original_filename or os.path.basename(image_path)).lower()

        # Build crop → disease-class mapping
        crop_groups: Dict[str, list] = {}
        for name in self.class_names:
            crop = self._extract_crop_type(name)
            crop_groups.setdefault(crop, []).append(name)
        
        random.seed(hash(image_path) % 100000)
        chosen_crop = None
        detection_method = "heuristic"
        
        # ── Priority 1: Real MobileNetV2 classification ──
        model_crop = self._classify_crop_with_model(image_path)
        if model_crop and model_crop in crop_groups:
            chosen_crop = model_crop
            detection_method = "mobilenet_v2"
        
        # ── Priority 2: Filename hints ──
        if chosen_crop is None:
            filename_crop_map = {
                "wheat": "Wheat", "rice": "Rice", "paddy": "Rice",
                "corn": "Corn", "maize": "Corn", "tomato": "Tomato",
                "potato": "Potato", "apple": "Apple", "grape": "Grape",
                "cherry": "Cherry", "peach": "Peach", "pepper": "Pepper",
                "strawberry": "Strawberry", "mango": "Mango",
                "banana": "Banana", "cotton": "Cotton", "soybean": "Soybean",
                "sugarcane": "Sugarcane",
            }
            for keyword, crop in filename_crop_map.items():
                if keyword in filename:
                    if crop in crop_groups:
                        chosen_crop = crop
                        detection_method = "filename"
                    break
        
        # ── Priority 3: Color heuristics (last resort) ──
        if chosen_crop is None:
            try:
                img = PILImage.open(image_path).convert("RGB")
                img_small = img.resize((64, 64))
                pixels = list(img_small.getdata())
                total_px = len(pixels)
                
                green_px = sum(1 for p in pixels if p[1] > p[0] and p[1] > p[2] and p[1] > 80)
                golden_px = sum(1 for p in pixels if p[0] > 130 and p[1] > 100 and p[1] < p[0] and p[2] < 100)
                red_px = sum(1 for p in pixels if p[0] > 150 and p[0] > p[1] * 1.5 and p[0] > p[2] * 1.5)
                
                green_pct = green_px / total_px
                golden_pct = golden_px / total_px
                red_pct = red_px / total_px
                
                if red_pct > 0.15:
                    preferred = ["Tomato", "Apple", "Strawberry", "Cherry"]
                elif golden_pct > 0.20:
                    preferred = ["Wheat", "Rice", "Corn"]
                elif green_pct > 0.35:
                    preferred = ["Corn", "Rice", "Potato", "Sugarcane"]
                else:
                    preferred = ["Grape", "Mango", "Banana", "Cotton"]
                
                chosen_crop = next((c for c in preferred if c in crop_groups), "Tomato")
            except Exception:
                chosen_crop = "Tomato"
        
        # ── Pick disease class for the chosen crop ──
        classes_for_crop = crop_groups[chosen_crop]
        predicted_disease = random.choice(classes_for_crop)
        confidence = round(random.uniform(85.0, 96.0), 2)
        
        # ── Build top-5 predictions (same crop first, then others) ──
        top5 = [{
            "disease": predicted_disease,
            "probability": round(confidence, 2),
            "crop": chosen_crop,
        }]
        
        # Add other classes from the SAME crop for positions 2-3
        same_crop_others = [c for c in classes_for_crop if c != predicted_disease]
        random.shuffle(same_crop_others)
        remaining = 100.0 - confidence
        for cls in same_crop_others[:2]:
            prob = round(random.uniform(1.0, remaining * 0.40), 2)
            remaining -= prob
            top5.append({
                "disease": cls,
                "probability": max(prob, 0.1),
                "crop": chosen_crop,
            })
        
        # Positions 4-5 from other crops
        other_classes = [c for c in self.class_names if self._extract_crop_type(c) != chosen_crop]
        random.shuffle(other_classes)
        for cls in other_classes[:max(0, 5 - len(top5))]:
            prob = round(random.uniform(0.3, remaining * 0.45), 2)
            remaining -= prob
            top5.append({
                "disease": cls,
                "probability": max(prob, 0.1),
                "crop": self._extract_crop_type(cls),
            })
        
        logger.info(
            f"Demo predict ({detection_method}): {predicted_disease} ({confidence:.1f}%) → crop={chosen_crop}"
        )
        
        return {
            "predicted_disease": predicted_disease,
            "confidence": confidence,
            "crop_type": chosen_crop,
            "top_predictions": top5[:5],
            "model_version": "resnet50_demo",
            "device": f"demo_{detection_method}",
            "demo_mode": True,
        }
    
    def _extract_crop_type(self, disease_name: str) -> str:
        """Extract crop type from disease class name"""
        # Disease names are in format: "Crop___Disease"
        if "___" in disease_name:
            return disease_name.split("___")[0]
        elif "_" in disease_name:
            # Handle different formats
            parts = disease_name.split("_")
            return parts[0]
        return "Unknown"
    
    def get_embedding(self, image_path: str) -> np.ndarray:
        """
        Extract feature embedding from image (before final classification layer)
        Used for multimodal fusion
        
        Args:
            image_path: Path to image
            
        Returns:
            Feature vector (numpy array)
        """
        if not TORCH_AVAILABLE or self.model is None:
            # Return dummy embedding
            return np.random.randn(2048).astype(np.float32)
            
        try:
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Extract features from layer before FC
            with torch.no_grad():
                # Forward pass up to avgpool
                x = self.model.conv1(image_tensor)
                x = self.model.bn1(x)
                x = self.model.relu(x)
                x = self.model.maxpool(x)
                
                x = self.model.layer1(x)
                x = self.model.layer2(x)
                x = self.model.layer3(x)
                x = self.model.layer4(x)
                
                x = self.model.avgpool(x)
                embedding = torch.flatten(x, 1)
            
            return embedding.cpu().numpy()[0]
            
        except Exception as e:
            logger.error(f"Embedding extraction error: {e}")
            # Return dummy embedding
            return np.zeros(2048)  # ResNet50 feature size


# Global instance
_vision_service = None

def get_vision_service() -> VisionModelService:
    """Get or create vision service singleton"""
    global _vision_service
    if _vision_service is None:
        _vision_service = VisionModelService()
    return _vision_service
