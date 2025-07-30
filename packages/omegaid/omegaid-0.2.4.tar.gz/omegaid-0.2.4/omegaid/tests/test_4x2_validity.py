import pytest
import numpy as np
import sys
import os
from itertools import product

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from omegaid.core.decomposition import calc_phiid_multivariate
from omegaid.core.doublet_lattice import build_doublet_matrix
from omegaid.core.entropy import local_entropy_mvn

def calc_entropy(data: np.ndarray) -> float:
    if data.shape[0] == 0:
        return 0.0
    cov = np.cov(data)
    if cov.ndim == 0:
        cov = np.array([[cov]])
    mu = np.mean(data, axis=1)
    entropy_values = local_entropy_mvn(data.T, mu, cov)
    return np.mean(entropy_values)

def mi_from_entropy(sources: np.ndarray, targets: np.ndarray) -> float:
    if sources.shape[0] == 0 or targets.shape[0] == 0:
        return 0.0
    
    data_st = np.vstack([sources, targets])
    h_s = calc_entropy(sources)
    h_t = calc_entropy(targets)
    h_st = calc_entropy(data_st)
    
    return h_s + h_t - h_st

@pytest.mark.parametrize("kind", ["gaussian"])
def test_4x2_decomposition_validity(kind):
    rng = np.random.default_rng(42)
    n_samples = 5000
    n_sources = 4
    n_targets = 2
    tau = 1

    sources = rng.standard_normal((n_sources, n_samples))
    targets = rng.standard_normal((n_targets, n_samples))

    targets[0, :] += 0.5 * sources[0, :] + 0.3 * sources[1, :]
    targets[1, :] += 0.4 * sources[2, :] - 0.2 * sources[3, :]

    atoms_res, _ = calc_phiid_multivariate(
        sources, targets, tau=tau, kind=kind
    )

    sources_past = sources[:, :-tau]
    targets_future = targets[:, tau:]

    matrix, mi_terms, doublet_atoms = build_doublet_matrix(n_sources, n_targets)

    for _i, (source_subset, target_subset) in enumerate(mi_terms):
        
        mi_predicted = 0
        for s_idx, t_idx in product(source_subset, target_subset):
            atom_name = (s_idx, t_idx)
            if atom_name in atoms_res:
                mi_predicted += atoms_res[atom_name]

        source_data = sources_past[list(source_subset), :]
        target_indices_local = [idx - n_sources for idx in target_subset]
        target_data = targets_future[target_indices_local, :]
        mi_ground_truth = mi_from_entropy(source_data, target_data)

        assert np.allclose(mi_predicted, mi_ground_truth, atol=1e-5)