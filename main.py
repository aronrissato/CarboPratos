"""
Main program for food calorie analysis.
"""

import sys
from pathlib import Path
from src.food_detector import FoodDetector
from src.calorie_calculator import CalorieCalculator
from src.image_processor import ImageProcessor


def main():
    """Main program function."""
    print("CarboPratos - Food Calorie Analyzer")
    print("=" * 40)
    
    # Gets and validates the path
    images_directory = GetFolderPath()
    if not ValidatePath(images_directory):
        return
    
    try:
        # Initialize system components
        print("\nInitializing system...")
        detector = FoodDetector()
        calculator = CalorieCalculator(detector)
        processor = ImageProcessor(calculator)
        print("System initialized successfully!")
        
        # Process directory
        results = ProcessDirectory(processor, images_directory)
        
        # Display summary
        PrintResume(results, images_directory)
        
    except Exception as e:
        print(f"ERROR during processing: {str(e)}")
        return


def GetFolderPath() -> str:
    """Gets the path to the images folder."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        return input("Enter the path to the images folder: ").strip()


def ValidatePath(directory_path: str) -> bool:
    """Validates if the directory exists."""
    if not Path(directory_path).exists():
        print(f"ERROR: Directory not found: {directory_path}")
        return False
    return True


def ProcessDirectory(processor: ImageProcessor, directory_path: str):
    """Processes all images in the directory."""
    print(f"\nProcessing images in: {directory_path}")
    return processor.ProcessDirectory(directory_path)


def PrintResume(results: list, directory_path: str):
    """Displays the processing summary."""
    print(f"\nPROCESSING SUMMARY")
    print("-" * 30)
    print(f"Images processed: {len(results)}")
    
    successful = [r for r in results if 'error' not in r]
    errors = [r for r in results if 'error' in r]
    
    print(f"Successes: {len(successful)}")
    print(f"Errors: {len(errors)}")
    
    if successful:
        total_calories = sum(r['total_calories'] for r in successful)
        print(f"Total calories detected: {total_calories:.1f} kcal")
    
    if errors:
        print(f"\nErrors found:")
        for error in errors:
            print(f"  - {Path(error['image_path']).name}: {error['error']}")
    
    print(f"\nProcessing completed!")
    print(f"Result files saved in folder: {directory_path}")


if __name__ == "__main__":
    main()
