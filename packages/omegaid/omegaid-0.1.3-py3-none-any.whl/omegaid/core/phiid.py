import numpy as np
from omegaid.utils.backend import xp
from omegaid.core.entropy import (
    local_entropy_mvn_batched,
    local_entropy_binary,
)
from omegaid.core.redundancy import (
    redundancy_mmi,
    redundancy_ccs,
)
from omegaid.utils.common import _binarize

def prepare_batched_data(X, X_mu, X_cov, index_combinations, backend):
    max_dim = max(len(ic) for ic in index_combinations)
    n_samples = X.shape[1]
    
    X_batch = backend.zeros((len(index_combinations), n_samples, max_dim))
    mu_batch = backend.zeros((len(index_combinations), max_dim))
    cov_batch = backend.zeros((len(index_combinations), max_dim, max_dim))
    
    for i, ic in enumerate(index_combinations):
        dim = len(ic)
        X_batch[i, :, :dim] = X[ic, :].T
        mu_batch[i, :dim] = X_mu[ic]
        cov_batch[i, :dim, :dim] = X_cov[backend.ix_(ic, ic)]
        
    return X_batch, mu_batch, cov_batch

def _calculate_phiid_core(src, trg, tau, kind, redundancy_measure, backend):
    if kind == "binary":
        src = _binarize(src)
        trg = _binarize(trg)

    n_features = src.shape[1]
    if src.ndim == 1:
        src = src.reshape(-1, 1)
        trg = trg.reshape(-1, 1)
        n_features = 1

    X = np.concatenate(
        [
            src[:-tau].reshape(-1, n_features),
            trg[:-tau].reshape(-1, n_features),
            trg[tau:].reshape(-1, n_features),
        ],
        axis=1,
    )
    X = backend.array(X)
    X_mu = backend.mean(X, axis=0)
    X_cov = backend.cov(X, rowvar=False)

    s1 = list(range(n_features))
    s2 = list(range(n_features, 2 * n_features))
    t = list(range(2 * n_features, 3 * n_features))

    if kind == "gaussian":
        index_combinations = [s1, s2, t, s1 + s2, s1 + t, s2 + t, s1 + s2 + t]
        X_batch, mu_batch, cov_batch = prepare_batched_data(
            X.T, X_mu, X_cov, index_combinations, backend
        )
        entropies = local_entropy_mvn_batched(X_batch, mu_batch, cov_batch, backend)
        h_s1, h_s2, h_t, h_s1s2, h_s1t, h_s2t, h_s1s2t = backend.mean(
            entropies, axis=1
        )
    elif kind == "binary":
        h_s1 = np.mean(local_entropy_binary(X[:, s1]))
        h_s2 = np.mean(local_entropy_binary(X[:, s2]))
        h_t = np.mean(local_entropy_binary(X[:, t]))
        h_s1s2 = np.mean(local_entropy_binary(X[:, s1 + s2]))
        h_s1t = np.mean(local_entropy_binary(X[:, s1 + t]))
        h_s2t = np.mean(local_entropy_binary(X[:, s2 + t]))
        h_s1s2t = np.mean(local_entropy_binary(X[:, s1 + s2 + t]))

    mi_s1_t = h_s1 + h_t - h_s1t
    mi_s2_t = h_s2 + h_t - h_s2t
    mi_s1s2_t = h_s1s2 + h_t - h_s1s2t

    if redundancy_measure == "MMI":
        I_red = redundancy_mmi(mi_s1_t, mi_s2_t, mi_s1s2_t, backend)
    elif redundancy_measure == "CCS":
        I_red = redundancy_ccs(mi_s1_t, mi_s2_t, mi_s1s2_t, backend)

    I_unq_s1 = mi_s1_t - I_red
    I_unq_s2 = mi_s2_t - I_red
    I_syn = mi_s1s2_t - mi_s1_t - mi_s2_t + I_red

    atoms_res = {
        "R": I_red,
        "U_s1": I_unq_s1,
        "U_s2": I_unq_s2,
        "S": I_syn,
    }

    calc_res = {
        "mi_s1_t": mi_s1_t,
        "mi_s2_t": mi_s2_t,
        "mi_s1s2_t": mi_s1s2_t,
    }

    if backend.__name__ == "cupy":
        atoms_res = {k: v.get() for k, v in atoms_res.items()}
        calc_res = {k: v.get() for k, v in calc_res.items()}

    return atoms_res, calc_res

def calc_phiid_mmi(src, trg, tau, kind="gaussian"):
    return _calculate_phiid_core(src, trg, tau, kind, "MMI", np)

def calc_phiid_ccs(src, trg, tau, kind="gaussian"):
    return _calculate_phiid_core(src, trg, tau, kind, "CCS", xp)

