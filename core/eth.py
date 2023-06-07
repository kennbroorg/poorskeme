#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import asyncio
import json
import pandas as pd
import time
import os.path
import requests
# from bscscan import BscScan

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

    # contract
    url = 'https://api.etherscan.io/api?module=contract&action=getabi&address=' + contract_address + '&apikey=' + key
    response = requests.get(url)

    json_obj_contract_abi = response.json()['result']

    url = 'https://api.etherscan.io/api?module=contract&action=getsourcecode&address=' + contract_address + '&apikey=' + key
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

    logger.info(" ")
    logger.info("=====================================================")
    logger.info(f"Collecting Contract transfers...")
    logger.info("=====================================================")
    startblock = block_from
    endblock = block_from + chunk

    json_total = []
    while startblock < block_to:
        try:
            url = 'https://api.etherscan.io/api?module=account&action=tokentx&address=' + contract_address + \
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
            url = 'https://api.etherscan.io/api?module=account&action=txlistinternal&address=' + contract_address + \
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

    logger.info(" ")
    logger.info("=====================================================")
    logger.info(f"Collecting logs...")
    logger.info("=====================================================")
    startblock = block_from
    endblock = block_from + chunk

    json_total = []
    while startblock < block_to:
        try:
            url = 'https://api.etherscan.io/api?module=logs&action=getLogs&address=' + contract_address + \
                  '&startblock=' + str(startblock) + '&endblock=' + str(endblock) + '&sort=asc&apikey=' + key
            response = requests.get(url)
            json_object = response.json()['result']

            if (len(json_object) > 0):
                logger.info(f"LOGS - From : {startblock} - To : {endblock} - Total TRX Block: {len(json_object)}")
            else:
                logger.info(f"LOGS - From : {startblock} - To : {endblock} - LOGS NOT FOUND")

            json_total += json_object

        except AssertionError:
            logger.info(f"LOGS - From : {startblock} - To : {endblock} - LOGS NOT FOUND")

        startblock += chunk + 1
        endblock += chunk + 1

    diff = int(block_to) - int(block_from)
    logger.info(" ")
    logger.info("=====================================================")
    logger.info("  LOGS TOTAL")
    logger.info("=====================================================")
    logger.info(f"  From : {block_from} - To : {block_to}")
    logger.info(f"  Diff : {diff} - Total TRX : {len(json_total)}")
    logger.info("=====================================================")

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

    filename = "contract-eth-" + contract_address + ".json"
    with open(filename, 'w') as outfile:
        json.dump(json_total, outfile)

    # PERF: Increase performanco with async

    eth_json_process(filename)


def eth_json_process(filename):
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

    # HACK: For DEBUG (remove)
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
        df_tra_1['isError'] = 0
        df_tra_1['file'] = 'tra'

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
        token_name = "ETH"
        # volume = round(df_transaction['value'].sum() / 1e+18, 2) + round(df_i['value'].sum() / 1e+18, 2)
        volume = df_transaction['value'].sum() + df_i['value'].sum()
        volume = round(volume / 1e+18, 2)
        # volume = round((df_transaction['value'].sum() / 1e+18, 2 + df_i['value'].sum() / 1e+18) / 2, 2)
    else:
        # NOTE : Display another tokens
        token = df_t.groupby('tokenSymbol').agg({'value': ['sum','count']})  # NOTE: Use for anomalies
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
    trx_total["Percentage"] = trx_total["value_in"] * 100 / trx_total['value_out']
    trx_total_dec = trx_total.sort_values(["Percentage"])
    trx_total_asc = trx_total.sort_values(["Percentage"], ascending=False)

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
    # logger.info(f"ABI type : {type(contract_abi)}")

    ABI = json.loads(contract_abi)
    # ABI = json.loads(ABI)

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
