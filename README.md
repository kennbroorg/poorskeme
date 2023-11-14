<div align="center" style="margin-bottom: 10px;">
    <a href="https://twitter.com/intent/follow?screen_name=kennbroorg">
	<img alt="follow on Twitter" src="https://img.shields.io/twitter/follow/kennbroorg.svg?label=follow%20&style=for-the-badge&logo=twitter&labelColor=abcdef&color=1da1f2">
    </a>
</div>

---

<div align="center">
    <img alt="Logo" src="https://kennbroorg.gitlab.io/poorskeme-page/img/poorSKeme-logo.png">
</div>

---
# poorSKeme

OSINT - Data Visualization - Blockchain - Awareness - Scam

<div align="center">
    <img alt="Principal" src="https://kennbroorg.gitlab.io/poorskeme-page/img/principal.png">
</div>

# Install
Go to this [site](https://kennbroorg.gitlab.io/poorskeme-page/) and click on the downdload button
Or go to release section. Download the ZIP file called poorSKeme.zip

Unzip it, install requeriments and execute it.

``` shell
unzip poorSKeme.zip
cd poorSKeme
pip install -r requirements.txt
python3 poorSKeme --help
```
```
$$$$$$$\                                       $$$$$$\  $$\   $$\
$$  __$$\                                     $$  __$$\ $$ | $$  |
$$ |  $$ | $$$$$$\   $$$$$$\   $$$$$$\        $$ /  \__|$$ |$$  / $$$$$$\  $$$$$$\$$$$\   $$$$$$\
$$$$$$$  |$$  __$$\ $$  __$$\ $$  __$$\       \$$$$$$\  $$$$$  / $$  __$$\ $$  _$$  _$$\ $$  __$$\
$$  ____/ $$ /  $$ |$$ /  $$ |$$ |  \__|       \____$$\ $$  $$<  $$$$$$$$ |$$ / $$ / $$ |$$$$$$$$ |
$$ |      $$ |  $$ |$$ |  $$ |$$ |            $$\   $$ |$$ |\$$\ $$   ____|$$ | $$ | $$ |$$   ____|
$$ |      \$$$$$$  |\$$$$$$  |$$ |            \$$$$$$  |$$ | \$$\\$$$$$$$\ $$ | $$ | $$ |\$$$$$$$\
\__|       \______/  \______/ \__|             \______/ \__|  \__|\_______|\__| \__| \__| \_______|

usage: poorSKeme.py [-h] [-bc {bsc,eth}] [-ct CONTRACT] [-bf BLOCK_FROM] [-bt BLOCK_TO] [-c CHUNK] [-f FILE] [-w]

Contract analyzer

optional arguments:
  -h, --help            show this help message and exit

Get and process data:
  -bc {bsc,eth}, --blockchain {bsc,eth}
                        Select Blockchain (bsc, eth)
  -ct CONTRACT, --contract CONTRACT
                        address of contract
  -bf BLOCK_FROM, --block-from BLOCK_FROM
                        Block start
  -bt BLOCK_TO, --block-to BLOCK_TO
                        Block end
  -c CHUNK, --chunk CHUNK
                        Chunks of blocks

Process data from JSON file:
  -f FILE, --file FILE  JSON file of recolected data

Start WebServer visualization data:
  -w, --web             WEB for data visaulization

            Examples
            --------

            # Extract TRXs of contract from block to block (Ethereum Network)
            python3 poorSKeme.py -bc eth -ct 0xb547027A4CCD46EC98199Fa88AAEDF5aA981Db26 -bt 6496413        # To collect

            # Extract TRXs of contract from block to block (Binance Smart Chain)
            python3 poorSKeme.py -bc bsc -ct 0xe878BccA052579C9061566Cec154B783Fc5b9fF1 -bt 15552901       # To collect

            # Data Visualization of processed contract information (Binance Smart Chain)
            python3 poorSKeme.py -bc bsc -f contract-0xe878BccA052579C9061566Cec154B783Fc5b9fF1.db -w  # To visualice data

```
If you use the web param, the port is 4200. The complete url is http://127.0.0.1:4200.

# API
Get the Free API from https://etherscan.io/apis (Ethereum) and from https://bscscan.com/apis (Binance Smart Chain)
Load them in the API.yaml file replacing the XXX by the corresponding APIKey

# Example
## Getting data
To collect data from contract 0xe878BccA052579C9061566Cec154B783Fc5b9fF1 (Ethereum is the blockchain default)
```
python3 poorSKeme.py -ct 0xb547027A4CCD46EC98199Fa88AAEDF5aA981Db26
```
But this could take too long, so you can pass by parameter the block from and block to
```
python3 poorSKeme.py -bc bsc -ct 0xe878BccA052579C9061566Cec154B783Fc5b9fF1 -bf 14040726 -bt 15552901
```
Or just block to
```
python3 poorSKeme.py -bc bsc -ct 0xe878BccA052579C9061566Cec154B783Fc5b9fF1 -bt 15552901
```
Note the -bc parameter which indicates the blockchain network (Binance Smart Chain in this case)


This will result in a file named contract-bsc-[CONTRACT].json, for our example it will be called contract-bsc-0xe878BccA052579C9061566Cec154B783Fc5b9fF1.json

## Process data and visualization
After obtaining the data file you can process the information and visualize it by executing
```
python3 poorSKeme.py -f ./contract-bsc-0xe878BccA052579C9061566Cec154B783Fc5b9fF1.db -w
```
The above command will turn on two services, an internal API on port 5000 and the webi visualization on port 4200. Just open the browser and enter the address http://127.0.0.1:4200

<p float="left" style="text-align: center;">
  <img alt="Resume" src="https://kennbroorg.gitlab.io/poorskeme-page/img/resume.png" style="width: 48%; margin: 10px;"/>
  <img alt="Detail" src="https://kennbroorg.gitlab.io/poorskeme-page/img/detail.png" style="width: 48%; margin: 10px;"/>
  <img alt="Code" src="https://kennbroorg.gitlab.io/poorskeme-page/img/code.png" style="width: 48%; margin: 10px;"/>
  <img alt="Diagram" src="https://kennbroorg.gitlab.io/poorskeme-page/img/diagram.png" style="width: 48%; margin: 10px;"/>
</p>

<div align="center">
    <img alt="Distribution" src="https://kennbroorg.gitlab.io/poorskeme-page/img/bkg_poorSKeme.png"/>
</div>

# Disclaimer
This is a young project, started in mid-March 2022, so it may contain errors.
Over time, and with feedback, the project will grow and bugs will be fixed, but it is a personal project and the time dedicated to it is undetermined.

# Disclaimer
This is a young project, started in mid-March 2022, so it may contain errors.
Over time, and with feedback, the project will grow and bugs will be fixed, but it is a personal project and the time dedicated to it is undetermined.

# Disclaimer
This is a young project, started in mid-March 2022, so it may contain errors.
Over time, and with feedback, the project will grow and bugs will be fixed, but it is a personal project and the time dedicated to it is undetermined.

> I posted the disclaimer three times, maybe you will read it even once

# Simple Roadmap
- [X] Binance Blockchain support
- [X] Ethereum Blockchain support
- [X] Data collect
- [X] Visualization
- [X] Early detection of scams
- [X] Automatic anomaly detection

...

- [?] Traceability
- [ ] Wallet identification

These last two points of the roadmap are subject to a lot of research, but nothing is impossible.
