# application.py
# -*- encoding: utf-8 -*-

from fastapi import FastAPI, APIRouter, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse

import os
import shutil
import time
import json
import pandas as pd
import ast
import sqlite3
import pyround      # TODO: Test and use

import coloredlogs, logging

from core import bchain

# create a logger object.
log_format = '%(asctime)s %(name)-10s %(lineno)-6d %(levelname)-7s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
coloredlogs.install(level='DEBUG', fmt=log_format, logger=logger)

__author__ = "KennBro"
__copyright__ = "Copyright 2023, Personal Research"
__credits__ = ["KennBro"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "KennBro"
__email__ = "kennbro <at> protonmail <dot> com"
__status__ = "Development"


# NOTE: Module directory, replaces Flask's current_app.root_path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

home = APIRouter()


def create_application(file=None, key=None):
    app = FastAPI()
    # NOTE: Fully open CORS, equivalent to flask_cors' CORS(app) defaults
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.file = file
    app.state.key = key
    app.include_router(home)
    return app


################################################
# Testing
################################################
@home.get("/testing")
def r_testing(request: Request):
    file = request.app.state.file
    logger.info(f"Read contract file in {file}")
    return {"testing": "OK"}


################################################
# Contract
################################################
@home.get("/contract")
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
    # sc = ast.literal_eval(source_code)[0]
    sc = ast.literal_eval(source_code)
    abi = sc['ABI']
    abi = abi.replace("\\", "")
    abi = abi.replace('\"', '"')
    abi = abi.replace(':false', ':"false"')
    abi = abi.replace(':true', ':"true"')
    abi = abi.replace('""', '"null"')

    abi = ast.literal_eval(abi)

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

    return {'contract': contract['contract'],
            'block_from': contract['block_from'],
            'block_to': contract['block_to'],
            'first_block': contract['first_block'],
            'first_trx': contract['transaction_creation'],
            'chainid': contract['chain_id'],
            'blockchain': contract['blockchain'],
            'classification': contract['classification'],
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
            }


################################################
# General Transactions
################################################
@home.get("/trans_info")
def r_transaction_general():

    tic = time.perf_counter()
    with open('tmp/transaction_resume.json', 'r') as f:
        tr = f.read()
    toc = time.perf_counter()
    logger.info(f"Read transaction resume file in {toc - tic:0.4f} seconds")

    # Fix JSON
    tr_resume = ast.literal_eval(tr)

    return tr_resume


################################################
# General Transfers
################################################
@home.get("/transfer_info")
def r_transfers_general():

    tic = time.perf_counter()
    with open('tmp/transfer_resume.json', 'r') as f:
        tr = f.read()
    toc = time.perf_counter()
    logger.info(f"Read transfers resume file in {toc - tic:0.4f} seconds")

    # Fix JSON
    tr_resume = ast.literal_eval(tr)

    return tr_resume


################################################
# Liquidity
################################################
@home.get("/liq")
def r_liq():

    tic = time.perf_counter()
    with open('tmp/liq.json', 'r') as f:
        liq = f.read()
    toc = time.perf_counter()
    logger.info(f"Read liquidity file in {toc - tic:0.4f} seconds")

    # Fix JSON
    liquidity = ast.literal_eval(liq)

    return liquidity


################################################
# Trans volume by day
################################################
@home.get("/tvd")
def r_tvd():

    tic = time.perf_counter()
    with open('tmp/trans_series.json', 'r') as f:
        trans = f.read()
    toc = time.perf_counter()
    logger.info(f"Read trans series file in {toc - tic:0.4f} seconds")

    # Fix JSON
    tvd = ast.literal_eval(trans)

    return tvd


################################################
# Transfers
################################################
@home.get("/transfers")
def r_transfers():

    tic = time.perf_counter()
    with open('tmp/bubbles.json', 'r') as f:
        trans = f.read()
    toc = time.perf_counter()
    logger.info(f"Read bubble transfer file in {toc - tic:0.4f} seconds")

    transfers = ast.literal_eval(trans)

    return transfers


################################################
# Anomalies
################################################
@home.get("/anomalies")
def r_anomalies():

    tic = time.perf_counter()
    with open('tmp/anomalies.json', 'r') as f:
        anomalies = f.read()
    toc = time.perf_counter()
    logger.info(f"Read anomalies transfer file in {toc - tic:0.4f} seconds")

    anomalies_json = ast.literal_eval(anomalies)

    return anomalies_json


################################################
# Adress details
################################################
# PERF: Use DB instead JSON
@home.get("/details/{address}")
def r_result(address: str):
    # TODO: Verify if the address is the contract
    tic = time.perf_counter()
    with open('tmp/stats.json', 'r') as f:
        stats = f.read()
    toc = time.perf_counter()
    logger.info(f"Read contract stats file in {toc - tic:0.4f} seconds")

    contract = ast.literal_eval(stats)

    if (contract["native"]):
        tic = time.perf_counter()
        df_t = pd.read_json('./tmp/uni.json')
        toc = time.perf_counter()
        logger.info(f"Read Unified file in {toc - tic:0.4f} seconds")
        # NOTE : Only transfers
        df_t = df_t[df_t['value'] != 0]
    else:
        tic = time.perf_counter()
        df_tc = pd.read_json('tmp/transfers_contract.json')
        df_tw = pd.read_json('tmp/transfers_wallet.json')
        df_t = pd.concat([df_tw, df_tc], ignore_index=True) # WARN: concat transfers
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

        # if (contract['contract'].lower() == detail_total['from'][i]):
        if (address.lower() != detail_total['from'][i]):
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

    return {"address": address,
            "fdate": first_date.strftime("%Y-%m-%d %H:%M:%S"),
            "ldate": last_date.strftime("%Y-%m-%d %H:%M:%S"),
            "from_sum": from_sum,
            "from_count": from_count,
            "to_sum": to_sum,
            "to_count": to_count,
            "trans_vol": trans_vol,
            "moves": moves}


################################################
# Trx details
################################################
@home.get("/trx_hash/{trx_hash}")
def r_trx(trx_hash: str):
    tic = time.perf_counter()
    with open('tmp/sourcecode.json', 'r') as f:
        source_code = f.read()
    toc = time.perf_counter()
    logger.info(f"Read contract source code file in {toc - tic:0.4f} seconds")
    # sc = ast.literal_eval(source_code)[0]
    sc = ast.literal_eval(source_code)
    abi = sc['ABI']
    abi = abi.replace("\\", "")
    abi = abi.replace('\"', '"')
    abi = abi.replace(':false', ':"false"')
    abi = abi.replace(':true', ':"true"')
    abi = abi.replace('""', '"null"')
    abi = ast.literal_eval(abi)

    logger.info(f"Read Source Code file in {toc - tic:0.4f} seconds")
    tic = time.perf_counter()
    df_uni = pd.read_json('tmp/uni.json')
    toc = time.perf_counter()
    logger.info(f"Read transfers file in {toc - tic:0.4f} seconds")
    tic = time.perf_counter()
    df_decode = pd.read_json('tmp/decoded.json')
    toc = time.perf_counter()
    logger.info(f"Read decoded file in {toc - tic:0.4f} seconds")

    # trx = (df_transaction[df_transaction['hash'] == trx_hash])
    trx = df_uni[(df_uni['hash'] == trx_hash) & (df_uni['file'] == "trx")]
    # transfers = (df_t[df_t['hash'] == trx_hash])
    transfers = df_uni[(df_uni['hash'] == trx_hash) & ((df_uni['file'] == "tra") | (df_uni['file'] == "int"))]

    trx_date = pd.to_datetime(trx['timeStamp'], unit='ns')
    transfers_date = pd.to_datetime(transfers['timeStamp'], unit='ns')
    trx['date'] = trx_date
    transfers['date'] = transfers_date

    trx_json = trx.to_json(orient = 'records')
    transfer_json = transfers.to_json(orient = 'records')
    trx_json = ast.literal_eval(trx_json)
    transfer_json = ast.literal_eval(transfer_json)

    decoded_constructor = (df_decode[df_decode['funct'] == "constructor"])
    decoded = (df_decode[df_decode['hash'] == trx_hash])

    func_name = decoded['funct'].values[0]
    args = decoded['args'].values[0][2:-2]

    args_const = decoded_constructor['args'].values[0][2:-2]

    args_a = args.split('), (')
    args_const_a = args_const.split('), (')

    if (func_name != "Not decoded"):
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
                        except Exception:
                            value = "none"
                        input_content.append({"name": j['name'] + ' ' + j['type'], "cssClass": "ngx-org-input", "image": "", "title": value, "childs": []})
                elif (i['type'] == 'function' and i['name'] == func_name):
                    for j in i['inputs']:
                        try:
                            value = values[j['name']]
                        except Exception:
                            value = "none"
                        input_content.append({"name": j['name'] + ' ' + j['type'], "cssClass": "ngx-org-input", "image": "", "title": value, "childs": []})

            output_content = []
            if ('outputs' in i):
                output = True
                if (i['type'] == "constructor"):
                    for j in i['outputs']:
                        try:
                            value = values_const[j['name']]
                        except Exception:
                            value = "none"
                        output_content.append({"name": j['name'] + ' ' + j['type'], "cssClass": "ngx-org-output", "image": "", "title": value, "childs": []})
                elif (i['type'] == 'function' and i['name'] == func_name):
                    for j in i['outputs']:
                        try:
                            value = values[j['name']]
                        except Exception:
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
        # NOTE: Fallback
        if (func_name == "fallback"):
            func_code = sc['fallback_code']
            diagram = {"name": "fallback: " + sc['fallback_function'], "cssClass": "ngx-org-output", "image": "", "title": "", "childs": []}
        else:
            funct_start = source.index("function " + str(func_name))
            func_code = source[funct_start - 4:]
            funct_end = func_code[12:].index("function ")
            func_code = func_code[:funct_end]

        result = {"hash": trx_hash,
                    "trx": trx_json,
                    "transfers": transfer_json,
                    "constructor": const,
                    "function": diagram,
                    "code": func_code}
    else:
        func_code = "\n\n\n\n\n\n\n                           Function name not decoded\n\n\n\n\n\n\n\n"
        diagram = {"name": "NOT DECODED", "cssClass": "ngx-org-output", "image": "", "title": "", "childs": []}
        result = {"hash": trx_hash,
                  "trx": trx_json,
                  "transfers": transfer_json,
                  "constructor": [],  # TODO : Return leyend
                  "function": diagram,
                  "code": func_code}  # TODO : Return leyend

    return result


################################################
# Contract Creator
################################################
@home.get("/creator")
def r_creator(request: Request):

    tic = time.perf_counter()
    filedb = request.app.state.file
    connection = sqlite3.connect(filedb)

    # Contract creator blocks
    df_creator = pd.read_sql_query("SELECT * FROM t_contract_creator", connection)

    json_format = df_creator.to_json(orient='records')
    json_creator = json.loads(json_format)[0]

    # Contract creator balances
    df_balances = pd.read_sql_query("SELECT * FROM t_balance", connection)

    json_balances = df_balances.to_json(orient='records')
    json_balances = json.loads(json_balances)

    # Contract creator another contracts
    df_contracts = pd.read_sql_query("SELECT wallet FROM t_tagging WHERE tag = 'Contract Created'", connection)

    json_contracts = df_contracts.to_json(orient='records')
    json_contracts = json.loads(json_contracts)

    toc = time.perf_counter()
    logger.info(f"Read contract creator info in {toc - tic:0.4f} seconds")

    return {"creator": json_creator, "balances": json_balances, "contracts": json_contracts}


################################################
# Transactions Creator
################################################
@home.get("/trans_creator")
def r_trans_creator(request: Request):

    tic = time.perf_counter()
    filedb = request.app.state.file
    connection = sqlite3.connect(filedb)
    cursor = connection.cursor()

    # Get Contract and Creator
    query = "SELECT contract, creator, blockchain FROM t_contract"
    cursor.execute(query)
    contract, creator, blockchain = cursor.fetchone()

    # Get tags
    df_tags = pd.read_sql_query("SELECT * FROM t_tagging", connection)

    json_format = df_tags.to_json(orient='records')
    json_tags = json.loads(json_format)

    nodes = []
    nodes_list = []
    links = []
    stat_trx = 0
    stat_int = 0
    stat_tra = 0
    stat_con = 0
    stat_coo = 0
    # stat_wal = 0  # TODO: Qty wallets

    cursor.execute("SELECT COUNT(*) FROM t_tagging WHERE tag = 'Contract Created'")
    stat_coo = int(cursor.fetchone()[0])

    stat_con = len(json_tags) - stat_coo

    # Transations
    df_creator = pd.read_sql_query("SELECT `from` || '-t' AS 'from', `to` || '-t' AS 'to', sum(value / 1e18) as sum_value, count(value) as qty FROM t_transactions_creator GROUP BY 1, 2", connection)
    for i in df_creator.index:
        # Get Nodes
        stat_trx = stat_trx + df_creator["qty"][i]
        if (df_creator["from"][i] not in nodes_list):
            tag = ""
            nodes_list.append(df_creator["from"][i])
            if (df_creator["from"][i][:-2] == contract.lower()):
                type = "contract"
            elif (df_creator["from"][i][:-2] == creator.lower()):
                type = "creator"
            else:
                type = "wallet"
                tag = next((t["tag"] for t in json_tags if t.get("wallet") == df_creator["from"][i][:-2]), "")

            nodes.append({"id": df_creator["from"][i],
                          "address": df_creator["from"][i][:-2],
                          "type": type,
                          "tag": tag,
                          "trx": "Transactions",
                          "token": "ETH" if blockchain == "eth" else "BNB",
                          "trx_in": 0,
                          "qty_in": 0,
                          "trx_out": float(df_creator["sum_value"][i]),
                          "qty_out": int(df_creator["qty"][i])})
        else:
            for node in nodes:
                if (node['id'] == df_creator["from"][i]):
                    node['trx_out'] += float(df_creator["sum_value"][i])
                    node['qty_out'] += int(df_creator["qty"][i])
        if (df_creator["to"][i] not in nodes_list):
            tag = ""
            nodes_list.append(df_creator["to"][i])
            if (df_creator["to"][i][:-2] == contract.lower()):
                type = "contract"
            elif (df_creator["to"][i][:-2] == creator.lower()):
                type = "creator"
            else:
                type = "wallet"
                tag = next((t["tag"] for t in json_tags if t.get("wallet") == df_creator["to"][i][:-2]), "")

            nodes.append({"id": df_creator["to"][i],
                          "address": df_creator["to"][i][:-2],
                          "type": type,
                          "tag": tag,
                          "trx": "Transactions",
                          "token": "ETH" if blockchain == "eth" else "BNB",
                          "trx_out": 0,
                          "qty_out": 0,
                          "trx_in": float(df_creator["sum_value"][i]),
                          "qty_in": int(df_creator["qty"][i])})
        else:
            for node in nodes:
                if (node['id'] == df_creator["to"][i]):
                    node['trx_in'] += float(df_creator["sum_value"][i])
                    node['qty_in'] += int(df_creator["qty"][i])
        # Get links
        links.append({"source": df_creator["from"][i], "target": df_creator["to"][i], "value": float(df_creator["sum_value"][i]), "qty": int(df_creator["qty"][i])})

    # Internals
    df_creator = pd.read_sql_query("SELECT `from` || '-i' AS 'from', `to` || '-i' AS 'to', sum(value / 1e18) as sum_value, count(value) as qty FROM t_internals_creator GROUP BY 1, 2", connection)
    for i in df_creator.index:
        stat_int = stat_int + df_creator["qty"][i]
        # Get Nodes
        if (df_creator["from"][i] not in nodes_list):
            tag = ""
            nodes_list.append(df_creator["from"][i])
            if (df_creator["from"][i][:-2] == contract.lower()):
                type = "contract"
            elif (df_creator["from"][i][:-2] == creator.lower()):
                type = "creator"
            else:
                type = "wallet"
                tag = next((t["tag"] for t in json_tags if t.get("wallet") == df_creator["from"][i][:-2]), "")

            nodes.append({"id": df_creator["from"][i],
                          "address": df_creator["from"][i][:-2],
                          "type": type,
                          "tag": tag,
                          "trx": "Internals",
                          "token": "ETH" if blockchain == "eth" else "BNB",
                          "trx_in": 0,
                          "qty_in": 0,
                          "trx_out": float(df_creator["sum_value"][i]),
                          "qty_out": int(df_creator["qty"][i])})
        else:
            for node in nodes:
                if (node['id'] == df_creator["from"][i]):
                    node['trx_out'] += float(df_creator["sum_value"][i])
                    node['qty_out'] += int(df_creator["qty"][i])
        if (df_creator["to"][i] not in nodes_list):
            tag = ""
            nodes_list.append(df_creator["to"][i])
            if (df_creator["to"][i][:-2] == contract.lower()):
                type = "contract"
            elif (df_creator["to"][i][:-2] == creator.lower()):
                type = "creator"
            else:
                type = "wallet"
                tag = next((t["tag"] for t in json_tags if t.get("wallet") == df_creator["to"][i][:-2]), "")

            nodes.append({"id": df_creator["to"][i],
                          "address": df_creator["to"][i][:-2],
                          "type": type,
                          "tag": tag,
                          "trx": "Internals",
                          "token": "ETH" if blockchain == "eth" else "BNB",
                          "trx_out": 0,
                          "qty_out": 0,
                          "trx_in": float(df_creator["sum_value"][i]),
                          "qty_in": int(df_creator["qty"][i])})
        else:
            for node in nodes:
                if (node['id'] == df_creator["to"][i]):
                    node['trx_in'] += float(df_creator["sum_value"][i])
                    node['qty_in'] += int(df_creator["qty"][i])
        # Get links
        links.append({"source": df_creator["from"][i], "target": df_creator["to"][i], "value": float(df_creator["sum_value"][i]), "qty": int(df_creator["qty"][i])})

    # BEP20 - ERC20 - Tokens
    df_creator = pd.read_sql_query("SELECT `from` || tokenSymbol AS 'from', `to` || tokenSymbol AS 'to', tokenSymbol, tokenName, sum(value / 1e18) as sum_value, count(value) as qty FROM t_transfers_creator GROUP BY 1, 2", connection)
    for i in df_creator.index:
        stat_tra = stat_tra + df_creator["qty"][i]
        len_tk_sym = len(df_creator["tokenSymbol"][i])
        # Get Nodes
        if (df_creator["from"][i] not in nodes_list):
            tag = ""
            nodes_list.append(df_creator["from"][i])
            if (df_creator["from"][i][:-(len_tk_sym)] == contract.lower()):
                type = "contract"
            elif (df_creator["from"][i][:-(len_tk_sym)] == creator.lower()):
                type = "creator"
            else:
                type = "wallet"
                tag = next((t["tag"] for t in json_tags if t.get("wallet") == df_creator["from"][i][:-(len_tk_sym)]), "")

            nodes.append({"id": df_creator["from"][i],
                          "address": df_creator["from"][i][:-(len_tk_sym)],
                          "type": type,
                          "tag": tag,
                          "trx": "ERC-20 Token" if blockchain == "eth" else "BEP-20 Token",
                          "token": str(df_creator["tokenSymbol"][i]),
                          "trx_in": 0,
                          "qty_in": 0,
                          "trx_out": float(df_creator["sum_value"][i]),
                          "qty_out": int(df_creator["qty"][i])})
        else:
            for node in nodes:
                if (node['id'] == df_creator["from"][i]):
                    node['trx_out'] += float(df_creator["sum_value"][i])
                    node['qty_out'] += int(df_creator["qty"][i])
        if (df_creator["to"][i] not in nodes_list):
            tag = ""
            nodes_list.append(df_creator["to"][i])
            if (df_creator["to"][i][:-(len_tk_sym)] == contract.lower()):
                type = "contract"
            elif (df_creator["to"][i][:-(len_tk_sym)] == creator.lower()):
                type = "creator"
            else:
                type = "wallet"
                tag = next((t["tag"] for t in json_tags if t.get("wallet") == df_creator["to"][i][:-(len_tk_sym)]), "")

            nodes.append({"id": df_creator["to"][i],
                          "address": df_creator["to"][i][:-(len_tk_sym)],
                          "type": type,
                          "tag": tag,
                          "trx": "ERC-20 Token" if blockchain == "eth" else "BEP-20 Token",
                          "token": str(df_creator["tokenSymbol"][i]),
                          "trx_out": 0,
                          "qty_out": 0,
                          "trx_in": float(df_creator["sum_value"][i]),
                          "qty_in": int(df_creator["qty"][i])})
        else:
            for node in nodes:
                if (node['id'] == df_creator["to"][i]):
                    node['trx_in'] += float(df_creator["sum_value"][i])
                    node['qty_in'] += int(df_creator["qty"][i])
        # Get links
        links.append({"source": df_creator["from"][i], "target": df_creator["to"][i], "value": float(df_creator["sum_value"][i]), "qty": int(df_creator["qty"][i])})

    trans_creator = {"nodes": nodes, "links": links}

    stat = {"stat_trx": int(stat_trx), "stat_int": int(stat_int), "stat_tra": int(stat_tra),
            "stat_con": int(stat_con), "stat_coo": int(stat_coo)}

    toc = time.perf_counter()
    logger.info(f"Read contract creator info in {toc - tic:0.4f} seconds")

    return {"trans_creator": trans_creator, "stat": stat}


################################################
# Process file
################################################
@home.post('/upload_file')
def upload_file(request: Request, file: UploadFile = File(...)):

    # TODO: Name validation
    if file.filename == '':
        return {"status": "error", "message": "The filename is empty"}

    elif file.filename[-2:] != 'db':
        return {"status": "error", "message": "The file must be SQlite extension"}

    else:
        temp_dir = os.path.join(BASE_DIR, 'temp_db')
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, file.filename)
        request.app.state.file = file_path
        with open(file_path, 'wb') as out:
            shutil.copyfileobj(file.file, out)
        return {'status': 'ok', 'message': 'File uploaded successfully', 'file_id': file.filename}


