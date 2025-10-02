"""
Image processor for a folder.
Responsible for processing all images in a directory.
"""

from typing import List
from pathlib import Path
from .calorie_calculator import CalorieCalculator


class ImageProcessor:
    """Image processor for calorie analysis."""
    
    def ProcessDirectory(self, directory_path: str, output_directory: str = None) -> List[dict]:
        """
        Processes all images in a directory.
        
        Args:
            directory_path: Path to the directory with images
            output_directory: Directory to save results (optional)
            
        Returns:
            List with processing results
        """
        self.VerifyDirectoryPath(directory_path)
        output_dir = self.SetupOutputDirectory(directory_path, output_directory)
        image_files = self.FindImageFiles(directory_path)
        
        results = []
        for image_file in image_files:
            result = self.ProcessImageFile(image_file)
            results.append(result)
            self.SaveResultToFile(result, image_file, output_dir)
        
        return results
    
    def VerifyDirectoryPath(self, directory_path: str):
        """Verifies if the directory path exists."""
        directory = Path(directory_path)
        if not directory.exists():
            raise ValueError(f"Directory not found: {directory_path}")
    
    def SetupOutputDirectory(self, directory_path: str, output_directory: str = None) -> Path:
        """Sets up the output directory for saving results."""
        if output_directory:
            output_dir = Path(output_directory)
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = Path(directory_path)
        return output_dir
    
    def FindImageFiles(self, directory_path: str) -> List[Path]:
        """Finds all supported image files in the directory."""
        directory = Path(directory_path)
        return [f for f in directory.iterdir() 
                if f.is_file() and f.suffix.lower() in self.supported_formats]
    
    def ProcessImageFile(self, image_file: Path) -> dict:
        """Processes a single image file and calculates calories."""
        try:
            return self.calculator.CalculatePlateCalories(str(image_file))
        except Exception as e:
            return {
                'image_path': str(image_file),
                'error': str(e),
                'total_calories': 0,
                'food_count': 0
            }
    
    def SaveResultToFile(self, result: dict, image_file: Path, output_dir: Path):
        """Saves the processing result to a text file."""
        self._SaveResultToFile(result, image_file, output_dir)
    
    def _SaveResultToFile(self, result: dict, image_file: Path, output_dir: Path):
        """
        Saves the result to a text file.
        
        Args:
            result: Calorie calculation result
            image_file: Original image file
            output_dir: Output directory
        """
        # Filename based on the image
        output_filename = image_file.stem + '_calories.txt'
        output_path = output_dir / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"CALORIE ANALYSIS - {image_file.name}\n")
            f.write("=" * 50 + "\n\n")
            
            if 'error' in result:
                f.write(f"ERROR: {result['error']}\n")
            else:
                f.write(f"Total calories: {result['total_calories']} kcal\n")
                f.write(f"Foods detected: {result['food_count']}\n\n")
                
                if result['food_details']:
                    f.write("Food details:\n")
                    f.write("-" * 30 + "\n")
                    for food in result['food_details']:
                        f.write(f"• {food['food'].title()}: ")
                        f.write(f"{food['weight_g']}g ({food['calories']} kcal) ")
                        f.write(f"[Confidence: {food['confidence']}]\n")
                else:
                    f.write("No foods were detected in the image.\n")
    
    def __init__(self, calorie_calculator: CalorieCalculator):
        """
        Initializes the processor.
        
        Args:
            calorie_calculator: Calorie calculator instance
        """
        self.calculator = calorie_calculator
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.avif', '.webp'}
