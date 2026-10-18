"""Shared pytest fixtures for the poorSKeme FastAPI test suite.

These tests exercise the FastAPI application against the existing tmp/*.json
fixtures already produced by a prior `data_db_process` run in this working
copy of the repository (see tmp/ directory). No network calls are made.
"""
import os
import sys

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from api_poorSKeme import create_application  # noqa: E402


@pytest.fixture(autouse=True)
def _chdir_repo_root(monkeypatch):
    """Route handlers open files using paths relative to the repo root
    (e.g. 'tmp/contract.json'), mirroring the original Flask app's behavior.
    Force the CWD for the duration of each test regardless of where pytest
    was invoked from.
    """
    monkeypatch.chdir(REPO_ROOT)


@pytest.fixture
def app():
    return create_application()


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def tmp_data_available():
    """True when the tmp/*.json fixtures produced by data_db_process exist."""
    return os.path.isfile(os.path.join(REPO_ROOT, "tmp", "contract.json"))


EXISTING_ETH_DB = os.path.join(
    REPO_ROOT, "contract-eth-0xb547027A4CCD46EC98199Fa88AAEDF5aA981Db26.db"
)
