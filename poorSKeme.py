#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import asyncio
import json
import pandas as pd
import argparse
import yaml
import textwrap
import time
import os.path
from bscscan import BscScan

import multiprocessing
import http.server
import socketserver
from termcolor import colored
import coloredlogs, logging

from api_poorSKeme import create_application


# create a logger object.
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')


__author__ = "KennBro"
__copyright__ = "Copyright 2022, Personal Research"
__credits__ = ["KennBro"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "KennBro"
__email__ = "kennbro <at> protonmail <dot> com"
__status__ = "Development"


def flaskServer(ip='127.0.0.1', port=5000):
    app = create_application()
    # app.run(host=ip, port=port, debug=True)
    logger.info("Flask serving...")
    app.run(port=port, debug=True, host=ip, use_reloader=False)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="./frontend/dist/", **kwargs)


def httpServer():
    PORT = 4200
    logger.info("HTTPD serving...")
    with socketserver.TCPServer(("", PORT), Handler) as httpd_server:
        httpd_server.serve_forever()


async def save_json(contract_address, block_from, block_to, key, chunk=30000):
    logger.info("=====================================================")
    logger.info("Collecting Contract data")
    logger.info("=====================================================")

    json_contract = {"contract": contract_address, 
                     "block_from": block_from,
                     "block_to": block_to}
    # contract
    async with BscScan(key) as client:
        json_result = await client.get_contract_abi(
                contract_address=contract_address,
            )
    json_str_contract_abi = json.dumps(json_result)
    json_obj_contract_abi = json.loads(json_str_contract_abi)

    async with BscScan(key) as client:
        json_result = await client.get_contract_source_code(
                contract_address=contract_address,
            )
    json_str_source_code = json.dumps(json_result)
    json_obj_source_code = json.loads(json_str_source_code)

    # get_circulating_supply_by_contract_address - Get circulating supply of token by its contract address
    async with BscScan(key) as client:
        json_result = await client.get_circulating_supply_by_contract_address(
                contract_address=contract_address,
            )
    json_str_circ_supply = json.dumps(json_result)
    json_obj_circ_supply = json.loads(json_str_circ_supply)

    # get_total_supply_by_contract_address - Get circulating supply of token by its contract address
    async with BscScan(key) as client:
        json_result = await client.get_total_supply_by_contract_address(
                contract_address=contract_address,
            )
    json_str_total_supply = json.dumps(json_result)
    json_obj_total_supply = json.loads(json_str_total_supply)

    logger.info(" ")
    logger.info("=====================================================")
    logger.info("Collecting Contract transactions")
    logger.info("=====================================================")
    startblock = block_from
    endblock = block_from + chunk

    json_total = []
    while startblock < block_to:
        try:
            async with BscScan(key) as client:
                json_result = await client.get_normal_txs_by_address(
                        address=contract_address,
                        startblock=startblock,
                        endblock=endblock,
                        sort="asc"
                    )
            json_str = json.dumps(json_result)
            json_object = json.loads(json_str)

            logger.info(f"TRANSACTIONS - From : {startblock} - To : {endblock} - Total TRX Block: {len(json_object)}")

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
            async with BscScan(key) as client:
                json_result = await client.get_bep20_token_transfer_events_by_address(
                        address=contract_address,
                        startblock=startblock,
                        endblock=endblock,
                        sort="asc"
                    )
            json_str = json.dumps(json_result)
            json_object = json.loads(json_str)

            logger.info(f"TRANSFER - From : {startblock} - To : {endblock} - Total TRX Block: {len(json_object)}")

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

    logger.info(" ")
    logger.info("=====================================================")
    logger.info(f"Collecting Internals transfers...")
    logger.info("=====================================================")
    startblock = block_from
    endblock = block_from + chunk

    json_total = []
    while startblock < block_to:
        try:
            async with BscScan(key) as client:
                json_result = await client.get_internal_txs_by_address(
                        address=contract_address,
                        startblock=startblock,
                        endblock=endblock,
                        sort="asc"
                    )
            json_str = json.dumps(json_result)
            json_object = json.loads(json_str)

            logger.info(f"INTERNALS - From : {startblock} - To : {endblock} - Total TRX Block: {len(json_object)}")

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

    # Consolidate data
    json_total = {"contract": json_contract,
                  "getabi": json_str_contract_abi,
                  "source_code": json_obj_source_code,
                  "circ_supply": json_str_circ_supply,
                  "total_supply": json_obj_total_supply,
                  "transactions": json_transaction,
                  "transfers": json_transfer,
                  "internals": json_internals}

    filename = "contract-" + contract_address + ".json"
    with open(filename, 'w') as outfile:
        json.dump(json_total, outfile)

    process_json(filename)


