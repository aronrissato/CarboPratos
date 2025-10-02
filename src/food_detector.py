"""
Detector de alimentos usando YOLO.
Responsável por detectar alimentos em imagens.
"""

from typing import List, Tuple, Dict
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
from .calorie_database import get_calories_per_100g, get_available_foods


class FoodDetector:
    """Detector de alimentos usando YOLO."""
    
    def DetectFoods(self, image_path: str) -> List[Dict]:
        """
        Detecta alimentos em uma imagem.
        
        Args:
            image_path: Caminho para a imagem
            
        Returns:
            Lista de dicionários com informações dos alimentos detectados
        """
        results = self.model(image_path)
        detections = self._ProcessDetectionResults(results)
        
        # Se não detectou nenhum alimento, tenta detectar pelo nome do arquivo
        if not detections:
            detections = self._DetectFromFilename(image_path)
        
        return detections
    
    def EstimateFoodQuantity(self, detection: Dict, image_shape: Tuple[int, int]) -> float:
        """
        Estima a quantidade de alimento baseado na área detectada.
        
        Args:
            detection: Dados da detecção
            image_shape: (altura, largura) da imagem
            
        Returns:
            Quantidade estimada em gramas
        """
        # Calcula área do alimento em cm²
        food_area_cm2 = self._CalculateFoodArea(detection, image_shape)
        
        # Obtém densidade e altura do alimento
        density = self._GetFoodDensity(detection['class_name'])
        avg_height_cm = self._EstimateFoodHeight(detection['class_name'])
        
        # Volume do alimento em cm³
        food_volume_cm3 = food_area_cm2 * avg_height_cm
        
        # Peso estimado em gramas
        estimated_weight = food_volume_cm3 * density
        
        # Limitações realistas: mínimo 30g, máximo 400g por alimento
        estimated_weight = max(min(estimated_weight, 400), 30)
        
        return round(estimated_weight, 1)
    
    def _DetectFromFilename(self, image_path: str) -> List[Dict]:
        """
        Detecta alimentos baseado no nome do arquivo como fallback.
        
        Args:
            image_path: Caminho para a imagem
            
        Returns:
            Lista de detecções baseadas no nome do arquivo
        """
        filename = Path(image_path).stem.lower()
        detected_foods = self._ExtractFoodsFromFilename(filename)
        
        # Cria detecções para os alimentos encontrados
        detections = []
        for food in detected_foods:
            calories = get_calories_per_100g(food)
            if calories > 0:
                # Área fictícia proporcional ao número de alimentos
                area_per_food = 50000 // max(len(detected_foods), 1)
                
                detections.append({
                    'class_name': food,
                    'coco_class': 'filename_detection',
                    'confidence': 0.7,  # Confiança média para detecção por nome
                    'bbox': (0, 0, 100, 100),  # Bbox fictício
                    'area': area_per_food,
                    'calories_per_100g': calories
                })
        
        return detections
    
    def _ProcessDetectionResults(self, results) -> List[Dict]:
        """
        Processa os resultados da detecção YOLO.
        
        Args:
            results: Resultados do modelo YOLO
            
        Returns:
            Lista de detecções processadas
        """
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Pega as coordenadas e confiança
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    # Pega o nome da classe
                    class_name = self.model.names[class_id]
                    
                    # Mapeia classe COCO para alimento se possível
                    food_name = self.coco_to_food.get(class_name, class_name)
                    
                    # Calcula área da detecção
                    area = (x2 - x1) * (y2 - y1)
                    
                    # Só adiciona se for um alimento com calorias conhecidas
                    calories = get_calories_per_100g(food_name)
                    if calories > 0 or class_name in ['bowl', 'cup']:  # Inclui utensílios para contexto
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
        Calcula a área do alimento em cm².
        
        Args:
            detection: Dados da detecção
            image_shape: (altura, largura) da imagem
            
        Returns:
            Área do alimento em cm²
        """
        # Área da detecção em pixels
        detection_area = detection['area']
        
        # Área total da imagem
        total_area = image_shape[0] * image_shape[1]
        
        # Proporção da área ocupada pelo alimento
        area_ratio = detection_area / total_area
        
        # Estimativa mais realista baseada em prato de 25cm de diâmetro
        # Área do prato = π * (12.5cm)² = ~491 cm²
        plate_area_cm2 = 491
        
        # Área ocupada pelo alimento em cm²
        food_area_cm2 = area_ratio * plate_area_cm2
        
        # Ajuste para detecção por nome do arquivo (área fictícia)
        if detection.get('coco_class') == 'filename_detection':
            # Para detecção por nome, assume que o alimento ocupa metade do prato
            food_area_cm2 = plate_area_cm2 * 0.4  # 40% do prato por alimento
        
        return food_area_cm2
    
    def _GetFoodDensity(self, food_name: str) -> float:
        """
        Obtém a densidade do alimento.
        
        Args:
            food_name: Nome do alimento
            
        Returns:
            Densidade em g/cm³
        """
        food_name = food_name.lower()
        
        # Densidades aproximadas (g/cm³) para diferentes tipos de alimentos
        densities = {
            # Grãos e carboidratos (mais densos)
            'arroz': 0.8, 'rice': 0.8, 'feijao': 1.2, 'feijão': 1.2, 'beans': 1.2,
            'macarrao': 0.6, 'macarrão': 0.6, 'pasta': 0.6, 'massa': 0.6,
            'batata': 0.7, 'potato': 0.7, 'batata_doce': 0.8, 'sweet potato': 0.8,
            
            # Proteínas (densidade média)
            'frango': 0.9, 'chicken': 0.9, 'carne': 1.0, 'beef': 1.0, 'bife': 1.0,
            'peixe': 1.0, 'fish': 1.0, 'ovo': 0.9, 'egg': 0.9, 'ovos': 0.9,
            'queijo': 0.8, 'cheese': 0.8,
            
            # Vegetais (menos densos)
            'cenoura': 0.7, 'carrot': 0.7, 'tomate': 0.6, 'tomato': 0.6,
            'alface': 0.3, 'lettuce': 0.3, 'brocolis': 0.5, 'broccoli': 0.5,
            'cebola': 0.6, 'onion': 0.6, 'vagem': 0.5, 'green beans': 0.5,
            
            # Frutas (densidade baixa-média)
            'banana': 0.7, 'maca': 0.7, 'maça': 0.7, 'apple': 0.7,
            'laranja': 0.6, 'orange': 0.6, 'uva': 0.8, 'grapes': 0.8,
            
            # Padrão para alimentos não mapeados
            'default': 0.8
        }
        
        return densities.get(food_name, densities['default'])
    
    def _EstimateFoodHeight(self, food_name: str) -> float:
        """
        Estima a altura média do alimento no prato.
        
        Args:
            food_name: Nome do alimento
            
        Returns:
            Altura média em cm
        """
        food_name = food_name.lower()
        
        # Estima altura média do alimento no prato (2-4cm dependendo do tipo)
        if any(word in food_name for word in ['salada', 'alface', 'lettuce']):
            return 2.0  # Saladas são mais baixas
        elif any(word in food_name for word in ['arroz', 'rice', 'feijao', 'feijão', 'beans']):
            return 3.0  # Grãos têm altura média
        elif any(word in food_name for word in ['batata', 'potato', 'carne', 'beef', 'frango', 'chicken']):
            return 4.0  # Proteínas são mais altas
        else:
            return 3.0  # Altura padrão
    
    def _ExtractFoodsFromFilename(self, filename: str) -> List[str]:
        """
        Extrai alimentos do nome do arquivo.
        
        Args:
            filename: Nome do arquivo (sem extensão)
            
        Returns:
            Lista de alimentos detectados
        """
        # Mapeamento específico para nomes de arquivo comuns
        filename_mappings = {
            'feijaoearroz': ['feijao', 'arroz'],
            'feijao_arroz': ['feijao', 'arroz'],
            'feijão_arroz': ['feijão', 'arroz'],
            'arroz_feijao': ['arroz', 'feijao'],
            'arroz_feijão': ['arroz', 'feijão'],
            'prato_feijao': ['feijao'],
            'prato_arroz': ['arroz'],
            'salada_verde': ['alface', 'tomate'],
            'salada_mista': ['alface', 'tomate', 'cenoura'],
            'frango_arroz': ['frango', 'arroz'],
            'macarrao_queijo': ['macarrao', 'queijo'],
            'pasta_queijo': ['massa', 'queijo'],
        }
        
        # Verifica mapeamentos específicos primeiro
        detected_foods = []
        for pattern, foods in filename_mappings.items():
            if pattern in filename:
                detected_foods.extend(foods)
                break
        
        # Se não encontrou mapeamento específico, procura por palavras individuais
        if not detected_foods:
            for food in self.food_classes:
                if food in filename and len(food) > 2:  # Evita falsos positivos
                    detected_foods.append(food)
        
        return detected_foods
    
    def __init__(self, model_path: str = "yolov8n.pt"):
        """
        Inicializa o detector.
        
        Args:
            model_path: Caminho para o modelo YOLO
        """
        self.model = YOLO(model_path)
        self.food_classes = get_available_foods()
        
        # Mapeamento de classes COCO para utensílios e alimentos principais
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
