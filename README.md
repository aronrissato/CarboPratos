# CarboPratos - Analisador de Calorias 🍽️

Um sistema simples e eficiente para análise de calorias em pratos de comida usando YOLO e IA.

## 🚀 Como usar

### 1. Instalação

```bash
pip install -r requirements.txt
```

### 2. Execução

```bash
python main.py "caminho/para/sua/pasta/imagens"
```

Ou execute sem parâmetros para inserir o caminho interativamente:

```bash
python main.py
```

### 3. Resultados

O programa irá:
- Processar todas as imagens JPEG/PNG na pasta
- Detectar alimentos usando YOLO
- Calcular calorias baseado nos alimentos detectados
- Gerar arquivos `.txt` com os resultados

## 📁 Estrutura do Projeto

```
CarboPratos/
├── src/
│   ├── calorie_database.py    # Base de dados de calorias
│   ├── food_detector.py       # Detector YOLO de alimentos
│   ├── calorie_calculator.py  # Calculadora de calorias
│   └── image_processor.py     # Processador de imagens
├── main.py                    # Programa principal
├── requirements.txt           # Dependências
└── README.md                  # Este arquivo
```

## 🍎 Alimentos Suportados

O sistema reconhece e calcula calorias para:
- Frutas (maçã, banana, uva, etc.)
- Vegetais (cenoura, brócolis, tomate, etc.)
- Proteínas (frango, carne, peixe, etc.)
- Carboidratos (pão, arroz, massa, etc.)
- Laticínios (queijo, leite)

## ⚡ Características

- **Simples**: Interface de linha de comando fácil de usar
- **Eficiente**: Processamento otimizado sem logs desnecessários
- **Extensível**: Fácil adição de novos alimentos na base de dados
- **Robusto**: Tratamento de erros e validações

## 🔧 Desenvolvimento

O projeto segue os princípios:
- **SOLID**: Separação de responsabilidades
- **KISS**: Simplicidade e clareza
- **Performance**: Otimizado para velocidade

## 📝 Exemplo de Saída

Para uma imagem `prato_arroz.jpg`, será gerado `prato_arroz_calories.txt`:

```
ANÁLISE DE CALORIAS - prato_arroz.jpg
==================================================

Calorias totais: 350.5 kcal
Alimentos detectados: 2

Detalhes dos alimentos:
------------------------------
• Rice: 150.0g (195.0 kcal) [Confiança: 0.85]
• Chicken: 120.0g (198.0 kcal) [Confiança: 0.92]
```
