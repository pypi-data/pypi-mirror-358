"""Module containing tests for the abllib.fs module"""

# pylint: disable=missing-class-docstring

import pathlib
import os

import pytest

from abllib import fs

def test_absolute():
    """Ensure that fs.absolute works as expected"""

    assert callable(fs.absolute)
    assert fs.absolute(os.getcwd()) == os.getcwd().replace("c:\\", "C:\\")
    assert fs.absolute("test.txt") == os.path.join(_uppercase_path(os.getcwd()), "test.txt")
    assert fs.absolute("subdir", "another", "test.txt") \
           == os.path.join(_uppercase_path(os.getcwd()), "subdir", "another", "test.txt")
    assert fs.absolute("subdir", pathlib.Path("another"), "test.txt") \
           == os.path.join(_uppercase_path(os.getcwd()), "subdir", "another", "test.txt")
    assert fs.absolute("subdir", "..", "test.txt") == os.path.join(_uppercase_path(os.getcwd()), "test.txt")

    with pytest.raises(TypeError):
        fs.absolute(None)
    with pytest.raises(TypeError):
        fs.absolute(1)
    with pytest.raises(TypeError):
        fs.absolute("one", "two", 3)
    with pytest.raises(ValueError):
        fs.absolute()

def _uppercase_path(path: str) -> str:
    if path.startswith("/"):
        return path

    first = path[0]
    first = first.upper()
    return first + path[1:]
