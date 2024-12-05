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
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import cloudscraper
import pyround
import datetime

# from termcolor import colored
import logging
import coloredlogs

from web3_input_decoder import InputDecoder # , decode_constructor

from core import eth
from core import bsc


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


def get_bchain_data(chain_id, address, module, action, key, start_block=0, end_block=99999999):

    base_url = "https://api.etherscan.io/v2/api"
    offset = 10000  # Maximum limit per request
    current_block = start_block

    params = {
        "chainid": chain_id,
        "module": module,
        "action": action, 
        "address": address,
        "startblock": current_block,
        "endblock": end_block,
        "page": 1,
        "offset": offset,
        "sort": "asc",
        "apikey": key,
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    return data


def fetch_all_transactions(chain_id, address, key, start_block=0, end_block=99999999):

    base_url = "https://api.etherscan.io/v2/api"
    transactions = []
    offset = 10000  # Maximum limit per request
    current_block = start_block

    while current_block < end_block:
        params = {
            "chainid": chain_id,
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": current_block,
            "endblock": end_block,
            "page": 1,
            "offset": offset,
            "sort": "asc",
            "apikey": key,
        }

        response = requests.get(base_url, params=params)
        data = response.json()

        if data["status"] != "1":
            # If no more transactions or an error occurred
            if data["message"] == "No transactions found":
                break
            else:
                raise Exception(f"Error fetching data: {data['message']} - {data['result']}")

        transactions_batch = data["result"]
        transactions.extend(transactions_batch)

        logger.info(f" Get {len(transactions_batch)} records")

        # If less than the maximum limit is returned, we have reached the last page
        if len(transactions_batch) < offset:
            break

        # Update the current_block to the last block number from the fetched transactions
        current_block = int(transactions_batch[-1]["blockNumber"]) + 1

    return transactions


def data_db_collect(chain_id, contract_address, key, filedb, block_from=0, block_to=99999999):

    base_url = "https://api.etherscan.io/v2/api"
    offset = 10000

    try:
        os.remove(filedb)
    except:
        pass
    logger.info(f"Creating db {filedb}")
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
    logger.info("Collecting Contract data")
    logger.info("=====================================================")
    logger.info("Creating Table t_contract")

    sql_create_contract_table = """CREATE TABLE IF NOT EXISTS t_contract (
                                   contract text NOT NULL,
                                   blockchain text NOT NULL,
                                   block_from text NOT NULL,
                                   block_to text NOT NULL,
                                   first_block text NOT NULL,
                                   transaction_creation text NOT NULL,
                                   date_creation datetime NOT NULL,
                                   creator text NOT NULL
                                 );"""
    cursor.execute(sql_create_contract_table)

    logger.info("Getting first block")
    url = f'{base_url}?chainid={chain_id}&module=account&action=txlist&address={contract_address}&startblock=0&endblock=99999999' + \
        f'&page=1&offset=1&sort=asc&apikey={key}'
    response = requests.get(url)

    # Validate API Key 
    if (response.json()['message'] == "NOTOK"):
        logger.error("Invalid API Key")
        os.remove(filedb)
        raise RuntimeError('Invalid API Key')
        
    first_block = response.json()['result'][0]

    if (block_from == 0):
        block_from = int(first_block['blockNumber'])
    contract_creator = first_block['from']

    logger.info("Storing first block")
    cursor.execute("""INSERT INTO t_contract VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", 
        (contract_address, 'eth', block_from, block_to, first_block['blockNumber'], 
        first_block['hash'], first_block['timeStamp'], first_block['from']))

    connection.commit()
    # tag
    internal_tagging.append({"wallet": contract_address, "tag": "Contract Analysed"})
    internal_tagging.append({"wallet": first_block['from'], "tag": "Contract Creator"})

    # Source code
    logger.info("Creating Table t_source_abi")

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

    logger.info("Getting source code and ABI")
    url = f'{base_url}?chainid={chain_id}&module=contract&action=getsourcecode&address={contract_address}&apikey={key}'
    response = requests.get(url)
    json_obj_source_code = response.json()['result'][0]

    logger.info("Storing source code and ABI")
    cursor.execute("""INSERT INTO t_source_abi VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
        (json_obj_source_code['SourceCode'],
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
    logger.info("Collecting Contract transactions")
    logger.info("=====================================================")
    logger.info("Creating Table t_transactions")

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
    logger.info("Getting transactions")
    tic = time.perf_counter()

    json_transactions = []
    current_block = block_from
    end_block = block_to

    while current_block < end_block:
        params = {
            "chainid": chain_id, "module": "account", "action": "txlist", "address": contract_address, "startblock": current_block,
            "endblock": end_block, "page": 1, "offset": offset, "sort": "asc", "apikey": key,
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["status"] != "1":
            if data["message"] == "No transactions found":
                break
            else:
                raise Exception(f"Error fetching data: {data['message']} - {data['result']}")

        data_batch = data["result"]
        json_transactions.extend(data_batch)

        logger.info(f" Get {len(data_batch)} records")

        # If less than the maximum limit is returned, we have reached the last page
        if len(data_batch) < offset:
            break

        # Update the current_block to the last block number from the fetched transactions
        current_block = int(data_batch[-1]["blockNumber"]) + 1

    # INFO: Store Transactions
    logger.info("Store transactions")
    if json_transactions != []:
        df_trx_store = pd.DataFrame(json_transactions)
        # df_trx_store["blockChain"] = chain_id  # TODO: Change chain_id by blockchain name
        # df_trx_store.to_sql("t_transactions", connection, if_exists="append", index=False, method=insert_with_ignore)
        df_trx_store.to_sql("t_transactions", connection, if_exists="append", index=False)
    toc = time.perf_counter()

    message = f"<strong>STORE</strong> - {len(json_transactions)} Transactions...<strong>{toc - tic:0.4f}</strong> seconds"
    logger.info(message.replace("<strong>", "").replace("</strong>", ""))
    # data = json.dumps({"msg": message, "end": False, "error": False, "content": {}})
    # yield f"data:{data}\n\n"

    logger.info(" ")
    logger.info("=====================================================")
    logger.info(f"Collecting Contract transfers...")
    logger.info("=====================================================")
    logger.info("Creating Table t_transfers")

    sql_create_transfers_table = """CREATE TABLE IF NOT EXISTS t_transfers (
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

    logger.info("Getting transactions")
    tic = time.perf_counter()

    json_transfers = []
    current_block = block_from
    end_block = block_to

    while current_block < end_block:
        params = {
            "chainid": chain_id, "module": "account", "action": "tokentx", "address": contract_address, "startblock": current_block,
            "endblock": end_block, "page": 1, "offset": offset, "sort": "asc", "apikey": key,
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["status"] != "1":
            if data["message"] == "No transactions found":
                break
            else:
                raise Exception(f"Error fetching data: {data['message']} - {data['result']}")

        data_batch = data["result"]
        json_transfers.extend(data_batch)

        logger.info(f" Get {len(data_batch)} records")

        if len(data_batch) < offset:
            break

        current_block = int(data_batch[-1]["blockNumber"]) + 1

    # INFO: Store Transfers
    logger.info("Store transfers")
    if json_transfers != []:
        df_tra_store = pd.DataFrame(json_transfers)
        df_tra_store.to_sql("t_transfers", connection, if_exists="append", index=False)
    toc = time.perf_counter()

    message = f"<strong>STORE</strong> - {len(json_transfers)} token transfers...<strong>{toc - tic:0.4f}</strong> seconds"
    logger.info(message.replace("<strong>", "").replace("</strong>", ""))
    # data = json.dumps({"msg": message, "end": False, "error": False, "content": {}})
    # yield f"data:{data}\n\n"

    logger.info(" ")
    logger.info("=====================================================")
    logger.info(f"Collecting Internals transfers...")
    logger.info("=====================================================")
    logger.info("Creating Table t_internals")

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

    logger.info("Getting internals")
    tic = time.perf_counter()

    json_internals = []
    current_block = block_from
    end_block = block_to

    while current_block < end_block:
        params = {
            "chainid": chain_id, "module": "account", "action": "txlistinternal", "address": contract_address, "startblock": current_block,
            "endblock": end_block, "page": 1, "offset": offset, "sort": "asc", "apikey": key,
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["status"] != "1":
            if data["message"] == "No transactions found":
                break
            else:
                raise Exception(f"Error fetching data: {data['message']} - {data['result']}")

        data_batch = data["result"]
        json_internals.extend(data_batch)

        logger.info(f" Get {len(data_batch)} records")

        if len(data_batch) < offset:
            break

        current_block = int(data_batch[-1]["blockNumber"]) + 1

    # INFO: Store Internals
    logger.info("Store internals")
    if json_internals != []:
        df_tra_store = pd.DataFrame(json_internals)
        df_tra_store.to_sql("t_internals", connection, if_exists="append", index=False)
    toc = time.perf_counter()

    message = f"<strong>STORE</strong> - {len(json_internals)} internals...<strong>{toc - tic:0.4f}</strong> seconds"
    logger.info(message.replace("<strong>", "").replace("</strong>", ""))
    # data = json.dumps({"msg": message, "end": False, "error": False, "content": {}})
    # yield f"data:{data}\n\n"

    connection.commit()

    # NOTE: Get info from wallet creator
    # - First movement of wallet creator (Block and time)
    # - Last movement of wallet creator (Block and time) 
    # - Balance of all assets
    # - Get Blocks info from contract creator (Refresh button)
    #   - Contracts deployed
    #   - TRXs
    logger.info("=====================================================")
    logger.info("Collecting Contract Creator data")
    logger.info("=====================================================")
    logger.info("Creating Table t_contract_creator")

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

    logger.info("Getting first block of contract creator")

    # TODO: The Funders trxs could be severals 
    url = f'{base_url}?chainid={chain_id}&module=account&action=txlist&address={contract_creator}&startblock=0&endblock=99999999' + \
        f'&page=1&offset=1&sort=asc&apikey={key}' 
    response = requests.get(url)

    first_block_creator = response.json()['result'][0]
    # first_block_number = int(first_block_creator['blockNumber'])

    # first_time = datetime.datetime.timestamp(first_block_creator['timeStamp'])
    first_time = datetime.datetime.fromtimestamp(int(first_block_creator['timeStamp']))

    # TODO: Do we need internals and ERC20? Answer is NOT because we need to find funder of contract deploy

    # TODO: Handle error if page change and handle several blockchain explorers
    url_home = "https://etherscan.io/address/" + contract_creator 
    url_tokens = "https://etherscan.io/address-tokenpage?m=normal&a=" + contract_creator

    # Home
    scraper = cloudscraper.create_scraper()
    r_home = scraper.get(url_home)

    html_doc = BeautifulSoup(r_home.content, "html.parser")
    div_card_body_container = html_doc.find_all('div', class_='card-body d-flex flex-column gap-5')
    balance_container = div_card_body_container[0].find_all('div')

    # Balances
    balances = []
    # balance = balance_container[1].find_all('div')
    balance_eth = balance_container[1].text.split()[2]
    balances.append(f"Balance : {balance_eth} ETH")

    token_list = div_card_body_container[0].find_all('li', class_='nav-item list-custom-ERC20')
    for i in token_list:
        balances.append(i.text)
    
    # FIX: Remove last block code until _last_block_
    # logger.info("Getting last block of contract creator")
    # div_table_container = html_doc.find('div', id='transactions')
    # table = div_table_container.find('table')
    # tbody = table.find('tbody')
    # td = tbody.tr.find_all('td')
    # last_block_number = td[3].text
    # last_time_trx = td[4].span.text
    # last_from_trx = td[6].span.text
    # try:
    #     last_to_trx = td[8].span.a['href'].split("/")[-1]
    # except Exception:
    #     try: 
    #         last_to_trx = td[8].a['href'].split("/")[-1]
    #     except Exception:
    #         last_to_trx = "N/A"
    # last_value_trx = td[9].text

    # url = f'{base_url}?chainid={chain_id}&module=account&action=txlist&address={contract_creator}' + \
    #     f'&startblock={last_block_number}&endblock={last_block_number}' + \
    #     f'&page=1&offset=1&sort=asc&apikey={key}'
    # response = requests.get(url)

    # last_block_creator = response.json()['result'][-1]
    # last_time = datetime.datetime.fromtimestamp(int(last_block_creator['timeStamp']))
    # FIX: _last_block_

    logger.info("Storing first and last block info of contract creator")
    # cursor.execute("""INSERT INTO t_contract_creator VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
    #     (contract_creator,
    #      block_from,
    #      block_to,
    #      first_block_creator['blockNumber'],
    #      first_time,
    #      first_block_creator['hash'],
    #      first_block_creator['to'],
    #      first_block_creator['from'],
    #      pyround.pyround(int(first_block_creator['value']) / 1e+18, 8),
    #      first_block_creator['input'],
    #      first_block_creator['functionName'],
    #      last_block_creator['blockNumber'],
    #      last_time,
    #      last_block_creator['hash'],
    #      last_block_creator['to'],
    #      last_block_creator['from'],
    #      pyround.pyround(int(last_block_creator['value']) / 1e+18, 8),
    #      last_block_creator['input'],
    #      last_block_creator['functionName']))
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
    logger.info("Collecting Balance Creator data")
    logger.info("=====================================================")
    logger.info("Creating Table t_balance")

    sql_create_balance_table = """CREATE TABLE IF NOT EXISTS t_balance (
                                   id number NOT NULL,
                                   balance text NOT NULL
                                 );"""
    cursor.execute(sql_create_balance_table)

    logger.info("Storing balances of contract creator")
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
    logger.info("Collecting Contract creator transactions")
    logger.info("=====================================================")
    logger.info("Creating Table t_transactions_wallet")

    sql_create_tran_creator_table = """CREATE TABLE IF NOT EXISTS t_transactions_wallet (
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

    logger.info("Getting transactions of contract creator")
    tic = time.perf_counter()

    json_trx_creator = []
    current_block = block_from
    end_block = block_to

    while current_block < end_block:
        params = {
            "chainid": chain_id, "module": "account", "action": "txlist", "address": contract_creator, "startblock": current_block,
            "endblock": end_block, "page": 1, "offset": offset, "sort": "asc", "apikey": key,
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["status"] != "1":
            if data["message"] == "No transactions found":
                break
            else:
                raise Exception(f"Error fetching data: {data['message']} - {data['result']}")

        data_batch = data["result"]
        json_trx_creator.extend(data_batch)

        logger.info(f" Get {len(data_batch)} records")

        if len(data_batch) < offset:
            break

        current_block = int(data_batch[-1]["blockNumber"]) + 1

    # INFO: Store Transactions creator
    logger.info("Store transactions creator")
    if json_trx_creator != []:
        df_tra_store = pd.DataFrame(json_trx_creator)
        df_tra_store.to_sql("t_transactions_wallet", connection, if_exists="append", index=False)
    toc = time.perf_counter()

    message = f"<strong>STORE</strong> - {len(json_trx_creator)} transactions creator...<strong>{toc - tic:0.4f}</strong> seconds"
    logger.info(message.replace("<strong>", "").replace("</strong>", ""))
    # data = json.dumps({"msg": message, "end": False, "error": False, "content": {}})
    # yield f"data:{data}\n\n"

    logger.info(" ")
    logger.info("=====================================================")
    logger.info(f"Collecting Contract Creator transfers...")
    logger.info("=====================================================")
    logger.info("Creating Table t_tra_creator")

    sql_create_tra_creator_table = """CREATE TABLE IF NOT EXISTS t_transfers_wallet (
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

    logger.info("Getting transfers contract creator")
    tic = time.perf_counter()

    json_tra_creator = []
    current_block = block_from
    end_block = block_to

    while current_block < end_block:
        params = {
            "chainid": chain_id, "module": "account", "action": "tokentx", "address": contract_creator, "startblock": current_block,
            "endblock": end_block, "page": 1, "offset": offset, "sort": "asc", "apikey": key,
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["status"] != "1":
            if data["message"] == "No transactions found":
                break
            else:
                raise Exception(f"Error fetching data: {data['message']} - {data['result']}")

        data_batch = data["result"]
        json_tra_creator.extend(data_batch)

        logger.info(f" Get {len(data_batch)} records")

        if len(data_batch) < offset:
            break

        current_block = int(data_batch[-1]["blockNumber"]) + 1

    # INFO: Store Transfers creator
    logger.info("Store transfers creator")
    if json_tra_creator != []:
        df_tra_store = pd.DataFrame(json_tra_creator)
        df_tra_store.to_sql("t_transfers_wallet", connection, if_exists="append", index=False)
    toc = time.perf_counter()

    message = f"<strong>STORE</strong> - {len(json_tra_creator)} transfers creator...<strong>{toc - tic:0.4f}</strong> seconds"
    logger.info(message.replace("<strong>", "").replace("</strong>", ""))
    # data = json.dumps({"msg": message, "end": False, "error": False, "content": {}})
    # yield f"data:{data}\n\n"

    logger.info(" ")
    logger.info("=====================================================")
    logger.info(f"Collecting Internals contract creator transfers...")
    logger.info("=====================================================")
    logger.info("Creating Table t_internals_wallet")

    sql_create_int_creator_table = """CREATE TABLE IF NOT EXISTS t_internals_wallet (
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

    logger.info("Getting internals contract creator")
    tic = time.perf_counter()

    json_int_creator = []
    current_block = block_from
    end_block = block_to

    while current_block < end_block:
        params = {
            "chainid": chain_id, "module": "account", "action": "txlistinternal", "address": contract_creator, "startblock": current_block,
            "endblock": end_block, "page": 1, "offset": offset, "sort": "asc", "apikey": key,
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["status"] != "1":
            if data["message"] == "No transactions found":
                break
            else:
                raise Exception(f"Error fetching data: {data['message']} - {data['result']}")

        data_batch = data["result"]
        json_int_creator.extend(data_batch)

        logger.info(f" Get {len(data_batch)} records")

        if len(data_batch) < offset:
            break

        current_block = int(data_batch[-1]["blockNumber"]) + 1

    # INFO: Store Internals creator
    logger.info("Store internals creator")
    if json_int_creator != []:
        df_tra_store = pd.DataFrame(json_int_creator)
        df_tra_store.to_sql("t_internals_wallet", connection, if_exists="append", index=False)
    toc = time.perf_counter()

    message = f"<strong>STORE</strong> - {len(json_int_creator)} internals creator...<strong>{toc - tic:0.4f}</strong> seconds"
    logger.info(message.replace("<strong>", "").replace("</strong>", ""))
    # data = json.dumps({"msg": message, "end": False, "error": False, "content": {}})
    # yield f"data:{data}\n\n"

    connection.commit()

    # TODO: Need refactor to _refactor_

    # tags - Transactions - other contract created
    query = f"SELECT DISTINCT(contractAddress) from t_transactions_wallet WHERE `to` = ''"
    cursor.execute(query)
    contracts = cursor.fetchall()
    for c in contracts:
        if not any(w.get("wallet") == c[0] for w in internal_tagging):
            internal_tagging.append({"wallet": c[0], "tag": "Contract Created"})

    # tags - Transactions creator
    query = f"SELECT DISTINCT(`to`) from t_transactions_wallet WHERE (input != '' AND input != '0x') AND `to` != ''"
    cursor.execute(query)
    contracts = cursor.fetchall()
    for c in contracts:
        if not any(w.get("wallet") == c[0] for w in internal_tagging):
            internal_tagging.append({"wallet": c[0], "tag": "Contract"})

    # tags - Transactions creator
    query = f"SELECT DISTINCT(contractAddress) from t_transactions_wallet"
    cursor.execute(query)
    contracts = cursor.fetchall()
    for c in contracts:
        if not any(w.get("wallet") == c[0] for w in internal_tagging):
            internal_tagging.append({"wallet": c[0], "tag": "Contract"})

    # tags - Internals creator
    query = f"SELECT DISTINCT(`to`) from t_internals_wallet WHERE (input != '' AND input != '0x') AND `to` != ''"
    cursor.execute(query)
    contracts = cursor.fetchall()
    for c in contracts:
        if not any(w.get("wallet") == c[0] for w in internal_tagging):
            internal_tagging.append({"wallet": c[0], "tag": "Contract"})

    # tags - Internals creator
    query = f"SELECT DISTINCT(contractAddress) from t_internals_wallet"
    cursor.execute(query)
    contracts = cursor.fetchall()
    for c in contracts:
        if not any(w.get("wallet") == c[0] for w in internal_tagging):
            internal_tagging.append({"wallet": c[0], "tag": "Contract"})

    # TODO: Confirm which this isn't necessary
    # # tags - Transfers creator
    # query = f"SELECT DISTINCT(`to`) from t_transfers_wallet WHERE (input != '' AND input != '0x') AND `to` != ''"
    # cursor.execute(query)
    # contracts = cursor.fetchall()
    # for c in contracts:
    #     if not any(w.get("wallet") == c[0] for w in internal_tagging):
    #         internal_tagging.append({"wallet": c[0], "tag": "Contract"})

    # tags - Transfers creator
    query = f"SELECT DISTINCT(contractAddress) from t_transfers_wallet"
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
    query = f"SELECT DISTINCT(contractAddress) from t_transfers"
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
        if (t['tag'] == 'Contract'):
            idx = idx + 1
            contracts = contracts + t['wallet'] + ','
    contracts_list.append(contracts)

    for l in contracts_list:
        url = f'{base_url}?chainid={chain_id}&module=contract&action=getcontractcreation&contractaddresses=' + l[:-1] + \
           '&apikey=' + key
        response = requests.get(url)

        for r in response.json()['result']:
            if (r['contractCreator'] == contract_creator):
                internal_tagging = [{**t, **{'tag': 'Contract Created'}} if t['wallet'] == r['contractAddress'] else t for t in internal_tagging]

    logger.info(f"Storing tags")
    for t in internal_tagging:
        if (t['wallet'] != ''):
            cursor.execute("""INSERT INTO t_tagging VALUES (?, ?)""", 
                (str(t['wallet']), str(t['tag'])))

    connection.commit()
    connection.close()
    return 0


def eth_db_process(filename):
    # Validate file
    if (not os.path.exists(filename)):
        raise FileNotFoundError("SQLite db file not found")

    # Split in temporary files
    if (not os.path.exists('./tmp')):
        os.makedirs('./tmp')

    # Open db
    connection = sqlite3.connect(filename)
    cursor = connection.cursor()

    tic = time.perf_counter()
    cursor.execute("SELECT * FROM t_contract")
    row = cursor.fetchone()
    column_names = [description[0] for description in cursor.description]
    contract = {column_names[i]: row[i] for i in range(len(column_names))}

    # TODO: Do this in collect stage
    contract['blockchain'] = 'eth'

    with open('./tmp/contract.json', 'w') as outfile:
        json.dump(contract, outfile)
    toc = time.perf_counter()
    logger.info(f"Get contract info in {toc - tic:0.4f} seconds")

    tic = time.perf_counter()
    # NOTE: Search Fallback function
    cursor.execute("SELECT * FROM t_source_abi")
    row = cursor.fetchone()
    column_names = [description[0] for description in cursor.description]
    source_code = {column_names[i]: row[i] for i in range(len(column_names))}
    json_str_source_code = source_code['SourceCode'] 
    contract_abi = source_code['ABI']

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
    df_t = pd.read_sql_query("SELECT * FROM t_transfers ORDER BY timeStamp ASC", connection, parse_dates=['timeStamp'])
    df_i = pd.read_sql_query("SELECT * FROM t_internals ORDER BY timeStamp ASC", connection, parse_dates=['timeStamp'])

    # Split in JSON files
    with open('./tmp/transactions.json', 'w') as outfile:
        df_transaction.to_json(outfile)
    with open('./tmp/transfers.json', 'w') as outfile:
        df_t.to_json(outfile)
    with open('./tmp/internals.json', 'w') as outfile:
        df_i.to_json(outfile)
    toc = time.perf_counter()
    logger.info(f"Split file in {toc - tic:0.4f} seconds")

    # NOTE: For DEBUG (remove)
    df_transaction.to_csv('./tmp/transaction.csv')
    df_t.to_csv('./tmp/transfers.csv')
    df_i.to_csv('./tmp/internals.csv')
    # df_l.to_csv('./tmp/logs.csv')

    native = False
    if (df_i.size > df_t.size):
        native = True
        logger.info(f"Detect NATIVE token")
    else: 
        logger.info(f"Detect NOT NATIVE token")

    # Get unified transaction-internals-transfers
    df_trx_0 = df_transaction[df_transaction['isError'] == 0]
    df_trx_1 = df_trx_0[['timeStamp', 'hash', 'from', 'to', 'value', 'input', 
                         'isError']]
    df_trx_1.insert(len(df_trx_1.columns), "file", "trx")
    df_uni = df_trx_1

    if (not df_t.empty):
        df_tra_0 = df_t
        df_tra_1 = df_tra_0[['timeStamp', 'hash', 'from', 'to', 'value', 'input']]
        df_tra_1.insert(len(df_tra_1.columns), "isError", 0)
        df_tra_1.insert(len(df_tra_1.columns), "file", "tra")

    if (not df_i.empty):
        df_int_0 = df_i
        # print(df_i.info())
        # print(df_i.head())
        df_int_1 = df_int_0[['timeStamp', 'hash', 'from', 'to', 'value', 'input',
                             'isError']]
        df_int_1.insert(len(df_int_1.columns), "file", "int")

    if (not df_t.empty):
        pd_uni = pd.concat([df_uni, df_tra_1], axis=0, ignore_index=True)
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

    # Get token and volume NOTE: Remove death code
    if (native):
        token_name = "ETH"
        # volume = round(df_transaction['value'].sum() / 1e+18, 2) + round(df_i['value'].sum() / 1e+18, 2)
        # volume = round((df_transaction['value'].sum() / 1e+18, 2 + df_i['value'].sum() / 1e+18) / 2, 2)
        volume = df_transaction['value'].sum() + df_i['value'].sum()
        volume = round(volume / 1e+18, 2)
    else:
        # NOTE : Display another tokens
        token = df_t.groupby('tokenSymbol').agg({'value': ['sum','count']})
        token = token.sort_values(by=[('value','count')], ascending=False)  
        token_name = token.index[0]
        # volume = round(token.iloc[0,0] / 1e+18, 2)
        volume = round(float(token.iloc[0,0] / 1e+18) / 2, 2)

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
    if (native):
        # NOTE : I replace the dftemp for df_uni. Remove if it's working
        dftemp = df_uni
        dftemp = dftemp.sort_values(["timeStamp"])

        unique_wallets = len(dftemp['from'].unique())

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
                # WARNING : Remove max_liq
                # if (max_liq < liq):
                #     max_liq = liq
                #     max_liq_date = dftemp["timeStamp"][i]
                if (max_liq_raw < liq_raw):
                    max_liq_raw = liq_raw
                    max_liq_date = dftemp["timeStamp"][i]
            else:
                remain = remain + value

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
        unique_wallets = len(df_t['from'].unique())
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
                    remain = remain + value

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
    df_anomalies = df_anomalies[trx_total_asc['Percentage'] >= 200]
    df_anomalies['Percentage'] = df_anomalies['Percentage'].astype(int)
    with open('./tmp/anomalies.json', 'w') as outfile:
        df_anomalies_json = df_anomalies.to_json(outfile, orient="records")

    # Statistic Percentage
    # TODO: Define the correct percentage in base to time period
    e_0 = trx_total[trx_total['Percentage'] == 0]
    e_0_100 = trx_total[(trx_total['Percentage'] > 0) & (trx_total['Percentage'] < 100)]
    e_100_241 = trx_total[(trx_total['Percentage'] >= 100) & (trx_total['Percentage'] <= 241)]
    e_241 = trx_total[trx_total['Percentage'] > 241]

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
        except:
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

    json_stats = {"contract": address_contract,
                  "fdate": first_date.strftime("%Y/%m/%d - %H:%M:%S"),
                  "ldate": last_date.strftime("%Y/%m/%d - %H:%M:%S"),
                  "token_name": token_name,
                  "native": int(native),
                  "creator": contract_creator,
                  "max_liq": round(max_liq_raw / 1e18, 2),
                  "max_liq_date": max_liq_date.strftime("%Y/%m/%d - %H:%M:%S"),
                  "volume": round(volume_raw / 1e18, 2),
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
    # coloredlogs.install(level=params["config"]["level"], fmt=log_format, logger=logger)
    coloredlogs.install(level="DEBUG", fmt=log_format, logger=logger)
    logger.propagate = False  # NOTE: To prevent duplicates with flask

    filename = os.path.basename(file)
    message = f"<strong>PROCESS</strong> - Processing file...{filename}"
    logger.info(message.replace("<strong>", "").replace("</strong>", ""))
    # data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {"wallet_detail": wallet_detail}})
    data = json.dumps({"msg": f"{message}", "end": False, "error": False, "content": {}})
    yield f"data:{data}\n\n"

    # FIX: Determine Blockchain 
    bsc.bsc_db_process(file)

    message = "<strong>END PROCESS</strong>"
    logger.error(message.replace("<strong>", "").replace("</strong>", ""))
    data = json.dumps({"msg": f"{message}", "end": True, "error": False, "content": {}})
    yield f"data:{data}\n\n"


