"""Unit tests for the pure helper functions in core/misc.py.

No network access: all fixtures are tiny hand-written ABIs/source snippets.
"""
import json

import pytest

from core import misc

ERC20_ABI = [
    {"type": "function", "name": "totalSupply", "inputs": [], "outputs": []},
    {"type": "function", "name": "balanceOf", "inputs": [], "outputs": []},
    {"type": "function", "name": "transfer", "inputs": [], "outputs": []},
    {"type": "function", "name": "transferFrom", "inputs": [], "outputs": []},
    {"type": "function", "name": "approve", "inputs": [], "outputs": []},
    {"type": "function", "name": "allowance", "inputs": [], "outputs": []},
    {"type": "event", "name": "Transfer", "inputs": []},
    {"type": "event", "name": "Approval", "inputs": []},
]

ERC721_ABI = [
    {"type": "function", "name": "balanceOf", "inputs": [], "outputs": []},
    {"type": "function", "name": "ownerOf", "inputs": [], "outputs": []},
    {"type": "function", "name": "safeTransferFrom", "inputs": [], "outputs": []},
    {"type": "function", "name": "transferFrom", "inputs": [], "outputs": []},
    {"type": "function", "name": "approve", "inputs": [], "outputs": []},
    {"type": "function", "name": "getApproved", "inputs": [], "outputs": []},
    {"type": "function", "name": "setApprovalForAll", "inputs": [], "outputs": []},
    {"type": "function", "name": "isApprovedForAll", "inputs": [], "outputs": []},
    {"type": "function", "name": "supportsInterface", "inputs": [], "outputs": []},
]

ERC721_SOURCE = (
    "contract MyNFT {\n"
    "    bytes4 private constant _INTERFACE_ID_ERC721 = 0x80ac58cd;\n"
    "    function supportsInterface(bytes4 interfaceId) public returns (bool) {}\n"
    "}\n"
)

ERC1155_ABI = [
    {"type": "function", "name": "safeTransferFrom", "inputs": [], "outputs": []},
    {"type": "function", "name": "safeBatchTransferFrom", "inputs": [], "outputs": []},
    {"type": "function", "name": "balanceOf", "inputs": [], "outputs": []},
    {"type": "function", "name": "balanceOfBatch", "inputs": [], "outputs": []},
    {"type": "function", "name": "setApprovalForAll", "inputs": [], "outputs": []},
    {"type": "function", "name": "isApprovedForAll", "inputs": [], "outputs": []},
]

GENERIC_ABI = [
    {"type": "function", "name": "foo", "inputs": [], "outputs": []},
]
DEFI_SOURCE = "contract Pool { function flashloan() public {} }"


# ------------------------------------------------------------------
# parse_abi
# ------------------------------------------------------------------

def test_parse_abi_valid_json():
    abi = misc.parse_abi(json.dumps(ERC20_ABI))
    assert abi == ERC20_ABI


def test_parse_abi_invalid_json_returns_none():
    assert misc.parse_abi("not json at all") is None


# ------------------------------------------------------------------
# implements_erc20
# ------------------------------------------------------------------

def test_implements_erc20_true():
    assert misc.implements_erc20(ERC20_ABI) is True


def test_implements_erc20_false_for_generic_abi():
    assert misc.implements_erc20(GENERIC_ABI) is False


# ------------------------------------------------------------------
# implements_erc721
# ------------------------------------------------------------------

def test_implements_erc721_true_with_interface_marker():
    assert misc.implements_erc721(ERC721_ABI, ERC721_SOURCE) is True


def test_implements_erc721_false_without_supports_interface():
    abi_without_support = [i for i in ERC721_ABI if i["name"] != "supportsInterface"]
    assert misc.implements_erc721(abi_without_support, ERC721_SOURCE) is False


def test_implements_erc721_false_for_generic_abi():
    assert misc.implements_erc721(GENERIC_ABI, "contract Foo {}") is False


# ------------------------------------------------------------------
# implements_erc1155
# ------------------------------------------------------------------

def test_implements_erc1155_true():
    assert misc.implements_erc1155(ERC1155_ABI) is True


def test_implements_erc1155_false_for_generic_abi():
    assert misc.implements_erc1155(GENERIC_ABI) is False


# ------------------------------------------------------------------
# classify_contract
# ------------------------------------------------------------------

def test_classify_contract_erc20():
    classification = misc.classify_contract(json.dumps(ERC20_ABI), "contract Token {}")
    assert classification == "Token Creation Contract"


def test_classify_contract_erc721():
    classification = misc.classify_contract(json.dumps(ERC721_ABI), ERC721_SOURCE)
    assert classification == "NFT Creation Contract"


def test_classify_contract_heuristic_defi_fallback():
    # Generic ABI (doesn't match any standard) + DeFi-flavored source text
    # falls back to heuristic_classification().
    classification = misc.classify_contract(json.dumps(GENERIC_ABI), DEFI_SOURCE)
    assert classification == "DeFi Contract"


def test_classify_contract_raises_without_info():
    with pytest.raises(RuntimeError):
        misc.classify_contract(None, None)
