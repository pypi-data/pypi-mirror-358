"""
    Pytest fixtures
"""

# pylint: disable=protected-access, missing-class-docstring

import os
import shutil

import pytest

from abllib import fs, log, storage, _storage, onexit

logger = log.get_logger("test")

@pytest.fixture(scope="session", autouse=True)
def setup():
    """Setup the PersistentStorage, VolatileStorage and StorageView for test usage"""

    # setup testing dirs
    STORAGE_DIR = fs.absolute(os.path.dirname(__file__), "..", "..", "test_run")
    shutil.rmtree(STORAGE_DIR, ignore_errors=True)
    os.makedirs(STORAGE_DIR, exist_ok=True)

    #  setup logging
    log.initialize(log.LogLevel.DEBUG)
    log.add_console_handler()
    log.add_file_handler(os.path.join(STORAGE_DIR, "test.log"))

    STORAGE_FILE = fs.absolute(STORAGE_DIR, "test.json")

    if os.path.isfile(STORAGE_FILE):
        os.remove(STORAGE_FILE)

    storage.initialize(STORAGE_FILE)

    yield None

    storage.PersistentStorage.save_to_disk()

@pytest.fixture(scope="function", autouse=True)
def clean_after_function():
    """Clean up the PersistentStorage, VolatileStorage and StorageView, removing all keys"""

    yield None

    for key in list(storage.PersistentStorage._store.keys()):
        del storage.PersistentStorage[key]

    for key in list(storage.VolatileStorage._store.keys()):
        del storage.VolatileStorage[key]

    for key in list(_storage.InternalStorage._store.keys()):
        if key not in ["_storage_file", "_onexit"]:
            del _storage.InternalStorage[key]

    onexit.reset()

@pytest.fixture(scope="function", autouse=False)
def capture_logs():
    """Save all log output to a new file test.log in the root dir"""

    log.initialize(log.LogLevel.DEBUG)
    log.add_file_handler("test.log")

    yield None

    log.initialize()
    os.remove("test.log")
