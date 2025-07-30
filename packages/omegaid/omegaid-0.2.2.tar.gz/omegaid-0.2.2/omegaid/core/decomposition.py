from omegaid.utils.backend import get_backend, to_device, to_cpu
from omegaid.core.entropy import local_entropy_mvn, local_entropy_binary
from omegaid.core.atoms import PhiID_atoms_abbr
from omegaid.core.doublet_lattice import generate_doublet_mi_tasks, build_doublet_matrix
import numpy as np

def _get_entropy_four_vec(X, kind):
    xp = get_backend()
    n_vars, n_samples = X.shape
    
    if kind == "gaussian":
        X_cov = xp.cov(X)
        X_mu = xp.mean(X, axis=1)
        
        def _h(indices):
            if not indices:
                return xp.zeros(n_samples)
            indices = xp.array(indices)
            sub_cov = X_cov[xp.ix_(indices, indices)]
            sub_mu = X_mu[indices]
            sub_X = X[indices, :].T
            return local_entropy_mvn(sub_X, sub_mu, sub_cov)

    elif kind == "discrete":
        def _h(indices):
            if not indices:
                return xp.zeros(n_samples)
            return local_entropy_binary(X[indices, :])
    else:
        raise ValueError("kind must be one of 'gaussian' or 'discrete'")

    indices_map = {
        "h_p1": [0], "h_p2": [1], "h_t1": [2], "h_t2": [3],
        "h_p1p2": [0, 1], "h_t1t2": [2, 3],
        "h_p1t1": [0, 2], "h_p1t2": [0, 3], "h_p2t1": [1, 2], "h_p2t2": [1, 3],
        "h_p1p2t1": [0, 1, 2], "h_p1p2t2": [0, 1, 3],
        "h_p1t1t2": [0, 2, 3], "h_p2t1t2": [1, 2, 3],
        "h_p1p2t1t2": [0, 1, 2, 3],
    }
    
    h_res = {key: _h(indices) for key, indices in indices_map.items()}
    return h_res

def _get_coinfo_four_vec(h_res):
    return {
        "I_xytab": h_res["h_p1p2"] + h_res["h_t1t2"] - h_res["h_p1p2t1t2"],
        "I_xta": h_res["h_p1"] + h_res["h_t1"] - h_res["h_p1t1"],
        "I_xtb": h_res["h_p1"] + h_res["h_t2"] - h_res["h_p1t2"],
        "I_yta": h_res["h_p2"] + h_res["h_t1"] - h_res["h_p2t1"],
        "I_ytb": h_res["h_p2"] + h_res["h_t2"] - h_res["h_p2t2"],
        "I_xyta": h_res["h_p1p2"] + h_res["h_t1"] - h_res["h_p1p2t1"],
        "I_xytb": h_res["h_p1p2"] + h_res["h_t2"] - h_res["h_p1p2t2"],
        "I_xtab": h_res["h_p1"] + h_res["h_t1t2"] - h_res["h_p1t1t2"],
        "I_ytab": h_res["h_p2"] + h_res["h_t1t2"] - h_res["h_p2t1t2"],
    }

def _get_redundancy_four_vec(redundancy, I_res):
    xp = get_backend()
    
    def redundancy_mmi(mi_1, mi_2):
        mean_mi_1 = xp.mean(mi_1)
        mean_mi_2 = xp.mean(mi_2)
        return mi_1 if mean_mi_1 < mean_mi_2 else mi_2

    def redundancy_ccs(mi_1, mi_2, mi_12):
        c = mi_12 - mi_1 - mi_2
        signs = xp.stack([xp.sign(mi_1), xp.sign(mi_2), xp.sign(mi_12), xp.sign(-c)], axis=0)
        all_same = xp.all(signs == signs[0, :], axis=0)
        return all_same * (-c)

    if redundancy == "MMI":
        def redundancy_func(mi_1, mi_2, mi_12):
            return redundancy_mmi(mi_1, mi_2)
    elif redundancy == "CCS":
        redundancy_func = redundancy_ccs
    else:
        raise ValueError("redundancy must be one of 'MMI' or 'CCS'")

    return {
        "R_xyta": redundancy_func(I_res["I_xta"], I_res["I_yta"], I_res["I_xyta"]),
        "R_xytb": redundancy_func(I_res["I_xtb"], I_res["I_ytb"], I_res["I_xytb"]),
        "R_xytab": redundancy_func(I_res["I_xtab"], I_res["I_ytab"], I_res["I_xytab"]),
        "R_abtx": redundancy_func(I_res["I_xta"], I_res["I_xtb"], I_res["I_xtab"]),
        "R_abty": redundancy_func(I_res["I_yta"], I_res["I_ytb"], I_res["I_ytab"]),
        "R_abtxy": redundancy_func(I_res["I_xyta"], I_res["I_xytb"], I_res["I_xytab"]),
    }

