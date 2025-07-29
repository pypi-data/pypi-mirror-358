import numpy as np
from queue import PriorityQueue

# Метод ветвей и границ с оценкой Липшица
def optimize (f, bounds, max_iter=500, L=10.0, eps=1e-5, **kwargs):
    # f — минимизируемая функция
    # bounds — границы для каждой переменной
    # L — оценка константы Липшица
    # max_iter — максимальное число итераций
    # eps — допустимая погрешность
    # **kwargs — дополнительные параметры

    # Создание приоритетной очереди, для хранения области с минимальной нижней оценкой в приоритете
    q = PriorityQueue()

    # Стартовая область — центр, значение функции в нём, нижняя граница
    x_c = [(b[0] + b[1]) / 2 for b in bounds]
    f_c = f(x_c)
    # Половина диагонали прямоугольника (максимальное расстояние от центра до любого угла)
    r = 0.5 * np.sqrt(sum((b[1] - b[0]) ** 2 for b in bounds))
    # Нижняя граница по неравенству Липшица
    lb = f_c - L * r

    # Помещаем исходную область в очередь
    q.put((lb, bounds, x_c, f_c))

    # Инициализация минимума
    best_val = f_c    # Лучшее значение функции
    best_point = x_c  # Лучшая точка

    for _ in range(max_iter):
        # Если очередь пустая, то выходим из цикла
        if q.empty():
            break

        # Извлекаем область с наименьшей нижней границей
        curr_lb, curr_bounds, curr_xc, curr_fc = q.get()

        # Если область не содержит лучших точек — пропускаем её
        if curr_lb > best_val - eps:
            continue

        # Выбираем для деления ту координату, по которой прямоугольник длиннее всего
        lengths = [b[1] - b[0] for b in curr_bounds]
        split_dim = np.argmax(lengths)
        mid = (curr_bounds[split_dim][0] + curr_bounds[split_dim][1]) / 2

        # Формируем две новые подобласти делением по выбранной координате
        bounds1 = [list(b) for b in curr_bounds]
        bounds2 = [list(b) for b in curr_bounds]
        bounds1[split_dim][1] = mid
        bounds2[split_dim][0] = mid

        for bds in [bounds1, bounds2]:
            # Центр новой подобласти
            x_c_new = [(b[0] + b[1]) / 2 for b in bds]
            # Значение функции в новом центре
            f_c_new = f(x_c_new)
            # Новый радиус
            r_new = 0.5 * np.sqrt(sum((b[1] - b[0])**2 for b in bds))
            # Новая нижняя гранциа
            lb_new = f_c_new - L * r_new

            # Обновляем минимум, если найдено лучшее значение функции
            if f_c_new < best_val:
                best_val = f_c_new
                best_point = x_c_new

            # Добавляем область в очередь, если она может содержать минимум
            if lb_new < best_val - eps:
                q.put((lb_new, [tuple(b) for b in bds], x_c_new, f_c_new))

    return best_point, best_val
