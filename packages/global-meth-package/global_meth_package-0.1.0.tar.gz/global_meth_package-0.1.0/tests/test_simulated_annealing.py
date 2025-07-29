from global_meth_package.simulated_annealing import simulated_annealing
from global_meth_package.utils import rastrigin

def test_simulated_annealing():
    bounds = [(-5.12, 5.12)]*3
    x, fx = simulated_annealing(rastrigin, bounds,seed=42)
    assert fx < 10