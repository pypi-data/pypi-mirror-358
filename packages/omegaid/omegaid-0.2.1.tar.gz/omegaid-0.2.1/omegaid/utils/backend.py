import os
import importlib

_backend = None
_backend_name = None

def set_backend(backend_name):
    global _backend, _backend_name
    if backend_name not in ["numpy", "cupy"]:
        raise ValueError("Backend must be 'numpy' or 'cupy'")
    try:
        _backend = importlib.import_module(backend_name)
        _backend_name = backend_name
    except ImportError as e:
        raise ImportError(f"Could not import backend: {backend_name}") from e

def get_backend():
    global _backend, _backend_name
    if _backend is None:
        backend_name = os.environ.get("OMEGAID_BACKEND", "numpy")
        set_backend(backend_name)
    return _backend

def get_backend_name():
    global _backend_name
    if _backend_name is None:
        get_backend()
    return _backend_name

def to_device(arr):
    xp = get_backend()
    if get_backend_name() == "cupy":
        return xp.asarray(arr)
    return arr

def to_cpu(arr):
    if get_backend_name() == "cupy":
        return arr.get()
    return arr
