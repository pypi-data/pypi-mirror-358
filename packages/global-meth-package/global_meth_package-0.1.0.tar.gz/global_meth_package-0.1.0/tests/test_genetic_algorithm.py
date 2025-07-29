from global_meth_package.genetic_algorithm import genetic_algorithm
from global_meth_package.utils import rastrigin

def test_grid_search():
    bounds = [(-5.12, 5.12)]*3
    x, fx = genetic_algorithm(rastrigin, bounds)
    assert fx < 10