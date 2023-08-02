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

# from termcolor import colored
# import coloredlogs, logging
import logging

from web3_input_decoder import InputDecoder # , decode_constructor


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


async def bsc_json_collect(contract_address, block_from, block_to, key, chunk=30000):
    logger.info("=====================================================")
    logger.info("Collecting Contract data")
    logger.info("=====================================================")

    url = 'https://api.bscscan.com/api?module=account&action=txlist&address=' + contract_address + '&startblock=0&endblock=99999999' + \
        '&page=1&offset=1&sort=asc&apikey=' + key 
    response = requests.get(url)

    # Validate API Key
    if (response.json()['message'] == "NOTOK"):
        logger.error("Invalid API Key")
        raise RuntimeError('Invalid API Key')
        
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
    # contract abi
    # HACK: Replace by the following call
    url = 'https://api.bscscan.com/api?module=contract&action=getabi&address=' + contract_address + '&apikey=' + key
    response = requests.get(url)

    json_obj_contract_abi = response.json()['result']

    url = 'https://api.bscscan.com/api?module=contract&action=getsourcecode&address=' + contract_address + '&apikey=' + key
    response = requests.get(url)
    json_obj_source_code = response.json()['result']


    # NOTE: Implement in future
    # get_circulating_supply_by_contract_address - Get circulating supply of token by its contract address
    # async with BscScan(key) as client:
    #     json_result = await client.get_circulating_supply_by_contract_address(
    #             contract_address=contract_address,
    #         )
    # json_str_circ_supply = json.dumps(json_result)
    # json_obj_circ_supply = json.loads(json_str_circ_supply)

    # NOTE: Implement in future
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

    json_total = []
    while startblock < block_to:
        try:
            url = 'https://api.bscscan.com/api?module=account&action=txlist&address=' + contract_address + \
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

    logger.info(" ")
    logger.info("=====================================================")
    logger.info(f"Collecting Contract transfers...")
    logger.info("=====================================================")
    startblock = block_from
    endblock = block_from + chunk

    json_total = []
    while startblock < block_to:
        try:
            url = 'https://api.bscscan.com/api?module=account&action=tokentx&address=' + contract_address + \
                  '&startblock=' + str(startblock) + '&endblock=' + str(endblock) + '&sort=asc&apikey=' + key
            response = requests.get(url)
            json_object = response.json()['result']

            if (len(json_object) > 0):
                logger.info(f"TRANSFERS - From : {startblock} - To : {endblock} - Total TRX Block: {len(json_object)}")
            else:
                logger.info(f"TRANSFERS - From : {startblock} - To : {endblock} - TRANSFERS NOT FOUND")

            json_total += json_object

        except AssertionError:
            logger.info(f"TRANSFERS - From : {startblock} - To : {endblock} - TRANSFERS NOT FOUND")

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

    logger.info(" ")
    logger.info("=====================================================")
    logger.info(f"Collecting Internals transfers...")
    logger.info("=====================================================")
    startblock = block_from
    endblock = block_from + chunk

    json_total = []
    while startblock < block_to:
        try:
            url = 'https://api.bscscan.com/api?module=account&action=txlistinternal&address=' + contract_address + \
                  '&startblock=' + str(startblock) + '&endblock=' + str(endblock) + '&sort=asc&apikey=' + key
            response = requests.get(url)
            json_object = response.json()['result']

            if (len(json_object) > 0):
                logger.info(f"INTERNALS - From : {startblock} - To : {endblock} - Total TRX Block: {len(json_object)}")
            else:
                logger.info(f"INTERNALS - From : {startblock} - To : {endblock} - INTERNALS NOT FOUND")

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

    # NOTE: It ins't necesary yet
    # logger.info(" ")
    # logger.info("=====================================================")
    # logger.info(f"Collecting logs...")
    # logger.info("=====================================================")
    # startblock = block_from
    # endblock = block_from + chunk

    # NOTE: It ins't necesary yet
    # json_total = []
    # while startblock < block_to:
    #     try:
    #         url = 'https://api.bscscan.com/api?module=logs&action=getLogs&address=' + contract_address + \
    #               '&startblock=' + str(startblock) + '&endblock=' + str(endblock) + '&sort=asc&apikey=' + key
    #         response = requests.get(url)
    #         json_object = response.json()['result']

    # NOTE: It ins't necesary yet
    #         if (len(json_object) > 0):
    #             logger.info(f"LOGS - From : {startblock} - To : {endblock} - Total TRX Block: {len(json_object)}")
    #         else:
    #             logger.info(f"LOGS - From : {startblock} - To : {endblock} - LOGS NOT FOUND")

    # NOTE: It ins't necesary yet
    #        json_total += json_object

    # NOTE: It ins't necesary yet
    #    except AssertionError:
    #        logger.info(f"LOGS - From : {startblock} - To : {endblock} - LOGS NOT FOUND")

    # NOTE: It ins't necesary yet
    #    startblock += chunk + 1
    #    endblock += chunk + 1

    # NOTE: It ins't necesary yet
    # diff = int(block_to) - int(block_from)
    # logger.info(" ")
    # logger.info("=====================================================")
    # logger.info("  LOGS TOTAL")
    # logger.info("=====================================================")
    # logger.info(f"  From : {block_from} - To : {block_to}")
    # logger.info(f"  Diff : {diff} - Total TRX : {len(json_total)}")
    # logger.info("=====================================================")
    json_logs = []

    json_logs = json_total

    # Consolidate data
    json_total = {"contract": json_contract,
                  # "getabi": json_str_contract_abi,
                  "getabi": json_obj_contract_abi,
                  "source_code": json_obj_source_code,
                  # "circ_supply": json_str_circ_supply,
                  # "total_supply": json_obj_total_supply,
                  "transactions": json_transaction,
                  "transfers": json_transfer,
                  "internals": json_internals,
                  "logs": json_logs}

    filename = "contract-bsc-" + contract_address + ".json"
    with open(filename, 'w') as outfile:
        json.dump(json_total, outfile)

    # PERF: Increase performanco with async

    bsc_json_process(filename)


