"""
Programa principal para análise de calorias em pratos de comida.
"""

import sys
from pathlib import Path
from src.food_detector import FoodDetector
from src.calorie_calculator import CalorieCalculator
from src.image_processor import ImageProcessor


def main():
    """Função principal do programa."""
    print("CarboPratos - Analisador de Calorias")
    print("=" * 40)
    
    # Obtém e valida o caminho
    images_directory = GetFolderPath()
    if not ValidatePath(images_directory):
        return
    
    try:
        # Inicializa componentes do sistema
        print("\nInicializando sistema...")
        detector = FoodDetector()
        calculator = CalorieCalculator(detector)
        processor = ImageProcessor(calculator)
        print("Sistema inicializado com sucesso!")
        
        # Processa diretório
        results = ProcessDirectory(processor, images_directory)
        
        # Exibe resumo
        PrintResume(results, images_directory)
        
    except Exception as e:
        print(f"ERRO durante o processamento: {str(e)}")
        return


def GetFolderPath() -> str:
    """Obtém o caminho da pasta com imagens."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        return input("Digite o caminho da pasta com as imagens: ").strip()


def ValidatePath(directory_path: str) -> bool:
    """Valida se o diretório existe."""
    if not Path(directory_path).exists():
        print(f"ERRO: Diretório não encontrado: {directory_path}")
        return False
    return True


def ProcessDirectory(processor: ImageProcessor, directory_path: str):
    """Processa todas as imagens do diretório."""
    print(f"\nProcessando imagens em: {directory_path}")
    return processor.ProcessDirectory(directory_path)


def PrintResume(results: list, directory_path: str):
    """Exibe o resumo do processamento."""
    print(f"\nRESUMO DO PROCESSAMENTO")
    print("-" * 30)
    print(f"Imagens processadas: {len(results)}")
    
    successful = [r for r in results if 'error' not in r]
    errors = [r for r in results if 'error' in r]
    
    print(f"Sucessos: {len(successful)}")
    print(f"Erros: {len(errors)}")
    
    if successful:
        total_calories = sum(r['total_calories'] for r in successful)
        print(f"Calorias totais detectadas: {total_calories:.1f} kcal")
    
    if errors:
        print(f"\nErros encontrados:")
        for error in errors:
            print(f"  - {Path(error['image_path']).name}: {error['error']}")
    
    print(f"\nProcessamento concluído!")
    print(f"Arquivos de resultado salvos na pasta: {directory_path}")


if __name__ == "__main__":
    main()
