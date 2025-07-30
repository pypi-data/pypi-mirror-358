import time
import numpy as np
import pytest
from omegaid.core.decomposition import calc_phiid_multivariate
from phyid.calculate import calc_PhiID as calc_PhiID_original
from omegaid.utils.backend import set_backend
import importlib.util
import collections

RESULTS: dict = {}

@pytest.fixture(scope="session", autouse=True)
def teardown():
    yield
    print("\n\n--- Benchmark Results ---")
    
    cases = collections.defaultdict(dict)
    for (dim, redundancy, impl), time_val in RESULTS.items():
        cases[f"{dim} {redundancy}"][impl] = time_val

    print(f"{'Test Case':<25} | {'Implementation':<25} | {'Time (s)':<15} | {'Speedup':<10}")
    print("-" * 85)

    for case_name, impls in sorted(cases.items()):
        phyid_time = impls.get('phyid')
        cpu_time = next((impls[k] for k in impls if 'cpu' in k), None)
        
        baseline_time = phyid_time if phyid_time is not None else cpu_time
        
        first_line = True
        for impl_name, time_val in sorted(impls.items()):
            speedup_str = "1.00x"
            if baseline_time and baseline_time > 0 and time_val > 0:
                # For non-baseline CPU, compare to phyid if possible
                if 'cpu' in impl_name and phyid_time:
                    speedup = phyid_time / time_val
                    speedup_str = f"{speedup:.2f}x"
                # For GPU, compare to its corresponding CPU time
                elif 'gpu' in impl_name and cpu_time:
                    speedup = cpu_time / time_val
                    speedup_str = f"{speedup:.2f}x"
                # For GPU, if no CPU time, compare to phyid
                elif 'gpu' in impl_name and phyid_time:
                    speedup = phyid_time / time_val
                    speedup_str = f"{speedup:.2f}x"

            display_name = case_name if first_line else ""
            print(f"{display_name:<25} | {impl_name:<25} | {time_val:<15.4f} | {speedup_str:<10}")
            first_line = False
        print("-" * 85)


def get_timeseries_data(n_vars, n_samples, seed=42):
    rng = np.random.default_rng(seed)
    return rng.standard_normal((n_vars, n_samples))

@pytest.mark.parametrize("n_sources, n_targets, n_samples, redundancy", [
    (2, 2, 100000, "MMI"), (2, 2, 100000, "CCS"),
    (4, 2, 100000, "MMI"), (4, 2, 100000, "CCS"),
    (4, 4, 100000, "MMI"),
])
def test_benchmark_cpu(n_sources, n_targets, n_samples, redundancy):
    set_backend('numpy')
    sources = get_timeseries_data(n_sources, n_samples)
    targets = get_timeseries_data(n_targets, n_samples)
    
    key_prefix = f"{n_sources}x{n_targets}"

    start_time = time.time()
    calc_phiid_multivariate(sources, targets, redundancy=redundancy)
    end_time = time.time()
    RESULTS[(key_prefix, redundancy, f'omegaid_{key_prefix}_cpu')] = end_time - start_time

    if n_sources == 2 and n_targets == 2:
        s1, s2 = sources[0], sources[1]
        start_time = time.time()
        calc_PhiID_original(s1, s2, tau=1, redundancy=redundancy)
        end_time = time.time()
        RESULTS[(key_prefix, redundancy, 'phyid')] = end_time - start_time

@pytest.mark.parametrize("n_sources, n_targets, n_samples, redundancy", [
    (2, 2, 100000, "MMI"), (2, 2, 100000, "CCS"),
    (4, 2, 100000, "MMI"), (4, 2, 100000, "CCS"),
    (4, 4, 100000, "MMI"),
])
def test_benchmark_gpu(n_sources, n_targets, n_samples, redundancy):
    if not importlib.util.find_spec("cupy"):
        pytest.skip("cupy not installed")
    
    set_backend('cupy')
    sources = get_timeseries_data(n_sources, n_samples)
    targets = get_timeseries_data(n_targets, n_samples)
    
    key_prefix = f"{n_sources}x{n_targets}"

    start_time = time.time()
    calc_phiid_multivariate(sources, targets, redundancy=redundancy)
    end_time = time.time()
    RESULTS[(key_prefix, redundancy, f'omegaid_{key_prefix}_gpu')] = end_time - start_time
    
    set_backend('numpy')