def bsc_json_process(filename):
    # Validate file
    if (not os.path.exists(filename)):
        raise FileNotFoundError("JSON File not found")

    # Read JSON file
    tic = time.perf_counter()
    with open(filename) as json_file:
        data = json.load(json_file)
    toc = time.perf_counter()
    logger.info(f"Read file in {toc - tic:0.4f} seconds")
    
    # Split in temporary files
    if (not os.path.exists('./tmp')):
        os.makedirs('./tmp')

    tic = time.perf_counter()
    contract = data['contract']
    with open('./tmp/contract.json', 'w') as outfile:
        json.dump(contract, outfile)

    contract_abi = data['getabi']
    with open('./tmp/contract-abi.json', 'w') as outfile:
        json.dump(contract_abi, outfile)

    source_code = data['source_code']
    # NOTE: Search Fallback function
    json_str_source_code = source_code[0]['SourceCode'] 

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

    # source_code[0]['fallback'] = fallback
    source_code[0]['fallback'] = "true" if fallback else "false"
    source_code[0]['fallback_function'] = fallback_function
    source_code[0]['fallback_code'] = fallback_code
    with open('./tmp/sourcecode.json', 'w') as outfile:
        json.dump(source_code, outfile)

    transactions = data['transactions']
    with open('./tmp/transactions.json', 'w') as outfile:
        json.dump(transactions, outfile)

    transfers = data['transfers']
    with open('./tmp/transfers.json', 'w') as outfile:
        json.dump(transfers, outfile)

    internals = data['internals']
    with open('./tmp/internals.json', 'w') as outfile:
        json.dump(internals, outfile)

    logs = data['logs']
    with open('./tmp/logs.json', 'w') as outfile:
        json.dump(logs, outfile)

    toc = time.perf_counter()
    logger.info(f"Split file in {toc - tic:0.4f} seconds")

    # Preprocess Statistics
    tic = time.perf_counter()
    
    # NOTE: I must reload the files for datatypes (Optimize?)
    df_transaction = pd.read_json('./tmp/transactions.json')
    df_t = pd.read_json('./tmp/transfers.json')
    df_i = pd.read_json('./tmp/internals.json')
    df_l = pd.read_json('./tmp/logs.json')
    print(df_t.info())

    # For DEBUG (remove)
    df_transaction.to_csv('./tmp/transaction.csv')
    df_t.to_csv('./tmp/transfers.csv')
    df_i.to_csv('./tmp/internals.csv')
    df_l.to_csv('./tmp/logs.csv')

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
        token_name = "BNB"
        # volume = round(df_transaction['value'].sum() / 1e+18, 2) + round(df_i['value'].sum() / 1e+18, 2)
        volume = round((df_transaction['value'].sum() / 1e+18, 2 + df_i['value'].sum() / 1e+18) / 2, 2)
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
        # dftemp_transaction = df_transaction[df_transaction['isError'] == 0]
        # dftemp_transaction = dftemp_transaction[['timeStamp','from', 'to', 'value']]
        # dftemp_transaction = dftemp_transaction[dftemp_transaction["value"] != 0]

        # dftemp_i = df_i[['timeStamp', 'from', 'to', 'value']]
        # dftemp = pd.concat([dftemp_transaction, dftemp_i],
        #                    join='inner', ignore_index=True)
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
                day = df_t['timeStamp'][i].strftime("%Y-%m-%d")
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
                    # if (max_liq < liq):
                    #     max_liq = liq
                    #     max_liq_date = df_t["timeStamp"][i]
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
    trx_total = from_trx_axis.join(to_trx_axis)
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
    trx_total_dec = trx_total.sort_values(["Percentage"])
    trx_total_asc = trx_total.sort_values(["Percentage"], ascending=False)

    # Anomalies
    df_anomalies = trx_total_asc[trx_total_asc['wallet'] != address_contract ]
    df_anomalies = df_anomalies[trx_total_asc['Percentage'] >= 200]
    df_anomalies['Percentage'] = df_anomalies['Percentage'].astype(int)
    print(df_anomalies.head())
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

    # Input decoded
    # PERF : Enhance decoder

    # ABI
    contract_abi = data['getabi']
    ABI = json.loads(contract_abi)

    df_hash = df_transaction["hash"][0:]
    input_constructor = df_transaction["input"][0]
    input_column = df_transaction["input"][1:]
    print(f"input_constructor: {input_constructor}")
    # print(f"input_hash: {df_transaction["hash"][0]})

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
            if (source_code[0]['fallback'] == "true"):
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
        trans_in = len(dftemp_transaction)
        trans_out = len(dftemp_i)
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


