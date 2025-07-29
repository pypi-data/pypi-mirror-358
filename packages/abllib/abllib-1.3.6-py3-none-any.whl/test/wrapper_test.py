"""Module containing tests for the abllib.wrapper module"""

# pylint: disable=function-redefined, consider-using-with

from datetime import datetime

import pytest

from abllib import error, wrapper
from abllib.pproc import WorkerThread

def test_lock():
    """Ensure that Lock works as expected"""

    assert hasattr(wrapper, "Lock")
    assert callable(wrapper.Lock)

    lock = wrapper.Lock()

    assert not lock.locked()
    assert lock.acquire(blocking=True, timeout=1)
    assert lock.locked()

    assert not lock.acquire(blocking=True, timeout=1)

    lock.release()
    assert not lock.locked()

def test_semaphore():
    """Ensure that Semaphore works as expected"""

    assert hasattr(wrapper, "Semaphore")
    assert callable(wrapper.Semaphore)

    sem = wrapper.Semaphore(3)

    assert not sem.locked()
    assert sem.acquire(blocking=True, timeout=1)
    assert sem.locked()
    assert sem.acquire(blocking=True, timeout=1)
    assert sem.locked()
    assert sem.acquire(blocking=True, timeout=1)
    assert sem.locked()

    # the semaphore is full
    assert not sem.acquire(blocking=True, timeout=1)

    sem.release()
    assert sem.locked()
    sem.release()
    assert sem.locked()
    sem.release()
    assert not sem.locked()

def test_namedlock():
    """Ensure that NamedLock works as expected"""

    assert hasattr(wrapper, "NamedLock")
    assert callable(wrapper.NamedLock)

    @wrapper.NamedLock("test1", timeout=0.1)
    def func1():
        return True

    assert not wrapper.NamedLock("test1").locked()
    assert func1()
    assert not wrapper.NamedLock("test1").locked()

    wrapper.NamedLock("test2").acquire()
    assert wrapper.NamedLock("test2").locked()
    assert wrapper.NamedLock("test2", timeout=1).locked()

    wrapper.NamedLock("test3").acquire()
    def func2():
        assert wrapper.NamedLock("test3").locked()
        wrapper.NamedLock("test3", timeout=4).acquire()

    start_time = datetime.now()
    thread = WorkerThread(target=func2)
    thread.start()
    with pytest.raises(error.LockAcquisitionTimeoutError):
        thread.join(reraise=True)

    duration = datetime.now() - start_time
    assert duration.total_seconds() > 3.5
    assert duration.total_seconds() < 4.5

def test_namedsemaphore():
    """Ensure that NamedSemaphore works as expected"""

    assert hasattr(wrapper, "NamedSemaphore")
    assert callable(wrapper.NamedSemaphore)

    @wrapper.NamedSemaphore("test1", timeout=0.1)
    def func1():
        return True

    assert not wrapper.NamedSemaphore("test1").locked()
    assert func1()
    assert not wrapper.NamedSemaphore("test1").locked()

    wrapper.NamedSemaphore("test2").acquire()
    assert wrapper.NamedSemaphore("test2").locked()
    assert wrapper.NamedSemaphore("test2", timeout=1).locked()

    wrapper.NamedLock("test3").acquire()
    def func2():
        assert not wrapper.NamedSemaphore("test3").locked()
        wrapper.NamedSemaphore("test3", timeout=4).acquire()

    start_time = datetime.now()
    thread = WorkerThread(target=func2)
    thread.start()
    with pytest.raises(error.LockAcquisitionTimeoutError):
        thread.join(reraise=True)

    duration = datetime.now() - start_time
    assert duration.total_seconds() > 3.5
    assert duration.total_seconds() < 4.5

def test_namedlocks_combined():
    """Ensure that NamedLock and NamedSemaphore work together correctly"""

    @wrapper.NamedLock("test1", timeout=0.1)
    def func():
        return True

    wrapper.NamedSemaphore("test1").acquire()
    with pytest.raises(error.LockAcquisitionTimeoutError):
        func()
    wrapper.NamedSemaphore("test1").release()


    @wrapper.NamedLock("test2", timeout=0.1)
    def func():
        return True

    wrapper.NamedSemaphore("test2").acquire()
    wrapper.NamedSemaphore("test2").acquire()
    wrapper.NamedSemaphore("test2").acquire()
    with pytest.raises(error.LockAcquisitionTimeoutError):
        func()
    wrapper.NamedSemaphore("test2").release()
    with pytest.raises(error.LockAcquisitionTimeoutError):
        func()
    wrapper.NamedSemaphore("test2").release()
    with pytest.raises(error.LockAcquisitionTimeoutError):
        func()
    wrapper.NamedSemaphore("test2").release()
    func()


    @wrapper.NamedSemaphore("test3", timeout=0.1)
    def func():
        return True

    wrapper.NamedLock("test3").acquire()
    with pytest.raises(error.LockAcquisitionTimeoutError):
        func()
    wrapper.NamedLock("test3").release()

def test_locks_underscore_names():
    """Ensure that named lock names can start with an underscore"""

    lock = wrapper.NamedSemaphore("_test1")
    assert not lock.locked()
    lock.acquire()
    assert lock.locked()
    assert wrapper.NamedSemaphore("_test1").locked()
    lock.release()
    assert not lock.locked()
    assert not wrapper.NamedSemaphore("_test1").locked()

    lock = wrapper.NamedLock("_test2")
    assert not lock.locked()
    lock.acquire()
    assert lock.locked()
    assert wrapper.NamedLock("_test2").locked()
    lock.release()
    assert not lock.locked()
    assert not wrapper.NamedLock("_test2").locked()

def test_singleuse():
    """Ensure that singleuse works as expected"""

    @wrapper.singleuse
    def func1():
        pass

    func1()

    with pytest.raises(error.CalledMultipleTimesError):
        func1()

    with pytest.raises(error.CalledMultipleTimesError):
        func1()

def test_singleuse_exception():
    """Ensure that raised exceptions reset singleuse flag"""

    data = [1, 2, 3]

    @wrapper.singleuse
    def func1():
        if len(data) > 0:
            data.pop(0)
            raise error.InternalCalculationError()

    with pytest.raises(error.InternalCalculationError):
        func1()
    with pytest.raises(error.InternalCalculationError):
        func1()
    with pytest.raises(error.InternalCalculationError):
        func1()

    func1()

    with pytest.raises(error.CalledMultipleTimesError):
        func1()

    with pytest.raises(error.CalledMultipleTimesError):
        func1()
