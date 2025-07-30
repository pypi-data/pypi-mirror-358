import time
import numpy as np

def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        return result, elapsed_time
    return wrapper

try:
    import cupy as cp
    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False

from phyid.calculate import calc_PhiID as calc_PhiID_original

try:
    from omegaid.utils.backend import set_backend
    from omegaid.core.decomposition import calc_PhiID as calc_PhiID_new
    OMEGAID_AVAILABLE = True
except ImportError:
    OMEGAID_AVAILABLE = False

@timer
def run_phyid_original(src, trg, tau):
    return calc_PhiID_original(src, trg, tau, kind="gaussian", redundancy="MMI")

@timer
def run_omegaid_new(src, trg, tau):
    return calc_PhiID_new(src, trg, tau, kind="gaussian", redundancy="MMI")

def run_benchmarks():
    data_sizes = [10000, 100000, 500000]
    tau = 1
    results = {}

    rng = np.random.default_rng(0)
    for n_samples in data_sizes:
        print(f"\n--- Benchmarking for {n_samples} samples ---")
        src_np = rng.standard_normal(n_samples)
        trg_np = rng.standard_normal(n_samples)
        
        results[n_samples] = {}

        _, elapsed_original = run_phyid_original(src_np, trg_np, tau)
        results[n_samples]["Original (scipy)"] = elapsed_original
        print(f"Original (scipy): {elapsed_original:.4f}s")

        if OMEGAID_AVAILABLE:
            set_backend("numpy")
            _, elapsed_omegaid_np = run_omegaid_new(src_np, trg_np, tau)
            results[n_samples]["OmegaID (numpy)"] = elapsed_omegaid_np
            print(f"OmegaID (numpy): {elapsed_omegaid_np:.4f}s")

            if CUPY_AVAILABLE:
                set_backend("cupy")
                src_cp = cp.asarray(src_np)
                trg_cp = cp.asarray(trg_np)
                _, elapsed_omegaid_cp = run_omegaid_new(src_cp, trg_cp, tau)
                results[n_samples]["OmegaID (cupy)"] = elapsed_omegaid_cp
                print(f"OmegaID (cupy): {elapsed_omegaid_cp:.4f}s")
        else:
            print("OmegaID implementation not available. Skipping benchmarks.")

    print_summary_table(results)

def print_summary_table(results):
    print("\n--- Performance Summary ---")
    
    headers = [
        "Data Size", "Original (scipy)", "OmegaID (numpy)", 
        "OmegaID (cupy)", "NumPy Speedup", "CuPy Speedup"
    ]
    
    print(
        f"{headers[0]:<12} | {headers[1]:<18} | {headers[2]:<18} | "
        f"{headers[3]:<18} | {headers[4]:<15} | {headers[5]:<15}"
    )
    print("-" * 110)

    for size, times in results.items():
        original_time = times.get("Original (scipy)", np.nan)
        numpy_time = times.get("OmegaID (numpy)", np.nan)
        cupy_time = times.get("OmegaID (cupy)", np.nan)

        numpy_speedup = f"{(original_time / numpy_time):.2f}x" if not np.isnan(numpy_time) else "N/A"
        cupy_speedup = f"{(original_time / cupy_time):.2f}x" if not np.isnan(cupy_time) else "N/A"
        
        original_time_str = f"{original_time:.4f}s" if not np.isnan(original_time) else "N/A"
        numpy_time_str = f"{numpy_time:.4f}s" if not np.isnan(numpy_time) else "N/A"
        cupy_time_str = f"{cupy_time:.4f}s" if not np.isnan(cupy_time) else "N/A"

        print(
            f"{size:<12} | {original_time_str:<18} | {numpy_time_str:<18} | "
            f"{cupy_time_str:<18} | {numpy_speedup:<15} | {cupy_speedup:<15}"
        )

if __name__ == "__main__":
    run_benchmarks()
