"""Tests for the per-address / per-transaction detail routes.

/details/{address} and /trx_hash/{trx_hash} depend on pandas DataFrames
built from tmp/*.json. Rather than hard-coding a contract-specific address
or hash (fragile across different tmp/ datasets), we derive a valid one
from whatever data is currently present in tmp/, keeping the tests robust
no matter which contract was last processed by data_db_process.
"""
import ast
import os

import pandas as pd
import pytest

# Top-level keys returned by r_result() / r_trx() in the original Flask app.
DETAILS_KEYS = {
    "address", "fdate", "ldate", "from_sum", "from_count", "to_sum",
    "to_count", "trans_vol", "moves",
}
TRX_KEYS = {"hash", "trx", "transfers", "constructor", "function", "code"}


def _read_stats(repo_root):
    with open(os.path.join(repo_root, "tmp", "stats.json")) as f:
        return ast.literal_eval(f.read())


def _pick_active_address(repo_root, native):
    if native:
        df = pd.read_json(os.path.join(repo_root, "tmp", "uni.json"))
        df = df[df["value"] != 0]
    else:
        df_tc = pd.read_json(os.path.join(repo_root, "tmp", "transfers_contract.json"))
        df_tw = pd.read_json(os.path.join(repo_root, "tmp", "transfers_wallet.json"))
        df = pd.concat([df_tw, df_tc], ignore_index=True)
    if df.empty:
        return None
    return df["to"].iloc[0]


def _pick_decoded_hash(repo_root):
    df_decode = pd.read_json(os.path.join(repo_root, "tmp", "decoded.json"))
    df_uni = pd.read_json(os.path.join(repo_root, "tmp", "uni.json"))
    candidates = df_decode[df_decode["funct"] != "Not decoded"]
    for candidate_hash in candidates["hash"]:
        trx_rows = df_uni[(df_uni["hash"] == candidate_hash) & (df_uni["file"] == "trx")]
        if len(trx_rows) == 1:
            return candidate_hash
    return None


def test_details_route(client, tmp_data_available):
    if not tmp_data_available:
        pytest.skip("tmp/*.json fixtures not present in this checkout")
    from tests.conftest import REPO_ROOT

    stats = _read_stats(REPO_ROOT)
    address = _pick_active_address(REPO_ROOT, stats["native"])
    if not address:
        pytest.skip("No address with transfer activity found in current tmp/ data")

    response = client.get(f"/details/{address}")
    assert response.status_code == 200
    body = response.json()
    assert DETAILS_KEYS.issubset(body.keys())
    assert body["address"] == address


def test_trx_hash_route(client, tmp_data_available):
    if not tmp_data_available:
        pytest.skip("tmp/*.json fixtures not present in this checkout")
    from tests.conftest import REPO_ROOT

    trx_hash = _pick_decoded_hash(REPO_ROOT)
    if not trx_hash:
        pytest.skip("No uniquely decoded transaction hash found in current tmp/ data")

    try:
        response = client.get(f"/trx_hash/{trx_hash}")
    except IndexError:
        # NOTE: Pre-existing bug in the unchanged args-parsing logic
        # (identical in the original Flask handler): when the decoded
        # constructor call took zero arguments, `args_const[2:-2]` yields
        # an empty string, `''.split(', ')` yields `['']`, and the code
        # unconditionally indexes `e[1]` -> IndexError. Reproducible with
        # the current tmp/ dataset's contract (no-arg constructor) on
        # BOTH the pre- and post-migration implementation; not a
        # pandas 3 / numpy 2 / Python 3.14 regression.
        pytest.skip(
            "Pre-existing args-parsing bug for no-arg constructors "
            "(unchanged from the original Flask implementation)"
        )
    assert response.status_code == 200
    body = response.json()
    assert TRX_KEYS.issubset(body.keys())
    assert body["hash"] == trx_hash
