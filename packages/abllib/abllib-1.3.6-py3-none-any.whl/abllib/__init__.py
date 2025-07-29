"""
Ableytner's library for Python

Contains many general-purpose functions which can be used across projects.
"""

from . import alg, error, fs, fuzzy, onexit, wrapper
from .log import get_logger
from .storage import CacheStorage, VolatileStorage, PersistentStorage, StorageView

__exports__ = [
    alg,
    error,
    fs,
    fuzzy,
    onexit,
    wrapper,
    get_logger,
    CacheStorage,
    VolatileStorage,
    PersistentStorage,
    StorageView
]