@home.get('/file_process')
def r_process_file(request: Request, file_id: str = None):
    if not file_id:
        return {"status": "error", "message": "File ID is required"}

    temp_dir = os.path.join(BASE_DIR, 'temp_db')
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file_id)

    return StreamingResponse(bchain.event_stream_data_file(file_path), media_type='text/event-stream')


################################################
# Collect data
################################################
@home.get('/get_data_process')
def r_get_data_process(request: Request, caddress: str = None, bfrom: str = None, bto: str = None, network: str = None):

    # TODO: Do validations
    if not caddress:
        return {"status": "error", "message": "You must specify Contract Address"}

    filename = f"contract-{network}-{caddress}.db"
    temp_dir = os.path.join(BASE_DIR, 'temp_db')
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, filename)
    request.app.state.file = file_path

    key = request.app.state.key

    return StreamingResponse(bchain.data_db_collect_event(network, caddress, key, file_path, bfrom, bto), media_type='text/event-stream')


################################################
# Collect data
################################################
@home.get('/download_db')
def download_investigation(request: Request):
    file_path = request.app.state.file
    return FileResponse(file_path, filename=os.path.basename(file_path))


# NOTE: Module-level app instance for ad-hoc runs, e.g.
#       uvicorn api_poorSKeme:app --port 5055
# poorSKeme.py builds its own instance via create_application(file=..., key=...)
app = create_application()
