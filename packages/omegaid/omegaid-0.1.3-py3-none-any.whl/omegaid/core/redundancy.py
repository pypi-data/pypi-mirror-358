import numpy as np

def redundancy_mmi(mi_1, mi_2, mi_12, backend):
    mi_1_cpu = mi_1.get() if hasattr(mi_1, 'get') else mi_1
    mi_2_cpu = mi_2.get() if hasattr(mi_2, 'get') else mi_2
    
    if backend.__name__ == 'cupy':
        return backend.array(np.minimum(mi_1_cpu, mi_2_cpu))
    else:
        return backend.minimum(mi_1, mi_2)

def redundancy_ccs(mi_1, mi_2, mi_12, backend):
    c = mi_12 - mi_1 - mi_2
    signs = backend.stack([backend.sign(mi_1), backend.sign(mi_2), backend.sign(mi_12), backend.sign(-c)], axis=0).T
    all_same = backend.all(signs == signs[:, 0][:, None], axis=1)
    
    abs_min = backend.min(backend.abs(backend.stack([mi_1, mi_2, mi_12, -c], axis=0)), axis=0)
    
    return backend.where(all_same, signs[:, 0] * abs_min, 0)

def double_redundancy_ccs(mi_lst, backend):
    signs = backend.stack([backend.sign(mi) for mi in mi_lst], axis=0).T
    all_same = backend.all(signs == signs[:, 0][:, None], axis=1)
    
    abs_min = backend.min(backend.abs(backend.stack(mi_lst, axis=0)), axis=0)
    
    return backend.where(all_same, signs[:, 0] * abs_min, 0)
