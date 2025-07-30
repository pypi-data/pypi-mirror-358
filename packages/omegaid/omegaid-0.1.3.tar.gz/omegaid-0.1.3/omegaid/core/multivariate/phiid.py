import time
import numpy as np
from itertools import product
from omegaid.utils.backend import xp
from omegaid.core.entropy import local_entropy_mvn_batched
from omegaid.core.multivariate.lattice import (
    get_partial_information_lattice,
    get_product_lattice_py,
    mobius_inversion_jit,
)
from omegaid.utils.common import (
    reshape_fortran,
    construct_state_space_timeseries,
    PhiID_atoms_abbr,
)


def _calculate_phiid_multivariate_core(
    sources, targets, tau, n_vars_src, n_vars_trg, kind, redundancy_measure, backend
):
    timing_info = {}
    t_start = time.perf_counter()

    if sources.ndim == 1:
        sources = sources.reshape(-1, 1)
    if targets.ndim == 1:
        targets = targets.reshape(-1, 1)

    n_features_src = sources.shape[1] // n_vars_src
    n_features_trg = targets.shape[1] // n_vars_trg

    sources_r = reshape_fortran(sources, (-1, n_vars_src, n_features_src))
    targets_r = reshape_fortran(targets, (-1, n_vars_trg, n_features_trg))

    t_lattice_start = time.perf_counter()
    (
        src_masks,
        src_descendants,
        src_sorted_indices,
    ) = get_partial_information_lattice(n_vars_src, return_descendants=True)
    (
        trg_masks,
        trg_descendants,
        trg_sorted_indices,
    ) = get_partial_information_lattice(n_vars_trg, return_descendants=True)
    product_lattice_nodes = get_product_lattice_py(n_vars_src, n_vars_trg)
    timing_info["lattice_generation"] = time.perf_counter() - t_lattice_start

    t_entropy_start = time.perf_counter()
    n_src_nodes = src_masks.shape[0]
    n_trg_nodes = trg_masks.shape[0]

    src_states, trg_states_past, trg_states_present = construct_state_space_timeseries(
        sources_r, targets_r, tau
    )

    x_data = backend.array(trg_states_present)
    cond_data = backend.array(
        np.concatenate([src_states, trg_states_past], axis=2)
    )

    x_mu = backend.mean(x_data, axis=0, keepdims=True)
    cond_mu = backend.mean(cond_data, axis=0, keepdims=True)
    x_cov = backend.cov(x_data, rowvar=False)
    cond_cov = backend.cov(cond_data, rowvar=False)

    x_data_batched = backend.array(
        [x_data[:, mask] for mask in trg_masks if np.any(mask)]
    )
    x_mu_batched = backend.array(
        [x_mu[0, mask] for mask in trg_masks if np.any(mask)]
    )
    x_cov_batched = backend.array(
        [x_cov[np.ix_(mask, mask)] for mask in trg_masks if np.any(mask)]
    )

    h_x = np.zeros(n_trg_nodes)
    if x_data_batched.size > 0:
        h_x_batched = local_entropy_mvn_batched(
            x_data_batched, x_mu_batched, x_cov_batched, backend
        )
        h_x[np.any(trg_masks, axis=1)] = backend.mean(h_x_batched, axis=1)

    cond_data_batched = backend.array(
        [cond_data[:, mask] for mask in src_masks if np.any(mask)]
    )
    cond_mu_batched = backend.array(
        [cond_mu[0, mask] for mask in src_masks if np.any(mask)]
    )
    cond_cov_batched = backend.array(
        [cond_cov[np.ix_(mask, mask)] for mask in src_masks if np.any(mask)]
    )

    h_cond = np.zeros(n_src_nodes)
    if cond_data_batched.size > 0:
        h_cond_batched = local_entropy_mvn_batched(
            cond_data_batched, cond_mu_batched, cond_cov_batched, backend
        )
        h_cond[np.any(src_masks, axis=1)] = backend.mean(h_cond_batched, axis=1)

    joint_masks = [
        np.concatenate([s_mask, t_mask])
        for s_mask, t_mask in product(src_masks, trg_masks)
    ]
    joint_data_batched = backend.array(
        [cond_data[:, mask] for mask in joint_masks if np.any(mask)]
    )
    joint_mu_batched = backend.array(
        [cond_mu[0, mask] for mask in joint_masks if np.any(mask)]
    )
    joint_cov_batched = backend.array(
        [cond_cov[np.ix_(mask, mask)] for mask in joint_masks if np.any(mask)]
    )

    h_joint = np.zeros(len(joint_masks))
    if joint_data_batched.size > 0:
        h_joint_batched = local_entropy_mvn_batched(
            joint_data_batched, joint_mu_batched, joint_cov_batched, backend
        )
        h_joint[np.any(joint_masks, axis=1)] = backend.mean(h_joint_batched, axis=1)

    h_joint = h_joint.reshape(n_src_nodes, n_trg_nodes)
    timing_info["entropy_calculation"] = time.perf_counter() - t_entropy_start

    t_mi_start = time.perf_counter()
    mi_vals = h_cond[:, None] + h_x[None, :] - h_joint
    timing_info["mi_calculation"] = time.perf_counter() - t_mi_start

    t_mobius_start = time.perf_counter()
    mobius_inversion_jit(mi_vals[:, -1], src_descendants)
    mobius_inversion_jit(mi_vals[-1, :], trg_descendants)

    atoms_product = np.zeros_like(mi_vals)
    for j in range(n_trg_nodes):
        atoms_product[:, j] = mobius_inversion_jit(mi_vals[:, j], src_descendants)

    for i in range(n_src_nodes):
        atoms_product[i, :] = mobius_inversion_jit(atoms_product[i, :], trg_descendants)
    timing_info["mobius_inversion"] = time.perf_counter() - t_mobius_start

    atoms_res = {
        PhiID_atoms_abbr[
            (
                tuple(sorted(product_lattice_nodes[i][0])),
                tuple(sorted(product_lattice_nodes[j][1])),
            )
        ]: atoms_product[
            src_sorted_indices.index(i), trg_sorted_indices.index(j)
        ]
        for i, j in product(range(len(src_sorted_indices)), range(len(trg_sorted_indices)))
    }

    timing_info["total_time"] = time.perf_counter() - t_start
    return atoms_res, timing_info


def calc_phiid_multivariate_mmi(
    sources, targets, tau, n_vars_src, n_vars_trg, kind="gaussian"
):
    return _calculate_phiid_multivariate_core(
        sources, targets, tau, n_vars_src, n_vars_trg, kind, "MMI", np
    )


def calc_phiid_multivariate_ccs(
    sources, targets, tau, n_vars_src, n_vars_trg, kind="gaussian"
):
    return _calculate_phiid_multivariate_core(
        sources, targets, tau, n_vars_src, n_vars_trg, kind, "CCS", xp
    )