def _get_double_redundancy_four_vec(redundancy, calc_res):
    xp = get_backend()
    I_res = calc_res["I_res"]
    R_res = calc_res["R_res"]

    if redundancy == "MMI":
        mi_lst = [I_res["I_xta"], I_res["I_xtb"], I_res["I_yta"], I_res["I_ytb"]]
        mi_mean_lst = [xp.mean(mi) for mi in mi_lst]
        min_index = xp.argmin(xp.stack(mi_mean_lst))
        if hasattr(min_index, 'item'):
            min_index = min_index.item()
        return mi_lst[min_index]
    
    elif redundancy == "CCS":
        double_coinfo = - I_res["I_xta"] - I_res["I_xtb"] - I_res["I_yta"] - I_res["I_ytb"] + \
            I_res["I_xtab"] + I_res["I_ytab"] + I_res["I_xyta"] + I_res["I_xytb"] - I_res["I_xytab"] + \
            R_res["R_xyta"] + R_res["R_xytb"] - R_res["R_xytab"] + \
            R_res["R_abtx"] + R_res["R_abty"] - R_res["R_abtxy"]
        mi_lst = [
            I_res["I_xta"], I_res["I_xtb"], I_res["I_yta"], I_res["I_ytb"], double_coinfo
        ]
        signs = xp.stack([xp.sign(mi) for mi in mi_lst], axis=0)
        all_same = xp.all(signs == signs[0, :], axis=0)
        return all_same * mi_lst[-1]
    else:
        raise ValueError("redundancy must be one of 'MMI' or 'CCS'")