async def aio_db_transactions(client_session, url, conn, table):    
    startblock = url.split("startblock=")[1].split("&endblock=")[0]
    endblock = url.split("endblock=")[1].split("&sort=")[0]
    logger.info(f"Processing - TRANSACTIONS from {startblock} to {endblock}")

    async with client_session.get(url) as resp:
        data = await resp.json()

        for json_object in data['result']:
            conn.execute(f"""INSERT INTO {table} VALUES 
                           (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                           ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                           """,
                (json_object['blockNumber'],
                 json_object['timeStamp'],
                 json_object['hash'],
                 json_object['nonce'],
                 json_object['blockHash'],
                 json_object['transactionIndex'],
                 json_object['from'],
                 json_object['to'],
                 json_object['value'],
                 json_object['gas'],
                 json_object['gasPrice'],
                 json_object['isError'],
                 json_object['txreceipt_status'],
                 json_object['input'],
                 json_object['contractAddress'],
                 json_object['cumulativeGasUsed'],
                 json_object['gasUsed'],
                 json_object['confirmations'],
                 json_object['methodId'],
                 json_object['functionName']))

        conn.commit()


async def aio_db_transfers(client_session, url, conn, table):    
    startblock = url.split("startblock=")[1].split("&endblock=")[0]
    endblock = url.split("endblock=")[1].split("&sort=")[0]
    logger.info(f"Processing - TRANSFERS from {startblock} to {endblock}")

    async with client_session.get(url) as resp:
        data = await resp.json()

        rows = []
        for json_object in data['result']:

            rows.append((json_object['blockNumber'],
                 json_object['timeStamp'],
                 json_object['hash'],
                 json_object['nonce'],
                 json_object['blockHash'],
                 json_object['from'],
                 json_object['contractAddress'],
                 json_object['to'],
                 json_object['value'],
                 json_object['tokenName'],
                 json_object['tokenSymbol'],
                 json_object['tokenDecimal'],
                 json_object['transactionIndex'],
                 json_object['gas'],
                 json_object['gasPrice'],
                 json_object['gasUsed'],
                 json_object['cumulativeGasUsed'],
                 json_object['input'],
                 json_object['confirmations']))

        if (rows != []):
            conn.executemany(f"""INSERT INTO {table} VALUES 
                             (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                             ?, ?, ?, ?, ?, ?, ?, ?, ?)
                             """,rows)
            conn.commit()


