from omegaid.utils.backend import xp
from itertools import product
from collections import Counter
import scipy.stats as sstats

def _multivariate_normal_pdf_svd(x, mu, cov, backend):
    n_dims = x.shape[1]
    x_minus_mu = x - mu
    
    u, s, vh = backend.linalg.svd(cov)
    
    tol = s.max() * n_dims * backend.finfo(s.dtype).eps
    rank = backend.sum(s > tol)
    
    if rank == n_dims:
        det_cov = backend.linalg.det(cov)
        inv_cov = backend.linalg.inv(cov)
        norm_fact = (2 * backend.pi) ** (-n_dims / 2)
        det_fact = det_cov ** (-0.5)
        exponent = -0.5 * backend.sum((x_minus_mu @ inv_cov) * x_minus_mu, axis=1)
        pdf = norm_fact * det_fact * backend.exp(exponent)
        return pdf

    s_inv = backend.where(s > tol, 1. / s, 0)
    pseudo_inv_cov = vh.T @ backend.diag(s_inv) @ u.T
    
    pseudo_det_cov = backend.prod(s[s > tol])
    
    norm_fact = (2 * backend.pi) ** (-rank / 2)
    det_fact = pseudo_det_cov ** (-0.5)
    
    exponent = -0.5 * backend.sum((x_minus_mu @ pseudo_inv_cov) * x_minus_mu, axis=1)
    
    pdf = norm_fact * det_fact * backend.exp(exponent)
    return pdf

def local_entropy_mvn(x, mu, cov, backend):
    if backend.__name__ == 'cupy':
        pdf = _multivariate_normal_pdf_svd(x, mu, cov, backend)
    else:
        pdf = sstats.multivariate_normal.pdf(x, mu, cov, allow_singular=True)
        
    pdf = backend.where(pdf > 0, pdf, 1e-300)
    return -backend.log(pdf)

def local_entropy_binary(x):
    if x.ndim == 1:
        x = x[None, :]
    n_dim, n_samp = x.shape
    combs = list(product([0, 1], repeat=n_dim))
    
    if hasattr(x, 'get'):
        distri = list(zip(*x.get().tolist()))
    else:
        distri = list(zip(*x.tolist()))
        
    c = Counter(distri)
    p = xp.array([c.get(comb, 0) for comb in combs]) / n_samp
    
    p_cpu = p.get() if hasattr(p, 'get') else p
    entropy_dict = {comb: -xp.log2(p_) for comb, p_ in zip(combs, p_cpu) if p_ > 0}
    
    return xp.array([entropy_dict.get(comb, 0) for comb in distri])


def _multivariate_normal_pdf_svd_batched(x, mu, cov, backend):
    n_batch, n_samples, n_dims = x.shape
    x_minus_mu = x - mu[:, None, :]

    if backend.__name__ == 'numpy':
        with backend.errstate(divide='ignore', invalid='ignore'):
            u, s, vh = backend.linalg.svd(cov)
            tol = s.max(axis=1, keepdims=True) * n_dims * backend.finfo(s.dtype).eps
            rank = backend.sum(s > tol, axis=1)
            s_inv = backend.where(s > tol, 1.0 / s, 0)
    else:
        u, s, vh = backend.linalg.svd(cov)
        tol = s.max(axis=1, keepdims=True) * n_dims * backend.finfo(s.dtype).eps
        rank = backend.sum(s > tol, axis=1)
        s_inv = backend.where(s > tol, 1.0 / s, 0)

    s_inv_diag = backend.zeros_like(cov)
    s_inv_diag[:, backend.arange(n_dims), backend.arange(n_dims)] = s_inv
    pseudo_inv_cov = backend.matmul(
        vh.transpose(0, 2, 1), backend.matmul(s_inv_diag, u.transpose(0, 2, 1))
    )
    s_masked = backend.where(s > tol, s, 1)
    pseudo_det_cov = backend.prod(s_masked, axis=1)
    rank_r = rank[:, None]
    pseudo_det_cov_r = pseudo_det_cov[:, None]
    norm_fact = (2 * backend.pi) ** (-rank_r / 2)
    det_fact = pseudo_det_cov_r ** (-0.5)
    tmp = backend.einsum("bsd,bde->bse", x_minus_mu, pseudo_inv_cov)
    exponent = -0.5 * backend.einsum("bsd,bsd->bs", tmp, x_minus_mu)
    pdf = norm_fact * det_fact * backend.exp(exponent)
    return pdf


def local_entropy_mvn_batched(x_batch, mu_batch, cov_batch, backend):
    pdf = _multivariate_normal_pdf_svd_batched(x_batch, mu_batch, cov_batch, backend)
    pdf = backend.where(pdf > 0, pdf, 1e-300)
    return -backend.log(pdf)
