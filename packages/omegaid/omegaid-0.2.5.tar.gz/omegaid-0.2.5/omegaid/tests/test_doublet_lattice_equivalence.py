import numpy as np
from omegaid.core.decomposition import calc_phiid_multivariate

def get_timeseries_data(n_samples=100, seed=42):
    rng = np.random.default_rng(seed)
    s1 = rng.standard_normal(n_samples)
    s2 = rng.standard_normal(n_samples)
    return s1, s2

def test_2x2_vs_doublet_equivalence():
    s1, s2 = get_timeseries_data()
    src_data = np.stack([s1, s2])
    
    atoms_2x2, _ = calc_phiid_multivariate(src_data, src_data, redundancy="MMI")
    atoms_doublet, _ = calc_phiid_multivariate(src_data, src_data, redundancy="MMI")

    for atom in atoms_2x2:
        assert np.allclose(atoms_2x2[atom], atoms_doublet[atom], atol=1e-5)
