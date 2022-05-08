# application.py
# -*- encoding: utf-8 -*-

from flask import Flask
from flask_cors import CORS
from flask import Blueprint, jsonify

import time
import json
import pandas as pd
import ast

import coloredlogs, logging

# create a logger object.
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')

home = Blueprint('home_views', __name__)


def create_application():
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(home)
    return app


################################################
# Testing
################################################
@home.route("/testing", methods=["GET"])
def r_testing():
    return jsonify({"testing": "OK"})


################################################
# Contract
################################################
@home.route("/contract", methods=["GET"])
def r_contract():

    tic = time.perf_counter()
    with open('tmp/contract.json', 'r') as f:
        contract_info = f.read()
    toc = time.perf_counter()
    logger.info(f"Read contract file in {toc - tic:0.4f} seconds")

    tic = time.perf_counter()
    with open('tmp/sourcecode.json', 'r') as f:
        source_code = f.read()
    toc = time.perf_counter()
    logger.info(f"Read contract source code file in {toc - tic:0.4f} seconds")

    tic = time.perf_counter()
    with open('tmp/stats.json', 'r') as f:
        stats = f.read()
    toc = time.perf_counter()
    logger.info(f"Read contract stats file in {toc - tic:0.4f} seconds")

    # Fix JSON
    sc = ast.literal_eval(source_code)[0]
    abi = sc['ABI']
    abi = abi.replace("\\", "")
    abi = abi.replace('\"', '"')
    abi = abi.replace(':false', ':"false"')
    abi = abi.replace(':true', ':"true"')
    abi = abi.replace('""', '"null"')

    abi = ast.literal_eval(abi)

    abi_total = []
    for i in abi:
        prop = ''
        input = False 
        output = False 
        head = f"{i['type']}"
        if ('stateMutability' in i):
            prop = prop + f"stateMutability: {i['stateMutability']}"
        if ('anonymous' in i):
            prop = prop + f"anonymous: {i['anonymous']}"
        if ('name' in i):
            head = head + f" - Name: {i['name']} ({prop})"

        if ('inputs' in i):
            input = True
            input_content = []
            for j in i['inputs']:
                input_content.append({"name": f"Name: {j['name']} - Type: {j['type']}"})

        if ('outputs' in i):
            output = True
            output_content = []
            for j in i['outputs']:
                output_content.append({"name": f"Name: {j['name']} - Type: {j['type']}"})

        if (output or input):
            children = []
            if (input):
                children.append({"name": "Input", "children": input_content})
            if (output):
                children.append({"name": "output", "children": output_content})
            abi_item = {"name": head, "children": children}
        
        abi_total.append(abi_item)

    contract = ast.literal_eval(contract_info)

    stats = ast.literal_eval(stats)

    return jsonify({'contract': contract['contract'],
                    'block_from': contract['block_from'], 
                    'block_to': contract['block_to'], 
                    'SourceCode': sc['SourceCode'], 
                    'abi': {"name": sc['ContractName'], "children": abi_total},
                    'abiraw': abi,
                    'ContractName': sc['ContractName'], 
                    'CompilerVersion': sc['CompilerVersion'],
                    'LicenseType': sc['LicenseType'],
                    'fdate': stats['fdate'],
                    'ldate': stats['ldate'],
                    'token_name': stats['token_name'],
                    'native': stats['native'],
                    'creator': stats['creator'],
                    'max_liq': stats['max_liq'],
                    'max_liq_date': stats['max_liq_date'],
                    'investments': stats['investments'],
                    'volume': stats['volume'],
                    'wallets': stats['wallets'],
                    'trx_out': stats['trx_out'],
                    'trx_in': stats['trx_in']
                    })


################################################
# General Transactions
################################################
@home.route("/trans_info", methods=["GET"])
def r_transaction_general():

    tic = time.perf_counter()
    with open('tmp/transaction_resume.json', 'r') as f:
        tr = f.read()
    toc = time.perf_counter()
    logger.info(f"Read transaction resume file in {toc - tic:0.4f} seconds")

    # Fix JSON
    tr_resume = ast.literal_eval(tr)

    return jsonify(tr_resume)


################################################
# General Transfers
################################################
@home.route("/transfer_info", methods=["GET"])
def r_transfers_general():

    tic = time.perf_counter()
    with open('tmp/transfer_resume.json', 'r') as f:
        tr = f.read()
    toc = time.perf_counter()
    logger.info(f"Read transfers resume file in {toc - tic:0.4f} seconds")

    # Fix JSON
    tr_resume = ast.literal_eval(tr)

    return jsonify(tr_resume)


################################################
# Liquidity
################################################
@home.route("/liq", methods=["GET"])
def r_liq():

    tic = time.perf_counter()
    with open('tmp/liq.json', 'r') as f:
        liq = f.read()
    toc = time.perf_counter()
    logger.info(f"Read liquidity file in {toc - tic:0.4f} seconds")

    # Fix JSON
    liquidity = ast.literal_eval(liq)

    return jsonify(liquidity)


