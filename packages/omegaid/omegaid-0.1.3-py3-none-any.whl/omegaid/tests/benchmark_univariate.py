import time
import numpy as np
import importlib
import sys
import os
import psutil
import gc

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

def run_legacy_benchmark(data, kind, calc_func_name, backend, monkeypatch):
    if backend == "cupy":
        try:
            xp = importlib.import_module("cupy")
        except ImportError:
            return -1, 0, 0
    else:
        xp = np

    import omegaid.utils.backend
    import omegaid.utils.common
    import omegaid.core.entropy
    import omegaid.core.redundancy
    import omegaid.core.phiid

    monkeypatch.setattr(omegaid.utils.backend, "xp", xp)
    monkeypatch.setattr(omegaid.utils.common, "xp", xp)
    monkeypatch.setattr(omegaid.core.entropy, "xp", xp)
    monkeypatch.setattr(omegaid.core.redundancy, "xp", xp)
    monkeypatch.setattr(omegaid.core.phiid, "xp", xp)

    importlib.reload(omegaid.core.phiid)
    calc_func = getattr(omegaid.core.phiid, calc_func_name)

    gc.collect()
    if backend == "cupy":
        xp.get_default_memory_pool().free_all_blocks()

    mem_before = get_memory_usage()
    gpu_mem_before = get_gpu_memory_usage()

    start_time = time.perf_counter()
    calc_func(data["src"], data["trg"], data["tau"], kind=kind)
    end_time = time.perf_counter()

    gc.collect()
    mem_after = get_memory_usage()
    gpu_mem_after = get_gpu_memory_usage()

    mem_increase = mem_after - mem_before
    gpu_mem_increase = gpu_mem_after - gpu_mem_before

    return end_time - start_time, mem_increase, gpu_mem_increase

def main():
    class MonkeyPatch:
        def setattr(self, target, name, value):
            setattr(target, name, value)

    monkeypatch = MonkeyPatch()

    n_samples = 50000
    dimensions = [16, 64, 256, 512, 1024]
    tau = 1
    results = []

    print(f"\n--- Running Legacy Benchmarks (Samples: {n_samples}) ---")
    test_params = [
        ("gaussian", "MMI", "calc_phiid_mmi"),
        ("gaussian", "CCS", "calc_phiid_ccs"),
    ]

    for n_dims in dimensions:
        print(f"\n--- Feature Dimensions: {n_dims}, DataType: float32 ---")
        rng = np.random.default_rng(0)
        src_cpu = rng.standard_normal((n_samples, n_dims), dtype=np.float32)
        trg_cpu = rng.standard_normal((n_samples, n_dims), dtype=np.float32)
        
        # Legacy functions expect 1D input for single variables
        data_cpu = {"src": src_cpu[:, 0], "trg": trg_cpu[:, 0], "tau": tau}
        
        try:
            cp = importlib.import_module("cupy")
            src_gpu = cp.asarray(src_cpu[:, 0])
            trg_gpu = cp.asarray(trg_cpu[:, 0])
            data_gpu = {"src": src_gpu, "trg": trg_gpu, "tau": tau}
        except ImportError:
            data_gpu = None

        for kind, _redundancy, calc_func_name in test_params:
            print(f"  {calc_func_name}:")
            
            numpy_time, _, _ = run_legacy_benchmark(data_cpu, kind, calc_func_name, "numpy", monkeypatch)
            print(f"    [omegaid-numpy] Time: {numpy_time:.6f}s")

            cupy_time = -1
            if calc_func_name == "calc_phiid_ccs" and data_gpu:
                cupy_time, _, _ = run_legacy_benchmark(data_gpu, kind, calc_func_name, "cupy", monkeypatch)
                print(f"    [omegaid-cupy] Time: {cupy_time:.6f}s")
            
            results.append({
                "dimensions": n_dims,
                "func_name": calc_func_name,
                "numpy_time": numpy_time,
                "cupy_time": cupy_time,
            })

    print("\n--- Legacy Benchmark Results Summary ---")
    print("| Dims | Function         | NumPy Time (s) | CuPy Time (s) | Perf Ratio |")
    print("| :--- | :--------------- | :------------- | :------------ | :--------- |")
    for res in results:
        perf_ratio = "N/A"
        if res["cupy_time"] > 0:
            perf_ratio = f"{res['numpy_time'] / res['cupy_time']:.2f}x"
        
        print(
            f"| {res['dimensions']:<4} | {res['func_name']:<16} | "
            f"{res['numpy_time']:.4f}         | "
            f"{res['cupy_time'] if res['cupy_time'] > 0 else 'N/A':<13} | "
            f"{perf_ratio:<10} |"
        )

    print("\n--- Benchmarks Complete ---")

if __name__ == "__main__":
    main()
    if NVML_AVAILABLE:
        pynvml.nvmlShutdown()