async def aio_db_internals(client_session, url, conn, table):    
    startblock = url.split("startblock=")[1].split("&endblock=")[0]
    endblock = url.split("endblock=")[1].split("&sort=")[0]
    logger.info(f"Processing - INTERNALS from {startblock} to {endblock}")

    async with client_session.get(url) as resp:
        data = await resp.json()

        for json_object in data['result']:
            conn.execute(f"""INSERT INTO {table} VALUES 
                           (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                           """,
                (json_object['blockNumber'],
                 json_object['timeStamp'],
                 json_object['hash'],
                 json_object['from'],
                 json_object['to'],
                 json_object['value'],
                 json_object['contractAddress'],
                 json_object['input'],
                 json_object['type'],
                 json_object['gas'],
                 json_object['gasUsed'],
                 json_object['isError'],
                 json_object['errCode']))

        conn.commit()


async def async_fetch_and_store(urls, conn, type, table):
    Client = aiohttp.ClientSession()
    Tasks = []
    for url in urls:
        if (type == "Transactions"):
            Tasks.append(aio_db_transactions(client_session=Client, url=url, conn=conn, table=table))
        if (type == "Transfers"):
            Tasks.append(aio_db_transfers(client_session=Client, url=url, conn=conn, table=table))
        if (type == "Internals"):
            Tasks.append(aio_db_internals(client_session=Client, url=url, conn=conn, table=table))
        
    try:
        await asyncio.gather(*Tasks)
        await asyncio.sleep(0.2)
    except:
        pass
    finally:
        await Client.close()


