# CarboPratos - Food Calorie Analyzer 🍽️

A simple and efficient system for analyzing calories in food plates using YOLO and AI.

## 🚀 How to Use

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Execution

```bash
python main.py "path/to/your/images/folder"
```

Or run without parameters to enter the path interactively:

```bash
python main.py
```

### 3. Results

The program will:
- Process all JPEG/PNG images in the folder
- Detect foods using YOLO
- Calculate calories based on detected foods
- Generate `.txt` files with results

## 📁 Project Structure

```
CarboPratos/
├── src/
│   ├── calorie_database.py    # Calorie database
│   ├── food_detector.py       # YOLO food detector
│   ├── calorie_calculator.py  # Calorie calculator
│   └── image_processor.py     # Image processor
├── main.py                    # Main program
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## 🍎 Supported Foods

The system recognizes and calculates calories for:
- Fruits (apple, banana, grapes, etc.)
- Vegetables (carrot, broccoli, tomato, etc.)
- Proteins (chicken, beef, fish, etc.)
- Carbohydrates (bread, rice, pasta, etc.)
- Dairy (cheese, milk)

## ⚡ Features

- **Simple**: Easy-to-use command line interface
- **Efficient**: Optimized processing without unnecessary logs
- **Extensible**: Easy addition of new foods to the database
- **Robust**: Error handling and validations

## 🔧 Development

The project follows these principles:
- **SOLID**: Separation of responsibilities
- **KISS**: Simplicity and clarity
- **Performance**: Optimized for speed

## 📝 Output Example

For an image `rice_plate.jpg`, it will generate `rice_plate_calories.txt`:

```
CALORIE ANALYSIS - rice_plate.jpg
==================================================

Total calories: 350.5 kcal
Foods detected: 2

Food details:
------------------------------
• Rice: 150.0g (195.0 kcal) [Confidence: 0.85]
• Chicken: 120.0g (198.0 kcal) [Confidence: 0.92]
```
