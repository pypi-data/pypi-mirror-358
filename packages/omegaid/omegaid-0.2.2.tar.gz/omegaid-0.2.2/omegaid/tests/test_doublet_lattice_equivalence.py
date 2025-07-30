import pytest
import numpy as np

from phyid.calculate import calc_PhiID as phyid_calc_phi_id
from omegaid.core.decomposition import calc_phiid_multivariate
from omegaid.utils.backend import set_backend, get_backend
from omegaid.core.atoms import PhiID_atoms_abbr

def get_timeseries_data(n_samples=100, seed=42):
    np.random.seed(seed)
    s1 = np.random.randn(n_samples)
    s2 = np.random.randn(n_samples)
    return s1, s2

@pytest.fixture
def timeseries_data():
    return get_timeseries_data()

def test_2x2_equivalence(timeseries_data):
    set_backend("numpy")
    xp = get_backend()
    s1, s2 = timeseries_data
    tau = 1

    phyid_results_dict, _ = phyid_calc_phi_id(s1, s2, tau=tau)
    phyid_results = np.array([np.mean(phyid_results_dict[atom]) for atom in PhiID_atoms_abbr])

    src_data = xp.array([s1, s2])
    trg_data = xp.array([s1, s2])
    
    omegaid_results_dict, _ = calc_phiid_multivariate(src_data, trg_data, tau=tau)
    omegaid_results = np.array([np.mean(omegaid_results_dict[atom]) for atom in PhiID_atoms_abbr])

    np.testing.assert_allclose(phyid_results, omegaid_results, atol=1e-9)

def test_2x2_equivalence_gpu():
    try:
        set_backend("cupy")
        xp = get_backend()
    except (ImportError, RuntimeError):
        pytest.skip("Cupy not available or no GPU found")

    s1_np, s2_np = get_timeseries_data()
    tau = 1

    src_data_np = np.array([s1_np, s2_np])
    trg_data_np = np.array([s1_np, s2_np])
    
    src_data_cp = xp.asarray(src_data_np)
    trg_data_cp = xp.asarray(trg_data_np)

    omegaid_results_cpu, _ = calc_phiid_multivariate(src_data_np, trg_data_np, tau=tau)
    omegaid_results_gpu, _ = calc_phiid_multivariate(src_data_cp, trg_data_cp, tau=tau)

    cpu_vals = np.array([np.mean(v) for v in omegaid_results_cpu.values()])
    gpu_vals = np.array([np.mean(v) for v in omegaid_results_gpu.values()])

    np.testing.assert_allclose(cpu_vals, gpu_vals, atol=1e-7)
