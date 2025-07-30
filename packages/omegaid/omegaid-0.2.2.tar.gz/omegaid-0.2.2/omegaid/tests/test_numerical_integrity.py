import pytest
import numpy as np
from scipy.io import loadmat
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from phyid.calculate import calc_PhiID as calc_PhiID_original
from phyid.utils import PhiID_atoms_abbr
from omegaid.core.decomposition import calc_phiid_multivariate as calc_PhiID_new

@pytest.fixture(scope="session")
def phiid_test_data():
    # Load data from the local file provided by the user
    file_path = os.path.join(os.path.dirname(__file__), '../../temp_data/PhiID-test-simple-1.mat')
    return loadmat(file_path)

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
    result_original = np.array([np.mean(atoms_res_original[abbr]) for abbr in PhiID_atoms_abbr])

    src_m = np.stack([src, src])
    trg_m = np.stack([trg, trg])
    atoms_res_new, _ = calc_PhiID_new(
        src_m, trg_m, tau, kind=kind, redundancy=redundancy
    )
    result_new = np.array([np.mean(atoms_res_new[abbr]) for abbr in PhiID_atoms_abbr])

    assert np.allclose(result_original, result_new, atol=1e-5)

@pytest.mark.parametrize("kind,redundancy", [
    ("gaussian", "MMI"),
    ("gaussian", "CCS"),
])
def test_numerical_integrity_from_random_data(kind, redundancy):
    rng = np.random.default_rng(0)
    n_samples = 1000
    tau = 1
    src = rng.standard_normal(n_samples)
    trg = rng.standard_normal(n_samples)

    atoms_res_original, _ = calc_PhiID_original(
        src, trg, tau, kind=kind, redundancy=redundancy
    )
    result_original = np.array([np.mean(atoms_res_original[abbr]) for abbr in PhiID_atoms_abbr])

    src_m = np.stack([src, src])
    trg_m = np.stack([trg, trg])
    atoms_res_new, _ = calc_PhiID_new(
        src_m, trg_m, tau, kind=kind, redundancy=redundancy
    )
    result_new = np.array([np.mean(atoms_res_new[abbr]) for abbr in PhiID_atoms_abbr])

    assert np.allclose(result_original, result_new, atol=1e-5)
