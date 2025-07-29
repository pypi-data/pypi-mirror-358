import numpy as np

# Метод имитации отжига
def optimize(f, bounds, max_iter=10000, seed=42, T_start=1000, T_end=1e-6, alpha=0.995, **kwargs):
    # f — минимизируемая функция
    # bounds — границы для каждой переменной
    # max_iter — максимальное число итераций
    # seed — для генератора случайных чисел
    # T_start — начальная температура
    # T_end — конечная температура
    # alpha — коэффициент "охлаждения"
    # **kwargs — дополнительные параметры

    rng = np.random.default_rng(seed)
    
    # Случайная стартовая точка
    x = np.array([rng.uniform(b[0], b[1]) for b in bounds])
    f_curr = f(x)
    x_best = x.copy()
    f_best = f_curr
    
    T = T_start
    
    for i in range(max_iter):
        # Делаем шаг относительно размера области и текущей температуры
        scale = [0.1 * (b[1] - b[0]) * T for b in bounds]
        # Генерируем новое решение в окрестности текущего
        x_new = x + rng.normal(0, scale, size=len(bounds))
        # Обрезаем по границам
        x_new = np.clip(x_new, [b[0] for b in bounds], [b[1] for b in bounds])
        f_new = f(x_new)
        
        # Разность целевых функций
        delta = f_new - f_curr
        # Критерий Метрополиса: всегда принимаем улучшение, иначе — с вероятностью exp(-ΔE/T)
        if delta < 0 or rng.uniform() < np.exp(-delta / T):
            x = x_new
            f_curr = f_new
            # Обновляем глобальный минимум, если нашли решение лучше
            if f_curr < f_best:
                x_best = x.copy()
                f_best = f_curr
        
        # Охлаждение
        T *= alpha
        if T < T_end:
            break

    return x_best.tolist(), f_best
