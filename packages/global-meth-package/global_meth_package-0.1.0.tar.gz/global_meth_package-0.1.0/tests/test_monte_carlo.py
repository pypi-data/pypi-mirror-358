from global_meth_package.monte_carlo import monte_carlo
from global_meth_package.utils import rastrigin

def test_monte_carlo():
    bounds = [(-5.12, 5.12)]*3
    x, fx = monte_carlo(rastrigin, bounds, max_iter=10000)
    assert fx < 10
