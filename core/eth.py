#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import asyncio
import json
import pandas as pd
import time
import os.path
import requests
from bscscan import BscScan

from termcolor import colored
import coloredlogs, logging

from web3_input_decoder import InputDecoder, decode_constructor

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


async def eth_json_collect(contract_address, block_from, block_to, key, chunk=30000):
    logger.info("=====================================================")
    logger.info("Collecting Contract data")
    logger.info("=====================================================")

    # url = 'https://api.bscscan.com/api?module=account&action=txlist&address=' + contract_address + '&startblock=0&endblock=99999999' + \
    #     '&page=1&offset=1&sort=asc&apikey=' + key 
    url = 'https://api.etherscan.io/api?module=account&action=txlist&address=' + contract_address + '&startblock=0&endblock=99999999' + \
        '&page=1&offset=1&sort=asc&apikey=' + key
    response = requests.get(url)
    first_block = response.json()['result'][0]

    if (block_from == 0):
        block_from = int(first_block['blockNumber'])

    json_contract = {"contract": contract_address, 
                     "block_from": block_from,
                     "block_to": block_to, 
                     "first_block": first_block['blockNumber'],
                     "transaction_creation": first_block['hash'],
                     "date_creation": first_block['timeStamp'],
                     "creator": first_block['from']}
    print('First Block')
    print(json_contract)

    # contract
    url = 'https://api.etherscan.io/api?module=contract&action=getabi&address=' + contract_address + '&apikey=' + key
    response = requests.get(url)

    # async with BscScan(key) as client:
    #     json_result = await client.get_contract_abi(
    #             contract_address=contract_address,
    #         )
    # json_str_contract_abi = json.dumps(json_result)
    json_obj_contract_abi = response.json()['result']
    print('ABI')
    print(json_obj_contract_abi)

    # async with BscScan(key) as client:
    #     json_result = await client.get_contract_source_code(
    #             contract_address=contract_address,
    #         )
    # json_str_source_code = json.dumps(json_result)
    # json_obj_source_code = json.loads(json_str_source_code)
    url = 'https://api.etherscan.io/api?module=contract&action=getsourcecode&address=' + contract_address + '&apikey=' + key
    response = requests.get(url)
    json_obj_source_code = response.json()['result']
    print('Source Code')
    print(json_obj_source_code)

    # TODO : Implement in future
    # get_circulating_supply_by_contract_address - Get circulating supply of token by its contract address
    # async with BscScan(key) as client:
    #     json_result = await client.get_circulating_supply_by_contract_address(
    #             contract_address=contract_address,
    #         )
    # json_str_circ_supply = json.dumps(json_result)
    # json_obj_circ_supply = json.loads(json_str_circ_supply)

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
    startblock = block_from
    endblock = block_from + chunk

    print("********************************")
    print(f"Start    : {startblock}")
    print(f"End      : {endblock}")
    print(f"Block fr : {block_from}")
    print(f"Block to : {block_to}")
    print(f"Chunk    : {chunk}")
    print("********************************")

    json_total = []
    while startblock < block_to:
        try:
    #         async with BscScan(key) as client:
    #             json_result = await client.get_normal_txs_by_address(
    #                     address=contract_address,
    #                     startblock=startblock,
    #                     endblock=endblock,
    #                     sort="asc"
    #                 )
    #         json_str = json.dumps(json_result)
    #         json_object = json.loads(json_str)
            url = 'https://api.etherscan.io/api?module=account&action=txlist&address=' + contract_address + \
                  '&startblock=' + str(startblock) + '&endblock=' + str(endblock) + '&sort=asc&apikey=' + key
            response = requests.get(url)
            json_object = response.json()['result']

            if (len(json_object) > 0):
                logger.info(f"TRANSACTIONS - From : {startblock} - To : {endblock} - Total TRX Block: {len(json_object)}")
            else:
                logger.info(f"TRANSACTIONS - From : {startblock} - To : {endblock} - TRANSACTION NOT FOUND")

            json_total += json_object

        except AssertionError:
            logger.info(f"TRANSACTIONS - From : {startblock} - To : {endblock} - TRANSACTION NOT FOUND")

        startblock += chunk + 1
        endblock += chunk + 1

    diff = int(block_to) - int(block_from)
    logger.info(" ")
    logger.info("=====================================================")
    logger.info("  TRANSACTIONS TOTAL")
    logger.info("=====================================================")
    logger.info(f"  From : {block_from} - To : {block_to}")
    logger.info(f"  Diff : {diff} - Total TRX : {len(json_total)}")
    logger.info("=====================================================")

    json_transaction = json_total
    print('TRXs')
    print(json_transaction)

    logger.info(" ")
    logger.info("=====================================================")
    logger.info(f"Collecting Contract transfers...")
    logger.info("=====================================================")
    startblock = block_from
    endblock = block_from + chunk

    json_total = []
    while startblock < block_to:
        try:
            # async with BscScan(key) as client:
            #     json_result = await client.get_bep20_token_transfer_events_by_address(
            #             address=contract_address,
            #             startblock=startblock,
            #             endblock=endblock,
            #             sort="asc"
            #         )
            # json_str = json.dumps(json_result)
            # json_object = json.loads(json_str)
            # url = 'https://api.etherscan.io/api?module=account&action=tokentx&contractaddress=' + contract_address + \
            #       '&address=' + address + '&startblock=' + str(startblock) + '&endblock=' + str(endblock) + '&sort=asc&apikey=' + key
            url = 'https://api.etherscan.io/api?module=account&action=tokentx&address=' + contract_address + \
                  '&startblock=' + str(startblock) + '&endblock=' + str(endblock) + '&sort=asc&apikey=' + key
            # url = 'https://api.etherscan.io/api?module=account&action=txlist&address=' + contract_address + \
            #       '&startblock=' + str(startblock) + '&endblock=' + str(endblock) + '&sort=asc&apikey=' + key
            response = requests.get(url)
            json_object = response.json()['result']

            if (len(json_object) > 0):
                logger.info(f"TRANSACTIONS - From : {startblock} - To : {endblock} - Total TRX Block: {len(json_object)}")
            else:
                logger.info(f"TRANSACTIONS - From : {startblock} - To : {endblock} - TRANSACTION NOT FOUND")

            json_total += json_object

        except AssertionError:
            logger.info(f"TRANSFER - From : {startblock} - To : {endblock} - TRANSFER NOT FOUND")

        startblock += chunk + 1
        endblock += chunk + 1

    diff = int(block_to) - int(block_from)
    logger.info(" ")
    logger.info("=====================================================")
    logger.info("  TRANSFER TOTAL")
    logger.info("=====================================================")
    logger.info(f"  From : {block_from} - To : {block_to}")
    logger.info(f"  Diff : {diff} - Total TRX : {len(json_total)}")
    logger.info("=====================================================")

    json_transfer = json_total
    print('Transfers')
    print(json_transfer)
    # ERROR : No colecta nada

    logger.info(" ")
    logger.info("=====================================================")
    logger.info(f"Collecting Internals transfers...")
    logger.info("=====================================================")
    startblock = block_from
    endblock = block_from + chunk

    json_total = []
    while startblock < block_to:
        try:
            # async with BscScan(key) as client:
            #     json_result = await client.get_internal_txs_by_address(
            #             address=contract_address,
            #             startblock=startblock,
            #             endblock=endblock,
            #             sort="asc"
            #         )
            # json_str = json.dumps(json_result)
            # json_object = json.loads(json_str)
            url = 'https://api.etherscan.io/api?module=account&action=txlistinternal&address=' + contract_address + \
                  '&startblock=' + str(startblock) + '&endblock=' + str(endblock) + '&sort=asc&apikey=' + key
            # url = 'https://api.etherscan.io/api?module=account&action=tokentx&address=' + contract_address + \
            #       '&startblock=' + str(startblock) + '&endblock=' + str(endblock) + '&sort=asc&apikey=' + key
            response = requests.get(url)
            json_object = response.json()['result']

            if (len(json_object) > 0):
                logger.info(f"TRANSACTIONS - From : {startblock} - To : {endblock} - Total TRX Block: {len(json_object)}")
            else:
                logger.info(f"TRANSACTIONS - From : {startblock} - To : {endblock} - TRANSACTION NOT FOUND")

            json_total += json_object

        except AssertionError:
            logger.info(f"INTERNALS - From : {startblock} - To : {endblock} - TRANSFER NOT FOUND")

        startblock += chunk + 1
        endblock += chunk + 1

    diff = int(block_to) - int(block_from)
    logger.info(" ")
    logger.info("=====================================================")
    logger.info("  INTERNALS TOTAL")
    logger.info("=====================================================")
    logger.info(f"  From : {block_from} - To : {block_to}")
    logger.info(f"  Diff : {diff} - Total TRX : {len(json_total)}")
    logger.info("=====================================================")

    json_internals = json_total
    print('Internals')
    print(json_internals)

    # # Consolidate data
    # json_total = {"contract": json_contract,
    #               "getabi": json_str_contract_abi,
    #               "source_code": json_obj_source_code,
    #               "circ_supply": json_str_circ_supply,
    #               "total_supply": json_obj_total_supply,
    #               "transactions": json_transaction,
    #               "transfers": json_transfer,
    #               "internals": json_internals}

    # filename = "contract-" + contract_address + ".json"
    # with open(filename, 'w') as outfile:
    #     json.dump(json_total, outfile)

    # eth_json_process(filename)


