from itertools import product, chain, combinations
from typing import List, Tuple
import numpy as np

def generate_doublet_atoms(n_sources: int, n_targets: int) -> List[Tuple[int, int]]:
    source_indices = range(n_sources)
    target_indices = range(n_sources, n_sources + n_targets)
    return list(product(source_indices, target_indices))

def generate_doublet_mi_tasks(
    n_sources: int, n_targets: int
) -> List[Tuple[List[int], List[int]]]:
    source_indices = list(range(n_sources))
    target_indices = list(range(n_sources, n_sources + n_targets))

    all_source_subsets = [
        list(s) for s in chain.from_iterable(
            combinations(source_indices, r) for r in range(len(source_indices) + 1)
        )
    ]
    all_target_subsets = [
        list(s) for s in chain.from_iterable(
            combinations(target_indices, r) for r in range(len(target_indices) + 1)
        )
    ]

    mi_tasks = list(product(all_source_subsets, all_target_subsets))
    
    return mi_tasks

def build_doublet_matrix(n_sources: int, n_targets: int):
    source_indices = range(n_sources)
    target_indices = range(n_sources, n_sources + n_targets)

    non_empty_source_subsets = [
        s for r in range(1, n_sources + 1) for s in combinations(source_indices, r)
    ]
    non_empty_target_subsets = [
        s for r in range(1, n_targets + 1) for s in combinations(target_indices, r)
    ]

    mi_terms = list(product(non_empty_source_subsets, non_empty_target_subsets))
    doublet_atoms = list(product(source_indices, target_indices))

    n_rows = len(mi_terms)
    n_cols = len(doublet_atoms)
    
    matrix = np.zeros((n_rows, n_cols), dtype=int)

    mi_term_map = {term: i for i, term in enumerate(mi_terms)}
    atom_map = {atom: i for i, atom in enumerate(doublet_atoms)}

    for (source_subset, target_subset), row_idx in mi_term_map.items():
        for s_i in source_subset:
            for t_j in target_subset:
                col_idx = atom_map[(s_i, t_j)]
                matrix[row_idx, col_idx] = 1
    
    return matrix, mi_terms, doublet_atoms