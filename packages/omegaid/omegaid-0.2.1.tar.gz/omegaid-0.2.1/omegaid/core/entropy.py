from omegaid.utils.backend import get_backend
from itertools import product
from collections import Counter

def local_entropy_mvn(x, mu, cov):
    xp = get_backend()
    n_samples, n_dims = x.shape

    sign, log_det_cov = xp.linalg.slogdet(cov)
    
    if sign <= 0:
        u, s, vh = xp.linalg.svd(cov)
        log_det_cov = xp.sum(xp.log(s + 1e-30))
        cov_inv = vh.T @ xp.diag(1 / (s + 1e-30)) @ vh
    else:
        cov_inv = xp.linalg.inv(cov)

    delta = x - mu
    mahalanobis_sq = xp.sum((delta @ cov_inv) * delta, axis=1)
    
    log_pdf = -0.5 * (n_dims * xp.log(2 * xp.pi) + log_det_cov + mahalanobis_sq)
    
    return -log_pdf

def local_entropy_binary(x):
    xp = get_backend()
    if x.ndim == 1:
        x = x[None, :]
    
    n_dim, n_samp = x.shape
    
    # Convert xp array to numpy array for Counter and product, then back to xp
    # This is a temporary workaround if xp.unique is not behaving identically for discrete data
    # The long-term solution would be to implement a fully xp-compatible discrete entropy calculation
    x_np = x.get() if xp.__name__ == 'cupy' else x
    
    combs = list(product([0, 1], repeat=n_dim))
    distri = list(zip(*x_np.tolist()))
    c = Counter(distri)
    p = xp.array([c.get(comb, 0) for comb in combs]) / n_samp
    
    # Add a small epsilon to avoid log2(0)
    entropy_values = -xp.log2(p + 1e-30)
    
    # Map back to original samples
    entropy_dict = {comb: entropy_values[i] for i, comb in enumerate(combs)}
    h = xp.array([entropy_dict[comb] for comb in distri])
    
    return h
