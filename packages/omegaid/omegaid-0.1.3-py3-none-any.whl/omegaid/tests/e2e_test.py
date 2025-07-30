import numpy as np
from omegaid.core.phiid import calc_phiid_mmi
from omegaid.core.multivariate.phiid import calc_phiid_multivariate_mmi

def run_e2e_test():
    print("Running end-to-end equivalence test for 1-source, 1-target system...")
    
    n_samples = 2000
    tau = 1
    
    rng = np.random.default_rng(0)
    src_1d = rng.standard_normal(n_samples)
    trg_1d = rng.standard_normal(n_samples)
    
    print(f"Generated mock data with {n_samples} samples.")

    try:
        atoms_orig, info_orig = calc_phiid_mmi(src_1d, trg_1d, tau=tau, kind="gaussian")
        
        src_2d = src_1d.reshape(-1, 1)
        trg_2d = trg_1d.reshape(-1, 1)
        atoms_gen, info_gen = calc_phiid_multivariate_mmi(src_2d, trg_2d, tau=tau, kind="gaussian")

        total_info_orig = info_orig["I_res"]["I_xytab"]

        # For a 1x1 system, the past has 1 var (src_past) and the future has 1 var (trg_past)
        # This is incorrect. The past has 2 vars (src_past, trg_past) and future has 2 vars (src_future, trg_future)
        
        # Let's call the generalized function with the appropriate inputs.
        # `sources` parameter should be the sources of information, i.e., the past variables.
        # `targets` parameter should be the targets of information, i.e., the future variables.
        n_s = n_samples - tau
        past_vars_for_gen = np.hstack([src_1d[:n_s].reshape(-1, 1), trg_1d[:n_s].reshape(-1, 1)])
        future_vars_for_gen = np.hstack([src_1d[tau:].reshape(-1, 1), trg_1d[tau:].reshape(-1, 1)])

        # We need a generalized function that decomposes I(A,B; C,D)
        # The current `_calculate_phiid_generalized_core` decomposes I(sources; targets)
        # So, sources = past_vars_for_gen, targets = future_vars_for_gen
        
        atoms_gen_2x2, info_gen_2x2 = calc_phiid_multivariate_mmi(past_vars_for_gen, future_vars_for_gen, tau=0)

        # The top node of the 2x2 lattice is ((0, 1), (0, 1))
        # Its value in mi_values should be I({past_0, past_1}; {future_0, future_1})
        top_node = (tuple(range(2)), tuple(range(2)))
        total_info_gen = info_gen_2x2["mi_values"][top_node]
        
        print(f"Original Total Info I(past;future): {total_info_orig.mean():.6f}")
        print(f"Generalized Total Info I(past;future): {total_info_gen:.6f}")
        
        assert np.allclose(total_info_orig.mean(), total_info_gen, atol=1e-6), "Total information mismatch!"
            
        print("\nEnd-to-end equivalence test PASSED.")
        
    except Exception as e:
        print(f"\nEnd-to-end test FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_e2e_test()
