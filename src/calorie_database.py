"""
Database de calorias por alimento detectado pelo YOLO.
Baseado nas classes COCO dataset que o YOLO reconhece.
"""

CALORIE_DATABASE = {
    # Frutas
    'apple': 52, 'maça': 52, 'maca': 52,
    'orange': 47, 'laranja': 47,
    'banana': 89,
    'grapes': 67, 'uva': 67, 'uvas': 67,
    'strawberry': 32, 'morango': 32, 'morangos': 32,
    'mango': 60, 'manga': 60,
    'pineapple': 50, 'abacaxi': 50,
    'watermelon': 30, 'melancia': 30,
    'lemon': 29, 'limão': 29, 'limao': 29,
    
    # Vegetais
    'carrot': 41, 'cenoura': 41, 'cenouras': 41,
    'broccoli': 34, 'brócolis': 34, 'brocolis': 34,
    'lettuce': 15, 'alface': 15,
    'tomato': 18, 'tomate': 18, 'tomates': 18,
    'onion': 40, 'cebola': 40, 'cebolas': 40,
    'cucumber': 16, 'pepino': 16,
    'potato': 77, 'batata': 77, 'batatas': 77,
    'sweet potato': 86, 'batata doce': 86, 'batata_doce': 86,
    'pepper': 31, 'pimentão': 31, 'pimentao': 31,
    'cabbage': 25, 'repolho': 25,
    'spinach': 23, 'espinafre': 23,
    'eggplant': 25, 'berinjela': 25,
    'zucchini': 17, 'abobrinha': 17,
    'corn': 96, 'milho': 96,
    'green beans': 31, 'vagem': 31, 'feijão verde': 31, 'feijao_verde': 31,
    'peas': 81, 'ervilha': 81, 'ervilhas': 81,
    
    # Legumes e Grãos
    'beans': 347, 'feijão': 347, 'feijao': 347,
    'lentils': 353, 'lentilha': 353, 'lentilhas': 353,
    'chickpeas': 364, 'grão de bico': 364, 'grao_de_bico': 364,
    'soybeans': 446, 'soja': 446,
    'quinoa': 368, 'quinua': 368,
    
    # Proteínas
    'chicken': 165, 'frango': 165,
    'beef': 250, 'carne': 250, 'bife': 250,
    'pork': 242, 'porco': 242, 'lombo': 242,
    'fish': 206, 'peixe': 206, 'salmão': 208, 'salmão': 208,
    'shrimp': 99, 'camarão': 99, 'camarao': 99,
    'egg': 155, 'ovo': 155, 'ovos': 155,
    'tofu': 76,
    'turkey': 189, 'peru': 189,
    
    # Carboidratos
    'bread': 265, 'pão': 265, 'pao': 265,
    'pizza': 266,
    'pasta': 131, 'macarrão': 131, 'macarrao': 131, 'massa': 131,
    'rice': 130, 'arroz': 130,
    'noodles': 138, 'talharim': 138,
    'lasagna': 132, 'lasanha': 132,
    'ravioli': 142, 'ravioli': 142,
    
    # Laticínios
    'cheese': 113, 'queijo': 113,
    'milk': 42, 'leite': 42,
    'yogurt': 59, 'iogurte': 59,
    'butter': 717, 'manteiga': 717,
    'cream': 345, 'creme': 345,
    'mozzarella': 280, 'mussarela': 280,
    'parmesan': 431, 'parmesão': 431, 'parmesao': 431,
    
    # Frutos Secos e Sementes
    'nuts': 607, 'castanha': 607, 'castanhas': 607,
    'almonds': 579, 'amêndoas': 579, 'amendoas': 579,
    'walnuts': 654, 'nozes': 654,
    'peanuts': 567, 'amendoim': 567,
    'cashews': 553, 'castanha de caju': 553, 'castanha_de_caju': 553,
    'seeds': 559, 'sementes': 559,
    'sunflower seeds': 584, 'semente de girassol': 584,
    
    # Outros
    'sandwich': 250, 'sanduíche': 250, 'sanduiche': 250,
    'cake': 350, 'bolo': 350,
    'donut': 452, 'rosquinha': 452,
    'hot dog': 290,
    'hamburger': 354, 'hambúrguer': 354, 'hamburguer': 354,
    'french fries': 365, 'batata frita': 365, 'batata_frita': 365,
    'ice cream': 207, 'sorvete': 207,
    'chocolate': 546, 'chocolate': 546,
    'cookie': 488, 'biscoito': 488,
    'cracker': 421, 'bolacha': 421,
    'soup': 25, 'sopa': 25,
    'salad': 20, 'salada': 20,
    'dressing': 450, 'molho': 450,
    'oil': 884, 'óleo': 884, 'oleo': 884,
    'olive oil': 884, 'azeite': 884,
    'vinegar': 19, 'vinagre': 19,
    'salt': 0, 'sal': 0,
    'sugar': 387, 'açúcar': 387, 'acucar': 387,
    'honey': 304, 'mel': 304,
    'jam': 265, 'geleia': 265,
    'mustard': 66, 'mostarda': 66,
    'ketchup': 112,
    'mayonnaise': 680, 'maionese': 680,
}

def get_calories_per_100g(food_item: str) -> int:
    """
    Retorna as calorias por 100g de um alimento.
    
    Args:
        food_item: Nome do alimento
        
    Returns:
        Calorias por 100g, ou 0 se não encontrado
    """
    return CALORIE_DATABASE.get(food_item.lower(), 0)

def get_available_foods() -> list:
    """Retorna lista de alimentos disponíveis na base de dados."""
    return list(CALORIE_DATABASE.keys())
