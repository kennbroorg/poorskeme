#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from bs4 import BeautifulSoup
import cloudscraper
import logging
import requests
import pyround

# create a logger object.
logger = logging.getLogger(__name__)

__author__ = "KennBro"
__copyright__ = "Copyright 2023, Personal Research"
__credits__ = ["KennBro"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "KennBro"
__email__ = "kennbro <at> protonmail <dot> com"
__status__ = "Development"


def get_balance(chain_id, native, explorer, address, key):
    
    try:
        url_home = f"{explorer}/address/{address}"

        # Home
        scraper = cloudscraper.create_scraper(delay=10, disableCloudflareV1=True)
        r_home = scraper.get(url_home)

        html_doc = BeautifulSoup(r_home.content, "html.parser")
        div_card_body_container = html_doc.find_all('div', class_='card-body d-flex flex-column gap-5')
        balance_container = div_card_body_container[0].find_all('div')

        # Balances
        balances = []
        balance_tk = balance_container[1].text.split()[2]
        balances.append(f"Balance : {balance_tk} {native}")

        token_list = div_card_body_container[0].find_all('li', class_='nav-item list-custom-ERC20')
        for i in token_list:
            balances.append(i.text)
    except Exception:
        url = f'https://api.etherscan.io/v2/api?chainid={chain_id}&module=account&action=balance&address={address}&tag=latest' + \
            f'&apikey={key}' 
        response = requests.get(url).json()
        if (response["status"] == '1'):
            balance = int(response['result']) / 1e+18
        else:
            balance = "Indefined"

        balances = [f'Balance : {balance:8f} {native}']

    return balances


def parse_abi(abi_str):
    """
    Parsea la ABI del contrato (que viene como string JSON).
    """
    import json
    try:
        abi = json.loads(abi_str)
        return abi
    except:
        return None


def implements_erc20(abi):
    # ERC-20 essential functions
    required_functions = {"totalSupply", "balanceOf", "transfer", "allowance", "approve", "transferFrom"}
    contract_functions = {f["name"] for f in abi if f.get("type") == "function"}
    return required_functions.issubset(contract_functions)


def implements_erc721(abi, source_code):
    # ERC-721 essential functions
    required_functions = {"balanceOf", "ownerOf", "safeTransferFrom", "transferFrom", "approve", "getApproved", "setApprovalForAll", "isApprovedForAll"}
    contract_functions = {f["name"] for f in abi if f.get("type") == "function"}

    if not required_functions.issubset(contract_functions):
        return False

    # The function supportsInterface is checked for existence
    supports_interface_present = any(
        (f.get("name") == "supportsInterface" and f.get("type") == "function") 
        for f in abi
    )

    if not supports_interface_present:
        # Even if it has no supportsInterface, it could be an incomplete ERC-721.
        # If we want to be strict, the absence of supportsInterface 
        # indicates that it is not ERC-165 compliant, and therefore not a complete ERC-721.
        return False
    else:
        # If supportsInterface is present, let's try to detect if it responds 
        # appropriately to 0x80ac58cd. Since we cannot execute the contract, 
        # we will search the source code for patterns that indicate its support.

        sc_lower = source_code.lower()
        # Simple pattern: look for the literal '0x80ac58cd' in the code.
        # We could also look for patterns like:
        # `bytes4 private constant _INTERFACE_ID_ERC721 = 0x80ac58cd;`
        # or conditional checks that return true when supportsInterface(0x80ac58cd) is called.
        # This is still a heuristic.
        if "0x80ac58cd" in sc_lower:
            # This is a good indicator, many contracts declare this constant.
            # We can also look for typical lines: interfaceId == 0x80ac58cd
            # or direct returns. For simplicity, if we find the constant,
            # we assume compliance.
            return True
        else:
            # Constant is not found directly. 
            # Many ERC-721s use OpenZeppelin, which defines:
            # `bytes4 private constant _INTERFACE_ID_ERC721 = 0x80ac58cd;`
            # If it is not found, it is possible that the contract calculates it in another way, 
            # or ERC-721 without explicit declaration (rare but possible).
            # As a second heuristic, the ERC165 interface and a generic implementation of supportsInterface are looked for.
            # This is very weak, but serves as an example.
            
            # We search for “supportsInterface” and “returns (bool)” in the same context:
            if "supportsinterface(" in sc_lower and "returns (bool)" in sc_lower:
                # If you get here, you can't be sure. 
                # Since it is full-featured and supportsInterface,
                # it is assumed to be ERC-721.
                return True
            else:
                # There is insufficient evidence that it supports the ERC-721 interfaceId.
                return False


def implements_erc1155(abi):
    # ERC-1155 essential functions
    required_functions = {"safeTransferFrom", "safeBatchTransferFrom", "balanceOf", "balanceOfBatch", "setApprovalForAll", "isApprovedForAll"}
    contract_functions = {f["name"] for f in abi if f.get("type") == "function"}
    if required_functions.issubset(contract_functions):
        return True
    return False


def heuristic_classification(source_code):
    # Heuristic classification by text patterns
    sc_lower = source_code.lower()

    # DeFi
    is_defi = any(k in sc_lower for k in ["flashloan", "borrow(", "lend(", "yield", "interest"])
    # DAO
    is_dao = any(k in sc_lower for k in ["proposal", "vote(", "quorum", "governance"])
    # Identity / Reputation
    is_identity = any(k in sc_lower for k in ["identity", "reputation", "attest", "erc-1820", "erc-725", "claim"])
    # Auctions / Markets
    is_auction = any(k in sc_lower for k in ["auction", "bid(", "buy(", "sell(", "listing"])
    
    # Token management/transaction patterns (non-creator)
    # If “transferFrom” is seen but ERC-20/721/1155 conditions are not met.
    # could be a contract interacting with external tokens.
    # This detection is weak, just an example:
    is_token_manager = "transferfrom(" in sc_lower

    if is_defi:
        classification = "DeFi Contract"
    elif is_dao:
        classification = "DAO Contract"
    elif is_identity:
        classification = "Identity/Reputation Contract"
    elif is_auction:
        classification = "Auctions/Markets Contract"
    elif is_token_manager:
        classification = "Token Management/Transaction Contract (non-creator)"
    else: 
        classification = "Unclassified or generic contract"

    return classification


def classify_contract(abi_str, source):
    # TODO:Search a better way to classify contract type
    if abi_str is None or source is None:
        raise RuntimeError("Not enough information could be obtained from the contract" )
    
    abi = parse_abi(abi_str)
    if abi is None:  # NOTE: Not ABI information
        classification = heuristic_classification(source)
    # Standard classification
    elif implements_erc20(abi):
        classification = "Token Creation Contract"
    elif implements_erc721(abi, source):
        classification = "NFT Creation Contract"
    elif implements_erc1155(abi):
        classification = "Multitoken Creation Contract"
    else:
        classification = heuristic_classification(source)

    return classification
