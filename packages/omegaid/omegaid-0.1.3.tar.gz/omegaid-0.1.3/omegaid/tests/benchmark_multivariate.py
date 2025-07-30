import time
import numpy as np
import importlib
import sys
import os
import psutil
import gc
import itertools

try:
    import pynvml
    pynvml.nvmlInit()
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def get_gpu_memory_usage():
    if not NVML_AVAILABLE:
        return 0
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    return info.used / (1024 * 1024)

def run_multivariate_benchmark(data, n_vars, kind, calc_func_name, backend, monkeypatch):
    if backend == "cupy":
        try:
            xp = importlib.import_module("cupy")
        except ImportError:
            return -1, 0, 0, None
    else:
        xp = np

    import omegaid.utils.backend
    import omegaid.core.entropy
    import omegaid.core.multivariate.phiid
    import omegaid.core.multivariate.lattice

    monkeypatch.setattr(omegaid.utils.backend, "xp", xp)
    monkeypatch.setattr(omegaid.core.entropy, "xp", xp)
    monkeypatch.setattr(omegaid.core.multivariate.phiid, "xp", xp)
    
    importlib.reload(omegaid.core.multivariate.phiid)
    calc_func = getattr(omegaid.core.multivariate.phiid, calc_func_name)

    gc.collect()
    if backend == "cupy":
        xp.get_default_memory_pool().free_all_blocks()

    mem_before = get_memory_usage()
    gpu_mem_before = get_gpu_memory_usage()

    start_time = time.perf_counter()
    _, info = calc_func(
        data["src"], data["trg"], data["tau"], 
        n_vars_src=n_vars, n_vars_trg=n_vars, 
        kind=kind
    )
    end_time = time.perf_counter()

    timing_info = info.get("timing_info", {})

    gc.collect()
    mem_after = get_memory_usage()
    gpu_mem_after = get_gpu_memory_usage()

    mem_increase = mem_after - mem_before
    gpu_mem_increase = gpu_mem_after - gpu_mem_before

    return end_time - start_time, mem_increase, gpu_mem_increase, timing_info

