"""Smoke tests for the GET routes that read tmp/*.json fixtures.

Expected top-level shapes were derived from the pre-migration Flask
implementation (`git show HEAD:api_poorSKeme.py`) to guarantee identical
HTTP behavior for the Angular frontend after the FastAPI migration.
"""
import pytest

# Top-level keys returned by r_contract() in the original Flask app.
CONTRACT_KEYS = {
    "contract", "block_from", "block_to", "first_block", "first_trx",
    "chainid", "blockchain", "classification", "SourceCode", "abi",
    "abiraw", "ContractName", "CompilerVersion", "LicenseType", "fdate",
    "ldate", "token_name", "native", "creator", "max_liq", "max_liq_date",
    "investments", "funct_stats", "volume", "wallets", "trx_out", "trx_in",
}


def test_testing_route(client):
    response = client.get("/testing")
    assert response.status_code == 200
    assert response.json() == {"testing": "OK"}


def test_contract_route(client, tmp_data_available):
    if not tmp_data_available:
        pytest.skip("tmp/contract.json fixtures not present in this checkout")
    response = client.get("/contract")
    assert response.status_code == 200
    body = response.json()
    assert CONTRACT_KEYS.issubset(body.keys())


def test_trans_info_route(client, tmp_data_available):
    if not tmp_data_available:
        pytest.skip("tmp/transaction_resume.json not present in this checkout")
    response = client.get("/trans_info")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert all({"name", "value"}.issubset(item.keys()) for item in body)


def test_transfer_info_route(client, tmp_data_available):
    if not tmp_data_available:
        pytest.skip("tmp/transfer_resume.json not present in this checkout")
    response = client.get("/transfer_info")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert all({"name", "value"}.issubset(item.keys()) for item in body)


def test_liq_route(client, tmp_data_available):
    if not tmp_data_available:
        pytest.skip("tmp/liq.json not present in this checkout")
    response = client.get("/liq")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_tvd_route(client, tmp_data_available):
    if not tmp_data_available:
        pytest.skip("tmp/trans_series.json not present in this checkout")
    response = client.get("/tvd")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert all({"name", "series"}.issubset(item.keys()) for item in body)


def test_transfers_route(client, tmp_data_available):
    if not tmp_data_available:
        pytest.skip("tmp/bubbles.json not present in this checkout")
    response = client.get("/transfers")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, dict)
    assert {"name", "children"}.issubset(body.keys())


def test_anomalies_route(client, tmp_data_available):
    if not tmp_data_available:
        pytest.skip("tmp/anomalies.json not present in this checkout")
    response = client.get("/anomalies")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
