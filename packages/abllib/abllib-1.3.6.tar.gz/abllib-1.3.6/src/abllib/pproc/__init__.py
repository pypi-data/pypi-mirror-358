"""A module containing parallel processing-related functionality, both with threads and processes"""

from ._worker_process import WorkerProcess
from ._worker_thread import WorkerThread
from ..wrapper import Lock, Semaphore

__exports__ = [
    WorkerProcess,
    WorkerThread,
    Lock,
    Semaphore
]
