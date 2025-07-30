import numpy as np
import itertools

# Метод сеточного поиска
def optimize(f, bounds, max_iter=None, grid_size=30, **kwargs):
    # f — минимизируемая функция
    # bounds — границы для каждой переменной
    # max_iter — максимальное число итераций
    # grid_size — количество узлов сетки на каждую переменную
    # **kwargs — дополнительные параметры

    # Построение сетки, имеющей grid_size узлов и grids точек
    grids = [np.linspace(b[0], b[1], grid_size) for b in bounds]

    # Инициализация минимума
    best_val = None    # Лучшее значение функции
    best_point = None  # Лучшая точка

    # Перебираем все узлы сетки (декартово произведение)
    for point in itertools.product(*grids):
        val = f(point)
        if (best_val is None) or (val < best_val):
            best_val = val
            best_point = point

    return best_point, best_val
