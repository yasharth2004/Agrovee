"""
Crop Disease Detection GUI Application
Simple interface to upload images and detect plant diseases
With Grad-CAM and LIME explainability visualization
"""

import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext
from PIL import Image, ImageTk
import torch
import torch.nn as nn
from torchvision import transforms, models
import json
import os
from gradcam import create_gradcam_for_resnet
from lime_explainer import create_lime_explainer

class CropDiseaseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Crop Disease Detection - Multi-Level Explainability")
        self.root.geometry("1600x850")
        self.root.configure(bg='#f0f0f0')
        
        # Load model and metadata
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.class_names = None
        self.transform = None
        self.current_image = None
        self.gradcam = None
        self.lime_explainer = None
        self.heatmap_image = None
        
        self.load_model()
        self.setup_ui()
        
    def load_model(self):
        """Load the trained model and metadata"""
        try:
            # Load metadata
            metadata_path = './models/metadata.json'
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                self.class_names = metadata['class_names']
                num_classes = metadata['num_classes']
            else:
                # Fallback if metadata doesn't exist - load from checkpoint
                checkpoint = torch.load('./models/best_model.pth', map_location=self.device)
                # We'll need to infer class names from the dataset
                print("Warning: metadata.json not found")
                return
            
            # Create model
            self.model = models.resnet50(weights=None)
            num_features = self.model.fc.in_features
            self.model.fc = nn.Linear(num_features, num_classes)
            
            # Load weights
            checkpoint = torch.load('./models/best_model.pth', map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.to(self.device)
            self.model.eval()
            
            # Setup transform
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                   std=[0.229, 0.224, 0.225])
            ])
            
            # Setup Grad-CAM
            self.gradcam = create_gradcam_for_resnet(self.model, self.device)
            
            # Setup LIME
            self.lime_explainer = create_lime_explainer(
                self.model, self.device, self.transform, self.class_names
            )
            
            print(f"✓ Model loaded successfully on {self.device}")
            print(f"✓ Number of classes: {num_classes}")
            print(f"✓ Grad-CAM initialized for visual explainability")
            print(f"✓ LIME initialized for feature attribution")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            self.show_error("Failed to load model. Please ensure best_model.pth exists.")
    
    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="🌿 Crop Disease Detection - Multi-Level AI Explainability",
            font=('Arial', 20, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=20)
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Left side - Original Image
        left_frame = tk.LabelFrame(
            main_frame, 
            text="Original Image",
            font=('Arial', 10, 'bold'),
            bg='white', 
            relief='solid', 
            borderwidth=1
        )
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        self.image_label = tk.Label(
            left_frame,
            text="No Image Loaded\n\nUpload to start",
            font=('Arial', 10),
            bg='white',
            fg='gray'
        )
        self.image_label.pack(fill='both', expand=True, padx=8, pady=8)
        
        # Middle-Left - Grad-CAM
        middle_left_frame = tk.LabelFrame(
            main_frame,
            text="Level 1: Grad-CAM (Visual)",
            font=('Arial', 10, 'bold'),
            bg='white',
            relief='solid',
            borderwidth=1
        )
        middle_left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        self.heatmap_label = tk.Label(
            middle_left_frame,
            text="Attention Map\n\nWhere AI looks",
            font=('Arial', 10),
            bg='white',
            fg='gray'
        )
        self.heatmap_label.pack(fill='both', expand=True, padx=8, pady=8)
        
        # Middle-Right - LIME
        middle_right_frame = tk.LabelFrame(
            main_frame,
            text="Level 2: LIME (Feature Attribution)",
            font=('Arial', 10, 'bold'),
            bg='white',
            relief='solid',
            borderwidth=1
        )
        middle_right_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        self.lime_label = tk.Label(
            middle_right_frame,
            text="Region Importance\n\nContribution %",
            font=('Arial', 10),
            bg='white',
            fg='gray'
        )
        self.lime_label.pack(fill='both', expand=True, padx=8, pady=8)
        
        # Right side - Controls and results
        right_frame = tk.Frame(main_frame, bg='#f0f0f0')
        right_frame.pack(side='right', fill='both', padx=(5, 0))
        
        # Upload button
        upload_btn = tk.Button(
            right_frame,
            text="📁 Upload Image",
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white',
            activebackground='#2980b9',
            activeforeground='white',
            cursor='hand2',
            command=self.upload_image,
            width=20,
            height=2
        )
        upload_btn.pack(pady=8)
        
        # Predict button
        self.predict_btn = tk.Button(
            right_frame,
            text="🔍 Analyze with AI",
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            activebackground='#229954',
            activeforeground='white',
            cursor='hand2',
            command=self.predict,
            width=20,
            height=2,
            state='disabled'
        )
        self.predict_btn.pack(pady=8)
        
        # Results frame
        results_frame = tk.LabelFrame(
            right_frame,
            text="Diagnosis Results",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50',
            relief='solid',
            borderwidth=1
        )
        results_frame.pack(fill='both', pady=8)
        
        # Plant type
        tk.Label(
            results_frame,
            text="Plant Type:",
            font=('Arial', 9, 'bold'),
            bg='white',
            fg='#34495e',
            anchor='w'
        ).pack(fill='x', padx=10, pady=(8, 2))
        
        self.plant_label = tk.Label(
            results_frame,
            text="---",
            font=('Arial', 11),
            bg='white',
            fg='#2c3e50',
            anchor='w'
        )
        self.plant_label.pack(fill='x', padx=10, pady=(0, 8))
        
        # Health status
        tk.Label(
            results_frame,
            text="Health Status:",
            font=('Arial', 9, 'bold'),
            bg='white',
            fg='#34495e',
            anchor='w'
        ).pack(fill='x', padx=10, pady=(0, 2))
        
        self.health_label = tk.Label(
            results_frame,
            text="---",
            font=('Arial', 11, 'bold'),
            bg='white',
            anchor='w'
        )
        self.health_label.pack(fill='x', padx=10, pady=(0, 8))
        
        # Disease info
        tk.Label(
            results_frame,
            text="Disease:",
            font=('Arial', 9, 'bold'),
            bg='white',
            fg='#34495e',
            anchor='w'
        ).pack(fill='x', padx=10, pady=(0, 2))
        
        self.disease_label = tk.Label(
            results_frame,
            text="---",
            font=('Arial', 10),
            bg='white',
            fg='#2c3e50',
            anchor='w',
            wraplength=280,
            justify='left'
        )
        self.disease_label.pack(fill='x', padx=10, pady=(0, 8))
        
        # Confidence
        tk.Label(
            results_frame,
            text="Confidence:",
            font=('Arial', 9, 'bold'),
            bg='white',
            fg='#34495e',
            anchor='w'
        ).pack(fill='x', padx=10, pady=(0, 2))
        
        self.confidence_label = tk.Label(
            results_frame,
            text="---",
            font=('Arial', 11),
            bg='white',
            fg='#2c3e50',
            anchor='w'
        )
        self.confidence_label.pack(fill='x', padx=10, pady=(0, 8))
        
        # Feature Attribution frame
        attribution_frame = tk.LabelFrame(
            right_frame,
            text="Feature Attribution (LIME)",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50',
            relief='solid',
            borderwidth=1
        )
        attribution_frame.pack(fill='both', expand=True, pady=(0, 8))
        
        # Scrolled text for explanations
        self.explanation_text = scrolledtext.ScrolledText(
            attribution_frame,
            font=('Consolas', 9),
            bg='#f8f9fa',
            fg='#2c3e50',
            height=10,
            wrap=tk.WORD,
            relief='flat'
        )
        self.explanation_text.pack(fill='both', expand=True, padx=8, pady=8)
        self.explanation_text.insert('1.0', 'Upload and analyze an image to see\nfeature attribution explanations...')
        self.explanation_text.config(state='disabled')
        
        # Footer
        footer = tk.Label(
            self.root,
            text="Level 1: Grad-CAM (Visual) | Level 2: LIME (Feature Attribution) | ResNet50 99.10% | GPU Accelerated",
            font=('Arial', 8),
            bg='#f0f0f0',
            fg='gray'
        )
        footer.pack(pady=(0, 8))
    
    def upload_image(self):
        """Handle image upload"""
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Load and display image
                image = Image.open(file_path)
                self.current_image = image.copy()
                
                # Resize for display
                display_size = (300, 300)
                image.thumbnail(display_size, Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(image)
                self.image_label.configure(image=photo, text="")
                self.image_label.image = photo  # Keep a reference
                
                # Clear visualizations
                self.heatmap_label.configure(
                    image='',
                    text="Grad-CAM will\nappear here"
                )
                self.lime_label.configure(
                    image='',
                    text="LIME regions\nwill appear here"
                )
                
                # Enable predict button
                self.predict_btn.configure(state='normal')
                
                # Clear previous results
                self.clear_results()
                
            except Exception as e:
                self.show_error(f"Failed to load image: {str(e)}")
    
    def predict(self):
        """Make prediction on the uploaded image with multi-level explainability"""
        if self.current_image is None or self.model is None:
            return
        
        # Update button to show processing
        self.predict_btn.configure(text="⏳ Processing...", state='disabled')
        self.root.update()
        
        try:
            # Preprocess image
            image_tensor = self.transform(self.current_image)
            image_tensor = image_tensor.unsqueeze(0).to(self.device)
            
            # Make prediction
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
                
                predicted_class = self.class_names[predicted.item()]
                confidence_score = confidence.item() * 100
            
            display_size = (300, 300)
            
            # Level 1: Generate Grad-CAM visualization
            try:
                overlay_image, cam, _ = self.gradcam.generate_visualization(
                    self.current_image,
                    image_tensor,
                    target_class=predicted.item(),
                    alpha=0.4
                )
                
                # Display Grad-CAM
                gradcam_display = overlay_image.copy()
                gradcam_display.thumbnail(display_size, Image.Resampling.LANCZOS)
                
                heatmap_photo = ImageTk.PhotoImage(gradcam_display)
                self.heatmap_label.configure(image=heatmap_photo, text="")
                self.heatmap_label.image = heatmap_photo
                
                print("✓ Grad-CAM visualization generated")
                
            except Exception as e:
                print(f"Warning: Grad-CAM failed: {e}")
                self.heatmap_label.configure(text="Visualization\nunavailable", fg='orange')
            
            # Level 2: Generate LIME explanation
            try:
                print("Generating LIME explanation (this may take 10-20 seconds)...")
                self.explanation_text.config(state='normal')
                self.explanation_text.delete('1.0', tk.END)
                self.explanation_text.insert('1.0', 'Generating LIME explanation...\nPlease wait...')
                self.explanation_text.config(state='disabled')
                self.root.update()
                
                # Generate LIME explanation
                explanation, pred_class = self.lime_explainer.explain_instance(
                    self.current_image,
                    top_labels=1,
                    num_samples=500,  # Reduced for faster processing
                    num_features=5
                )
                
                # Create visualization
                lime_vis, feature_importance = self.lime_explainer.visualize_explanation(
                    self.current_image,
                    explanation,
                    pred_class,
                    num_features=5,
                    positive_only=True
                )
                
                # Display LIME visualization
                lime_display = lime_vis.copy()
                lime_display.thumbnail(display_size, Image.Resampling.LANCZOS)
                
                lime_photo = ImageTk.PhotoImage(lime_display)
                self.lime_label.configure(image=lime_photo, text="")
                self.lime_label.image = lime_photo
                
                # Generate text explanation
                explanation_text = self.lime_explainer.get_text_explanation(
                    feature_importance,
                    predicted_class,
                    confidence_score
                )
                
                # Update explanation text
                self.explanation_text.config(state='normal')
                self.explanation_text.delete('1.0', tk.END)
                self.explanation_text.insert('1.0', explanation_text)
                self.explanation_text.config(state='disabled')
                
                print("✓ LIME explanation generated")
                
            except Exception as e:
                print(f"Warning: LIME explanation failed: {e}")
                self.lime_label.configure(text="LIME visualization\nunavailable", fg='orange')
                self.explanation_text.config(state='normal')
                self.explanation_text.delete('1.0', tk.END)
                self.explanation_text.insert('1.0', f'LIME explanation unavailable:\n{str(e)}')
                self.explanation_text.config(state='disabled')
            
            # Parse the class name
            plant_type, health_status, disease = self.parse_class_name(predicted_class)
            
            # Update UI
            self.plant_label.configure(text=plant_type)
            
            if health_status == "Healthy":
                self.health_label.configure(text="✓ Healthy", fg='#27ae60')
                self.disease_label.configure(text="No disease detected", fg='#27ae60')
            else:
                self.health_label.configure(text="✗ Diseased", fg='#e74c3c')
                self.disease_label.configure(text=disease, fg='#e74c3c')
            
            self.confidence_label.configure(text=f"{confidence_score:.2f}%")
            
        except Exception as e:
            self.show_error(f"Prediction failed: {str(e)}")
        
        finally:
            # Re-enable button
            self.predict_btn.configure(text="🔍 Analyze with AI", state='normal')
    
    def parse_class_name(self, class_name):
        """Parse class name to extract plant type, health status, and disease"""
        # Class names are in format: "Plant___Disease" or "Plant___healthy"
        parts = class_name.split('___')
        
        if len(parts) >= 2:
            plant_type = parts[0].replace('_', ' ').title()
            disease_part = parts[1].replace('_', ' ').title()
            
            if 'healthy' in disease_part.lower():
                return plant_type, "Healthy", "None"
            else:
                return plant_type, "Diseased", disease_part
        else:
            return class_name, "Unknown", "Unknown"
    
    def clear_results(self):
        """Clear result labels"""
        self.plant_label.configure(text="---")
        self.health_label.configure(text="---", fg='#2c3e50')
        self.disease_label.configure(text="---", fg='#2c3e50')
        self.confidence_label.configure(text="---")
    
    def show_error(self, message):
        """Show error message"""
        from tkinter import messagebox
        messagebox.showerror("Error", message)

def main():
    root = tk.Tk()
    app = CropDiseaseGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
