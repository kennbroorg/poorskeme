#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys
import asyncio
import argparse
import yaml
import textwrap

import multiprocessing
import http.server
import socketserver
from termcolor import colored
import coloredlogs, logging

from api_poorSKeme import create_application
from core import bsc
from core import eth


# create a logger object.
logger = logging.getLogger(__name__)


__author__ = "KennBro"
__copyright__ = "Copyright 2022, Personal Research"
__credits__ = ["KennBro"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "KennBro"
__email__ = "kennbro <at> protonmail <dot> com"
__status__ = "Development"


def flaskServer(ip='127.0.0.1', port=5000, file=None):
    app = create_application()
    app.config['file'] = file
    logger.info("Flask serving...")
    app.run(port=port, debug=True, host=ip, use_reloader=False)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="./frontend/dist/", **kwargs)


def httpServer():
    PORT = 4200
    logger.info("HTTPD serving... Data Visualization Web on http://127.0.0.1:4200")
    with socketserver.TCPServer(("", PORT), Handler) as httpd_server:
        httpd_server.serve_forever()


if __name__ == "__main__":

    print("""
$$$$$$$\                                       $$$$$$\  $$\   $$\                                  
$$  __$$\                                     $$  __$$\ $$ | $$  |                                 
$$ |  $$ | $$$$$$\   $$$$$$\   $$$$$$\        $$ /  \__|$$ |$$  / $$$$$$\  $$$$$$\$$$$\   $$$$$$\  
$$$$$$$  |$$  __$$\ $$  __$$\ $$  __$$\       \$$$$$$\  $$$$$  / $$  __$$\ $$  _$$  _$$\ $$  __$$\ 
$$  ____/ $$ /  $$ |$$ /  $$ |$$ |  \__|       \____$$\ $$  $$<  $$$$$$$$ |$$ / $$ / $$ |$$$$$$$$ |
$$ |      $$ |  $$ |$$ |  $$ |$$ |            $$\   $$ |$$ |\$$\ $$   ____|$$ | $$ | $$ |$$   ____|
$$ |      \$$$$$$  |\$$$$$$  |$$ |            \$$$$$$  |$$ | \$$\\\$$$$$$$\ $$ | $$ | $$ |\$$$$$$$\ 
\__|       \______/  \______/ \__|             \______/ \__|  \__|\_______|\__| \__| \__| \_______|

    """)

    # Parse arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            Contract analyzer
            '''),
        epilog='''
            Examples
            --------

            # Extract TRXs of contract from block to block (Ethereum Network)
            python3 poorSKeme.py -bc eth -ct 0xb547027A4CCD46EC98199Fa88AAEDF5aA981Db26 -bt 6496413        # To collect

            # Extract TRXs of contract from block to block (Binance Smart Chain)
            python3 poorSKeme.py -bc bsc -ct 0xe878BccA052579C9061566Cec154B783Fc5b9fF1 -bt 15552901       # To collect

            # Data Visualization of processed contract information (Binance Smart Chain)
            python3 poorSKeme.py -bc bsc -f F/contract-0xe878BccA052579C9061566Cec154B783Fc5b9fF1.json -w  # To visualice data
            ''')

    group1 = parser.add_argument_group("Get and process data")
    group2 = parser.add_argument_group("Process data from JSON file")
    group3 = parser.add_argument_group("Start WebServer visualization data")

    group1.add_argument('-bc', '--blockchain', choices=["bsc", "eth"], 
                        default="eth", help="Select Blockchain (bsc, eth)")
    group1.add_argument('-ct', '--contract',
                        help="address of contract")
    group1.add_argument('-bf', '--block-from', default=0, type=int,
                        help="Block start")
    group1.add_argument('-bt', '--block-to', default=99999999, type=int,
                        help="Block end")
    group1.add_argument('-c', '--chunk', type=int, default=10000,
                        help='Chunks of blocks')

    group2.add_argument('-f', '--file', type=str,
                        help="JSON file of recolected data")

    group3.add_argument('-w', '--web', action='store_true',
                        help="WEB for data visaulization")

    args = parser.parse_args()

    # Read config and keys
    with open(r'./API.yaml') as file:
        key = yaml.load(file, Loader=yaml.FullLoader)

    coloredlogs.install(level='INFO')
    try:
        coloredlogs.install(level=key['level'])
    except Exception:
        logger.error("The level parameter is worng, set to INFO by default")
        coloredlogs.install(level='INFO')

    # Validations
    if (args.contract):
        filedb = "contract-" + args.blockchain + "-" + args.contract + ".db"

        if (args.file):
            logger.warning("Parameter file are discarded because contract is provided")

        if (args.blockchain == "bsc"):
            # WARNING: Remove
            # asyncio.run(bsc.bsc_json_collect(args.contract, args.block_from, args.block_to, key['bscscan'], chunk=args.chunk))
            bsc.bsc_db_collect_async(args.contract, args.block_from, args.block_to, key['bscscan'], filedb, chunk=args.chunk)

        if (args.blockchain == "eth"):
            # WARNING: Remove
            # asyncio.run(eth.eth_json_collect(args.contract, args.block_from, args.block_to, key['ethscan'], chunk=args.chunk))
            eth.eth_db_collect_async(args.contract, args.block_from, args.block_to, key['ethscan'], filedb, chunk=args.chunk)

    elif (args.file):
        if (args.blockchain == "bsc"):
            rc = bsc.bsc_db_process(args.file)
        if (args.blockchain == "eth"):
            rc = eth.eth_db_process(args.file)

    # WARNING: Death code soon
    # elif (args.file[-4:] == 'json'):
    #     if (args.blockchain == "bsc"):
    #         rc = bsc.bsc_json_process(args.file)
    #     if (args.blockchain == "eth"):
    #         rc = eth.eth_json_process(args.file)

    else:
        if (args.block_from or args.block_to or args.chunck):
            logger.error("The CONTRACT ADDRESS is not specified")
            raise RuntimeError("The CONTRACT ADDRESS is not specified")

    if (args.web):
        sys.stdout.flush()
        # File to process
        if (args.file):
            filename = args.file
        else:
            filename = filedb
        
        kwargs_flask = {"ip": "127.0.0.1", "port": 5000, "file": filename}
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
