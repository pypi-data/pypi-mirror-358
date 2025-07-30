from omegaid.utils.backend import get_backend
from itertools import product
from collections import Counter

def local_entropy_mvn(x, mu, cov):
    xp = get_backend()
    n_samples, n_dims = x.shape

    try:
        sign, log_det_cov = xp.linalg.slogdet(cov)
        if sign <= 0:
            raise xp.linalg.LinAlgError("Covariance matrix is not positive definite.")
        cov_inv = xp.linalg.inv(cov)
    except xp.linalg.LinAlgError:
        u, s, vh = xp.linalg.svd(cov)
        # Add a small epsilon to prevent log(0) and division by zero
        s_reg = s + 1e-6
        log_det_cov = xp.sum(xp.log(s_reg))
        cov_inv = vh.T @ xp.diag(1 / s_reg) @ vh

    delta = x - mu
    mahalanobis_sq = xp.sum((delta @ cov_inv) * delta, axis=1)
    
    log_pdf = -0.5 * (n_dims * xp.log(2 * xp.pi) + log_det_cov + mahalanobis_sq)
    
    return -log_pdf

def local_entropy_binary(x):
    xp = get_backend()
    if x.ndim == 1:
        x = x[None, :]
    
    n_dim, n_samp = x.shape
    
    x_np = x.get() if xp.__name__ == 'cupy' else x
    
    combs = list(product([0, 1], repeat=n_dim))
    distri = list(zip(*x_np.tolist()))
    c = Counter(distri)
    p = xp.array([c.get(comb, 0) for comb in combs]) / n_samp
    
    # Use natural log to be consistent with mvn, then convert to base 2 if needed
    # H_2(X) = H_e(X) / ln(2)
    entropy_values = -xp.log(p + 1e-30) / xp.log(2)
    
    entropy_dict = {comb: entropy_values[i] for i, comb in enumerate(combs)}
    h = xp.array([entropy_dict[comb] for comb in distri])
    
    return h
