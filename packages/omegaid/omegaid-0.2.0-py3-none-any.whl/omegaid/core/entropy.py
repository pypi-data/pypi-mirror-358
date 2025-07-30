from omegaid.utils.backend import get_backend

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
    
    powers_of_2 = 2 ** xp.arange(n_dim, dtype=x.dtype)
    int_repr = x.T.dot(powers_of_2)
    
    unique_ints, inverse_indices, counts = xp.unique(
        int_repr, return_inverse=True, return_counts=True
    )
    
    probs = counts / n_samp
    
    entropy_values = -xp.log2(probs + 1e-30)
    
    h = entropy_values[inverse_indices]
    
    return h
