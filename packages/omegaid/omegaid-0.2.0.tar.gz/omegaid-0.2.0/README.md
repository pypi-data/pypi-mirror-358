# ΩID

[![PyPI version](https://badge.fury.io/py/omegaid.svg)](https://badge.fury.io/py/omegaid)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/dmf-archive/OmegaID)

ΩID is a Python package for calculating the integrated information decomposition (ΦID) of time series data. It is designed for high-performance computing, with optional GPU acceleration via CuPy.

## Features

- **Backend Agnostic**: Seamlessly switch between CPU (NumPy) and GPU (CuPy) for computation.
- **High Performance**: Vectorized operations and GPU support for significant speedups on large datasets.
- **Numerical Integrity**: Results are numerically consistent with the original `phyid` implementation.

## Installation

ΩID is available on PyPI. You can install it with `pip` or `uv pip`.

### Standard Installation (CPU only)

```bash
pip install omegaid
```

### With GPU support

To install ΩID with GPU support, you need to have a CUDA-enabled GPU and the CUDA toolkit installed. Choose the command that matches your CUDA version.

**For CUDA 12.x:**

```bash
pip install "omegaid[cuda-12x]"
```

**For CUDA 11.x:**

```bash
pip install "omegaid[cuda-11x]"
```

## Usage

### Selecting the Backend

You can select the computation backend by setting the `OMEGAID_BACKEND` environment variable before running your Python script.

- **For NumPy (default):**

    ```bash
    export OMEGAID_BACKEND=numpy
    ```

- **For CuPy:**

    ```bash
    export OMEGAID_BACKEND=cupy
    ```

If the variable is not set, OmegaID will default to using NumPy.

### Example

Here is a simple example of how to use `omegaid` to calculate the Phi-ID decomposition.

```python
import numpy as np
from omegaid.core.decomposition import calc_PhiID
from omegaid.utils.backend import set_backend

# For programmatic control, you can also use set_backend
# set_backend('cupy') 

# Generate some random time series data
n_samples = 10000
tau = 1
src = np.random.randn(n_samples)
trg = np.random.randn(n_samples)

# Calculate Phi-ID
atoms_res, calc_res = calc_PhiID(src, trg, tau)

# Print the synergistic atom (sts)
print("Synergy (sts):", np.mean(atoms_res["sts"]))
```

## Performance

The package has been benchmarked against the original `phyid` implementation. The NumPy backend provides a consistent ~1.4-2x speedup. The CuPy backend shows significant performance gains on larger datasets, leveraging GPU acceleration effectively.

**Note:** The current benchmarks are based on a 2x2 system (two scalar time series).

| Data Size | Original (scipy) | OmegaID (numpy) | OmegaID (cupy) | NumPy Speedup | CuPy Speedup |
| :-------- | :--------------- | :-------------- | :------------- | :------------ | :----------- |
| 10,000    | 0.0112s          | 0.0071s         | 0.3243s        | 1.58x         | 0.03x        |
| 100,000   | 0.1161s          | 0.0846s         | 0.0932s        | 1.37x         | 1.25x        |
| 500,000   | 0.6492s          | 0.4592s         | 0.3207s        | 1.41x         | 2.02x        |

The results demonstrate that for data lengths exceeding 100,000 samples, the CuPy backend begins to outperform both the original and the NumPy-based implementations, with the trend suggesting greater speedups for even larger datasets.

## License

This project is licensed under the BSD 3-Clause License.
