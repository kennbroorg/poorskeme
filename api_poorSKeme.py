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
# coloredlogs.install(level='DEBUG')

__author__ = "KennBro"
__copyright__ = "Copyright 2023, Personal Research"
__credits__ = ["KennBro"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "KennBro"
__email__ = "kennbro <at> protonmail <dot> com"
__status__ = "Development"


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

    # abi_total = []
    # for i in abi:
    #     prop = ''
    #     input = False 
    #     output = False 
    #     head = f"{i['type']}"
    #     if ('stateMutability' in i):
    #         prop = prop + f"stateMutability: {i['stateMutability']}"
    #     if ('anonymous' in i):
    #         prop = prop + f"anonymous: {i['anonymous']}"
    #     if ('name' in i):
    #         head = head + f" - Name: {i['name']} ({prop})"

    #     if ('inputs' in i):
    #         input = True
    #         input_content = []
    #         for j in i['inputs']:
    #             input_content.append({"name": f"Name: {j['name']} - Type: {j['type']}"})

    #     if ('outputs' in i):
    #         output = True
    #         output_content = []
    #         for j in i['outputs']:
    #             output_content.append({"name": f"Name: {j['name']} - Type: {j['type']}"})

    #     if (output or input):
    #         children = []
    #         if (input):
    #             children.append({"name": "Input", "children": input_content})
    #         if (output):
    #             children.append({"name": "output", "children": output_content})
    #         abi_item = {"name": head, "children": children}
        
    #     abi_total.append(abi_item)

    abi_org = []
    const = []
    event = []
    funct = []
    for i in abi:
        input = False 
        output = False 

        input_content = []
        if ('inputs' in i):
            input = True
            for j in i['inputs']:
                input_content.append({"name": j['name'], "cssClass": "ngx-org-input", "image": "", "title": j['type'], "childs": []})

        output_content = []
        if ('outputs' in i):
            output = True
            for j in i['outputs']:
                output_content.append({"name": j['name'], "cssClass": "ngx-org-output", "image": "", "title": j['type'], "childs": []})

        if (output or input):
            children_io = []
            # if (input):
            if (input_content != []):
                # children.append({"name": "Input", "children": input_content})
                children_io.append({"name": "INPUT", "cssClass": "ngx-org-input-tag", "image": "", "title": "", "childs": input_content})
            if (output_content != []):
                # children.append({"name": "output", "children": output_content})
                children_io.append({"name": "OUTPUT", "cssClass": "ngx-org-output-tag", "image": "", "title": "", "childs": output_content})
            # abi_item = {"name": head, "children": children}

        if (i['type'] == 'constructor'):
            const.append({"name": "CONSTRUCTOR", "cssClass": "ngx-org-constructor-node", "image": "", "title": "", "childs": children_io})

        if (i['type'] == 'event'):
            event.append({"name": i['name'], "cssClass": "ngx-org-event", "image": "", "title": "Name", "childs": children_io})

        if (i['type'] == 'function'):
            funct.append({"name": i['name'], "cssClass": "ngx-org-funct", "image": "", "title": "Name", "childs": children_io})

    abi_org.append(const[0])
    if (event != []):
        abi_org.append({"name": "EVENTS", "cssClass": "ngx-org-event-node", "image": "", "title": "", "childs": event})
    if (funct != []):
        abi_org.append({"name": "FUNCTIONS", "cssClass": "ngx-org-funct-node", "image": "", "title": "", "childs": funct})

    contract = ast.literal_eval(contract_info)

    stats = ast.literal_eval(stats)

    return jsonify({'contract': contract['contract'],
                    'block_from': contract['block_from'], 
                    'block_to': contract['block_to'], 
                    'first_block': contract['first_block'], 
                    'first_trx': contract['transaction_creation'], 
                    'SourceCode': sc['SourceCode'], 
                    # 'abi': {"name": sc['ContractName'], "children": abi_total},
                    'abi': abi_org,
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
                    'funct_stats': stats['funct_stats'],
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
# Adress details
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
        # TODO KKK
        # tic = time.perf_counter()
        # df_transaction = pd.read_json('./tmp/transactions.json')
        # print(df_transaction.info())
        # toc = time.perf_counter()
        # logger.info(f"Read transfers file in {toc - tic:0.4f} seconds")
        tic = time.perf_counter()
        # df_i = pd.read_json('./tmp/internals.json')
        df_t = pd.read_json('./tmp/internals.json')
        print(df_t.info())
        toc = time.perf_counter()
        logger.info(f"Read transfers file in {toc - tic:0.4f} seconds")
        tic = time.perf_counter()

        # dftemp_transaction = df_transaction[df_transaction['isError'] == 0]
        # dftemp_transaction = dftemp_transaction[['timeStamp','from', 'to', 'value']]
        # dftemp_transaction = dftemp_transaction[dftemp_transaction["value"] != 0]

        # # TODO : This 
        # dftemp_i = df_i[['timeStamp', 'from', 'to', 'value']]
        # dftemp = pd.concat([dftemp_transaction, dftemp_i],
        #                    join='inner', ignore_index=True)
        # df_t = dftemp.sort_values(["timeStamp"])
        # print("dftemp")
        print(df_t.info())
    else:
        tic = time.perf_counter()
        df_t = pd.read_json('tmp/transfers.json')
        toc = time.perf_counter()
        logger.info(f"Read transfers file in {toc - tic:0.4f} seconds")

    tic = time.perf_counter()
    df_decoded = pd.read_json('./tmp/decoded.json')
    toc = time.perf_counter()
    logger.info(f"Read decoded functions file in {toc - tic:0.4f} seconds")

    detail_from = df_t[df_t['from'] == address]
    from_sum = round(detail_from['value'].sum() / 1e+18, 2)
    from_count = len(detail_from)

    detail_to = df_t[df_t['to'] == address]
    to_sum = round(detail_to['value'].sum() / 1e+18, 2)
    to_count = len(detail_to)

    detail_total = pd.concat([detail_from, detail_to], axis=0)
    detail_total = detail_total.sort_values(["timeStamp"])
    print(detail_total.info())

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
            trx_hash = detail_total['hash'][i]
            funct = (df_decoded[df_decoded['hash'] == trx_hash])
            moves.append({"date": detail_total['timeStamp'][i].strftime("%Y-%m-%d %H:%M:%S"), 
                          "hash": trx_hash,
                          "funct": (funct['funct']).to_string(index=False),
                          "name": "IN", 
                          "value": value})
        else: 
            trx_out_day = trx_out_day + value
            trx_hash = detail_total['hash'][i]
            funct = (df_decoded[df_decoded['hash'] == trx_hash])
            moves.append({"date": detail_total['timeStamp'][i].strftime("%Y-%m-%d %H:%M:%S"), 
                          "hash": trx_hash,
                          "funct": (funct['funct']).to_string(index=False),
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


################################################
# Trx details
################################################
@home.route("/trx_hash/<trx_hash>")
def r_trx(trx_hash):
    tic = time.perf_counter()
    with open('tmp/sourcecode.json', 'r') as f:
        source_code = f.read()
    toc = time.perf_counter()
    logger.info(f"Read contract source code file in {toc - tic:0.4f} seconds")
    sc = ast.literal_eval(source_code)[0]
    abi = sc['ABI']
    abi = abi.replace("\\", "")
    abi = abi.replace('\"', '"')
    abi = abi.replace(':false', ':"false"')
    abi = abi.replace(':true', ':"true"')
    abi = abi.replace('""', '"null"')
    abi = ast.literal_eval(abi)

    logger.info(f"Read transfers file in {toc - tic:0.4f} seconds")
    tic = time.perf_counter()
    df_transaction = pd.read_json('./tmp/transactions.json')
    toc = time.perf_counter()
    logger.info(f"Read transfers file in {toc - tic:0.4f} seconds")
    tic = time.perf_counter()
    df_i = pd.read_json('./tmp/internals.json')
    toc = time.perf_counter()
    logger.info(f"Read transfers file in {toc - tic:0.4f} seconds")
    tic = time.perf_counter()
    df_t = pd.read_json('tmp/transfers.json')
    toc = time.perf_counter()
    logger.info(f"Read transfers file in {toc - tic:0.4f} seconds")
    tic = time.perf_counter()
    df_decode = pd.read_json('tmp/decoded.json')
    toc = time.perf_counter()
    logger.info(f"Read decoded file in {toc - tic:0.4f} seconds")

    trx = (df_transaction[df_transaction['hash'] == trx_hash])
    transfers = (df_t[df_t['hash'] == trx_hash])
    trx_date = pd.to_datetime(trx['timeStamp'], unit='ns')
    # trx_date = trx['timeStamp'].dt.strftime('%Y/%m/%d %H:%M:%S')
    print(trx_date)
    transfers_date = pd.to_datetime(transfers['timeStamp'], unit='ns')
    # transfers_date = trx['timeStamp'].dt.strftime('%Y/%m/%d %H:%M:%S')
    trx['date'] = trx_date
    transfers['date'] = transfers_date

    decoded_constructor = (df_decode[df_decode['funct'] == "constructor"])
    decoded = (df_decode[df_decode['hash'] == trx_hash])

    func_name = decoded['funct'].values[0]
    args = decoded['args'].values[0][2:-2]

    args_const = decoded_constructor['args'].values[0][2:-2]

    args_a = args.split('), (')
    args_const_a = args_const.split('), (')

    values = {}
    if (args != ''):
        for i in args_a:
            e = i.split(', ')
            name = e[1].strip("'")
            value = e[2].strip("'")
            values[name] = value

    values_const = {}
    for i in args_const_a:
        e = i.split(', ')
        name = e[1].strip("'")
        value = e[2].strip("'")
        values_const[name] = value

    # Diagram
    funct = []
    const = {}
    for i in abi:
        input = False 
        output = False 

        input_content = []
        if ('inputs' in i):
            input = True
            if (i['type'] == "constructor"):
                for j in i['inputs']:
                    try:
                        value = values_const[j['name']]
                    except:
                        value = "none"
                    input_content.append({"name": j['name'] + ' ' + j['type'], "cssClass": "ngx-org-input", "image": "", "title": value, "childs": []})
            elif (i['type'] == 'function' and i['name'] == func_name):
                for j in i['inputs']:
                    try:
                        value = values[j['name']]
                    except:
                        value = "none"
                    input_content.append({"name": j['name'] + ' ' + j['type'], "cssClass": "ngx-org-input", "image": "", "title": value, "childs": []})

        output_content = []
        if ('outputs' in i):
            output = True
            if (i['type'] == "constructor"):
                for j in i['outputs']:
                    try:
                        value = values_const[j['name']]
                    except:
                        value = "none"
                    output_content.append({"name": j['name'] + ' ' + j['type'], "cssClass": "ngx-org-output", "image": "", "title": value, "childs": []})
            elif (i['type'] == 'function' and i['name'] == func_name):
                for j in i['outputs']:
                    try:
                        value = values[j['name']]
                    except:
                        value = "none"
                    output_content.append({"name": j['name'] + ' ' + j['type'], "cssClass": "ngx-org-output", "image": "", "title": value, "childs": []})

        if (output or input):
            children_io = []
            if (input_content != []):
                children_io.append({"name": "INPUT", "cssClass": "ngx-org-input-tag", "image": "", "title": "", "childs": input_content})
            if (output_content != []):
                children_io.append({"name": "OUTPUT", "cssClass": "ngx-org-output-tag", "image": "", "title": "", "childs": output_content})

        if (i['type'] == 'constructor'):
            const = {"name": "CONSTRUCTOR", "cssClass": "ngx-org-constructor-node", "image": "", "title": "", "childs": children_io}

        if (i['type'] == 'function' and i['name'] == func_name):
            funct = [{"name": i['name'], "cssClass": "ngx-org-funct", "image": "", "title": "Name", "childs": children_io}]

    if (funct != []):
        diagram = {"name": "FUNCTIONS", "cssClass": "ngx-org-funct-node", "image": "", "title": "", "childs": funct}

    # Code
    source = sc['SourceCode']
    funct_start = source.index("function " + func_name)
    func_code = source[funct_start - 4:]
    funct_end = func_code[12:].index("function ")
    func_code = func_code[:funct_end]

    trx_json = trx.to_json(orient = 'records')
    transfer_json = transfers.to_json(orient = 'records')
    trx_json = ast.literal_eval(trx_json)
    transfer_json = ast.literal_eval(transfer_json)

    result = {"hash": trx_hash,
                "trx": trx_json,
                "transfers": transfer_json,
                "constructor": const,
                "function": diagram,
                "code": func_code}
    return jsonify(result)
