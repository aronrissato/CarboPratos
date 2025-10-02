"""
Food detector using YOLO.
Responsible for detecting foods in images.
"""

from typing import List, Tuple, Dict
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
from .calorie_database import get_calories_per_100g, get_available_foods


class FoodDetector:
    """Food detector using YOLO."""
    
    def DetectFoods(self, image_path: str) -> List[Dict]:
        """
        Detects foods in an image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            List of dictionaries with detected food information
        """
        yolo_detections = self.RunYOLODetection(image_path)
        detections = self.ProcessYOLOResults(yolo_detections)
        
        return detections
    
    def RunYOLODetection(self, image_path: str):
        """Runs YOLO model on the image."""
        return self.model(image_path)
    
    def ProcessYOLOResults(self, results) -> List[Dict]:
        """Processes YOLO detection results."""
        return self._ProcessDetectionResults(results)
    
    def VisualizeDetections(self, image_path: str, output_path: str = None, show_all: bool = True) -> str:
        """
        Creates a visualization of YOLO detections on the image.
        
        Args:
            image_path: Path to the input image
            output_path: Path to save the visualization (optional)
            show_all: If True, shows all detections; if False, only food detections
            
        Returns:
            Path to the saved visualization image
        """
        # Run YOLO detection
        results = self.RunYOLODetection(image_path)
        
        # Load the original image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        detection_count = 0
        
        # Draw all detections
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Get coordinates and confidence
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    class_name = self.model.names[class_id]
                    
                    # Check if we should show this detection
                    if not show_all:
                        # Only show food-related detections
                        calories = get_calories_per_100g(class_name)
                        if calories <= 0 and class_name not in ['bowl', 'cup', 'dining table']:
                            continue
                    
                    detection_count += 1
                    
                    # Choose color based on detection type
                    if class_name in ['bowl', 'cup', 'dining table']:
                        color = (255, 0, 0)  # Red for utensils/table
                    elif get_calories_per_100g(class_name) > 0:
                        color = (0, 255, 0)  # Green for food
                    else:
                        color = (0, 0, 255)  # Blue for other objects
                    
                    # Draw bounding box
                    cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    
                    # Draw label with confidence
                    label = f"{class_name}: {confidence:.2f}"
                    label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                    cv2.rectangle(image, (int(x1), int(y1) - label_size[1] - 10), 
                                 (int(x1) + label_size[0], int(y1)), color, -1)
                    cv2.putText(image, label, (int(x1), int(y1) - 5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # Add detection count to image
        cv2.putText(image, f"Total detections: {detection_count}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        # Generate output path if not provided
        if output_path is None:
            input_path = Path(image_path)
            suffix = "_all_detections" if show_all else "_food_detections"
            output_path = input_path.parent / f"{input_path.stem}{suffix}{input_path.suffix}"
        
        # Save the visualization
        cv2.imwrite(str(output_path), image)
        return str(output_path)
    
    
    def EstimateFoodQuantity(self, detection: Dict, image_shape: Tuple[int, int]) -> float:
        """
        Estimates food quantity based on detected area.
        
        Args:
            detection: Detection data
            image_shape: (height, width) of the image
            
        Returns:
            Estimated quantity in grams
        """
        food_area_cm2 = self.CalculateFoodArea(detection, image_shape)
        density = self.GetFoodDensity(detection['class_name'])
        avg_height_cm = self.EstimateFoodHeight(detection['class_name'])
        food_volume_cm3 = self.CalculateFoodVolume(food_area_cm2, avg_height_cm)
        estimated_weight = self.CalculateFoodWeight(food_volume_cm3, density)
        
        return self.ApplyWeightLimitations(estimated_weight)
    
    def CalculateFoodArea(self, detection: Dict, image_shape: Tuple[int, int]) -> float:
        """Calculates food area in cm²."""
        return self._CalculateFoodArea(detection, image_shape)
    
    def GetFoodDensity(self, food_name: str) -> float:
        """Gets food density."""
        return self._GetFoodDensity(food_name)
    
    def EstimateFoodHeight(self, food_name: str) -> float:
        """Estimates average food height on the plate."""
        return self._EstimateFoodHeight(food_name)
    
    def CalculateFoodVolume(self, area_cm2: float, height_cm: float) -> float:
        """Calculates food volume in cm³."""
        return area_cm2 * height_cm
    
    def CalculateFoodWeight(self, volume_cm3: float, density: float) -> float:
        """Calculates estimated food weight in grams."""
        return volume_cm3 * density
    
    def ApplyWeightLimitations(self, weight: float) -> float:
        """Applies realistic weight limitations (30g-400g)."""
        limited_weight = max(min(weight, 400), 30)
        return round(limited_weight, 1)
    
    
    def _ProcessDetectionResults(self, results) -> List[Dict]:
        """
        Processes YOLO detection results.
        
        Args:
            results: YOLO model results
            
        Returns:
            List of processed detections
        """
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Get coordinates and confidence
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    # Get class name
                    class_name = self.model.names[class_id]
                    
                    # Map COCO class to food if possible
                    food_name = self.coco_to_food.get(class_name, class_name)
                    
                    # Calculate detection area
                    area = (x2 - x1) * (y2 - y1)
                    
                    # Only add if it's a food with known calories
                    calories = get_calories_per_100g(food_name)
                    if calories > 0 or class_name in ['bowl', 'cup']:  # Include utensils for context
                        detections.append({
                            'class_name': food_name,
                            'coco_class': class_name,
                            'confidence': float(confidence),
                            'bbox': (float(x1), float(y1), float(x2), float(y2)),
                            'area': float(area),
                            'calories_per_100g': calories
                        })
        
        return detections
    
    def _CalculateFoodArea(self, detection: Dict, image_shape: Tuple[int, int]) -> float:
        """
        Calculates food area in cm².
        
        Args:
            detection: Detection data
            image_shape: (height, width) of the image
            
        Returns:
            Food area in cm²
        """
        # Detection area in pixels
        detection_area = detection['area']
        
        # Total image area
        total_area = image_shape[0] * image_shape[1]
        
        # Proportion of area occupied by food
        area_ratio = detection_area / total_area
        
        # More realistic estimate based on 25cm diameter plate
        # Plate area = π * (12.5cm)² = ~491 cm²
        plate_area_cm2 = 491
        
        # Food occupied area in cm²
        food_area_cm2 = area_ratio * plate_area_cm2
        
        return food_area_cm2
    
    def _GetFoodDensity(self, food_name: str) -> float:
        """
        Gets food density.
        
        Args:
            food_name: Food name
            
        Returns:
            Density in g/cm³
        """
        food_name = food_name.lower()
        
        # Approximate densities (g/cm³) for different food types
        densities = {
            # Grains and carbohydrates (denser)
            'arroz': 0.8, 'rice': 0.8, 'feijao': 1.2, 'feijão': 1.2, 'beans': 1.2,
            'macarrao': 0.6, 'macarrão': 0.6, 'pasta': 0.6, 'massa': 0.6,
            'batata': 0.7, 'potato': 0.7, 'batata_doce': 0.8, 'sweet potato': 0.8,
            
            # Proteins (medium density)
            'frango': 0.9, 'chicken': 0.9, 'carne': 1.0, 'beef': 1.0, 'bife': 1.0,
            'peixe': 1.0, 'fish': 1.0, 'ovo': 0.9, 'egg': 0.9, 'ovos': 0.9,
            'queijo': 0.8, 'cheese': 0.8,
            
            # Vegetables (less dense)
            'cenoura': 0.7, 'carrot': 0.7, 'tomate': 0.6, 'tomato': 0.6,
            'alface': 0.3, 'lettuce': 0.3, 'brocolis': 0.5, 'broccoli': 0.5,
            'cebola': 0.6, 'onion': 0.6, 'vagem': 0.5, 'green beans': 0.5,
            
            # Fruits (low-medium density)
            'banana': 0.7, 'maca': 0.7, 'maça': 0.7, 'apple': 0.7,
            'laranja': 0.6, 'orange': 0.6, 'uva': 0.8, 'grapes': 0.8,
            
            # Default for unmapped foods
            'default': 0.8
        }
        
        return densities.get(food_name, densities['default'])
    
    def _EstimateFoodHeight(self, food_name: str) -> float:
        """
        Estimates average food height on the plate.
        
        Args:
            food_name: Food name
            
        Returns:
            Average height in cm
        """
        food_name = food_name.lower()
        
        # Estimates average food height on plate (2-4cm depending on type)
        if any(word in food_name for word in ['salada', 'alface', 'lettuce']):
            return 2.0  # Salads are lower
        elif any(word in food_name for word in ['arroz', 'rice', 'feijao', 'feijão', 'beans']):
            return 3.0  # Grains have medium height
        elif any(word in food_name for word in ['batata', 'potato', 'carne', 'beef', 'frango', 'chicken']):
            return 4.0  # Proteins are higher
        else:
            return 3.0  # Default height
    
    
    def __init__(self, model_path: str = "yolov8n.pt"):
        """
        Initializes the detector.
        
        Args:
            model_path: Path to YOLO model
        """
        self.model = YOLO(model_path)
        self.food_classes = get_available_foods()
        
        # Mapping of COCO classes to utensils and main foods
        self.coco_to_food = {
            'bowl': 'bowl',
            'cup': 'cup',
            'fork': 'utensil',
            'knife': 'utensil',
            'spoon': 'utensil',
            'carrot': 'carrot',
            'broccoli': 'broccoli',
            'cake': 'cake',
            'donut': 'donut',
            'pizza': 'pizza',
            'sandwich': 'sandwich',
            'hot dog': 'hot dog',
            'hamburger': 'hamburger'
        }
