#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import json
import re
import numpy as np
import pandas as pd
import time
import os.path
from pandas.core.series import unpack_1tuple
import requests
import sqlite3
# import asyncio
# import aiohttp
from bs4 import BeautifulSoup
import cloudscraper
import pyround
import datetime

# from termcolor import colored
import logging
import coloredlogs

from web3_input_decoder import InputDecoder # , decode_constructor

from core import eth  # TODO: Remove
from core import bsc  # TODO: Remove
from core import misc


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


def validate_blockchain(chain_id):
    """Validate Blockchains"""
    bc = {
      "1": {
        "explorer": "Etherscan",
        "explorer_name": "https://etherscan.io/",
        "chainId": 1,
        "name": "Ethereum Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "Ether (ETH)"
      },
      "56": {
        "explorer": "BscScan",
        "explorer_name": "https://bscscan.com/",
        "chainId": 56,
        "name": "Binance Smart Chain Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "BNB"
      },
      "137": {
        "explorer": "PolygonScan",
        "chainId": 137,
        "name": "Polygon Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "MATIC"
      },
      "1101": {
        "explorer": "zkEVM PolygonScan",
        "chainId": 1101,
        "name": "Polygon zkEVM Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "Ether (ETH)"
      },
      "8453": {
        "explorer": "BaseScan",
        "explorer_name": "https://basescan.org",
        "chainId": 8453,
        "name": "Base Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "Ether (ETH)"
      },
      "42161": {
        "explorer": "Arbiscan",
        "explorer_name": "https://basescan.org/",
        "chainId": 42161,
        "name": "Arbitrum One",
        "networkType": "mainnet",
        "cryptocurrency": "Ether (ETH)"
      },
      "42170": {
        "explorer": "Nova Arbiscan",
        "chainId": 42170,
        "name": "Arbitrum Nova",
        "networkType": "mainnet",
        "cryptocurrency": "Ether (ETH)"
      },
      "59144": {
        "explorer": "LineaScan",
        "chainId": 59144,
        "name": "Consensys Linea Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "Ether (ETH)"
      },
      "250": {
        "explorer": "FTMScan",
        "chainId": 250,
        "name": "Fantom Opera Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "FTM"
      },
      "81457": {
        "explorer": "BlastScan",
        "chainId": 81457,
        "name": "Blast Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "BLAST"
      },
      "10": {
        "explorer": "Optimistic Etherscan",
        "chainId": 10,
        "name": "Optimism Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "Ether (ETH)"
      },
      "43114": {
        "explorer": "SnowScan",
        "chainId": 43114,
        "name": "Avalanche C-Chain Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "AVAX"
      },
      "199": {
        "explorer": "BTTCScan",
        "chainId": 199,
        "name": "BitTorrent Chain Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "BTT"
      },
      "42220": {
        "explorer": "CeloScan",
        "chainId": 42220,
        "name": "Celo Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "CELO"
      },
      "25": {
        "explorer": "Cronoscan",
        "chainId": 25,
        "name": "Cronos Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "CRO"
      },
      "252": {
        "explorer": "Fraxscan",
        "chainId": 252,
        "name": "Frax Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "FRAX"
      },
      "100": {
        "explorer": "GnosisScan",
        "chainId": 100,
        "name": "Gnosis Chain",
        "networkType": "mainnet",
        "cryptocurrency": "xDAI"
      },
      "255": {
        "explorer": "KromaScan",
        "chainId": 255,
        "name": "Kroma Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "Ether (ETH)"
      },
      "5000": {
        "explorer": "Mantlescan",
        "chainId": 5000,
        "name": "Mantle Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "Ether (ETH)"
      },
      "1284": {
        "explorer": "Moonbeam Moonscan",
        "chainId": 1284,
        "name": "Moonbeam Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "GLMR"
      },
      "1285": {
        "explorer": "Moonriver Moonscan",
        "chainId": 1285,
        "name": "Moonriver Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "MOVR"
      },
      "204": {
        "explorer": "opBNB BscScan",
        "chainId": 204,
        "name": "opBNB Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "BNB"
      },
      "534352": {
        "explorer": "ScrollScan",
        "chainId": 534352,
        "name": "Scroll Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "Ether (ETH)"
      },
      "167000": {
        "explorer": "Taikoscan",
        "chainId": 167000,
        "name": "Taiko Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "Ether (ETH)"
      },
      "1111": {
        "explorer": "WemixScan",
        "chainId": 1111,
        "name": "WEMIX Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "WEMIX"
      },
      "324": {
        "explorer": "zkSync Era",
        "chainId": 324,
        "name": "zkSync Era Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "Ether (ETH)"
      },
      "660279": {
        "explorer": "Xaiscan",
        "chainId": 660279,
        "name": "Xai Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "XAI"
      },
      "33139": {
        "explorer": "Apescan",
        "chainId": 33139,
        "name": "ApeChain Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "APE"
      },
      "50104": {
        "explorer": "Sophon",
        "chainId": 50104,
        "name": "Sophon Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "SPN"
      },
      "480": {
        "explorer": "WorldScan",
        "chainId": 480,
        "name": "Worldcoin Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "WLD"
      },
      "50": {
        "explorer": "XDCscan",
        "chainId": 50,
        "name": "XDC Network Mainnet",
        "networkType": "mainnet",
        "cryptocurrency": "XDC"
      }
    }

    implemented_blockchain = [1, 56, 8453]

    if (int(chain_id) in implemented_blockchain):
        return True, bc[str(chain_id)]['name'], bc[str(chain_id)]['cryptocurrency'], bc[str(chain_id)]['explorer_name']
    else: 
        return False, "", "", ""


def is_token_contract(abi_json):
    abi = json.loads(abi_json)
    
    # Functions and events
    functions = [item for item in abi if item.get('type') == 'function']
    events = [item for item in abi if item.get('type') == 'event']

    function_names = {f['name'] for f in functions}
    event_names = {e['name'] for e in events}

    # Check the existence of ERC-20 functions
    erc20_functions = {"totalSupply", "balanceOf", "transfer", "transferFrom", "approve", "allowance"}
    if erc20_functions.issubset(function_names):
        # Check standard envents of ERC-20
        if "Transfer" in event_names and "Approval" in event_names:
            return True, "ERC-20"

    # Check ERC-721
    erc721_functions = {"balanceOf", "ownerOf", "transferFrom", "approve", "getApproved", "setApprovalForAll", "isApprovedForAll"}
    if erc721_functions.issubset(function_names):
        if "Transfer" in event_names and "Approval" in event_names:
            return True, "ERC-721"
    
    return False, None


