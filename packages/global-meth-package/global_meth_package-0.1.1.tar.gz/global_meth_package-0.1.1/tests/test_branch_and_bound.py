from global_meth_package.branch_and_bound import branch_and_bound
from global_meth_package.utils import rastrigin

def test_branch_and_bound():
    bounds = [(-5.12, 5.12)]*3
    x, fx = branch_and_bound(rastrigin, bounds, L = 103)
    assert fx < 10