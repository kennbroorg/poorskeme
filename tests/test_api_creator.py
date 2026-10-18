"""DB-backed route tests for /creator and /trans_creator.

Uses the existing contract-eth-0xb547027A4CCD46EC98199Fa88AAEDF5aA981Db26.db
fixture at the repo root when present. That file predates the
FEAT/NewDataGatherer schema change (it lacks the *_creator-suffixed
tables used by /trans_creator), so each test checks for the tables it
needs and skips with a clear reason instead of failing on an unrelated
fixture/schema mismatch.
"""
import os
import sqlite3

import pytest

from api_poorSKeme import create_application
from fastapi.testclient import TestClient

from tests.conftest import EXISTING_ETH_DB


def _table_exists(db_path, table_name):
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )
        return cur.fetchone() is not None
    finally:
        conn.close()


@pytest.fixture
def creator_client():
    if not os.path.isfile(EXISTING_ETH_DB):
        pytest.skip("Fixture DB not present at repo root in this checkout")
    app = create_application(file=EXISTING_ETH_DB)
    return TestClient(app)


def test_creator_route(creator_client):
    if not _table_exists(EXISTING_ETH_DB, "t_contract_creator"):
        pytest.skip("Fixture DB has no t_contract_creator table")
    response = creator_client.get("/creator")
    assert response.status_code == 200
    body = response.json()
    assert {"creator", "balances", "contracts"}.issubset(body.keys())


def test_trans_creator_route(creator_client):
    required_tables = ("t_transactions_creator", "t_internals_creator", "t_transfers_creator")
    missing = [t for t in required_tables if not _table_exists(EXISTING_ETH_DB, t)]
    if missing:
        pytest.skip(
            "Fixture DB predates the NewDataGatherer schema; missing tables: "
            + ", ".join(missing)
        )
    response = creator_client.get("/trans_creator")
    assert response.status_code == 200
    body = response.json()
    assert {"trans_creator", "stat"}.issubset(body.keys())