def main():
    class MonkeyPatch:
        def setattr(self, target, name, value):
            setattr(target, name, value)

    monkeypatch = MonkeyPatch()

    n_samples = 1000
    tau = 1
    
    variable_dims = [2, 3]
    feature_dims = [1, 16, 32]
    
    results = []

    print(f"\n--- Running Multivariate Benchmarks (Samples: {n_samples}) ---")
    test_params = [
        ("gaussian", "CCS", "calc_phiid_multivariate_ccs"),
    ]

    param_combinations = []
    for var_dim, feat_dim in itertools.product(variable_dims, feature_dims):
        if var_dim >= 3 and feat_dim > 1:
            continue
        param_combinations.append((var_dim, feat_dim))
    
    # Add the challenge case
    if NVML_AVAILABLE:
        param_combinations.append((3, 16))


    for m_dim, f_dim in param_combinations:
        print(f"\n--- System: {m_dim}x{m_dim}x{f_dim}, DataType: float32 ---")
        
        rng = np.random.default_rng(0)
        src_cpu = rng.standard_normal((n_samples, m_dim * f_dim), dtype=np.float32)
        trg_cpu = rng.standard_normal((n_samples, m_dim * f_dim), dtype=np.float32)
        data_cpu = {"src": src_cpu, "trg": trg_cpu, "tau": tau}
        
        try:
            cp = importlib.import_module("cupy")
            src_gpu = cp.asarray(src_cpu)
            trg_gpu = cp.asarray(trg_cpu)
            data_gpu = {"src": src_gpu, "trg": trg_gpu, "tau": tau}
        except ImportError:
            data_gpu = None

        for kind, _redundancy, calc_func_name in test_params:
            print(f"  {calc_func_name}:")

            numpy_time, cupy_time = -1, -1
            numpy_timing, cupy_timing = None, None

            # For the challenge case, only run cupy
            if m_dim == 3 and f_dim == 16:
                if "ccs" in calc_func_name and data_gpu:
                    cupy_time, _, _, cupy_timing = run_multivariate_benchmark(data_gpu, m_dim, kind, calc_func_name, "cupy", monkeypatch)
                    print(f"    [omegaid-cupy] Time: {cupy_time:.6f}s")
            else:
                numpy_time, _, _, numpy_timing = run_multivariate_benchmark(data_cpu, m_dim, kind, calc_func_name, "numpy", monkeypatch)
                print(f"    [omegaid-numpy] Time: {numpy_time:.6f}s")
                if "ccs" in calc_func_name and data_gpu:
                    cupy_time, _, _, cupy_timing = run_multivariate_benchmark(data_gpu, m_dim, kind, calc_func_name, "cupy", monkeypatch)
                    print(f"    [omegaid-cupy] Time: {cupy_time:.6f}s")
            
            results.append({
                "var_dims": m_dim,
                "feat_dims": f_dim,
                "func_name": calc_func_name,
                "numpy_time": numpy_time,
                "cupy_time": cupy_time,
                "numpy_timing": numpy_timing,
                "cupy_timing": cupy_timing,
            })

    print("\n--- Multivariate Benchmark Results Summary ---")
    print("| System (NxMxFeat) | Backend | Total Time (s) | Data Prep (s) | Lattice Gen (s) | Entropy (s) | MI (s)    | Mobius (s) | Perf Ratio |")
    print("| :------ | :-- | :--- | :-- | :---- | :------ | :---- | :----- | :----- |")
    
    last_numpy_time = -1
    for res in results:
        system_str = f"{res['var_dims']}x{res['var_dims']}x{res['feat_dims']}"
        
        numpy_total_time = res["numpy_time"]
        numpy_timing_info = res["numpy_timing"]
        if numpy_total_time > 0 and numpy_timing_info:
            last_numpy_time = numpy_total_time
            data_prep = numpy_timing_info.get("data_prep", 0)
            lattice_gen = numpy_timing_info.get("lattice_generation", 0)
            entropy_calc = numpy_timing_info.get("entropy_calculation", 0)
            mi_calc = numpy_timing_info.get("mi_calculation", 0)
            mobius_inv = numpy_timing_info.get("mobius_inversion", 0)
            print(
                f"| {system_str:<17} | numpy   | "
                f"{numpy_total_time:<14.4f} | "
                f"{data_prep:<13.4f} | "
                f"{lattice_gen:<15.4f} | "
                f"{entropy_calc:<11.4f} | "
                f"{mi_calc:<9.4f} | "
                f"{mobius_inv:<10.4f} | N/A        |"
            )

        cupy_total_time = res["cupy_time"]
        cupy_timing_info = res["cupy_timing"]
        if cupy_total_time > 0 and cupy_timing_info:
            perf_ratio = f"{last_numpy_time / cupy_total_time:.2f}x" if last_numpy_time > 0 else "N/A"
            data_prep = cupy_timing_info.get("data_prep", 0)
            lattice_gen = cupy_timing_info.get("lattice_generation", 0)
            entropy_calc = cupy_timing_info.get("entropy_calculation", 0)
            mi_calc = cupy_timing_info.get("mi_calculation", 0)
            mobius_inv = cupy_timing_info.get("mobius_inversion", 0)
            print(
                f"| {system_str:<17} | cupy    | "
                f"{cupy_total_time:<14.4f} | "
                f"{data_prep:<13.4f} | "
                f"{lattice_gen:<15.4f} | "
                f"{entropy_calc:<11.4f} | "
                f"{mi_calc:<9.4f} | "
                f"{mobius_inv:<10.4f} | {perf_ratio:<10} |"
            )

    print("\n--- Benchmarks Complete ---")

if __name__ == "__main__":
    main()
    if NVML_AVAILABLE:
        pynvml.nvmlShutdown()
