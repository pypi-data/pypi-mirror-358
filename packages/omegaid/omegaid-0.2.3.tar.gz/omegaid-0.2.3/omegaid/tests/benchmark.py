import time
import numpy as np
import pytest
from omegaid.core.decomposition import calc_phiid_multivariate
import importlib.util

def get_timeseries_data(n_vars=2, n_samples=1000, seed=42):
    rng = np.random.default_rng(seed)
    return rng.standard_normal((n_vars, n_samples))

@pytest.mark.parametrize("n_vars, n_samples", [
    (2, 1000),
    (4, 1000),
    (8, 1000),
    (2, 5000),
    (4, 5000),
])
def test_benchmark_multivariate(n_vars, n_samples):
    data = get_timeseries_data(n_vars, n_samples)
    
    start_time = time.time()
    calc_phiid_multivariate(data, data)
    end_time = time.time()
    
    print(f"Benchmark ({n_vars} vars, {n_samples} samples): {end_time - start_time:.4f}s")

@pytest.mark.parametrize("n_vars, n_samples", [
    (2, 1000),
    (4, 1000),
    (8, 1000),
    (2, 5000),
    (4, 5000),
])
def test_benchmark_gpu(n_vars, n_samples):
    if not importlib.util.find_spec("cupy"):
        pytest.skip("cupy not installed, skipping GPU benchmark")

    from omegaid.utils.backend import set_backend
    set_backend('cupy')

    data = get_timeseries_data(n_vars, n_samples)
    
    start_time = time.time()
    calc_phiid_multivariate(data, data)
    end_time = time.time()
    
    print(f"GPU Benchmark ({n_vars} vars, {n_samples} samples): {end_time - start_time:.4f}s")
