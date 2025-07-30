import numpy as np

# Метод Монте-Карло
def optimize(f, bounds, max_iter=10000, seed=42, **kwargs):
    # f — минимизируемая функция
    # bounds — границы для каждой переменной
    # max_iter —количество случайных точек
    # seed — для генератора случайных чисел
    # **kwargs — дополнительные параметры

    rng = np.random.default_rng(seed)
    
    # Инициализация минимума
    best_val = None    # Лучшее значение функции
    best_point = None  # Лучшая точка

    # Генерируем и проверяем случайные точки
    for _ in range(max_iter):
        x = [rng.uniform(b[0], b[1]) for b in bounds]
        val = f(x)
        if (best_val is None) or (val < best_val):
            best_val = val
            best_point = x

    return best_point, best_val