def process_json(filename):
    # Validate file
    if (not os.path.exists(filename)):
        raise("JSON File not found")

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

    toc = time.perf_counter()
    logger.info(f"Split file in {toc - tic:0.4f} seconds")

    # Preprocess Statistics
    tic = time.perf_counter()
    
    # I must reload the files for datatypes (Optimize?)
    df_transaction = pd.read_json('./tmp/transactions.json')
    df_t = pd.read_json('./tmp/transfers.json')
    df_i = pd.read_json('./tmp/internals.json')

    native = False
    if (df_i.size > df_t.size):
        native = True

    # Get contract creator
    contract_creator = df_transaction["from"][0]

    # Get token and volume
    if (native):
        token_name = "Native Token"  # TODO 
        volume = round(df_transaction['value'].sum() / 1e+18, 2) + round(df_i['value'].sum() / 1e+18, 2)
    else:
        token = df_t.groupby('tokenSymbol').agg({'value': ['sum','count']})  # TODO: Use for anomalies
        token = token.sort_values(by=[('value','count')], ascending=False)  
        token_name = token.index[0]
        volume = round(token.iloc[0,0] / 1e+18, 2)

    # Liquidity and dates
    address_contract = contract["contract"].lower()
    liq = 0
    max_liq = 0
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
        dftemp_transaction = df_transaction[df_transaction['isError'] == 0]
        dftemp_transaction = dftemp_transaction[['timeStamp','from', 'to', 'value']]
        dftemp_transaction = dftemp_transaction[dftemp_transaction["value"] != 0]

        dftemp_i = df_i[['timeStamp', 'from', 'to', 'value']]
        dftemp = pd.concat([dftemp_transaction, dftemp_i],
                           join='inner', ignore_index=True)
        dftemp = dftemp.sort_values(["timeStamp"])

        unique_wallets = len(dftemp['from'].unique())

        for i in dftemp.index: 
            value = round(dftemp["value"][i] / 1e+18, 2)
            address_from = dftemp["from"][i]
            address_to = dftemp["to"][i]

            if (address_from == address_contract):
                liq = liq - value
                trx_out = trx_out + value
                trx_out_day = trx_out_day + value
            elif (address_to == address_contract):
                liq = liq + value
                trx_in = trx_in + value
                trx_in_day = trx_in_day + value
                if (max_liq < liq):
                    max_liq = liq
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
        last_date = dftemp['timeStamp'].iloc[-1]  # TODO : When Liq == 0

    else:
        unique_wallets = len(df_t['from'].unique())
        for i in df_t.index: 
            if (df_t["tokenSymbol"][i] == token_name):
                value = round(df_t["value"][i] / 1e+18, 2)
                address_from = df_t["from"][i].lower()
                address_to = df_t["to"][i].lower()

                if (address_from == address_contract):
                    liq = liq - value
                    trx_out = trx_out + value
                    trx_out_day = trx_out_day + value
                elif (address_to == address_contract):
                    liq = liq + value
                    trx_in = trx_in + value
                    trx_in_day = trx_in_day + value
                    if (max_liq < liq):
                        max_liq = liq
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
    from_trx.set_axis(['value_out', 'count_out'], axis=1, inplace=True)
    to_trx = df_t.groupby('to').agg({'value': ['sum','count']})
    to_trx.set_axis(['value_in', 'count_in'], axis=1, inplace=True)

    # Merge
    trx_total = from_trx.join(to_trx)
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

    # Porcentajes estadisticos
    e_0 = trx_total[trx_total['Percentage'] == 0]
    e_0_100 = trx_total[(trx_total['Percentage'] > 0) & (trx_total['Percentage'] < 100)]
    e_100_241 = trx_total[(trx_total['Percentage'] >= 100) & (trx_total['Percentage'] <= 241)]
    e_241 = trx_total[trx_total['Percentage'] > 241]

    investments = []
    investments.append({"name": "Total Loses", "value": len(e_0)})
    investments.append({"name": "Loses", "value": len(e_0_100)})
    investments.append({"name": "Earnings", "value": len(e_100_241)})
    investments.append({"name": "Top Profit", "value": len(e_241)})

    json_stats = {"contract": address_contract,
                  "fdate": first_date.strftime("%Y/%m/%d - %H:%M:%S"),
                  "ldate": last_date.strftime("%Y/%m/%d - %H:%M:%S"),
                  "token_name": token_name,
                  "native": int(native),
                  "creator": contract_creator,
                  "max_liq": max_liq,
                  "max_liq_date": max_liq_date.strftime("%Y/%m/%d - %H:%M:%S"),
                  "volume": volume,
                  "wallets": unique_wallets,
                  "investments": investments,
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
    if (native):  # TODO : For native
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


if __name__ == "__main__":

    # Read bscscan Key
    with open(r'./API.yaml') as file:
        key = yaml.load(file, Loader=yaml.FullLoader)

    print("""
$$$$$$$\                                       $$$$$$\  $$\   $$\                                  
$$  __$$\                                     $$  __$$\ $$ | $$  |                                 
$$ |  $$ | $$$$$$\   $$$$$$\   $$$$$$\        $$ /  \__|$$ |$$  / $$$$$$\  $$$$$$\$$$$\   $$$$$$\  
$$$$$$$  |$$  __$$\ $$  __$$\ $$  __$$\       \$$$$$$\  $$$$$  / $$  __$$\ $$  _$$  _$$\ $$  __$$\ 
$$  ____/ $$ /  $$ |$$ /  $$ |$$ |  \__|       \____$$\ $$  $$<  $$$$$$$$ |$$ / $$ / $$ |$$$$$$$$ |
$$ |      $$ |  $$ |$$ |  $$ |$$ |            $$\   $$ |$$ |\$$\ $$   ____|$$ | $$ | $$ |$$   ____|
$$ |      \$$$$$$  |\$$$$$$  |$$ |            \$$$$$$  |$$ | \$$\\$$$$$$$\ $$ | $$ | $$ |\$$$$$$$\ 
\__|       \______/  \______/ \__|             \______/ \__|  \__|\_______|\__| \__| \__| \_______|

    """)

    # Parse arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            PONZI contract analyzer
            '''),
        epilog='''
            Examples
            --------

            # Extract TRXs of contract from block to block
            python3 ponzi.py -ct 0x029397845754854784 -bf 1000123 -bt 2034985 -w
            ''')

    group1 = parser.add_argument_group("Get and process data")
    group2 = parser.add_argument_group("Process data from JSON file")
    group3 = parser.add_argument_group("Start WebServer visualization data")

    group1.add_argument('-c', '--chunk', type=int, default=10000,
                        help='Chunks of blocks')
    group1.add_argument('-ct', '--contract',
                        help="address of contract")
    group1.add_argument('-bf', '--block-from', default=0, type=int,
                        help="Block start")
    group1.add_argument('-bt', '--block-to', default=9999999, type=int,
                        help="Block end")

    group2.add_argument('-f', '--file', type=str,
                        help="JSON file of recolected data")

    group3.add_argument('-w', '--web', action='store_true',
                        help="WEB for data visaulization")

    args = parser.parse_args()

    # Validations
    if (args.contract):
        asyncio.run(save_json(args.contract, args.block_from, args.block_to, key['bscscan'], chunk=args.chunk))
        if (args.file):
            print("Parameter JSON file are discarded because contract is provided")

    elif (args.file):
        rc = process_json(args.file)

    else:
        parser.print_help(sys.stderr)

    if (args.web):
        sys.stdout.flush()
        kwargs_flask = {"ip": "127.0.0.1", "port": 5000}
        flask_proc = multiprocessing.Process(name='flask',
                                                target=flaskServer,
                                                kwargs=kwargs_flask)
        flask_proc.daemon = True

        sys.stdout.flush()
        httpd_proc = multiprocessing.Process(name='httpd',
                                                target=httpServer)
        httpd_proc.daemon = True

        flask_proc.start()
        httpd_proc.start()
        flask_proc.join()
        httpd_proc.join()
