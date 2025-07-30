import pytest
import numpy as np
import sys
import os
from scipy.io import loadmat

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from omegaid.core.decomposition import calc_phiid_multivariate
from phyid.calculate import calc_PhiID as calc_PhiID_original
from phyid.utils import PhiID_atoms_abbr

@pytest.fixture(scope="session")
def phiid_test_data():
    file_path = os.path.join(os.path.dirname(__file__), '../../temp_data/PhiID-test-simple-1.mat')
    return loadmat(file_path)

def _get_mean_atoms(atoms_res):
    return {abbr: np.mean(atoms_res[abbr]) for abbr in PhiID_atoms_abbr}

@pytest.mark.parametrize("kind,redundancy", [
    ("gaussian", "MMI"),
    ("gaussian", "CCS"),
    ("discrete", "MMI"),
    ("discrete", "CCS"),
])
def test_2x2_equivalence_from_mat_data(phiid_test_data, kind, redundancy):
    data = phiid_test_data
    src = data["src"].squeeze()
    trg = data["trg"].squeeze()
    tau = int(data["tau"].squeeze())

    src_data = np.stack([src, trg])
    trg_data = np.stack([src, trg])

    atoms_res_new, _ = calc_phiid_multivariate(
        src_data, trg_data, tau=tau, kind=kind, redundancy=redundancy
    )
    results_new = _get_mean_atoms(atoms_res_new)

    atoms_res_orig, _ = calc_PhiID_original(
        src, trg, tau, kind=kind, redundancy=redundancy
    )
    results_orig = _get_mean_atoms(atoms_res_orig)

    for atom in PhiID_atoms_abbr:
        assert np.allclose(results_new[atom], results_orig[atom], atol=1e-5)

@pytest.mark.parametrize("kind,redundancy", [
    ("gaussian", "MMI"),
    ("gaussian", "CCS"),
])
def test_2x2_equivalence_from_random_data(kind, redundancy):
    rng = np.random.default_rng(42)
    n_samples = 2000
    tau = 1

    s1 = rng.standard_normal(n_samples)
    s2 = rng.standard_normal(n_samples)

    src_data = np.stack([s1, s2])
    trg_data = np.stack([s1, s2])

    atoms_res_new, _ = calc_phiid_multivariate(
        src_data, trg_data, tau=tau, kind=kind, redundancy=redundancy
    )
    results_new = _get_mean_atoms(atoms_res_new)

    atoms_res_orig, _ = calc_PhiID_original(
        s1, s2, tau, kind=kind, redundancy=redundancy
    )
    results_orig = _get_mean_atoms(atoms_res_orig)

    for atom in PhiID_atoms_abbr:
        assert np.allclose(results_new[atom], results_orig[atom], atol=1e-5)