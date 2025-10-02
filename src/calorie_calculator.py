"""
Calculadora de calorias baseada em detecções de alimentos.
"""

from typing import List, Dict
from pathlib import Path
from .food_detector import FoodDetector
import cv2
import numpy as np
from PIL import Image


class CalorieCalculator:
    """Calculadora de calorias para pratos de comida."""
    
    def __init__(self, detector: FoodDetector):
        """
        Inicializa a calculadora.
        
        Args:
            detector: Instância do detector de alimentos
        """
        self.detector = detector
    
    def CalculatePlateCalories(self, image_path: str) -> Dict:
        """
        Calcula as calorias de um prato baseado nas detecções.
        
        Args:
            image_path: Caminho para a imagem do prato
            
        Returns:
            Dicionário com informações sobre o prato e suas calorias
        """
        # Detecta alimentos na imagem
        detections = self.detector.DetectFoods(image_path)
        
        # Carrega a imagem para obter dimensões
        image = self._LoadImage(image_path)
        image_shape = image.shape[:2]  # (altura, largura)
        
        total_calories = 0
        food_details = []
        
        # Processa cada detecção
        for detection in detections:
            # Estima a quantidade em gramas
            estimated_weight = self.detector.EstimateFoodQuantity(detection, image_shape)
            
            # Calcula calorias para esta quantidade
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
        Carrega uma imagem usando OpenCV, com fallback para PIL.
        
        Args:
            image_path: Caminho para a imagem
            
        Returns:
            Array numpy da imagem
            
        Raises:
            ValueError: Se a imagem não puder ser carregada
        """
        # Converte para caminho absoluto e verifica se existe
        abs_path = Path(image_path).resolve()
        if not abs_path.exists():
            raise ValueError(f"Image Not Found {abs_path}")
        
        # Tenta carregar com OpenCV primeiro
        image = cv2.imread(str(abs_path))
        if image is not None:
            return image
        
        # Se OpenCV falhou, tenta com PIL
        try:
            with Image.open(image_path) as pil_image:
                # Converte PIL para numpy array (RGB)
                pil_array = np.array(pil_image)
                
                # Se a imagem tem canal alpha, remove
                if len(pil_array.shape) == 3 and pil_array.shape[2] == 4:
                    pil_array = pil_array[:, :, :3]
                
                # Converte RGB para BGR (OpenCV usa BGR)
                if len(pil_array.shape) == 3:
                    pil_array = cv2.cvtColor(pil_array, cv2.COLOR_RGB2BGR)
                
                return pil_array
                
        except Exception as e:
            raise ValueError(f"Unsupported Image Format or Corrupted File: {image_path} - {str(e)}")
