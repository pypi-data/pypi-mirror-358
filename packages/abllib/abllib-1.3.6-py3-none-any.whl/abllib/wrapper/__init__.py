"""A module containing various wrappers"""

from ._lock import Lock, Semaphore
from ._lock_wrapper import NamedLock, NamedSemaphore, WriteLock, ReadLock
from ._singleuse_wrapper import singleuse
from ._deprecated import deprecated

__exports__ = [
    Lock,
    Semaphore,
    NamedLock,
    NamedSemaphore,
    WriteLock,
    ReadLock,
    singleuse,
    deprecated
]
