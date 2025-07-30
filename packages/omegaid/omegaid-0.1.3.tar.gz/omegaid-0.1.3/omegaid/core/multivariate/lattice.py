import numpy as np
import numba
from itertools import chain, combinations, product
from functools import lru_cache

def get_partial_information_lattice(n_vars, return_descendants=False):
    nodes = list(range(n_vars))
    powerset_list = list(powerset(nodes))
    
    n_nodes = len(powerset_list)
    
    descendants_map = {i: [] for i in range(n_nodes)}
    
    for i, s1 in enumerate(powerset_list):
        for j, s2 in enumerate(powerset_list):
            if i != j and set(s1).issubset(set(s2)):
                descendants_map[i].append(j)

    sorted_indices = sorted(range(n_nodes), key=lambda k: len(powerset_list[k]))
    
    sorted_nodes = [powerset_list[i] for i in sorted_indices]
    
    sorted_node_masks = np.zeros((n_nodes, n_vars), dtype=bool)
    for i, node in enumerate(sorted_nodes):
        if node:
            sorted_node_masks[i, list(node)] = True
            
    if not return_descendants:
        return sorted_node_masks, None, sorted_indices

    new_descendants_map = {
        new_idx: [
            sorted_indices.index(desc) for desc in descendants_map[old_idx]
        ]
        for new_idx, old_idx in enumerate(sorted_indices)
    }
    
    max_len = max(len(v) for v in new_descendants_map.values()) if new_descendants_map else 0
    descendants_map_adj = np.full((n_nodes, max_len), -1, dtype=np.int32)
    for i in range(n_nodes):
        descs = new_descendants_map[i]
        if descs:
            descendants_map_adj[i, :len(descs)] = descs
            
    return sorted_node_masks, descendants_map_adj, sorted_indices

def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

@lru_cache(maxsize=None)
def get_product_lattice_py(n_sources, n_targets):
    source_indices = tuple(range(n_sources))
    target_indices = tuple(range(n_targets))
    
    source_powerset = list(powerset(source_indices))
    target_powerset = list(powerset(target_indices))
    
    product_lattice_nodes = list(product(source_powerset, target_powerset))
    return product_lattice_nodes

@numba.jit(nopython=True)
def mobius_inversion_jit(sorted_values, descendants_map_adj):
    num_nodes = len(sorted_values)
    atoms = np.zeros_like(sorted_values)
    
    for i in range(num_nodes):
        val = sorted_values[i]
        
        descendants = descendants_map_adj[i]
        sum_of_descendants = 0.0
        for j in range(descendants.shape[0]):
            desc_idx = descendants[j]
            if desc_idx == -1:
                break
            sum_of_descendants += atoms[desc_idx]
            
        atoms[i] = val - sum_of_descendants
        
    return atoms
