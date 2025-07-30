import time
import pytest
import urllib.request
import numpy as np
import importlib

@pytest.fixture(scope="session")
def PhiID_test_simple_1(tmp_path_factory):
    """Load test data."""
    fn = tmp_path_factory.mktemp("test-data") / "PhiID_test_simple_1.mat"
    urllib.request.urlretrieve("https://osf.io/download/45u3y/", fn)
    from scipy.io import loadmat
    return loadmat(fn)

calc_phiid_test_params = [
    ("gaussian", "MMI", "PhiIDFull_MMI", "calc_phiid_mmi"),
    ("gaussian", "CCS", "PhiIDFull_CCS", "calc_phiid_ccs"),
]

def _run_phiid_with_backend(backend_name, data, kind, calc_func_name, monkeypatch):
    if backend_name == 'cupy':
        xp = pytest.importorskip('cupy')
    else:
        xp = np

    import omegaid.utils.backend
    import omegaid.utils.common
    import omegaid.core.entropy
    import omegaid.core.redundancy
    import omegaid.core.phiid
    
    monkeypatch.setattr(omegaid.utils.backend, 'xp', xp)
    monkeypatch.setattr(omegaid.utils.common, 'xp', xp)
    monkeypatch.setattr(omegaid.core.entropy, 'xp', xp)
    monkeypatch.setattr(omegaid.core.phiid, 'xp', xp)
    
    importlib.reload(omegaid.core.phiid)
    calc_func = getattr(omegaid.core.phiid, calc_func_name)

    start_time = time.perf_counter()
    atoms_res, _ = calc_func(
        data["src"].squeeze(),
        data["trg"].squeeze(),
        int(data["tau"].squeeze()),
        kind=kind,
    )
    end_time = time.perf_counter()
    print(f"\n[omegaid-{backend_name}] {calc_func_name}-{kind}: {end_time - start_time:.6f} seconds")
    
    return atoms_res

@pytest.mark.parametrize("kind,redundancy,type,calc_func_name", calc_phiid_test_params)
def test_calc_phiid_sample_1(PhiID_test_simple_1, kind, redundancy, type, calc_func_name, monkeypatch):
    data = PhiID_test_simple_1
    from omegaid.utils.common import PhiID_atoms_abbr

    atoms_res_numpy = _run_phiid_with_backend("numpy", data, kind, calc_func_name, monkeypatch)
    
    calc_L_list_numpy = [atoms_res_numpy[key] for key in PhiID_atoms_abbr]
    calc_L_numpy = np.array(calc_L_list_numpy)
    calc_A_numpy = np.mean(calc_L_numpy, axis=1)

    assert np.allclose(data[f"{type}_L"], calc_L_numpy, atol=1e-6)
    assert np.allclose(data[f"{type}_A"].squeeze(), calc_A_numpy, atol=1e-6)
    print(f"✅ [omegaid-numpy] passed ground truth comparison for {calc_func_name}-{kind}.")

    try:
        importlib.import_module('cupy')
        atoms_res_cupy = _run_phiid_with_backend("cupy", data, kind, calc_func_name, monkeypatch)
        
        for key in PhiID_atoms_abbr:
            val_numpy = atoms_res_numpy[key]
            val_cupy_raw = atoms_res_cupy[key]
            # Transfer from GPU to CPU only if it's a cupy array
            val_cupy = val_cupy_raw.get() if hasattr(val_cupy_raw, 'get') else val_cupy_raw
            assert np.allclose(val_numpy, val_cupy, atol=1e-5), f"Mismatch in atom {key}"
        
        print(f"✅ [omegaid-cupy] passed consistency check against numpy for {calc_func_name}-{kind}.")

    except ImportError:
        pytest.skip("cupy not installed, skipping GPU consistency check.")

def test_multivariate_vs_legacy_equivalence(monkeypatch):
    """
    Tests that the generalized implementation produces the same total mutual information
    as the legacy implementation for a 2-source, 2-target system.
    """
    import omegaid.core.phiid as phiid
    importlib.reload(phiid)

    n_samples = 2000
    tau = 1
    
    rng = np.random.default_rng(0)
    src = rng.standard_normal(n_samples)
    trg = rng.standard_normal(n_samples)

    # 1. Calculate with legacy function
    _, info_legacy = phiid.calc_phiid_mmi(src, trg, tau=tau, kind="gaussian")
    total_mi_legacy = np.mean(info_legacy["I_res"]["I_xytab"])

    # 2. Prepare data for multivariate function
    n_s = n_samples - tau
    sources = np.c_[src[:n_s], trg[:n_s]]
    targets = np.c_[src[tau:], trg[tau:]]

    # 3. Calculate with multivariate function
    # Note: tau=0 because the time lag is already handled in data preparation
    atoms_multi, info_multi = phiid.calc_phiid_multivariate_mmi(sources, targets, tau=0, kind="gaussian")
    
    # The top node of the 2x2 lattice represents the total mutual information
    top_node = (tuple(range(sources.shape[1])), tuple(range(targets.shape[1])))
    total_mi_multivariate = info_multi["mi_values"][top_node]

    print(f"\nLegacy Total MI: {total_mi_legacy}")
    print(f"Multivariate Total MI: {total_mi_multivariate}")
    assert np.allclose(total_mi_legacy, total_mi_multivariate, atol=1e-6)
    print("✅ Equivalence test passed.")