def bsc_db_collect_async(contract_address, block_from, block_to, key, filedb, chunk=30000):
    
    try:
        os.remove(filedb)
    except:
        pass
    logger.info(f"Creating db {filedb}")
    connection = sqlite3.connect(filedb)
    cursor = connection.cursor()

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
    url = 'https://api.bscscan.com/api?module=account&action=txlist&address=' + contract_address + '&startblock=0&endblock=99999999' + \
        '&page=1&offset=1&sort=asc&apikey=' + key 
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
        (contract_address, 'bsc', block_from, block_to, first_block['blockNumber'], 
        first_block['hash'], first_block['timeStamp'], first_block['from']))

    connection.commit()

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
    url = 'https://api.bscscan.com/api?module=contract&action=getsourcecode&address=' + contract_address + '&apikey=' + key
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

    # NOTE: Implement in future
    # get_circulating_supply_by_contract_address - Get circulating supply of token by its contract address
    # async with BscScan(key) as client:
    #     json_result = await client.get_circulating_supply_by_contract_address(
    #             contract_address=contract_address,
    #         )
    # json_str_circ_supply = json.dumps(json_result)
    # json_obj_circ_supply = json.loads(json_str_circ_supply)

    # NOTE: Implement in future
    # get_total_supply_by_contract_address - Get circulating supply of token by its contract address
    # async with BscScan(key) as client:
    #     json_result = await client.get_total_supply_by_contract_address(
    #             contract_address=contract_address,
    #         )
    # json_str_total_supply = json.dumps(json_result)
    # json_obj_total_supply = json.loads(json_str_total_supply)

    logger.info("Building URLs")
    startblock = block_from
    endblock = block_from + chunk

    urls_transactions = []
    urls_internals = []
    urls_transfers = []
    urls_trx_creator = []
    urls_int_creator = []
    urls_tra_creator = []
    while startblock < block_to:
        urls_transactions.append('https://api.bscscan.com/api?module=account&action=txlist&address=' + contract_address + \
                  '&startblock=' + str(startblock) + '&endblock=' + str(endblock) + '&sort=asc&apikey=' + key)
        urls_internals.append('https://api.bscscan.com/api?module=account&action=txlistinternal&address=' + contract_address + \
                  '&startblock=' + str(startblock) + '&endblock=' + str(endblock) + '&sort=asc&apikey=' + key)
        urls_transfers.append('https://api.bscscan.com/api?module=account&action=tokentx&address=' + contract_address + \
                  '&startblock=' + str(startblock) + '&endblock=' + str(endblock) + '&sort=asc&apikey=' + key)
        urls_trx_creator.append('https://api.bscscan.com/api?module=account&action=txlist&address=' + contract_creator + \
                  '&startblock=' + str(startblock) + '&endblock=' + str(endblock) + '&sort=asc&apikey=' + key)
        urls_int_creator.append('https://api.bscscan.com/api?module=account&action=txlistinternal&address=' + contract_creator + \
                  '&startblock=' + str(startblock) + '&endblock=' + str(endblock) + '&sort=asc&apikey=' + key)
        urls_tra_creator.append('https://api.bscscan.com/api?module=account&action=tokentx&address=' + contract_creator + \
                  '&startblock=' + str(startblock) + '&endblock=' + str(endblock) + '&sort=asc&apikey=' + key)
        startblock += chunk + 1
        endblock += chunk + 1

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

    logger.info("Getting transactions async")

    start_time = time.time()

    split_urls = [urls_transactions[i:i + 5] for i in range(0, len(urls_transactions), 5)]
    for urls in split_urls:
        asyncio.run(async_fetch_and_store(urls, connection, "Transactions", "t_transactions"))

    end_time = time.time()
    elapsed_time = end_time - start_time
    requests_per_second = len(urls_transactions) / elapsed_time
    
    # Get total transactions registered
    query = f"SELECT COUNT(*) FROM t_transactions"
    cursor.execute(query)
    total = cursor.fetchone()[0]

    logger.info(f"=========================================================")
    logger.info(f" Total requests: {len(urls_transactions)}")
    logger.info(f" Total Blocks: {len(urls_transactions) * chunk}")
    logger.info(f" Total TRX: {total}")
    logger.info(f" Elapsed time: {elapsed_time} seconds")
    logger.info(f" Requests per second: {requests_per_second}")
    logger.info(f"=========================================================")

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

    logger.info("Getting transfers async")

    start_time = time.time()

    split_urls = [urls_transfers[i:i + 5] for i in range(0, len(urls_transfers), 5)]
    for urls in split_urls:
        asyncio.run(async_fetch_and_store(urls, connection, "Transfers", "t_transfers"))

    end_time = time.time()
    elapsed_time = end_time - start_time
    requests_per_second = len(urls_transfers) / elapsed_time
    
    # Get total transactions registered
    query = f"SELECT COUNT(*) FROM t_transfers"
    cursor.execute(query)
    total = cursor.fetchone()[0]

    logger.info(f"=========================================================")
    logger.info(f" Total requests: {len(urls_transfers)}")
    logger.info(f" Total Blocks: {len(urls_transfers) * chunk}")
    logger.info(f" Total TRX: {total}")
    logger.info(f" Elapsed time: {elapsed_time} seconds")
    logger.info(f" Requests per second: {requests_per_second}")
    logger.info(f"=========================================================")

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
                                       isError integer NOT NULL,
                                       errCode text NOT NULL
                                 );"""
    connection.execute(sql_create_internals_table)

    logger.info("Getting internals async")

    start_time = time.time()

    split_urls = [urls_internals[i:i + 5] for i in range(0, len(urls_internals), 5)]
    for urls in split_urls:
        asyncio.run(async_fetch_and_store(urls, connection, "Internals", "t_internals"))

    end_time = time.time()
    elapsed_time = end_time - start_time
    requests_per_second = len(urls_internals) / elapsed_time
    
    # Get total transactions registered
    query = f"SELECT COUNT(*) FROM t_internals"
    cursor.execute(query)
    total = cursor.fetchone()[0]

    logger.info(f"=========================================================")
    logger.info(f" Total requests: {len(urls_internals)}")
    logger.info(f" Total Blocks: {len(urls_internals) * chunk}")
    logger.info(f" Total TRX: {total}")
    logger.info(f" Elapsed time: {elapsed_time} seconds")
    logger.info(f" Requests per second: {requests_per_second}")
    logger.info(f"=========================================================")

    # NOTE: It ins't necesary yet
    # logger.info(" ")
    # logger.info("=====================================================")
    # logger.info(f"Collecting logs...")
    # logger.info("=====================================================")
    # startblock = block_from
    # endblock = block_from + chunk

    # NOTE: It ins't necesary yet
    # json_total = []
    # while startblock < block_to:
    #     try:
    #         url = 'https://api.bscscan.com/api?module=logs&action=getLogs&address=' + contract_address + \
    #               '&startblock=' + str(startblock) + '&endblock=' + str(endblock) + '&sort=asc&apikey=' + key
    #         response = requests.get(url)
    #         json_object = response.json()['result']

    # NOTE: It ins't necesary yet
    #         if (len(json_object) > 0):
    #             logger.info(f"LOGS - From : {startblock} - To : {endblock} - Total TRX Block: {len(json_object)}")
    #         else:
    #             logger.info(f"LOGS - From : {startblock} - To : {endblock} - LOGS NOT FOUND")

    # NOTE: It ins't necesary yet
    #        json_total += json_object

    # NOTE: It ins't necesary yet
    #    except AssertionError:
    #        logger.info(f"LOGS - From : {startblock} - To : {endblock} - LOGS NOT FOUND")

    # NOTE: It ins't necesary yet
    #    startblock += chunk + 1
    #    endblock += chunk + 1

    # NOTE: It ins't necesary yet
    # diff = int(block_to) - int(block_from)
    # logger.info(" ")
    # logger.info("=====================================================")
    # logger.info("  LOGS TOTAL")
    # logger.info("=====================================================")
    # logger.info(f"  From : {block_from} - To : {block_to}")
    # logger.info(f"  Diff : {diff} - Total TRX : {len(json_total)}")
    # logger.info("=====================================================")

    # json_logs = []

    # json_logs = json_total

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
                                   last_block text NOT NULL,
                                   last_date datetime NOT NULL,
                                   last_hash text NOT NULL,
                                   last_to text NOT NULL,
                                   last_from text NOT NULL,
                                   last_value integer NOT NULL,
                                   last_input text NOT NULL
                                 );"""
    cursor.execute(sql_create_contract_table)

    logger.info("Getting first block of contract creator")

    url = 'https://api.bscscan.com/api?module=account&action=txlist&address=' + contract_creator + '&startblock=0&endblock=99999999' + \
        '&page=1&offset=1&sort=asc&apikey=' + key 
    response = requests.get(url)

    first_block_creator = response.json()['result'][0]
    # first_block_number = int(first_block_creator['blockNumber'])

    print(f"Block number (first): {first_block_creator['blockNumber']}")
    print(f"Hash (first) : {first_block_creator['hash']}")
    print(f"Timestamp (first) : {first_block_creator['timeStamp']}")
    print(f"From (first) : {first_block_creator['from']}")  # La que es distinta hay que resaltarla y dibujar esta transaccion
    print(f"To (first) : {first_block_creator['to']}")
    print(f"Value (first) : {first_block_creator['value']}")
    print(f"Input (first) : {first_block_creator['input']}")
    print ("============================================================")
    # TODO: Do we need internals and BEP20?

    url_home = "https://bscscan.com/address/" + contract_creator 
    url_tokens = "https://bscscan.com/address-tokenpage?m=normal&a=" + contract_creator

    # Home
    scraper = cloudscraper.create_scraper()
    r_home = scraper.get(url_home)

    html_doc = BeautifulSoup(r_home.content, "html.parser")
    div_card_body_container = html_doc.find_all('div', class_='card-body')
    balance_container = div_card_body_container[0].find_all('div', class_='row')

    # Balances
    balances = []
    # Get BNB
    balance = balance_container[0].find_all('div')
    balance_bnb = balance[1].text.split(' ')[0]
    balances.append(balance_bnb)
    print(f"Balance de BNB : {balance_bnb}")

    # Get USD del BNB
    # balance = balance_container[1].find_all('div')
    # balance_usd = balance[1].text
    # print(f"Balance de USD : {balance_usd} (Esto es en base a el valor actual, por lo que tenes que actualizarlo)")

    # Get USD de otras
    # balance = balance_container[2].find('a', id='availableBalanceDropdown')
    # balance_tok = balance
    # print(f"Balance de USD : {balance_tok.contents[0].strip()} (Esto es en base a el valor actual, por lo que tenes que actualizarlo)")
    # print(f"Balance de USD : {balance_tok.span['title']} (Esto es en base a el valor actual, por lo que tenes que actualizarlo)")

    balance_list = balance_container[2].find('ul', class_='list list-unstyled mb-0')
    token_list = balance_list.find_all('li', class_='list-custom-BEP-20')
    for i in token_list:
        balances.append(i.text)

    logger.info("Getting last block of contract creator")
    # print(f"===============================================")
    # print(f"= Transacciones ===============================")
    table = div_card_body_container[2].find_all('table', class_='table table-hover')[0]
    tbody = table.find('tbody')
    td = tbody.tr.find_all('td')
    # print(td)
    last_block_number = td[3].text
    last_time_trx = td[4].span.text
    last_from_trx = td[6].span.text
    try:
        last_to_trx = td[8].span.a['href'].split("/")[-1]
    except Exception:
        try: 
            last_to_trx = td[8].a['href'].split("/")[-1]
        except Exception:
            last_to_trx = "N/A"
    last_value_trx = td[9].text
    print(f"Block : {last_block_number}")
    print(f"Time : {last_time_trx}")
    print(f"From : {last_from_trx}")
    print(f"To : {last_to_trx}")
    print(f"Value : {last_value_trx}")

    url = f'https://api.bscscan.com/api?module=account&action=txlist&address={contract_creator}' + \
        f'&startblock={last_block_number}&endblock={last_block_number}' + \
        f'&page=1&offset=1&sort=asc&apikey={key}'
    response = requests.get(url)

    last_block_creator = response.json()['result'][-1]

    # NOTE: Implement in FUTURE
    # print(f"===============================================")
    # print(f"= Internals ===================================")
    # table = div_card_body_container[2].find_all('table', class_='table table-hover')[1]
    # tbody = table.find('tbody')
    # try: 
    #     td = tbody.tr.find_all('td')
    #     print(td)
    #     last_time_int = td[2].span.text
    #     last_from_int = td[4].text
    #     last_to_int = td[6].span['title']
    #     last_value_int = td[7].text
    #     print(f"Time : {last_time_int}")
    #     print(f"From : {last_from_int}")
    #     print(f"To : {last_to_int}")
    #     print(f"Value : {last_value_int}")
    # except Exception:
    #     last_time_int = "N/A"
    #     last_from_int = "N/A"
    #     last_to_int = "N/A"
    #     last_value_int = "N/A"
    #     print(f"Time : {last_time_int}")
    #     print(f"From : {last_from_int}")
    #     print(f"To : {last_to_int}")
    #     print(f"Value : {last_value_int}")


    # NOTE: Implement in FUTURE
    # print(f"===============================================")
    # print(f"= BEP20 =======================================")
    # # Tokens
    # # r_tokens = requests.get(url_tokens)
    # r_tokens = scraper.get(url_tokens)
    # html_tok = BeautifulSoup(r_tokens.text, "html.parser")
    # # print(r_tokens.content)
    # # div_card_body_container = html_tok.find_all('div', class_='card-body')
    # # balance_container = div_card_body_container[0].find_all('div', class_='row')
    # # table = div_card_body_container[2].find_all('table', class_='table table-hover')[2]
    # table = html_tok.find('table', class_='table table-hover')
    # tbody = table.find('tbody')
    # td = tbody.tr.find_all('td')
    # print(td)
    # # print(td.span.text)
    # # print(td.span['title'])
    # last_time_bep = td[2].span.text
    # try: 
    #     last_from_bep = td[4].span['title']
    # except Exception:
    #     try:
    #         last_from_bep = td[4].a['href'].split("/")[-1]
    #     except Exception:
    #         last_from_bep = "N\A"
    # last_to_bep = td[6].text
    # last_value_bep = td[7].text
    # print(f"Time : {last_time_bep}")
    # print(f"From : {last_from_bep}")
    # print(f"To : {last_to_bep}")
    # print(f"Value : {last_value_bep}")

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

    logger.info("Storing first and last block info of contract creator")
    cursor.execute("""INSERT INTO t_contract_creator VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
        (contract_creator,
         block_from,
         block_to,
         first_block_creator['blockNumber'],
         first_block_creator['timeStamp'].strftime("%Y/%m/%d - %H:%M:%S"),
         first_block_creator['hash'],
         first_block_creator['to'],
         first_block_creator['from'],
         pyround.pyround(first_block_creator['value'],8),
         first_block_creator['functionName'],
         last_block_creator['blockNumber'],
         last_block_creator['timeStamp'].strftime("%Y/%m/%d - %H:%M:%S"),
         last_block_creator['hash'],
         last_block_creator['to'],
         last_block_creator['from'],
         pyround.pyround(last_block_creator['value'],8),
         last_block_creator['functionName'],
         ""))
         # last_block_number,
         # last_time_trx,
         # "",  # TODO: Falta HASH
         # last_to_trx,
         # last_from_trx,
         # pyround.pyround(last_value_trx,8),
         # ""))  # TODO: Input
 
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

    logger.info("Getting transactions of contract creator async")

    start_time = time.time()

    split_urls = [urls_tra_creator[i:i + 5] for i in range(0, len(urls_tra_creator), 5)]
    for urls in split_urls:
        asyncio.run(async_fetch_and_store(urls, connection, "Transactions", "t_transactions_wallet"))

    end_time = time.time()
    elapsed_time = end_time - start_time
    requests_per_second = len(urls_tra_creator) / elapsed_time
    
    # Get total transactions registered
    query = f"SELECT COUNT(*) FROM t_transactions_wallet"
    cursor.execute(query)
    total = cursor.fetchone()[0]

    logger.info(f"=========================================================")
    logger.info(f" Total requests: {len(urls_tra_creator)}")
    logger.info(f" Total Blocks: {len(urls_tra_creator) * chunk}")
    logger.info(f" Total TRX: {total}")
    logger.info(f" Elapsed time: {elapsed_time} seconds")
    logger.info(f" Requests per second: {requests_per_second}")
    logger.info(f"=========================================================")
    
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

    logger.info("Getting transfers contract creator async")

    start_time = time.time()

    split_urls = [urls_tra_creator[i:i + 5] for i in range(0, len(urls_tra_creator), 5)]
    for urls in split_urls:
        asyncio.run(async_fetch_and_store(urls, connection, "Transfers", "t_transfers_wallet"))

    end_time = time.time()
    elapsed_time = end_time - start_time
    requests_per_second = len(urls_tra_creator) / elapsed_time
    
    # Get total transactions registered
    query = f"SELECT COUNT(*) FROM t_transfers_wallet"
    cursor.execute(query)
    total = cursor.fetchone()[0]

    logger.info(f"=========================================================")
    logger.info(f" Total requests: {len(urls_tra_creator)}")
    logger.info(f" Total Blocks: {len(urls_tra_creator) * chunk}")
    logger.info(f" Total TRX: {total}")
    logger.info(f" Elapsed time: {elapsed_time} seconds")
    logger.info(f" Requests per second: {requests_per_second}")
    logger.info(f"=========================================================")

    logger.info(" ")
    logger.info("=====================================================")
    logger.info(f"Collecting Internals contract creator transfers...")
    logger.info("=====================================================")
    logger.info("Creating Table t_internals_wsllet")

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
                                      isError integer NOT NULL,
                                      errCode text NOT NULL
                                 );"""
    connection.execute(sql_create_int_creator_table)

    logger.info("Getting internals contract creator async")

    start_time = time.time()

    split_urls = [urls_int_creator[i:i + 5] for i in range(0, len(urls_int_creator), 5)]
    for urls in split_urls:
        asyncio.run(async_fetch_and_store(urls, connection, "Internals", "t_internals_wallet"))

    end_time = time.time()
    elapsed_time = end_time - start_time
    requests_per_second = len(urls_int_creator) / elapsed_time
    
    # Get total transactions registered
    query = f"SELECT COUNT(*) FROM t_internals_wallet"
    cursor.execute(query)
    total = cursor.fetchone()[0]

    logger.info(f"=========================================================")
    logger.info(f" Total requests: {len(urls_int_creator)}")
    logger.info(f" Total Blocks: {len(urls_int_creator) * chunk}")
    logger.info(f" Total TRX: {total}")
    logger.info(f" Elapsed time: {elapsed_time} seconds")
    logger.info(f" Requests per second: {requests_per_second}")
    logger.info(f"=========================================================")


    connection.close()
    return 0


def bsc_db_process(filename):
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
    contract['blockchain'] = 'bsc'

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
        token_name = "BNB"
        # volume = round(df_transaction['value'].sum() / 1e+18, 2) + round(df_i['value'].sum() / 1e+18, 2)
        volume = round((df_transaction['value'].sum() / 1e+18, 2 + df_i['value'].sum() / 1e+18) / 2, 2)
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
        trans_in = len(dftemp_transaction)
        trans_out = len(dftemp_i)
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
