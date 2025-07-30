import pytest
import numpy as np
from scipy.io import loadmat
import urllib.request

from phyid.calculate import calc_PhiID as calc_PhiID_original
from phyid.utils import PhiID_atoms_abbr

try:
    from omegaid.core.decomposition import calc_PhiID as calc_PhiID_new
except ImportError:
    calc_PhiID_new = None

@pytest.fixture(scope="session")
def phiid_test_data(tmp_path_factory):
    fn = tmp_path_factory.mktemp("test-data") / "PhiID_test_simple_1.mat"
    urllib.request.urlretrieve("https://osf.io/download/45u3y/", fn)
    return loadmat(fn)

@pytest.mark.skipif(calc_PhiID_new is None, reason="OmegaID implementation not yet available.")
@pytest.mark.parametrize("kind,redundancy", [
    ("gaussian", "MMI"),
    ("gaussian", "CCS"),
    ("discrete", "MMI"),
    ("discrete", "CCS"),
])
def test_numerical_integrity_from_mat_data(phiid_test_data, kind, redundancy):
    data = phiid_test_data
    src = data["src"].squeeze()
    trg = data["trg"].squeeze()
    tau = int(data["tau"].squeeze())

    atoms_res_original, _ = calc_PhiID_original(
        src, trg, tau, kind=kind, redundancy=redundancy
    )
    result_original = np.array([atoms_res_original[abbr] for abbr in PhiID_atoms_abbr])

    atoms_res_new, _ = calc_PhiID_new(
        src, trg, tau, kind=kind, redundancy=redundancy
    )
    result_new = np.array([atoms_res_new[abbr] for abbr in PhiID_atoms_abbr])

    assert np.allclose(result_original, result_new)

@pytest.mark.skipif(calc_PhiID_new is None, reason="OmegaID implementation not yet available.")
@pytest.mark.parametrize("kind,redundancy", [
    ("gaussian", "MMI"),
    ("gaussian", "CCS"),
])
def test_numerical_integrity_from_random_data(kind, redundancy):
    np.random.seed(0)
    n_samples = 1000
    tau = 1
    src = np.random.randn(n_samples)
    trg = np.random.randn(n_samples)

    atoms_res_original, _ = calc_PhiID_original(
        src, trg, tau, kind=kind, redundancy=redundancy
    )
    result_original = np.array([atoms_res_original[abbr] for abbr in PhiID_atoms_abbr])

    atoms_res_new, _ = calc_PhiID_new(
        src, trg, tau, kind=kind, redundancy=redundancy
    )
    result_new = np.array([atoms_res_new[abbr] for abbr in PhiID_atoms_abbr])

    assert np.allclose(result_original, result_new)