def _get_atoms_four_vec(calc_res):
    xp = get_backend()
    I_res = calc_res["I_res"]
    R_res = calc_res["R_res"]
    rtr = calc_res["rtr"]

    knowns = xp.stack([
        rtr,
        R_res["R_xyta"], R_res["R_xytb"], R_res["R_xytab"],
        R_res["R_abtx"], R_res["R_abty"], R_res["R_abtxy"],
        I_res["I_xta"], I_res["I_xtb"], I_res["I_yta"], I_res["I_ytb"],
        I_res["I_xyta"], I_res["I_xytb"], I_res["I_xtab"], I_res["I_ytab"], I_res["I_xytab"]
    ], axis=0)

    knowns_to_atoms_mat = xp.array([
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
        [1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
        [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0],
        [1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ], dtype=knowns.dtype)

    atoms_mat = xp.linalg.solve(knowns_to_atoms_mat, knowns)
    return {abbr: atoms_mat[i, :] for i, abbr in enumerate(PhiID_atoms_abbr)}

def _binarize(v):
    xp = get_backend()
    return (v > xp.mean(v)).astype(int)

def _calc_phiid_2x2(src, trg, tau, kind="gaussian", redundancy="MMI"):
    xp = get_backend()
    
    src_past, src_future = src[:, :-tau], src[:, tau:]
    trg_past, trg_future = trg[:, :-tau], trg[:, tau:]

    if kind == "gaussian":
        X = xp.stack([src_past[0], src_past[1], trg_future[0], trg_future[1]], axis=0)
        X_norm = X / xp.std(X, axis=1, ddof=1, keepdims=True)
        X_input = X_norm
    elif kind == "discrete":
        X_input = xp.stack([
            _binarize(src_past[0]), _binarize(src_past[1]),
            _binarize(trg_future[0]), _binarize(trg_future[1])
        ], axis=0)
    else:
        raise ValueError("kind must be one of 'gaussian' or 'discrete'")

    h_res = _get_entropy_four_vec(X_input, kind=kind)
    I_res = _get_coinfo_four_vec(h_res)
    R_res = _get_redundancy_four_vec(redundancy, I_res)
    
    calc_res = {"h_res": h_res, "I_res": I_res, "R_res": R_res}
    rtr = _get_double_redundancy_four_vec(redundancy, calc_res)
    calc_res["rtr"] = rtr
    
    atoms_res = _get_atoms_four_vec(calc_res)
    return atoms_res, calc_res

def _get_entropy_multivariate(X, tasks, kind):
    xp = get_backend()
    n_vars, n_samples = X.shape
    
    if kind == "gaussian":
        X_cov = xp.cov(X)
        X_mu = xp.mean(X, axis=1)
        
        def _h(indices):
            if not indices:
                return xp.zeros(n_samples)
            indices = xp.array(indices)
            sub_cov = X_cov[xp.ix_(indices, indices)]
            sub_mu = X_mu[indices]
            sub_X = X[indices, :].T
            return local_entropy_mvn(sub_X, sub_mu, sub_cov)

    elif kind == "discrete":
        def _h(indices):
            if not indices:
                return xp.zeros(n_samples)
            return local_entropy_binary(X[indices, :])
    else:
        raise ValueError("kind must be one of 'gaussian' or 'discrete'")

    return {tuple(task): _h(task) for task in tasks}

def _calc_phiid_doublet(src, trg, tau, kind="gaussian"):
    xp = get_backend()
    n_sources, n_samples = src.shape
    n_targets, _ = trg.shape

    src_past, src_future = src[:, :-tau], src[:, tau:]
    trg_past, trg_future = trg[:, :-tau], trg[:, tau:]
    
    X = xp.concatenate([src_past, trg_past], axis=0)

    matrix, mi_terms, doublet_atoms = build_doublet_matrix(n_sources, n_targets)
    
    all_indices = set()
    for sources, targets in mi_terms:
        all_indices.add(tuple(sources))
        all_indices.add(tuple(targets))
        all_indices.add(tuple(sorted(sources + targets)))
    
    entropy_tasks = [list(item) for item in all_indices]
    entropies = _get_entropy_multivariate(X, entropy_tasks, kind)

    mi_values = []
    for sources, targets in mi_terms:
        h_s = entropies[tuple(sources)]
        h_t = entropies[tuple(targets)]
        h_st = entropies[tuple(sorted(sources + targets))]
        mi = h_s + h_t - h_st
        mi_values.append(xp.mean(mi))

    b = xp.array(mi_values)
    A = xp.array(matrix, dtype=b.dtype)

    atom_values = xp.linalg.lstsq(A, b, rcond=None)[0]

    atoms_res = {atom: val for atom, val in zip(doublet_atoms, atom_values)}
    return atoms_res, None

def calc_phiid_multivariate(src, trg, tau=1, kind="gaussian", redundancy="MMI"):
    src, trg = to_device(src), to_device(trg)
    n_sources, _ = src.shape
    n_targets, _ = trg.shape

    is_2x2 = n_sources == 2 and n_targets == 2
    if is_2x2:
        atoms_res, calc_res = _calc_phiid_2x2(src, trg, tau, kind, redundancy)
    else:
        atoms_res, calc_res = _calc_phiid_doublet(src, trg, tau, kind)

    atoms_res_cpu = {}
    for k, v in atoms_res.items():
        v_cpu = to_cpu(v)
        if not is_2x2 and hasattr(v_cpu, 'item'):
             atoms_res_cpu[k] = v_cpu.item()
        else:
            atoms_res_cpu[k] = v_cpu

    if calc_res:
        calc_res_cpu = {
            k: {k_inner: to_cpu(v_inner) for k_inner, v_inner in v.items()} if isinstance(v, dict) else to_cpu(v)
            for k, v in calc_res.items()
        }
    else:
        calc_res_cpu = None

    return atoms_res_cpu, calc_res_cpu
