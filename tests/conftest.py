"""Isolated, short Inspect data paths also work on Windows SQLite builds."""

import hashlib

import pytest


@pytest.fixture
def inspect_runtime(tmp_path, monkeypatch):
    cache = tmp_path.parent / ("i" + hashlib.sha256(tmp_path.name.encode()).hexdigest()[:5])
    cache.mkdir(exist_ok=True)
    for variable in (
        "WIN_PD_OVERRIDE_LOCAL_APPDATA",
        "LOCALAPPDATA",
        "XDG_DATA_HOME",
        "XDG_CACHE_HOME",
    ):
        monkeypatch.setenv(variable, str(cache))
    return cache
