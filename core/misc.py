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

    # Comprobamos si existe la función supportsInterface
    supports_interface_present = any(
        (f.get("name") == "supportsInterface" and f.get("type") == "function") 
        for f in abi
    )

    if not supports_interface_present:
        # Aunque no tenga supportsInterface, podría ser un ERC-721 incompleto.
        # Si queremos ser estrictos, la ausencia de supportsInterface 
        # indica que no cumple con ERC-165, y por ende no es un ERC-721 completo.
        return False
    else:
        # Si supportsInterface está presente, intentemos detectar si responde 
        # apropiadamente a 0x80ac58cd. Como no podemos ejecutar el contrato, 
        # buscaremos en el código fuente patrones que indiquen su soporte.

        sc_lower = source_code.lower()
        # Patrón simple: buscar el literal '0x80ac58cd' en el código.
        # También podríamos buscar patrones como:
        # `bytes4 private constant _INTERFACE_ID_ERC721 = 0x80ac58cd;`
        # o chequeos condicionales que devuelvan true cuando se llama a supportsInterface(0x80ac58cd).
        # Esto sigue siendo una heurística.
        if "0x80ac58cd" in sc_lower:
            # Es un buen indicador, muchos contratos declaran esta constante.
            # También podemos buscar líneas típicas: interfaceId == 0x80ac58cd
            # o retornos directos. Por simplicidad, si encontramos la constante,
            # asumimos cumplimiento.
            return True
        else:
            # No encontramos la constante directamente. 
            # Muchos ERC-721 usan OpenZeppelin, que define:
            # `bytes4 private constant _INTERFACE_ID_ERC721 = 0x80ac58cd;`
            # Si no la encontramos, es posible que el contrato la calcule de otra forma, 
            # o sea ERC-721 sin declaración explícita (raro pero posible).
            # Como segunda heurística, busquemos la interfaz ERC165 y una implementación genérica de supportsInterface.
            # Esto es muy débil, pero sirve como ejemplo.
            
            # Buscamos "supportsInterface" y "returns (bool)" en el mismo contexto:
            if "supportsinterface(" in sc_lower and "returns (bool)" in sc_lower:
                # Si llegamos aquí, no podemos estar seguros. 
                # Dado que tiene todas las funciones y soporta supportsInterface,
                # asumamos que es ERC-721.
                return True
            else:
                # No hay suficientes indicios de que soporte el interfaceId ERC-721.
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
    
    # Patrones de gestión/transacción de tokens (sin ser creadores)
    # Si vemos "transferFrom" pero no se cumplen las condiciones de ERC-20/721/1155
    # podría ser un contrato que interactúa con tokens externos.
    # Esta detección es débil, solo un ejemplo:
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
        classification = "Token Creation Contract (ERC-20)"
    elif implements_erc721(abi, source):
        classification = "Token Creation Contract (ERC-721)"
    elif implements_erc1155(abi):
        classification = "Token Creation Contract (ERC-1155)"
    else:
        classification = heuristic_classification(source)

    return classification
