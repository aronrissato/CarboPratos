"""
Calorie calculator based on food detections.
"""

from typing import List, Dict
from pathlib import Path
from .food_detector import FoodDetector
import cv2
import numpy as np
from PIL import Image


class CalorieCalculator:
    """Calorie calculator for food plates."""
    
    def __init__(self, detector: FoodDetector):
        """
        Initializes the calculator.
        
        Args:
            detector: Food detector instance
        """
        self.detector = detector
    
    def CalculatePlateCalories(self, image_path: str) -> Dict:
        """
        Calculates plate calories based on detections.
        
        Args:
            image_path: Path to the plate image
            
        Returns:
            Dictionary with plate and calorie information
        """
        # Detect foods in the image
        detections = self.detector.DetectFoods(image_path)
        
        # Load image to get dimensions
        image = self._LoadImage(image_path)
        image_shape = image.shape[:2]  # (height, width)
        
        total_calories = 0
        food_details = []
        
        # Process each detection
        for detection in detections:
            # Estimate quantity in grams
            estimated_weight = self.detector.EstimateFoodQuantity(detection, image_shape)
            
            # Calculate calories for this quantity
            calories = (detection['calories_per_100g'] * estimated_weight) / 100
            
            total_calories += calories
            
            food_details.append({
                'food': detection['class_name'],
                'weight_g': round(estimated_weight, 1),
                'calories': round(calories, 1),
                'confidence': round(detection['confidence'], 2)
            })
        
        return {
            'total_calories': round(total_calories, 1),
            'food_count': len(detections),
            'food_details': food_details,
            'image_path': image_path
        }
    
    def _LoadImage(self, image_path: str) -> np.ndarray:
        """
        Loads an image using OpenCV, with PIL fallback.
        
        Args:
            image_path: Path to the image
            
        Returns:
            Numpy array of the image
            
        Raises:
            ValueError: If image cannot be loaded
        """
        # Convert to absolute path and check if exists
        abs_path = Path(image_path).resolve()
        if not abs_path.exists():
            raise ValueError(f"Image Not Found {abs_path}")
        
        # Try loading with OpenCV first
        image = cv2.imread(str(abs_path))
        if image is not None:
            return image
        
        # If OpenCV failed, try with PIL
        try:
            with Image.open(image_path) as pil_image:
                # Convert PIL to numpy array (RGB)
                pil_array = np.array(pil_image)
                
                # If image has alpha channel, remove it
                if len(pil_array.shape) == 3 and pil_array.shape[2] == 4:
                    pil_array = pil_array[:, :, :3]
                
                # Convert RGB to BGR (OpenCV uses BGR)
                if len(pil_array.shape) == 3:
                    pil_array = cv2.cvtColor(pil_array, cv2.COLOR_RGB2BGR)
                
                return pil_array
                
        except Exception as e:
            raise ValueError(f"Unsupported Image Format or Corrupted File: {image_path} - {str(e)}")
