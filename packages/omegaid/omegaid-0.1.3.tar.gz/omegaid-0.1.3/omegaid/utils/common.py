import numpy as np

def reshape_fortran(x, shape):
    if hasattr(x, 'reshape'):
        return x.reshape(shape, order='F')
    return np.reshape(x, shape, order='F')

def get_combinations(ts, n_features):
    return [
        list(range(i, i + n_features))
        for i in range(0, len(ts.columns), n_features)
    ]

def construct_state_space_timeseries(sources, targets, tau):
    n_samples = sources.shape[0]
    
    src_states = sources[: n_samples - tau]
    trg_states_past = targets[: n_samples - tau]
    trg_states_present = targets[tau:]
    
    return src_states, trg_states_past, trg_states_present

def _get_vars_from_node(node, n_features):
    if not node:
        return []
    return list(range(node[0] * n_features, (node[-1] + 1) * n_features))

def _binarize(x, threshold=None):
    if threshold is None:
        threshold = np.median(x)
    return (x > threshold).astype(int)

PhiID_atoms = {
    "R": "Redundancy",
    "U_s1": "Unique_s1",
    "U_s2": "Unique_s2",
    "S": "Synergy",
}

PhiID_atoms_abbr = {
    (s, t): f"{atom_name}({s};{t})"
    for (atom_name, _), (s, t) in zip(
        PhiID_atoms.items(),
        [
            ((("s1",), ("s2",)), ("t",)),
            (("s1",),),
            (("s2",),),
            ((("s1",), ("s2",)), ("t",)),
        ],
    )
}
