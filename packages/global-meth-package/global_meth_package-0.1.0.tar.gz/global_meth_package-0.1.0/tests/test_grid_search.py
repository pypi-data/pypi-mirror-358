from global_meth_package.grid_search import grid_search
from global_meth_package.utils import rastrigin

def test_grid_search():
    bounds = [(-5.12, 5.12)]*2
    x, fx = grid_search(rastrigin, bounds,grid_size=50)
    assert fx < 10