def data_db_collect_event(chain_id, contract_address, key, filedb, block_from=0, block_to=99999999):

    base_url = "https://api.etherscan.io/v2/api"
    offset = 10000
    timeout = False

    try:
        os.remove(filedb)
    except Exception:
        pass
    filename = os.path.basename(filedb)
    message = f"<strong class='normal'>DB</strong> - Creating db {filedb}"
    # message = f"<strong class='normal'>DB</strong> - Creating db {filename}"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n" 

    connection = sqlite3.connect(filedb)
    cursor = connection.cursor()

    # Internal tagging
    internal_tagging = []
    sql_create_tagging_table = """CREATE TABLE IF NOT EXISTS t_tagging (
                                   wallet text NOT NULL,
                                   tag text NOT NULL
                                 );"""
    cursor.execute(sql_create_tagging_table)

    logger.info("=====================================================")

    message = "<strong class='normal'>COLLECT</strong> - Collecting Contract data..."
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    logger.info("=====================================================")
    message = "<strong class='normal'>CREATE</strong> - Creating Table t_contract"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    sql_create_contract_table = """CREATE TABLE IF NOT EXISTS t_contract (
                                   contract text NOT NULL,
                                   chain_id number NOT NULL,
                                   blockchain text NOT NULL,
                                   native text NOT NULL,
                                   explorer text NOT NULL,
                                   block_from text NOT NULL,
                                   block_to text NOT NULL,
                                   first_block text NOT NULL,
                                   transaction_creation text NOT NULL,
                                   date_creation datetime NOT NULL,
                                   creator text NOT NULL
                                 );"""
    cursor.execute(sql_create_contract_table)

    message = "<strong class='normal'>GET</strong> - Getting first block"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    url = f'{base_url}?chainid={chain_id}&module=account&action=txlist&address={contract_address}&startblock=0&endblock=99999999' + \
        f'&page=1&offset=1&sort=asc&apikey={key}'
    response = requests.get(url)

    # NOTE: Validate API key
    if (response.json()['message'] == "NOTOK"):
        os.remove(filedb)
        message = "<strong class='error'>ERROR</strong> - Invalid API key"
        logger.error(message.replace("<strong class='error'>", "").replace("</strong>", ""))
        data = json.dumps({"msg": f"{message}", "end": True, "error": True, "content": {}})
        yield f"data:{data}\n\n"
        raise RuntimeError(message.replace("<strong class='error'>", "").replace("</strong>", ""))
        
    # NOTE: Validate blockchain
    implemented, blockchain, native, explorer = validate_blockchain(chain_id)
    if not implemented:
        os.remove(filedb)
        message = "<strong class='error'>ERROR</strong> - Blockchain not implemented"
        logger.error(message.replace("<strong class='error'>", "").replace("</strong>", ""))
        data = json.dumps({"msg": f"{message}", "end": True, "error": True, "content": {}})
        yield f"data:{data}\n\n"
        raise RuntimeError(message.replace("<strong class='error'>", "").replace("</strong>", ""))

    first_block = response.json()['result'][0]

    if (block_from == 0):
        block_from = int(first_block['blockNumber'])
    contract_creator = first_block['from']

    message = "<strong class='normal'>STORE</strong> - Storing first block"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    cursor.execute("""INSERT INTO t_contract VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
        (contract_address, chain_id, blockchain, native, explorer, block_from, block_to, first_block['blockNumber'], 
        first_block['hash'], first_block['timeStamp'], first_block['from']))

    connection.commit()
    # tag
    internal_tagging.append({"wallet": contract_address, "tag": "Contract Analysed"})
    internal_tagging.append({"wallet": first_block['from'], "tag": "Contract Creator"})

    # Source code
    message = "<strong class='normal'>CREATE</strong> - Creating Table t_source_abi"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    sql_create_source_abi_table = """CREATE TABLE IF NOT EXISTS t_source_abi (
                                     SourceCode text NOT NULL,
                                     ABI text NOT NULL,
                                     ContractName text NOT NULL,
                                     CompilerVersion text NOT NULL,
                                     OptimizationUsed text NOT NULL,
                                     Runs text NOT NULL,
                                     ConstructorArguments text NOT NULL,
                                     EVMVersion text NOT NULL,
                                     Library text NOT NULL,
                                     LicenseType text NOT NULL,
                                     Proxy text NOT NULL,
                                     Implementation text NOT NULL,
                                     SwarmSource text NOT NULL
                                   );"""
    cursor.execute(sql_create_source_abi_table)

    message = "<strong class='normal'>COLLECT</strong> - Getting source code and ABI"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    url = f'{base_url}?chainid={chain_id}&module=contract&action=getsourcecode&address={contract_address}&apikey={key}'
    response = requests.get(url).json()
    json_obj_source_code = response['result'][0]

    source_code = ""
    if response["status"] == "1" and response["result"]:
        # Concat sourceCode
        for contract_data in response["result"]:
            source_code_part = contract_data.get("SourceCode", "")
            # A veces el código viene envuelto en { ... } para contratos múltiples
            # Intentamos limpiar si es el caso:
            if source_code_part.startswith("{") and source_code_part.endswith("}"):
                # Puede contener JSON u otro formato. Lo simplificamos:
                # Este es un caso complejo, para simplificar vamos a concatenar tal cual
                source_code += source_code_part
            else:
                source_code += source_code_part

    # NOTE: Validate if this is a contract
    if (source_code == ""):
        os.remove(filedb)
        message = "<strong class='error'>ERROR</strong> - The address is not a contract"
        logger.error(message.replace("<strong class='error'>", "").replace("</strong>", ""))
        data = json.dumps({"msg": f"{message}", "end": True, "error": True, "content": {}})
        yield f"data:{data}\n\n"
        raise RuntimeError(message.replace("<strong class='error'>", "").replace("</strong>", ""))

    message = "<strong class='normal'>STORE</strong> - Storing source code and ABI"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    cursor.execute("""INSERT INTO t_source_abi VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
        (source_code,
         json_obj_source_code['ABI'],
         json_obj_source_code['ContractName'],
         json_obj_source_code['CompilerVersion'],
         json_obj_source_code['OptimizationUsed'],
         json_obj_source_code['Runs'],
         json_obj_source_code['ConstructorArguments'],
         json_obj_source_code['EVMVersion'],
         json_obj_source_code['Library'],
         json_obj_source_code['LicenseType'],
         json_obj_source_code['Proxy'],
         json_obj_source_code['Implementation'],
         json_obj_source_code['SwarmSource']))

    connection.commit()
    # connection.close()

    # TODO: Implement in future
    # get_circulating_supply_by_contract_address - Get circulating supply of token by its contract address
    # async with BscScan(key) as client:
    #     json_result = await client.get_circulating_supply_by_contract_address(
    #             contract_address=contract_address,
    #         )
    # json_str_circ_supply = json.dumps(json_result)
    # json_obj_circ_supply = json.loads(json_str_circ_supply)

    # TODO: Implement in future
    # get_total_supply_by_contract_address - Get circulating supply of token by its contract address
    # async with BscScan(key) as client:
    #     json_result = await client.get_total_supply_by_contract_address(
    #             contract_address=contract_address,
    #         )
    # json_str_total_supply = json.dumps(json_result)
    # json_obj_total_supply = json.loads(json_str_total_supply)

    logger.info(" ")
    logger.info("=====================================================")

    message = "<strong class='normal'>COLLECT</strong> - Collecting Contract transactions..."
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    logger.info("=====================================================")
    message = "<strong class='normal'>CREATE</strong> - Creating Table t_transactions"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    sql_create_transactions_table = """CREATE TABLE IF NOT EXISTS t_transactions (
                                       blockNumber integer NOT NULL,
                                       timeStamp datetime NOT NULL,
                                       hash text NOT NULL,
                                       nonce integer NOT NULL,
                                       blockHash text NOT NULL,
                                       transactionIndex integer NOT NULL,
                                       `from` text NOT NULL,
                                       `to` text NOT NULL,
                                       value integer NOT NULL,
                                       gas integer NOT NULL,
                                       gasPrice integer NOT NULL,
                                       isError integer NOT NULL,
                                       txreceipt_status integer NOT NULL,
                                       input text NOT NULL,
                                       contractAddress text NOT NULL,
                                       cumulativeGasUsed integer NOT NULL,
                                       gasUsed integer NOT NULL,
                                       confirmations integer NOT NULL,
                                       methodId text NOT NULL,
                                       functionName text NOT NULL
                                 );"""
    connection.execute(sql_create_transactions_table)

    # INFO: Get Transactions
    message = "<strong class='normal'>GET</strong> - Getting Contract transactions"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    tic = time.perf_counter()

    json_transactions = []
    current_block = block_from
    end_block = block_to

    while int(current_block) < int(end_block):
        params = {
            "chainid": chain_id, "module": "account", "action": "txlist", "address": contract_address, "startblock": current_block,
            "endblock": end_block, "page": 1, "offset": offset, "sort": "asc", "apikey": key,
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["status"] != "1":
            if data["message"] == "No transactions found":
                break
            elif "Timeout" in data['message']:
                message = "<strong class='normal'>TIMEOUT</strong> -   Waiting 5 seg"
                logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
                data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
                yield f"data:{data}\n\n"
                time.sleep(5)
                timeout = True
            else:
                message = f"<strong class='error'>ERROR</strong> - {data['message']}"
                logger.error(message.replace("<strong class='error'>", "").replace("</strong>", ""))
                data = json.dumps({"msg": f"{message}", "end": True, "error": True, "content": {}})
                yield f"data:{data}\n\n"
                raise RuntimeError(f"Error fetching data: {data['message']} - {data['result']}")

        if (not timeout):
            data_batch = data["result"]
            json_transactions.extend(data_batch)

            message = f"<strong class='normal'>GET</strong> -   Get {len(data_batch)} records"
            logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
            data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
            yield f"data:{data}\n\n"
            time.sleep(1)

            if len(data_batch) < offset:
                break

            current_block = int(data_batch[-1]["blockNumber"]) + 1
        timeout = False

    # INFO: Store Transactions
    message = "<strong class='normal'>STORE</strong> - Storing Contract transactions"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    if json_transactions != []:
        df_trx_store = pd.DataFrame(json_transactions)
        # df_trx_store["blockChain"] = chain_id  # TODO: Change chain_id by blockchain name
        # df_trx_store.to_sql("t_transactions", connection, if_exists="append", index=False, method=insert_with_ignore)
        df_trx_store.to_sql("t_transactions", connection, if_exists="append", index=False)
    toc = time.perf_counter()

    message = f"<strong class='normal'>STORE</strong> - {len(json_transactions)} Transactions...<strong class='normal'>{toc - tic:0.4f}</strong> seconds"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": message, "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    logger.info(" ")
    logger.info("=====================================================")

    message = "<strong class='normal'>COLLECT</strong> - Collecting Contract transfers... (as contract)"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    logger.info("=====================================================")
    message = "<strong class='normal'>CREATE</strong> - Creating Table t_transfers_as_contract"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    sql_create_transfers_table = """CREATE TABLE IF NOT EXISTS t_transfers_as_contract (
                                       blockNumber integer NOT NULL,
                                       timeStamp datetime NOT NULL,
                                       hash text NOT NULL,
                                       nonce integer NOT NULL,
                                       blockHash text NOT NULL,
                                       `from` text NOT NULL,
                                       contractAddress text NOT NULL,
                                       `to` text NOT NULL,
                                       value integer NOT NULL,
                                       tokenName text NOT NULL,
                                       tokenSymbol text NOT NULL,
                                       tokenDecimal integer NOT NULL,
                                       transactionIndex integer NOT NULL,
                                       gas integer NOT NULL,
                                       gasPrice integer NOT NULL,
                                       gasUsed integer NOT NULL,
                                       cumulativeGasUsed integer NOT NULL,
                                       input text NOT NULL,
                                       confirmations integer NOT NULL
                                 );"""
    connection.execute(sql_create_transfers_table)

    # INFO: Get Transfers
    message = "<strong class='normal'>GET</strong> - Getting Contract transfers as contract"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    tic = time.perf_counter()

    json_transfers = []
    current_block = block_from
    end_block = block_to

    while int(current_block) < int(end_block):
        params = {
            # "chainid": chain_id, "module": "account", "action": "tokentx", "address": contract_address, "startblock": current_block,
            "chainid": chain_id, "module": "account", "action": "tokentx", "contractaddress": contract_address, "startblock": current_block,
            "endblock": end_block, "page": 1, "offset": offset, "sort": "asc", "apikey": key,
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["status"] != "1":
            # TODO: Warning message to frontend
            if data["message"] == "No transactions found":
                break
            elif "Timeout" in data['message']:
                message = "<strong class='normal'>TIMEOUT</strong> -   Waiting 5 seg"
                logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
                data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
                yield f"data:{data}\n\n"
                time.sleep(5)
                timeout = True
            else:
                message = f"<strong class='error'>ERROR</strong> - {data['message']}"
                logger.error(message.replace("<strong class='error'>", "").replace("</strong>", ""))
                data = json.dumps({"msg": f"{message}", "end": True, "error": True, "content": {}})
                yield f"data:{data}\n\n"
                raise RuntimeError(f"Error fetching data: {data['message']} - {data['result']}")

        if (not timeout):
            timeout = False
            data_batch = data["result"]
            json_transfers.extend(data_batch)

            message = f"<strong class='normal'>GET</strong> -   Get {len(data_batch)} records"
            logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
            data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
            yield f"data:{data}\n\n"
            time.sleep(1)

            if len(data_batch) < offset:
                break

            current_block = int(data_batch[-1]["blockNumber"]) + 1
        timeout = False

    # INFO: Store Transfers
    message = "<strong class='normal'>STORE</strong> - Storing Contract transfers as contract"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    if json_transfers != []:
        df_tra_store = pd.DataFrame(json_transfers)
        df_tra_store.to_sql("t_transfers_as_contract", connection, if_exists="append", index=False)
    toc = time.perf_counter()

    message = f"<strong class='normal'>STORE</strong> - {len(json_transfers)} token transfers as contract...<strong class='normal'>{toc - tic:0.4f}</strong> seconds"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": message, "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    logger.info(" ")
    logger.info("=====================================================")

    message = "<strong class='normal'>COLLECT</strong> - Collecting Contract transfers... (as wallet)"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    logger.info("=====================================================")
    message = "<strong class='normal'>CREATE</strong> - Creating Table t_transfers_as_wallet"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    sql_create_transfers_table = """CREATE TABLE IF NOT EXISTS t_transfers_as_wallet (
                                       blockNumber integer NOT NULL,
                                       timeStamp datetime NOT NULL,
                                       hash text NOT NULL,
                                       nonce integer NOT NULL,
                                       blockHash text NOT NULL,
                                       `from` text NOT NULL,
                                       contractAddress text NOT NULL,
                                       `to` text NOT NULL,
                                       value integer NOT NULL,
                                       tokenName text NOT NULL,
                                       tokenSymbol text NOT NULL,
                                       tokenDecimal integer NOT NULL,
                                       transactionIndex integer NOT NULL,
                                       gas integer NOT NULL,
                                       gasPrice integer NOT NULL,
                                       gasUsed integer NOT NULL,
                                       cumulativeGasUsed integer NOT NULL,
                                       input text NOT NULL,
                                       confirmations integer NOT NULL
                                 );"""
    connection.execute(sql_create_transfers_table)

    # INFO: Get Transfers
    message = "<strong class='normal'>GET</strong> - Getting Contract transfers as wallet"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    tic = time.perf_counter()

    json_transfers = []
    current_block = block_from
    end_block = block_to

    while int(current_block) < int(end_block):
        params = {
            # "chainid": chain_id, "module": "account", "action": "tokentx", "address": contract_address, "startblock": current_block,
            "chainid": chain_id, "module": "account", "action": "tokentx", "address": contract_address, "startblock": current_block,
            "endblock": end_block, "page": 1, "offset": offset, "sort": "asc", "apikey": key,
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["status"] != "1":
            # TODO: Warning message to frontend
            if data["message"] == "No transactions found":
                break
            elif "Timeout" in data['message']:
                message = "<strong class='normal'>TIMEOUT</strong> -   Waiting 5 seg"
                logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
                data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
                yield f"data:{data}\n\n"
                time.sleep(5)
                timeout = True
            else:
                message = f"<strong class='error'>ERROR</strong> - {data['message']}"
                logger.error(message.replace("<strong class='error'>", "").replace("</strong>", ""))
                data = json.dumps({"msg": f"{message}", "end": True, "error": True, "content": {}})
                yield f"data:{data}\n\n"
                raise RuntimeError(f"Error fetching data: {data['message']} - {data['result']}")

        if (not timeout):
            timeout = False
            data_batch = data["result"]
            json_transfers.extend(data_batch)

            message = f"<strong class='normal'>GET</strong> -   Get {len(data_batch)} records"
            logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
            data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
            yield f"data:{data}\n\n"
            time.sleep(1)

            if len(data_batch) < offset:
                break

            current_block = int(data_batch[-1]["blockNumber"]) + 1
        timeout = False

    # INFO: Store Transfers
    message = "<strong class='normal'>STORE</strong> - Storing Contract transfers as wallet"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    if json_transfers != []:
        df_traw_store = pd.DataFrame(json_transfers)
        df_traw_store.to_sql("t_transfers_as_wallet", connection, if_exists="append", index=False)
    toc = time.perf_counter()

    message = f"<strong class='normal'>STORE</strong> - {len(json_transfers)} token transfers as wallet...<strong class='normal'>{toc - tic:0.4f}</strong> seconds"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": message, "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    logger.info(" ")
    logger.info("=====================================================")

    message = "<strong class='normal'>COLLECT</strong> - Collecting Contract nft... (as contract)"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    logger.info("=====================================================")
    message = "<strong class='normal'>CREATE</strong> - Creating Table t_nft_as_contract"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    sql_create_transfers_table = """CREATE TABLE IF NOT EXISTS t_nft_as_contract (
                                       blockNumber integer NOT NULL,
                                       timeStamp datetime NOT NULL,
                                       hash text NOT NULL,
                                       nonce integer NOT NULL,
                                       blockHash text NOT NULL,
                                       `from` text NOT NULL,
                                       contractAddress text NOT NULL,
                                       `to` text NOT NULL,
                                       tokenID integer NOT NULL,
                                       tokenName text NOT NULL,
                                       tokenSymbol text NOT NULL,
                                       tokenDecimal integer NOT NULL,
                                       transactionIndex integer NOT NULL,
                                       gas integer NOT NULL,
                                       gasPrice integer NOT NULL,
                                       gasUsed integer NOT NULL,
                                       cumulativeGasUsed integer NOT NULL,
                                       input text NOT NULL,
                                       confirmations integer NOT NULL
                                 );"""
    connection.execute(sql_create_transfers_table)

    # INFO: Get NFTs as contract
    message = "<strong class='normal'>GET</strong> - Getting Contract nft as contract"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    tic = time.perf_counter()

    json_transfers = []
    current_block = block_from
    end_block = block_to

    while int(current_block) < int(end_block):
        params = {
            # "chainid": chain_id, "module": "account", "action": "tokentx", "address": contract_address, "startblock": current_block,
            "chainid": chain_id, "module": "account", "action": "tokennfttx", "contractaddress": contract_address, "startblock": current_block,
            "endblock": end_block, "page": 1, "offset": offset, "sort": "asc", "apikey": key,
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["status"] != "1":
            # TODO: Warning message to frontend
            if data["message"] == "No transactions found":
                break
            elif "Timeout" in data['message']:
                message = "<strong class='normal'>TIMEOUT</strong> -   Waiting 5 seg"
                logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
                data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
                yield f"data:{data}\n\n"
                time.sleep(5)
                timeout = True
            else:
                message = f"<strong class='error'>ERROR</strong> - {data['message']}"
                logger.error(message.replace("<strong class='error'>", "").replace("</strong>", ""))
                data = json.dumps({"msg": f"{message}", "end": True, "error": True, "content": {}})
                yield f"data:{data}\n\n"
                raise RuntimeError(f"Error fetching data: {data['message']} - {data['result']}")

        if (not timeout):
            timeout = False
            data_batch = data["result"]
            json_transfers.extend(data_batch)

            message = f"<strong class='normal'>GET</strong> -   Get {len(data_batch)} records"
            logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
            data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
            yield f"data:{data}\n\n"
            time.sleep(1)

            if len(data_batch) < offset:
                break

            current_block = int(data_batch[-1]["blockNumber"]) + 1
        timeout = False

    # INFO: Store NFTs as contract
    message = "<strong class='normal'>STORE</strong> - Storing Contract nft as contract"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    if json_transfers != []:
        df_traw_store = pd.DataFrame(json_transfers)
        df_traw_store.to_sql("t_nft_as_contract", connection, if_exists="append", index=False)
    toc = time.perf_counter()

    message = f"<strong class='normal'>STORE</strong> - {len(json_transfers)} NFTs transfers as contract...<strong class='normal'>{toc - tic:0.4f}</strong> seconds"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": message, "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    logger.info(" ")
    logger.info("=====================================================")

    message = "<strong class='normal'>COLLECT</strong> - Collecting Contract nft... (as wallet)"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    logger.info("=====================================================")
    message = "<strong class='normal'>CREATE</strong> - Creating Table t_nft_as_wallet"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    sql_create_transfers_table = """CREATE TABLE IF NOT EXISTS t_nft_as_wallet (
                                       blockNumber integer NOT NULL,
                                       timeStamp datetime NOT NULL,
                                       hash text NOT NULL,
                                       nonce integer NOT NULL,
                                       blockHash text NOT NULL,
                                       `from` text NOT NULL,
                                       contractAddress text NOT NULL,
                                       `to` text NOT NULL,
                                       tokenID integer NOT NULL,
                                       tokenName text NOT NULL,
                                       tokenSymbol text NOT NULL,
                                       tokenDecimal integer NOT NULL,
                                       transactionIndex integer NOT NULL,
                                       gas integer NOT NULL,
                                       gasPrice integer NOT NULL,
                                       gasUsed integer NOT NULL,
                                       cumulativeGasUsed integer NOT NULL,
                                       input text NOT NULL,
                                       confirmations integer NOT NULL
                                 );"""
    connection.execute(sql_create_transfers_table)

    # INFO: Get NFTs as wallet
    message = "<strong class='normal'>GET</strong> - Getting Contract nft as wallet"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    tic = time.perf_counter()

    json_transfers = []
    current_block = block_from
    end_block = block_to

    while int(current_block) < int(end_block):
        params = {
            # "chainid": chain_id, "module": "account", "action": "tokentx", "address": contract_address, "startblock": current_block,
            "chainid": chain_id, "module": "account", "action": "tokennfttx", "address": contract_address, "startblock": current_block,
            "endblock": end_block, "page": 1, "offset": offset, "sort": "asc", "apikey": key,
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["status"] != "1":
            # TODO: Warning message to frontend
            if data["message"] == "No transactions found":
                break
            elif "Timeout" in data['message']:
                message = "<strong class='normal'>TIMEOUT</strong> -   Waiting 5 seg"
                logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
                data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
                yield f"data:{data}\n\n"
                time.sleep(5)
                timeout = True
            else:
                message = f"<strong class='error'>ERROR</strong> - {data['message']}"
                logger.error(message.replace("<strong class='error'>", "").replace("</strong>", ""))
                data = json.dumps({"msg": f"{message}", "end": True, "error": True, "content": {}})
                yield f"data:{data}\n\n"
                raise RuntimeError(f"Error fetching data: {data['message']} - {data['result']}")

        if (not timeout):
            timeout = False
            data_batch = data["result"]
            json_transfers.extend(data_batch)

            message = f"<strong class='normal'>GET</strong> -   Get {len(data_batch)} records"
            logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
            data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
            yield f"data:{data}\n\n"
            time.sleep(1)

            if len(data_batch) < offset:
                break

            current_block = int(data_batch[-1]["blockNumber"]) + 1
        timeout = False

    # INFO: Store NFTs as wallet
    message = "<strong class='normal'>STORE</strong> - Storing Contract nft as wallet"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    if json_transfers != []:
        df_traw_store = pd.DataFrame(json_transfers)
        df_traw_store.to_sql("t_nft_as_wallet", connection, if_exists="append", index=False)
    toc = time.perf_counter()

    message = f"<strong class='normal'>STORE</strong> - {len(json_transfers)} NFTs transfers as wallet...<strong class='normal'>{toc - tic:0.4f}</strong> seconds"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": message, "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    logger.info(" ")
    logger.info("=====================================================")

    message = "<strong class='normal'>COLLECT</strong> - Collecting Contract multitoken... (as contract)"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    logger.info("=====================================================")
    message = "<strong class='normal'>CREATE</strong> - Creating Table t_multitoken_as_contract"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    sql_create_transfers_table = """CREATE TABLE IF NOT EXISTS t_multitoken_as_contract (
                                       blockNumber integer NOT NULL,
                                       timeStamp datetime NOT NULL,
                                       hash text NOT NULL,
                                       nonce integer NOT NULL,
                                       blockHash text NOT NULL,
                                       transactionIndex integer NOT NULL,
                                       gas integer NOT NULL,
                                       gasPrice integer NOT NULL,
                                       gasUsed integer NOT NULL,
                                       cumulativeGasUsed integer NOT NULL,
                                       input text NOT NULL,
                                       contractAddress text NOT NULL,
                                       `from` text NOT NULL,
                                       `to` text NOT NULL,
                                       tokenID integer NOT NULL,
                                       tokenValue integer NOT NULL,
                                       tokenName text NOT NULL,
                                       tokenSymbol text NOT NULL,
                                       confirmations integer NOT NULL
                                 );"""
    connection.execute(sql_create_transfers_table)

    # INFO: Get Multitoken as contract
    message = "<strong class='normal'>GET</strong> - Getting Contract multitoken as contract"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    tic = time.perf_counter()

    json_transfers = []
    current_block = block_from
    end_block = block_to

    while int(current_block) < int(end_block):
        params = {
            # "chainid": chain_id, "module": "account", "action": "tokentx", "address": contract_address, "startblock": current_block,
            "chainid": chain_id, "module": "account", "action": "token1155tx", "contractaddress": contract_address, "startblock": current_block,
            "endblock": end_block, "page": 1, "offset": offset, "sort": "asc", "apikey": key,
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["status"] != "1":
            # TODO: Warning message to frontend
            if data["message"] == "No transactions found":
                break
            elif "Timeout" in data['message']:
                message = "<strong class='normal'>TIMEOUT</strong> -   Waiting 5 seg"
                logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
                data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
                yield f"data:{data}\n\n"
                time.sleep(5)
                timeout = True
            else:
                message = f"<strong class='error'>ERROR</strong> - {data['message']}"
                logger.error(message.replace("<strong class='error'>", "").replace("</strong>", ""))
                data = json.dumps({"msg": f"{message}", "end": True, "error": True, "content": {}})
                yield f"data:{data}\n\n"
                raise RuntimeError(f"Error fetching data: {data['message']} - {data['result']}")

        if (not timeout):
            timeout = False
            data_batch = data["result"]
            json_transfers.extend(data_batch)

            message = f"<strong class='normal'>GET</strong> -   Get {len(data_batch)} records"
            logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
            data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
            yield f"data:{data}\n\n"
            time.sleep(1)

            if len(data_batch) < offset:
                break

            current_block = int(data_batch[-1]["blockNumber"]) + 1
        timeout = False

    # INFO: Store Multitoken as contract
    message = "<strong class='normal'>STORE</strong> - Storing Contract multitoken as contract"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    if json_transfers != []:
        df_traw_store = pd.DataFrame(json_transfers)
        df_traw_store.to_sql("t_multitoken_as_contract", connection, if_exists="append", index=False)
    toc = time.perf_counter()

    message = f"<strong class='normal'>STORE</strong> - {len(json_transfers)} multitoken transfers as contract...<strong class='normal'>{toc - tic:0.4f}</strong> seconds"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": message, "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    logger.info(" ")
    logger.info("=====================================================")

    message = "<strong class='normal'>COLLECT</strong> - Collecting Contract Multitoken... (as wallet)"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    logger.info("=====================================================")
    message = "<strong class='normal'>CREATE</strong> - Creating Table t_multitoken_as_wallet"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    sql_create_transfers_table = """CREATE TABLE IF NOT EXISTS t_multitoken_as_wallet (
                                       blockNumber integer NOT NULL,
                                       timeStamp datetime NOT NULL,
                                       hash text NOT NULL,
                                       nonce integer NOT NULL,
                                       blockHash text NOT NULL,
                                       transactionIndex integer NOT NULL,
                                       gas integer NOT NULL,
                                       gasPrice integer NOT NULL,
                                       gasUsed integer NOT NULL,
                                       cumulativeGasUsed integer NOT NULL,
                                       input text NOT NULL,
                                       contractAddress text NOT NULL,
                                       `from` text NOT NULL,
                                       `to` text NOT NULL,
                                       tokenID integer NOT NULL,
                                       tokenValue integer NOT NULL,
                                       tokenName text NOT NULL,
                                       tokenSymbol text NOT NULL,
                                       confirmations integer NOT NULL
                                 );"""
    connection.execute(sql_create_transfers_table)

    # INFO: Get Multitoken as wallet
    message = "<strong class='normal'>GET</strong> - Getting Contract multitoken as wallet"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    tic = time.perf_counter()

    json_transfers = []
    current_block = block_from
    end_block = block_to

    while int(current_block) < int(end_block):
        params = {
            # "chainid": chain_id, "module": "account", "action": "tokentx", "address": contract_address, "startblock": current_block,
            "chainid": chain_id, "module": "account", "action": "token1155tx", "address": contract_address, "startblock": current_block,
            "endblock": end_block, "page": 1, "offset": offset, "sort": "asc", "apikey": key,
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["status"] != "1":
            # TODO: Warning message to frontend
            if data["message"] == "No transactions found":
                break
            elif "Timeout" in data['message']:
                message = "<strong class='normal'>TIMEOUT</strong> -   Waiting 5 seg"
                logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
                data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
                yield f"data:{data}\n\n"
                time.sleep(5)
                timeout = True
            else:
                message = f"<strong class='error'>ERROR</strong> - {data['message']}"
                logger.error(message.replace("<strong class='error'>", "").replace("</strong>", ""))
                data = json.dumps({"msg": f"{message}", "end": True, "error": True, "content": {}})
                yield f"data:{data}\n\n"
                raise RuntimeError(f"Error fetching data: {data['message']} - {data['result']}")

        if (not timeout):
            data_batch = data["result"]
            json_transfers.extend(data_batch)

            message = f"<strong class='normal'>GET</strong> -   Get {len(data_batch)} records"
            logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
            data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
            yield f"data:{data}\n\n"
            time.sleep(1)

            if len(data_batch) < offset:
                break

            current_block = int(data_batch[-1]["blockNumber"]) + 1
        timeout = False

    # INFO: Store Multitoken as wallet
    message = "<strong class='normal'>STORE</strong> - Storing Contract multitoken as wallet"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    if json_transfers != []:
        df_traw_store = pd.DataFrame(json_transfers)
        df_traw_store.to_sql("t_multitoken_as_wallet", connection, if_exists="append", index=False)
    toc = time.perf_counter()

    message = f"<strong class='normal'>STORE</strong> - {len(json_transfers)} Multitoken transfers as wallet...<strong class='normal'>{toc - tic:0.4f}</strong> seconds"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": message, "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    logger.info(" ")
    logger.info("=====================================================")

    message = "<strong class='normal'>COLLECT</strong> - Collecting Contract internal transfers..."
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    logger.info("=====================================================")
    message = "<strong class='normal'>CREATE</strong> - Creating Table t_internals"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    sql_create_internals_table = """CREATE TABLE IF NOT EXISTS t_internals (
                                       blockNumber integer NOT NULL,
                                       timeStamp datetime NOT NULL,
                                       hash text NOT NULL,
                                       `from` text NOT NULL,
                                       `to` text NOT NULL,
                                       value integer NOT NULL,
                                       contractAddress text NOT NULL,
                                       input text NOT NULL,
                                       type text NOT NULL,
                                       gas integer NOT NULL,
                                       gasUsed integer NOT NULL,
                                       traceId integer NOT NULL,
                                       isError integer NOT NULL,
                                       errCode text NOT NULL
                                 );"""
    connection.execute(sql_create_internals_table)

    message = "<strong class='normal'>GET</strong> - Getting Contract internals"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    tic = time.perf_counter()

    json_internals = []
    current_block = block_from
    end_block = block_to

    while int(current_block) < int(end_block):
        params = {
            "chainid": chain_id, "module": "account", "action": "txlistinternal", "address": contract_address, "startblock": current_block,
            "endblock": end_block, "page": 1, "offset": offset, "sort": "asc", "apikey": key,
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["status"] != "1":
            if data["message"] == "No transactions found":
                break
            elif "Timeout" in data['message']:
                message = "<strong class='normal'>TIMEOUT</strong> -   Waiting 5 seg"
                logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
                data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
                yield f"data:{data}\n\n"
                time.sleep(5)
                timeout = True
            else:
                message = f"<strong class='error'>ERROR</strong> - {data['message']}"
                logger.error(message.replace("<strong class='error'>", "").replace("</strong>", ""))
                data = json.dumps({"msg": f"{message}", "end": True, "error": True, "content": {}})
                yield f"data:{data}\n\n"
                raise RuntimeError(f"Error fetching data: {data['message']} - {data['result']}")

        if (not timeout):
            timeout = False
            data_batch = data["result"]
            json_internals.extend(data_batch)

            message = f"<strong class='normal'>GET</strong> -   Get {len(data_batch)} records"
            logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
            data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
            yield f"data:{data}\n\n"
            time.sleep(1)

            if len(data_batch) < offset:
                break

            current_block = int(data_batch[-1]["blockNumber"]) + 1
        timeout = False

        data_batch = data["result"]
        json_internals.extend(data_batch)

        message = f"<strong class='normal'>GET</strong> -   Get {len(data_batch)} records"
        logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
        data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
        yield f"data:{data}\n\n"
        time.sleep(1)


        if len(data_batch) < offset:
            break

        current_block = int(data_batch[-1]["blockNumber"]) + 1

    # INFO: Store Internals
    message = "<strong class='normal'>STORE</strong> - Storing Contract internals"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    if json_internals != []:
        df_tra_store = pd.DataFrame(json_internals)
        df_tra_store.to_sql("t_internals", connection, if_exists="append", index=False)
    toc = time.perf_counter()

    message = f"<strong class='normal'>STORE</strong> - {len(json_internals)} internals...<strong class='normal'>{toc - tic:0.4f}</strong> seconds"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": message, "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    connection.commit()

    # NOTE: Get info from wallet creator
    # - First movement of wallet creator (Block and time)
    # - Last movement of wallet creator (Block and time) 
    # - Balance of all assets
    # - Get Blocks info from contract creator (Refresh button)
    #   - Contracts deployed
    #   - TRXs
    logger.info("=====================================================")

    message = "<strong class='normal'>COLLECT</strong> - Collecting Creator data..."
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    logger.info("=====================================================")
    message = "<strong class='normal'>CREATE</strong> - Creating Table t_contract_creator"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    sql_create_contract_table = """CREATE TABLE IF NOT EXISTS t_contract_creator (
                                   wallet text NOT NULL,
                                   block_from integer NOT NULL,
                                   block_to text NOT NULL,
                                   first_block integer NOT NULL,
                                   first_date datetime NOT NULL,
                                   first_hash text NOT NULL,
                                   first_to text NOT NULL,
                                   first_from text NOT NULL,
                                   first_value integer NOT NULL,
                                   first_input text NOT NULL,
                                   first_func text NOT NULL,
                                   last_block text NOT NULL,
                                   last_date datetime NOT NULL,
                                   last_hash text NOT NULL,
                                   last_to text NOT NULL,
                                   last_from text NOT NULL,
                                   last_value integer NOT NULL,
                                   last_input text NOT NULL,
                                   last_func text NOT NULL
                                 );"""
    cursor.execute(sql_create_contract_table)

    message = "<strong class='normal'>GET</strong> - Getting first block of contract creator"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    # TODO: The Funders trxs could be severals 
    url = f'{base_url}?chainid={chain_id}&module=account&action=txlist&address={contract_creator}&startblock=0&endblock=99999999' + \
        f'&page=1&offset=1&sort=asc&apikey={key}' 
    response = requests.get(url)

    first_block_creator = response.json()['result'][0]

    first_time = datetime.datetime.fromtimestamp(int(first_block_creator['timeStamp']))

    balances = misc.get_balance(chain_id, native, explorer, contract_creator, key)    

    message = "<strong class='normal'>STORE</strong> - Storing first block info of contract creator"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    cursor.execute("""INSERT INTO t_contract_creator VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
        (contract_creator,
         block_from,
         block_to,
         first_block_creator['blockNumber'],
         first_time,
         first_block_creator['hash'],
         first_block_creator['to'],
         first_block_creator['from'],
         pyround.pyround(int(first_block_creator['value']) / 1e+18, 8),
         first_block_creator['input'],
         first_block_creator['functionName'],
         "",
         "",
         "",
         "",
         "",
         0,
         "",
         ""))

    connection.commit()
    
    logger.info("=====================================================")

    message = "<strong class='normal'>COLLECT</strong> - Collecting balance Creator data..."
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    logger.info("=====================================================")
    message = "<strong class='normal'>CREATE</strong> - Creating Table t_balance"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    sql_create_balance_table = """CREATE TABLE IF NOT EXISTS t_balance (
                                   id number NOT NULL,
                                   balance text NOT NULL
                                 );"""
    cursor.execute(sql_create_balance_table)

    message = "<strong class='normal'>STORE</strong> - Storing balances of contract creator"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    id = 0
    for balance in balances:
        # print(f"{balance} - {type(balance)}")
        id += 1
        cursor.execute("""INSERT INTO t_balance VALUES (?, ?)""", 
            (id, balance))

    connection.commit()

    # TODO: Get the tags!!! TRX : 0xe5a4b28559a45c2d003831d4ac905842cea45df394b2eb85ad235bd96e5e443f

    logger.info(" ")
    logger.info("=====================================================")

    message = "<strong class='normal'>COLLECT</strong> - Collecting Creator transactions..."
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    logger.info("=====================================================")
    message = "<strong class='normal'>CREATE</strong> - Creating Table t_transactions_creator"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    sql_create_tran_creator_table = """CREATE TABLE IF NOT EXISTS t_transactions_creator (
                                       blockNumber integer NOT NULL,
                                       timeStamp datetime NOT NULL,
                                       hash text NOT NULL,
                                       nonce integer NOT NULL,
                                       blockHash text NOT NULL,
                                       transactionIndex integer NOT NULL,
                                       `from` text NOT NULL,
                                       `to` text NOT NULL,
                                       value integer NOT NULL,
                                       gas integer NOT NULL,
                                       gasPrice integer NOT NULL,
                                       isError integer NOT NULL,
                                       txreceipt_status integer NOT NULL,
                                       input text NOT NULL,
                                       contractAddress text NOT NULL,
                                       cumulativeGasUsed integer NOT NULL,
                                       gasUsed integer NOT NULL,
                                       confirmations integer NOT NULL,
                                       methodId text NOT NULL,
                                       functionName text NOT NULL
                                 );"""
    connection.execute(sql_create_tran_creator_table)

    message = "<strong class='normal'>GET</strong> - Getting transactions of contract creator"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    tic = time.perf_counter()

    json_trx_creator = []
    current_block = block_from
    end_block = block_to

    while int(current_block) < int(end_block):
        params = {
            "chainid": chain_id, "module": "account", "action": "txlist", "address": contract_creator, "startblock": current_block,
            "endblock": end_block, "page": 1, "offset": offset, "sort": "asc", "apikey": key,
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["status"] != "1":
            if data["message"] == "No transactions found":
                break
            elif "Timeout" in data['message']:
                message = "<strong class='normal'>TIMEOUT</strong> -   Waiting 5 seg"
                logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
                data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
                yield f"data:{data}\n\n"
                time.sleep(5)
                timeout = True
            else:
                message = f"<strong class='error'>ERROR</strong> - {data['message']}"
                logger.error(message.replace("<strong class='error'>", "").replace("</strong>", ""))
                data = json.dumps({"msg": f"{message}", "end": True, "error": True, "content": {}})
                yield f"data:{data}\n\n"
                raise RuntimeError(f"Error fetching data: {data['message']} - {data['result']}")

        if (not timeout):
            timeout = False
            data_batch = data["result"]
            json_trx_creator.extend(data_batch)

            message = f"<strong class='normal'>GET</strong> -   Get {len(data_batch)} records"
            logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
            data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
            yield f"data:{data}\n\n"
            time.sleep(1)

            if len(data_batch) < offset:
                break

            current_block = int(data_batch[-1]["blockNumber"]) + 1
        timeout = False

    # INFO: Store Transactions creator
    message = "<strong class='normal'>STORE</strong> - Storing transactions of creator"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    if json_trx_creator != []:
        df_tra_store = pd.DataFrame(json_trx_creator)
        df_tra_store.to_sql("t_transactions_creator", connection, if_exists="append", index=False)
    toc = time.perf_counter()

    message = f"<strong class='normal'>STORE</strong> - {len(json_trx_creator)} transactions creator...<strong class='normal'>{toc - tic:0.4f}</strong> seconds"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": message, "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    logger.info(" ")
    logger.info("=====================================================")

    message = "<strong class='normal'>COLLECT</strong> - Collecting Creator transfers..."
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    logger.info("=====================================================")
    message = "<strong class='normal'>CREATE</strong> - Creating Table t_transfers_creator"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    sql_create_tra_creator_table = """CREATE TABLE IF NOT EXISTS t_transfers_creator (
                                      blockNumber integer NOT NULL,
                                      timeStamp datetime NOT NULL,
                                      hash text NOT NULL,
                                      nonce integer NOT NULL,
                                      blockHash text NOT NULL,
                                      `from` text NOT NULL,
                                      contractAddress text NOT NULL,
                                      `to` text NOT NULL,
                                      value integer NOT NULL,
                                      tokenName text NOT NULL,
                                      tokenSymbol text NOT NULL,
                                      tokenDecimal integer NOT NULL,
                                      transactionIndex integer NOT NULL,
                                      gas integer NOT NULL,
                                      gasPrice integer NOT NULL,
                                      gasUsed integer NOT NULL,
                                      cumulativeGasUsed integer NOT NULL,
                                      input text NOT NULL,
                                      confirmations integer NOT NULL
                                 );"""
    connection.execute(sql_create_tra_creator_table)

    message = "<strong class='normal'>GET</strong> - Getting transfers of contract creator"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    tic = time.perf_counter()

    json_tra_creator = []
    current_block = block_from
    end_block = block_to

    while int(current_block) < int(end_block):
        params = {
            "chainid": chain_id, "module": "account", "action": "tokentx", "address": contract_creator, "startblock": current_block,
            "endblock": end_block, "page": 1, "offset": offset, "sort": "asc", "apikey": key,
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["status"] != "1":
            if data["message"] == "No transactions found":
                break
            elif "Timeout" in data['message']:
                message = "<strong class='normal'>TIMEOUT</strong> -   Waiting 5 seg"
                logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
                data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
                yield f"data:{data}\n\n"
                time.sleep(5)
                timeout = True
            else:
                message = f"<strong class='error'>ERROR</strong> - {data['message']}"
                logger.error(message.replace("<strong class='error'>", "").replace("</strong>", ""))
                data = json.dumps({"msg": f"{message}", "end": True, "error": True, "content": {}})
                yield f"data:{data}\n\n"
                raise RuntimeError(f"Error fetching data: {data['message']} - {data['result']}")

        if (not timeout):
            timeout = False
            data_batch = data["result"]
            json_tra_creator.extend(data_batch)

            message = f"<strong class='normal'>GET</strong> -   Get {len(data_batch)} records"
            logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
            data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
            yield f"data:{data}\n\n"
            time.sleep(1)

            if len(data_batch) < offset:
                break

            current_block = int(data_batch[-1]["blockNumber"]) + 1
        timeout = False

    # INFO: Store Transfers creator
    message = "<strong class='normal'>STORE</strong> - Storing transfers of creator"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    if json_tra_creator != []:
        df_tra_store = pd.DataFrame(json_tra_creator)
        df_tra_store.to_sql("t_transfers_creator", connection, if_exists="append", index=False)
    toc = time.perf_counter()

    message = f"<strong class='normal'>STORE</strong> - {len(json_tra_creator)} transfers creator...<strong class='normal'>{toc - tic:0.4f}</strong> seconds"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": message, "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    logger.info(" ")
    logger.info("=====================================================")

    message = "<strong class='normal'>COLLECT</strong> - Collecting Creator internal transfers..."
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    logger.info("=====================================================")
    message = "<strong class='normal'>CREATE</strong> - Creating Table t_internals_creator"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    sql_create_int_creator_table = """CREATE TABLE IF NOT EXISTS t_internals_creator (
                                      blockNumber integer NOT NULL,
                                      timeStamp datetime NOT NULL,
                                      hash text NOT NULL,
                                      `from` text NOT NULL,
                                      `to` text NOT NULL,
                                      value integer NOT NULL,
                                      contractAddress text NOT NULL,
                                      input text NOT NULL,
                                      type text NOT NULL,
                                      gas integer NOT NULL,
                                      gasUsed integer NOT NULL,
                                      traceId integer NOT NULL,
                                      isError integer NOT NULL,
                                      errCode text NOT NULL
                                 );"""
    connection.execute(sql_create_int_creator_table)

    message = "<strong class='normal'>GET</strong> - Getting internals of contract creator"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    tic = time.perf_counter()

    json_int_creator = []
    current_block = block_from
    end_block = block_to

    while int(current_block) < int(end_block):
        params = {
            "chainid": chain_id, "module": "account", "action": "txlistinternal", "address": contract_creator, "startblock": current_block,
            "endblock": end_block, "page": 1, "offset": offset, "sort": "asc", "apikey": key,
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["status"] != "1":
            if data["message"] == "No transactions found":
                break
            elif "Timeout" in data['message']:
                message = "<strong class='normal'>TIMEOUT</strong> -   Waiting 5 seg"
                logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
                data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
                yield f"data:{data}\n\n"
                time.sleep(5)
                timeout = True
            else:
                message = f"<strong class='error'>ERROR</strong> - {data['message']}"
                logger.error(message.replace("<strong class='error'>", "").replace("</strong>", ""))
                data = json.dumps({"msg": f"{message}", "end": True, "error": True, "content": {}})
                yield f"data:{data}\n\n"
                raise RuntimeError(f"Error fetching data: {data['message']} - {data['result']}")

        if (not timeout):
            timeout = False
            data_batch = data["result"]
            json_int_creator.extend(data_batch)

            message = f"<strong class='normal'>GET</strong> -   Get {len(data_batch)} records"
            logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
            data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
            yield f"data:{data}\n\n"
            time.sleep(1)

            if len(data_batch) < offset:
                break

            current_block = int(data_batch[-1]["blockNumber"]) + 1
        timeout = False

        data_batch = data["result"]
        json_int_creator.extend(data_batch)

        message = f"<strong class='normal'>GET</strong> -   Get {len(data_batch)} records"
        logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
        data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
        yield f"data:{data}\n\n"
        time.sleep(1)

        if len(data_batch) < offset:
            break

        current_block = int(data_batch[-1]["blockNumber"]) + 1

    # INFO: Store Internals creator
    message = "<strong class='normal'>STORE</strong> - Storing internals of creator"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    if json_int_creator != []:
        df_tra_store = pd.DataFrame(json_int_creator)
        df_tra_store.to_sql("t_internals_creator", connection, if_exists="append", index=False)
    toc = time.perf_counter()

    message = f"<strong class='normal'>STORE</strong> - {len(json_int_creator)} internals creator...<strong class='normal'>{toc - tic:0.4f}</strong> seconds"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": message, "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    connection.commit()

    # TODO: Need refactor to _refactor_

    # tags - Transactions - other contract created
    query = f"SELECT DISTINCT(contractAddress) from t_transactions_creator WHERE `to` = ''"
    cursor.execute(query)
    contracts = cursor.fetchall()
    for c in contracts:
        if not any(w.get("wallet") == c[0] for w in internal_tagging):
            internal_tagging.append({"wallet": c[0], "tag": "Contract Created"})

    # tags - Transactions creator
    query = f"SELECT DISTINCT(`to`) from t_transactions_creator WHERE (input != '' AND input != '0x') AND `to` != ''"
    cursor.execute(query)
    contracts = cursor.fetchall()
    for c in contracts:
        if not any(w.get("wallet") == c[0] for w in internal_tagging):
            internal_tagging.append({"wallet": c[0], "tag": "Contract"})

    # tags - Transactions creator
    query = f"SELECT DISTINCT(contractAddress) from t_transactions_creator"
    cursor.execute(query)
    contracts = cursor.fetchall()
    for c in contracts:
        if not any(w.get("wallet") == c[0] for w in internal_tagging):
            internal_tagging.append({"wallet": c[0], "tag": "Contract"})

    # tags - Internals creator
    query = f"SELECT DISTINCT(`to`) from t_internals_creator WHERE (input != '' AND input != '0x') AND `to` != ''"
    cursor.execute(query)
    contracts = cursor.fetchall()
    for c in contracts:
        if not any(w.get("wallet") == c[0] for w in internal_tagging):
            internal_tagging.append({"wallet": c[0], "tag": "Contract"})

    # tags - Internals creator
    query = f"SELECT DISTINCT(contractAddress) from t_internals_creator"
    cursor.execute(query)
    contracts = cursor.fetchall()
    for c in contracts:
        if not any(w.get("wallet") == c[0] for w in internal_tagging):
            internal_tagging.append({"wallet": c[0], "tag": "Contract"})

    # TODO: Confirm which this isn't necessary
    # # tags - Transfers creator
    # query = f"SELECT DISTINCT(`to`) from t_transfers_creator WHERE (input != '' AND input != '0x') AND `to` != ''"
    # cursor.execute(query)
    # contracts = cursor.fetchall()
    # for c in contracts:
    #     if not any(w.get("wallet") == c[0] for w in internal_tagging):
    #         internal_tagging.append({"wallet": c[0], "tag": "Contract"})

    # tags - Transfers creator
    query = f"SELECT DISTINCT(contractAddress) from t_transfers_creator"
    cursor.execute(query)
    contracts = cursor.fetchall()
    for c in contracts:
        if not any(w.get("wallet") == c[0] for w in internal_tagging):
            internal_tagging.append({"wallet": c[0], "tag": "Contract"})

    # tags - Transactions
    query = f"SELECT DISTINCT(contractAddress) from t_transactions"
    cursor.execute(query)
    contracts = cursor.fetchall()
    for c in contracts:
        if not any(w.get("wallet") == c[0] for w in internal_tagging):
            internal_tagging.append({"wallet": c[0], "tag": "Contract"})

    # tags - Internals
    query = f"SELECT DISTINCT(contractAddress) from t_internals"
    cursor.execute(query)
    contracts = cursor.fetchall()
    for c in contracts:
        if not any(w.get("wallet") == c[0] for w in internal_tagging):
            internal_tagging.append({"wallet": c[0], "tag": "Contract"})

    # tags - Transfers
    query = f"SELECT DISTINCT(contractAddress) from t_transfers_as_wallet"
    cursor.execute(query)
    contracts = cursor.fetchall()
    for c in contracts:
        if not any(w.get("wallet") == c[0] for w in internal_tagging):
            internal_tagging.append({"wallet": c[0], "tag": "Contract"})

    # tags - Transfers
    query = f"SELECT DISTINCT(contractAddress) from t_transfers_as_contract"
    cursor.execute(query)
    contracts = cursor.fetchall()
    for c in contracts:
        if not any(w.get("wallet") == c[0] for w in internal_tagging):
            internal_tagging.append({"wallet": c[0], "tag": "Contract"})

    # TODO: _refactor_

    # Get another contracts created by creator
    contracts = ""
    contracts_list = []
    idx = 1
    for t in internal_tagging:
        if (idx % 5 == 0):
            contracts_list.append(contracts)
            contracts = ""
        if (t['tag'] == 'Contract') and (t['wallet'] != ''):
            idx = idx + 1
            contracts = contracts + t['wallet'] + ','
    contracts_list.append(contracts)

    for l in contracts_list:
        if (l != ''):
            url = f'{base_url}?chainid={chain_id}&module=contract&action=getcontractcreation&contractaddresses=' + l[:-1] + \
               '&apikey=' + key
            response = requests.get(url)

            for r in response.json()['result']:
                if (r['contractCreator'] == contract_creator):
                    internal_tagging = [{**t, **{'tag': 'Contract Created'}} if t['wallet'] == r['contractAddress'] else t for t in internal_tagging]

    message = "<strong class='normal'>STORE</strong> - Storing tags"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    for t in internal_tagging:
        if (t['wallet'] != ''):
            cursor.execute("""INSERT INTO t_tagging VALUES (?, ?)""", 
                (str(t['wallet']), str(t['tag'])))

    connection.commit()
    connection.close()

    filename = os.path.basename(filedb)
    message = f"<strong class='normal'>PROCESS</strong> - Processing file...{filename}"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    # data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {"wallet_detail": wallet_detail}})
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    if (implemented):
        message = f"<strong class='normal'>PROCESS</strong> - Blockchain {blockchain}..."
        logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
        # data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {"wallet_detail": wallet_detail}})
        data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
        yield f"data:{data}\n\n"
        # data_db_process(filedb)
    else:
        message = f"<strong style='color: red'>ERROR</strong> - Chain ID {chain_id} not supported"
        logger.info(message.replace("<strong style='color: red'>", "").replace("</strong>", ""))
        data = json.dumps({"msg": f"{message}", "end": True, "error": True, "content": {}})
        yield f"data:{data}\n\n"

    message = "<strong class='normal'>END PROCESS</strong>"
    logger.error(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": True, "error": False, "content": {}})
    yield f"data:{data}\n\n"


def data_db_process(filename):
    """Process data from file"""
    # Validate file
    if (not os.path.exists(filename)):
        raise FileNotFoundError("File not found")

    # Split in temporary files
    if (not os.path.exists('./tmp')):
        os.makedirs('./tmp')

    # Remove temporary files
    [os.remove(os.path.join("./tmp", file)) for file in os.listdir("./tmp") if os.path.isfile(os.path.join("./tmp", file))]

    # Open db
    connection = sqlite3.connect(filename)
    cursor = connection.cursor()

    tic = time.perf_counter()
    cursor.execute("SELECT * FROM t_contract")
    row = cursor.fetchone()
    column_names = [description[0] for description in cursor.description]
    contract = {column_names[i]: row[i] for i in range(len(column_names))}

    # NOTE: Search Fallback function
    cursor.execute("SELECT * FROM t_source_abi")
    row = cursor.fetchone()
    column_names = [description[0] for description in cursor.description]
    source_code = {column_names[i]: row[i] for i in range(len(column_names))}
    json_str_source_code = source_code['SourceCode'] 
    contract_abi = source_code['ABI']

    # contract_token, erc = is_token_contract(contract_abi) 
    classification = misc.classify_contract(contract_abi, json_str_source_code)
    logger.info(f"Classification : {classification}")
    contract["classification"] = classification

    with open('./tmp/contract.json', 'w') as outfile:
        json.dump(contract, outfile)
    toc = time.perf_counter()
    logger.info(f"Get contract info in {toc - tic:0.4f} seconds")

    tic = time.perf_counter()
    fallback = False
    fallback_function = ''
    fallback_code = ''
    # receive = False  # TODO: 

    fallback_pattern  = r'(fallback[\s+]?\([.*]?\)\s)'
    fallback_result = re.search(fallback_pattern, json_str_source_code)

    if (fallback_result): 
        fallback = True
        fallback_function = fallback_result.group(1)
    if (not fallback): 
        # Compatibility
        fallback_pattern  = r'(function[\s+]?\([.*]?\)\s)'
        fallback_result = re.search(fallback_pattern, json_str_source_code)
        if (fallback_result): 
            fallback = True
            fallback_function = fallback_result.group(1)
    # Code
    if (fallback):
        funct_start = json_str_source_code.index(fallback_function)
        fallback_code = json_str_source_code[funct_start - 4:]
        funct_end = fallback_code[12:].index("function ")
        fallback_code = fallback_code[:funct_end]

    source_code['fallback'] = "true" if fallback else "false"
    source_code['fallback_function'] = fallback_function
    source_code['fallback_code'] = fallback_code

    with open('./tmp/sourcecode.json', 'w') as outfile:
        json.dump(source_code, outfile)
    with open('./tmp/contract-abi.json', 'w') as outfile:
        json.dump(contract_abi, outfile)
    toc = time.perf_counter()
    logger.info(f"Get Source code and ABI info in {toc - tic:0.4f} seconds")

    # Preprocess Statistics
    tic = time.perf_counter()
    
    # NOTE: Read db to pd
    # df_transaction = pd.read_json('./tmp/transactions.json')
    # df_t = pd.read_json('./tmp/transfers.json')
    # df_i = pd.read_json('./tmp/internals.json')
    # df_l = pd.read_json('./tmp/logs.json')
    
    df_transaction = pd.read_sql_query("SELECT * FROM t_transactions ORDER BY timeStamp ASC", connection, parse_dates=['timeStamp'])
    df_tw = pd.read_sql_query("SELECT * FROM t_transfers_as_wallet ORDER BY timeStamp ASC", connection, parse_dates=['timeStamp'])
    df_tc = pd.read_sql_query("SELECT * FROM t_transfers_as_contract ORDER BY timeStamp ASC", connection, parse_dates=['timeStamp'])
    df_i = pd.read_sql_query("SELECT * FROM t_internals ORDER BY timeStamp ASC", connection, parse_dates=['timeStamp'])

    # Split in JSON files
    with open('./tmp/transactions.json', 'w') as outfile:
        df_transaction.to_json(outfile)
    with open('./tmp/transfers_wallet.json', 'w') as outfile:
        df_tw.to_json(outfile)
    with open('./tmp/transfers_contract.json', 'w') as outfile:
        df_tc.to_json(outfile)
    with open('./tmp/internals.json', 'w') as outfile:
        df_i.to_json(outfile)
    toc = time.perf_counter()
    logger.info(f"Split file in {toc - tic:0.4f} seconds")

    # TODO: Refactor until _refactor_
    native = False
    if (df_i.size > df_tw.size + df_tc.size):
        native = True
        logger.info("Detect NATIVE token")
    else: 
        logger.info("Detect NOT NATIVE token")
    # TODO: _refactor_

    # Get unified transaction-internals-transfers
    df_trx_0 = df_transaction[df_transaction['isError'] == 0]
    df_trx_1 = df_trx_0[['timeStamp', 'hash', 'from', 'to', 'value', 'input', 
                         'isError']]
    df_trx_1.insert(len(df_trx_1.columns), "file", "trx")
    df_uni = df_trx_1

    if (not df_tw.empty):
        df_traw_0 = df_tw
        df_traw_1 = df_traw_0[['timeStamp', 'hash', 'from', 'to', 'value', 'input']]
        df_traw_1.insert(len(df_traw_1.columns), "isError", 0)
        df_traw_1.insert(len(df_traw_1.columns), "file", "tra")

    if (not df_tc.empty):
        df_trac_0 = df_tc
        df_trac_1 = df_trac_0[['timeStamp', 'hash', 'from', 'to', 'value', 'input']]
        df_trac_1.insert(len(df_trac_1.columns), "isError", 0)
        df_trac_1.insert(len(df_trac_1.columns), "file", "tra")

    if (not df_i.empty):
        df_int_0 = df_i
        df_int_1 = df_int_0[['timeStamp', 'hash', 'from', 'to', 'value', 'input',
                             'isError']]
        df_int_1.insert(len(df_int_1.columns), "file", "int")

    if (not df_tw.empty):
        pd_uni = pd.concat([df_uni, df_traw_1], axis=0, ignore_index=True)
        df_uni = pd.DataFrame(pd_uni)
    if (not df_tc.empty):
        pd_uni = pd.concat([df_uni, df_trac_1], axis=0, ignore_index=True)
        df_uni = pd.DataFrame(pd_uni)
    if (not df_i.empty):
        pd_uni = pd.concat([df_uni, df_int_1], axis=0, ignore_index=True)
        df_uni = pd.DataFrame(pd_uni)

    df_uni = df_uni.sort_values(by=['timeStamp','file'], ascending=False)  
    df_uni.to_csv('./tmp/uni.csv')
    with open('./tmp/uni.json', 'w') as outfile:
        df_uni_json = df_uni.to_json(outfile)
    
    # Get contract creator
    contract_creator = df_transaction["from"][0]

    # TODO : Determine decimal digits in base of range 

    # NOTE: Get token and volume
    if (native):
        token_name = contract['native']
        # volume = round(df_transaction['value'].sum() / 1e+18, 2) + round(df_i['value'].sum() / 1e+18, 2)
        # volume = round((df_transaction['value'].sum() / 1e+18, 2 + df_i['value'].sum() / 1e+18) / 2, 2)
        volume = df_transaction['value'].sum() + df_i['value'].sum()
        volume = round(volume / 1e+18, 2)
    else:
        # NOTE : Display another tokens
        if classification == "Token Creation Contract":
            token = df_tc.groupby('tokenSymbol').agg({'value': ['sum','count']})
            token = token.sort_values(by=[('value','count')], ascending=False)  
            token_name = token.index[0]
            maxSupply = df_tc.iloc[0]['value']
        else:
            token = df_tw.groupby('tokenSymbol').agg({'value': ['sum','count']})
            token = token.sort_values(by=[('value','count')], ascending=False)  
            token_name = token.index[0]

    # Liquidity and dates
    address_contract = contract["contract"].lower()
    liq = 0
    liq_raw = 0
    max_liq = 0
    max_liq_raw = 0
    volume_raw = 0
    trx_out = 0 
    trx_in = 0
    trx_out_day = 0 
    trx_in_day = 0
    remain = 0
    liq_series = []
    trx_in_series = []
    trx_out_series = []
    day = ''
    day_prev = ''
    day_prev_complete = ''

    df_t = pd.concat([df_tw, df_tc], ignore_index=True) # WARN: concat transfers

    if (native):
        # NOTE : I replace the dftemp for df_uni. Remove if it's working
        dftemp = df_uni
        dftemp = dftemp.sort_values(["timeStamp"])

        unique_wallets = len(dftemp['from'].unique())
        max_liq_date = dftemp["timeStamp"][0]  # NOTE: Initialization

        for i in dftemp.index: 
            value_raw = dftemp["value"][i]
            value = round(value_raw / 1e+18, 2)
            address_from = dftemp["from"][i]
            address_to = dftemp["to"][i]

            if (address_from == address_contract):
                liq = liq - value
                liq_raw = liq_raw - int(value_raw)
                trx_out = trx_out + value
                trx_out_day = trx_out_day + value
            elif (address_to == address_contract):
                liq = liq + value
                liq_raw = liq_raw + int(value_raw)
                volume_raw = volume_raw + int(value_raw)
                trx_in = trx_in + value
                trx_in_day = trx_in_day + value
                if (max_liq_raw < liq_raw):
                    max_liq_raw = liq_raw
                    max_liq_date = dftemp["timeStamp"][i]
            else:
                remain = remain + int(value_raw)

            if (day == ''):
                # print(df_t.info())
                # print(df_t.head())
                day = dftemp['timeStamp'][i].strftime("%Y-%m-%d")
                day_prev = day
                day_prev_complete = dftemp['timeStamp'][i]
            elif (day_prev != day):
                liq_series.append({"name": day_prev_complete.strftime("%Y-%m-%dT%H:%M:%S.009Z"),
                                "value": liq})
                trx_in_series.append({"name": day_prev_complete.strftime("%Y-%m-%dT%H:%M:%S.009Z"),
                                      "value": trx_in_day})
                trx_out_series.append({"name": day_prev_complete.strftime("%Y-%m-%dT%H:%M:%S.009Z"),
                                       "value": trx_out_day})
                day_prev = day
                day_prev_complete = dftemp['timeStamp'][i]
                trx_in_day = 0
                trx_out_day = 0
            else:
                day = dftemp['timeStamp'][i].strftime("%Y-%m-%d")

        first_date = dftemp['timeStamp'][0]
        last_date = dftemp['timeStamp'].iloc[-1]  # TODO: When Liq == 0

    else:  # NOTE : Not native
        # TODO: Include to field
        unique_wallets = len(df_t['from'].unique())

        # TODO: In a Token creation contract, the max liquidity must be the max supply
        max_liq_date = df_t["timeStamp"][0] # NOTE: Initialization
        for i in df_t.index: 
            if (df_t["tokenSymbol"][i] == token_name):
                value_raw = df_t["value"][i]
                value = round(value_raw / 1e+18, 2)
                address_from = df_t["from"][i].lower()
                address_to = df_t["to"][i].lower()

                if (address_from == address_contract):
                    liq = liq - value
                    liq_raw = liq_raw - int(value_raw)
                    trx_out = trx_out + value
                    trx_out_day = trx_out_day + value
                elif (address_to == address_contract):
                    liq = liq + value
                    liq_raw = liq_raw + int(value_raw)
                    volume_raw = volume_raw + int(value_raw)
                    trx_in = trx_in + value
                    trx_in_day = trx_in_day + value
                    if (max_liq_raw < liq_raw):
                        max_liq_raw = liq_raw
                        max_liq_date = df_t["timeStamp"][i]
                else:
                    remain = remain + int(value_raw)

                if (day == ''):
                    day = df_t['timeStamp'][i].strftime("%Y-%m-%d")
                    day_prev = day
                    day_prev_complete = df_t['timeStamp'][i]
                elif (day_prev != day):
                    liq_series.append({"name": day_prev_complete.strftime("%Y-%m-%dT%H:%M:%S.009Z"),
                                       "value": liq})
                    trx_in_series.append({"name": day_prev_complete.strftime("%Y-%m-%dT%H:%M:%S.009Z"),
                                          "value": trx_in_day})
                    trx_out_series.append({"name": day_prev_complete.strftime("%Y-%m-%dT%H:%M:%S.009Z"),
                                           "value": trx_out_day})
                    day_prev = day
                    day_prev_complete = df_t['timeStamp'][i]
                    trx_in_day = 0
                    trx_out_day = 0
                else:
                    day = df_t['timeStamp'][i].strftime("%Y-%m-%d")

        first_date = df_t['timeStamp'][0]
        last_date = df_t['timeStamp'].iloc[-1]  # TODO : When Liq == 0

    ## Statistics
    # Unification for Native
    if (native):
        df_t = dftemp
    # Group by
    from_trx = df_t.groupby('from').agg({'value': ['sum','count']})
    # from_trx.set_axis(['value_out', 'count_out'], axis=1, inplace=False)
    from_trx_axis = from_trx.set_axis(['value_out', 'count_out'], axis=1)
    to_trx = df_t.groupby('to').agg({'value': ['sum','count']})
    # to_trx.set_axis(['value_in', 'count_in'], axis=1, inplace=True)
    to_trx_axis = to_trx.set_axis(['value_in', 'count_in'], axis=1)

    # Merge
    trx_total = from_trx_axis.join(to_trx_axis, how='outer')  # NOTE: OUTER
    trx_total['wallet'] = trx_total.index
    trx_total = trx_total.sort_values(["wallet"])
    trx_total.reset_index(drop=True, inplace=True)
    trx_total.fillna(0, inplace=True)

    total = []
    # JSON Bubbles file
    for i in trx_total.index: 
        wallet = trx_total["wallet"][i]

        child = [{"name": "IN", 
                 "size": round(trx_total["value_in"][i] / 1e+18, 2),

                  "count": int(trx_total["count_in"][i])}]
        child.append({"name": "OUT", 
                      "size": round(trx_total["value_out"][i] / 1e+18, 2),
                      "count": int(trx_total["count_out"][i])})
        item = {"name": wallet, "children": child}
        total.append(item)

    json_bubbles = {"name": "Schema", "children": total}

    with open('./tmp/bubbles.json', 'w') as outfile:
        json.dump(json_bubbles, outfile)

    # Add Percentage
    trx_total["Percentage"] = round(trx_total["value_in"] * 100 / trx_total['value_out'], 0)
    trx_total.replace([np.inf, -np.inf], 9999999, inplace=True)  # NOTE: Handle division by 0
    trx_total_dec = trx_total.sort_values(["Percentage"])
    trx_total_asc = trx_total.sort_values(["Percentage"], ascending=False)

    # Anomalies
    df_anomalies = trx_total_asc[trx_total_asc['wallet'] != address_contract ]
    df_anomalies = df_anomalies[trx_total_asc['Percentage'] >= 10]
    df_anomalies['Percentage'] = df_anomalies['Percentage'].astype(int)
    with open('./tmp/anomalies.json', 'w') as outfile:
        df_anomalies_json = df_anomalies.to_json(outfile, orient="records")

    # Statistic Percentage
    # TODO: Define the correct percentage in base to time period
    e_0 = trx_total[trx_total['Percentage'] == 0]
    e_0_100 = trx_total[(trx_total['Percentage'] > 0) & (trx_total['Percentage'] < 100)]
    e_100_241 = trx_total[(trx_total['Percentage'] >= 100) & (trx_total['Percentage'] <= 200)]
    e_241 = trx_total[trx_total['Percentage'] > 200]

    investments = []
    investments.append({"name": "Total Loses", "value": len(e_0)})
    investments.append({"name": "Loses", "value": len(e_0_100)})
    investments.append({"name": "Earnings", "value": len(e_100_241)})
    investments.append({"name": "Top Profit", "value": len(e_241)})

    # ABI
    ABI = json.loads(contract_abi)

    df_hash = df_transaction["hash"][0:]
    input_constructor = df_transaction["input"][0]
    input_column = df_transaction["input"][1:]

    decoder = InputDecoder(ABI)
    constructor_call = decoder.decode_constructor((input_constructor),)

    functions = []
    functions.append(constructor_call.name)
    arguments = []
    arguments.append(str(constructor_call.arguments))
    for i in input_column:
        try:
            func_call = decoder.decode_function((i),)
            functions.append(func_call.name)
            arguments.append(str(func_call.arguments))
        except Exception:
            # HACK: Fallback
            if (source_code['fallback'] == "true"):
                functions.append('fallback')
                arguments.append("null")
            else:
                functions.append("Not decoded")
                arguments.append("Not decoded")

    df_decoded = pd.DataFrame({"hash": df_hash, "funct": functions, "args": arguments})
    # df_decoded = pd.DataFrame({"hash": df_hash, "funct": functions})
    dict_decoded = df_decoded.to_dict()

    with open('./tmp/decoded.json', 'w') as outfile:
        json.dump(dict_decoded, outfile)

    # Functions stats
    funct_stats = df_decoded['funct'].value_counts()
    funct_stats_json = []
    for i in funct_stats.index: 
        funct_stats_json.append({"name": str(i), "value": int(funct_stats[i])})

    # Calculate volume
    if (classification == "Token Creation Contract"):
        volume = round(remain / 1e18, 2)
        max_liq_raw = maxSupply
    else:
        volume = round(volume_raw / 1e18, 2)

    json_stats = {"contract": address_contract,
                  "fdate": first_date.strftime("%Y/%m/%d - %H:%M:%S"),
                  "ldate": last_date.strftime("%Y/%m/%d - %H:%M:%S"),
                  "token_name": token_name,
                  "native": int(native),
                  "creator": contract_creator,
                  "max_liq": round(max_liq_raw / 1e18, 2),
                  "max_liq_date": max_liq_date.strftime("%Y/%m/%d - %H:%M:%S"),
                  "volume": volume,
                  "wallets": unique_wallets,
                  "investments": investments,
                  "funct_stats": funct_stats_json,
                #   "funct_stats": investments,
                  "trx_out": trx_out,
                  "trx_in": trx_in}

    with open('./tmp/stats.json', 'w') as outfile:
        json.dump(json_stats, outfile)

    # Liquidity graph
    json_liq = liq_series

    with open('./tmp/liq.json', 'w') as outfile:
        json.dump(json_liq, outfile)

    # Trans Volume graph
    json_trans_vol = [{"name": "Trans OUT",
                      "series": trx_out_series},
                      {"name": "Trans IN",
                      "series": trx_in_series}]

    with open('./tmp/trans_series.json', 'w') as outfile:
        json.dump(json_trans_vol, outfile)

    # Transaction resume
    trans_ok = len(df_transaction[df_transaction['isError'] == 0])
    trans_error = len(df_transaction[df_transaction['isError'] != 0])

    trans_resume = [{'name': 'Transactions OK', 'value': trans_ok}, 
                    {'name': 'Transactions ERROR', 'value': trans_error}]

    with open('./tmp/transaction_resume.json', 'w') as outfile:
        json.dump(trans_resume, outfile)

    # Transfer resume
    if (native):  # NOTE: For native
        trans_in = len(dftemp[dftemp['file'] == 'trx'])  # TODO: Remove value = 0
        trans_out = len(dftemp[dftemp['file'] == 'int'])
    else:
        trans_in = len(df_t[df_t['from'].str.contains(address_contract, case=False)])
        trans_out = len(df_t[df_t['to'].str.contains(address_contract, case=False)])

    trans_io = [{'name': 'Transfers IN', 'value': trans_in}, 
                {'name': 'Transfers OUT', 'value': trans_out}]

    with open('./tmp/transfer_resume.json', 'w') as outfile:
        json.dump(trans_io, outfile)

    toc = time.perf_counter()
    logger.info(f"Preprocess Statistic file in {toc - tic:0.4f} seconds")

    return 0


def event_stream_data_file(file):
    # NOTE: Config Log Level
    log_format = "%(asctime)s %(name)s %(lineno)d %(levelname)s %(message)s"
    coloredlogs.install(level="DEBUG", fmt=log_format, logger=logger)
    logger.propagate = False  # NOTE: To prevent duplicates with flask

    filename = os.path.basename(file)
    message = f"<strong class='normal'>PROCESS</strong> - Processing file...{filename}"
    logger.info(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    # data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {"wallet_detail": wallet_detail}})
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    # NOTE: Generic file process function
    data_db_process(file)
    # bsc.bsc_db_process(file)

    message = "<strong class='normal'>END PROCESS</strong>"
    logger.error(message.replace("<strong class='normal'>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": True, "error": False, "content": {}})
    yield f"data:{data}\n\n"


