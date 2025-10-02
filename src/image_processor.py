"""
Processador de imagens de uma pasta.
Responsável por processar todas as imagens em um diretório.
"""

import os
from typing import List
from pathlib import Path
from .calorie_calculator import CalorieCalculator
from .food_detector import FoodDetector


class ImageProcessor:
    """Processador de imagens para análise de calorias."""
    
    def __init__(self, calorie_calculator: CalorieCalculator):
        """
        Inicializa o processador.
        
        Args:
            calorie_calculator: Instância da calculadora de calorias
        """
        self.calculator = calorie_calculator
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.avif', '.webp'}
    
    def ProcessDirectory(self, directory_path: str, output_directory: str = None) -> List[dict]:
        """
        Processa todas as imagens em um diretório.
        
        Args:
            directory_path: Caminho para o diretório com imagens
            output_directory: Diretório para salvar os resultados (opcional)
            
        Returns:
            Lista com resultados do processamento
        """
        directory = Path(directory_path)
        if not directory.exists():
            raise ValueError(f"Diretório não encontrado: {directory_path}")
        
        if output_directory:
            output_dir = Path(output_directory)
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = directory
        
        results = []
        image_files = [f for f in directory.iterdir() 
                      if f.is_file() and f.suffix.lower() in self.supported_formats]
        
        for image_file in image_files:
            try:
                result = self.calculator.CalculatePlateCalories(str(image_file))
                results.append(result)
                
                # Salva resultado em arquivo de texto
                self._SaveResultToFile(result, image_file, output_dir)
                
            except Exception as e:
                error_result = {
                    'image_path': str(image_file),
                    'error': str(e),
                    'total_calories': 0,
                    'food_count': 0
                }
                results.append(error_result)
        
        return results
    
    def _SaveResultToFile(self, result: dict, image_file: Path, output_dir: Path):
        """
        Salva o resultado em um arquivo de texto.
        
        Args:
            result: Resultado do cálculo de calorias
            image_file: Arquivo da imagem original
            output_dir: Diretório de saída
        """
        # Nome do arquivo baseado na imagem
        output_filename = image_file.stem + '_calories.txt'
        output_path = output_dir / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"ANÁLISE DE CALORIAS - {image_file.name}\n")
            f.write("=" * 50 + "\n\n")
            
            if 'error' in result:
                f.write(f"ERRO: {result['error']}\n")
            else:
                f.write(f"Calorias totais: {result['total_calories']} kcal\n")
                f.write(f"Alimentos detectados: {result['food_count']}\n\n")
                
                if result['food_details']:
                    f.write("Detalhes dos alimentos:\n")
                    f.write("-" * 30 + "\n")
                    for food in result['food_details']:
                        f.write(f"• {food['food'].title()}: ")
                        f.write(f"{food['weight_g']}g ({food['calories']} kcal) ")
                        f.write(f"[Confiança: {food['confidence']}]\n")
                else:
                    f.write("Nenhum alimento foi detectado na imagem.\n")
