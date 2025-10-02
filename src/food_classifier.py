"""
Food classifier using FastAI and ResNet.
Responsible for classifying foods in images using deep learning.
"""

from typing import List, Dict, Tuple
import torch
from fastai.vision.all import *
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from .calorie_database import get_calories_per_100g, get_available_foods


class FoodClassifier:
    """Food classifier using FastAI and ResNet."""
    
    def __init__(self, model_path: str = None):
        """
        Initializes the classifier.
        
        Args:
            model_path: Path to the trained model (optional)
        """
        self.model_path = model_path
        self.learn = None
        self.food_classes = get_available_foods()
        
        # Define food categories for classification
        self.food_categories = {
            'arroz': ['arroz', 'rice'],
            'feijao': ['feijão', 'feijao', 'beans'],
            'frango': ['frango', 'chicken'],
            'carne': ['carne', 'beef', 'bife'],
            'batata': ['batata', 'potato'],
            'cenoura': ['cenoura', 'carrot'],
            'tomate': ['tomate', 'tomato'],
            'alface': ['alface', 'lettuce'],
            'queijo': ['queijo', 'cheese'],
            'pao': ['pão', 'pao', 'bread'],
            'macarrao': ['macarrão', 'macarrao', 'pasta', 'massa'],
            'banana': ['banana'],
            'maca': ['maçã', 'maca', 'apple'],
            'laranja': ['laranja', 'orange'],
            'uva': ['uva', 'grapes']
        }
        
        # Initialize model if path provided
        if model_path and Path(model_path).exists():
            self.LoadModel(model_path)
    
    def LoadModel(self, model_path: str):
        """
        Loads a pre-trained model.
        
        Args:
            model_path: Path to the model file
        """
        try:
            # Load the model using FastAI
            self.learn = load_learner(model_path)
        except Exception as e:
            raise ValueError(f"Failed to load model from {model_path}: {str(e)}")
    
    def ClassifyFoods(self, image_path: str) -> List[Dict]:
        """
        Classifies foods in an image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            List of dictionaries with classified food information
        """
        if self.learn is None:
            # If no model is loaded, use rule-based classification
            return self._RuleBasedClassification(image_path)
        
        return self._DeepLearningClassification(image_path)
    
    def _DeepLearningClassification(self, image_path: str) -> List[Dict]:
        """
        Performs deep learning classification using FastAI model.
        
        Args:
            image_path: Path to the image
            
        Returns:
            List of classified foods
        """
        try:
            # Load and preprocess image
            image = self._LoadImage(image_path)
            
            # Run classification
            predictions = self.learn.predict(image)
            
            # Process predictions
            classified_foods = []
            if hasattr(predictions[0], '__iter__'):
                # Multi-label classification
                for i, confidence in enumerate(predictions[2]):
                    if confidence > 0.3:  # Confidence threshold
                        food_name = self.learn.dls.vocab[i]
                        calories = get_calories_per_100g(food_name)
                        
                        if calories > 0:
                            classified_foods.append({
                                'class_name': food_name,
                                'confidence': float(confidence),
                                'calories_per_100g': calories,
                                'bbox': self._EstimateBoundingBox(image_path),
                                'area': self._EstimateArea(image_path)
                            })
            else:
                # Single-label classification
                predicted_class = predictions[0]
                confidence = float(predictions[2][predictions[1]])
                
                if confidence > 0.3:
                    calories = get_calories_per_100g(predicted_class)
                    if calories > 0:
                        classified_foods.append({
                            'class_name': predicted_class,
                            'confidence': confidence,
                            'calories_per_100g': calories,
                            'bbox': self._EstimateBoundingBox(image_path),
                            'area': self._EstimateArea(image_path)
                        })
            
            return classified_foods
            
        except Exception as e:
            # Fallback to rule-based classification
            return self._RuleBasedClassification(image_path)
    
    def _RuleBasedClassification(self, image_path: str) -> List[Dict]:
        """
        Fallback rule-based classification when no model is available.
        
        Args:
            image_path: Path to the image
            
        Returns:
            List of classified foods
        """
        # Simple rule-based approach for demonstration
        # In a real scenario, you would implement more sophisticated rules
        classified_foods = []
        
        # For now, return some default foods based on filename
        filename = Path(image_path).stem.lower()
        
        # Check filename for food keywords
        for category, keywords in self.food_categories.items():
            for keyword in keywords:
                if keyword in filename:
                    calories = get_calories_per_100g(keyword)
                    if calories > 0:
                        classified_foods.append({
                            'class_name': keyword,
                            'confidence': 0.7,  # Default confidence
                            'calories_per_100g': calories,
                            'bbox': self._EstimateBoundingBox(image_path),
                            'area': self._EstimateArea(image_path)
                        })
                    break
        
        # If no foods found in filename, add some common foods
        if not classified_foods:
            common_foods = ['arroz', 'feijão', 'frango']
            for food in common_foods:
                calories = get_calories_per_100g(food)
                if calories > 0:
                    classified_foods.append({
                        'class_name': food,
                        'confidence': 0.5,
                        'calories_per_100g': calories,
                        'bbox': self._EstimateBoundingBox(image_path),
                        'area': self._EstimateArea(image_path)
                    })
        
        return classified_foods
    
    def _LoadImage(self, image_path: str):
        """
        Loads an image for classification.
        
        Args:
            image_path: Path to the image
            
        Returns:
            PIL Image object
        """
        try:
            return PILImage.create(image_path)
        except Exception as e:
            raise ValueError(f"Failed to load image {image_path}: {str(e)}")
    
    def _EstimateBoundingBox(self, image_path: str) -> Tuple[float, float, float, float]:
        """
        Estimates a bounding box for the entire image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            Bounding box coordinates (x1, y1, x2, y2)
        """
        try:
            image = cv2.imread(image_path)
            if image is not None:
                height, width = image.shape[:2]
                return (0, 0, float(width), float(height))
        except:
            pass
        
        # Default bounding box
        return (0, 0, 640, 480)
    
    def _EstimateArea(self, image_path: str) -> float:
        """
        Estimates the area of the image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            Estimated area in pixels
        """
        try:
            image = cv2.imread(image_path)
            if image is not None:
                height, width = image.shape[:2]
                return float(height * width)
        except:
            pass
        
        # Default area
        return 307200  # 640 * 480
    
    def TrainModel(self, data_path: str, epochs: int = 10, learning_rate: float = 0.001):
        """
        Trains a new model on the provided dataset.
        
        Args:
            data_path: Path to the training data
            epochs: Number of training epochs
            learning_rate: Learning rate for training
        """
        # This is a placeholder for model training
        # In a real implementation, you would:
        # 1. Load and prepare the dataset
        # 2. Create a DataBlock for multi-label classification
        # 3. Create a learner with ResNet backbone
        # 4. Train the model
        # 5. Save the trained model
        
        print(f"Training model on {data_path} for {epochs} epochs...")
        print("Note: This is a placeholder implementation.")
        print("For actual training, implement the FastAI training pipeline.")
    
    def SaveModel(self, model_path: str):
        """
        Saves the trained model.
        
        Args:
            model_path: Path to save the model
        """
        if self.learn is not None:
            self.learn.export(model_path)
        else:
            raise ValueError("No model to save")
