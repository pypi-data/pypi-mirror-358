import numpy as np
import array_api_compat
try:
    import torch
except ModuleNotFoundError:
    torch = None
try:
    import cupy as cp
except ModuleNotFoundError:
    cp = None
try:
    import cupyx as cpx
except ModuleNotFoundError:
    cpx = None
from scipy.sparse import issparse


__all__ = ['_is_torch_tensor', '_is_cupy_array',
           '_iscxsparse', '_istsparse', '_issparse']


def _is_torch_tensor(t):
    if torch is None:
        return False
    else:
        return isinstance(t, torch.Tensor)


def _is_cupy_array(x):
    if cp is None:
        return False
    else:
        return isinstance(x, cp.ndarray)


def _iscxsparse(x):
    if cpx is None:
        return False
    else:
        from cupyx.scipy.sparse import issparse
        return issparse(x)


def _istsparse(x):
    if torch is None:
        return False
    else:
        if hasattr(x, 'is_sparse') and hasattr(x, 'layout'):
            return x.is_sparse or x.layout == torch.sparse_csr
        else:
            return False


def _issparse(x):
    return issparse(x) or _iscxsparse(x) or _istsparse(x)
