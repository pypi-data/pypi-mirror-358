import os
import importlib

def get_backend():
    if os.environ.get('CUPY_ENABLED', 'false').lower() in ('true', '1', 't'):
        try:
            return importlib.import_module('cupy')
        except ImportError as e:
            raise ImportError(
                "CuPy is not installed, but CUPY_ENABLED is set to True. "
                "Please install CuPy or disable GPU support."
            ) from e
    return importlib.import_module('numpy')

xp = get_backend()