################################################
# Trans volume by day
################################################
@home.route("/tvd", methods=["GET"])
def r_tvd():

    tic = time.perf_counter()
    with open('tmp/trans_series.json', 'r') as f:
        trans = f.read()
    toc = time.perf_counter()
    logger.info(f"Read trans series file in {toc - tic:0.4f} seconds")

    # Fix JSON
    tvd = ast.literal_eval(trans)

    return jsonify(tvd)


################################################
# Transfers
################################################
@home.route("/transfers", methods=["GET"])
def r_transfers():
    
    tic = time.perf_counter()
    with open('tmp/bubbles.json', 'r') as f:
        trans = f.read()
    toc = time.perf_counter()
    logger.info(f"Read bubble transfer file in {toc - tic:0.4f} seconds")

    transfers = ast.literal_eval(trans)

    return transfers


################################################
# Result
################################################
@home.route("/details/<address>")
def r_result(address):
    # TODO: Verify if the address is the contract
    tic = time.perf_counter()
    with open('tmp/stats.json', 'r') as f:
        stats = f.read()
    toc = time.perf_counter()
    logger.info(f"Read contract stats file in {toc - tic:0.4f} seconds")

    contract = ast.literal_eval(stats)

    if (contract["native"]):
        tic = time.perf_counter()
        df_transaction = pd.read_json('./tmp/transactions.json')
        toc = time.perf_counter()
        logger.info(f"Read transfers file in {toc - tic:0.4f} seconds")
        tic = time.perf_counter()
        df_i = pd.read_json('./tmp/internals.json')
        toc = time.perf_counter()
        logger.info(f"Read transfers file in {toc - tic:0.4f} seconds")

        dftemp_transaction = df_transaction[df_transaction['isError'] == 0]
        dftemp_transaction = dftemp_transaction[['timeStamp','from', 'to', 'value']]
        dftemp_transaction = dftemp_transaction[dftemp_transaction["value"] != 0]

        dftemp_i = df_i[['timeStamp', 'from', 'to', 'value']]
        dftemp = pd.concat([dftemp_transaction, dftemp_i],
                           join='inner', ignore_index=True)
        df_t = dftemp.sort_values(["timeStamp"])
    else:
        tic = time.perf_counter()
        df_t = pd.read_json('tmp/transfers.json')
        toc = time.perf_counter()
        logger.info(f"Read transfers file in {toc - tic:0.4f} seconds")

    detail_from = df_t[df_t['from'] == address]
    from_sum = round(detail_from['value'].sum() / 1e+18, 2)
    from_count = len(detail_from)

    detail_to = df_t[df_t['to'] == address]
    to_sum = round(detail_to['value'].sum() / 1e+18, 2)
    to_count = len(detail_to)

    detail_total = pd.concat([detail_from, detail_to], axis=0)
    detail_total = detail_total.sort_values(["timeStamp"])

    first_date = detail_total['timeStamp'].iloc[0]
    last_date = detail_total['timeStamp'].iloc[-1]

    moves = []
    trx_out_day = 0
    trx_in_day = 0
    day = ''
    day_prev = day
    trx_in_series = []
    trx_out_series = []
    for i in detail_total.index: 
        value = round(detail_total['value'][i] / 1e+18, 2)
        day = detail_total['timeStamp'][i].strftime("%Y-%m-%d")
        if (day_prev == ''):
            day_prev = day

        if (day_prev != day):
            trx_in_series.append({"name": day_prev,
                                    "value": trx_in_day})
            trx_out_series.append({"name": day_prev,
                                    "value": trx_out_day})
            day_prev = day
            day = detail_total['timeStamp'][i].strftime("%Y-%m-%d")
            trx_in_day = 0
            trx_out_day = 0

        if (contract['contract'].lower() == detail_total['from'][i]):
            trx_in_day = trx_in_day + value
            moves.append({"date": detail_total['timeStamp'][i].strftime("%Y-%m-%d %H:%M:%S"), 
                          "name": "IN", 
                          "value": value})
        else: 
            trx_out_day = trx_out_day + value
            moves.append({"date": detail_total['timeStamp'][i].strftime("%Y-%m-%d %H:%M:%S"), 
                          "name": "OUT", 
                          "value": value})

    trx_in_series.append({"name": day,
                            "value": trx_in_day})
    trx_out_series.append({"name":  day,
                            "value": trx_out_day})
    trans_vol = [{"name": "Trans OUT",
                  "series": trx_out_series},
                 {"name": "Trans IN",
                  "series": trx_in_series}]

    return jsonify({"address": address,
                    "fdate": first_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "ldate": last_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "from_sum": from_sum,
                    "from_count": from_count,
                    "to_sum": to_sum,
                    "to_count": to_count,
                    "trans_vol": trans_vol,
                    "moves": moves})