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
    <img alt="Logo" src="https://kennbroorg.gitlab.io/poorskeme-page/img/principal.png">
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
$$ |      \$$$$$$  |\$$$$$$  |$$ |            \$$$$$$  |$$ | \$$\$$$$$$$\ $$ | $$ | $$ |\$$$$$$$\
\__|       \______/  \______/ \__|             \______/ \__|  \__|\_______|\__| \__| \__| \_______|


usage: poorSKeme.py [-h] [-c CHUNK] [-ct CONTRACT] [-bf BLOCK_FROM] [-bt BLOCK_TO] [-f FILE] [-w]

PONZI contract analyzer

optional arguments:
  -h, --help            show this help message and exit

  Get and process data:
    -c CHUNK, --chunk CHUNK 
                        Chunks of blocks
    -ct CONTRACT, --contract CONTRACT
                        address of contract
    -bf BLOCK_FROM, --block-from BLOCK_FROM
                        Block start
    -bt BLOCK_TO, --block-to BLOCK_TO
                        Block end

  Process data from JSON file:
    -f FILE, --file FILE  JSON file of recolected data

  Start WebServer visualization data:
    -w, --web             WEB for data visaulization>
```
If you use the web param, the port is 4200. The complete url is http://127.0.0.1:4200.

# API
Get the Free API from https://bscscan.com/apis 
Load them in the API.yaml file replacing the XXX by the APIKey

# Example
## Getting data
To collect data from contract 0xe878BccA052579C9061566Cec154B783Fc5b9fF1
```
python3 poorSKeme -ct 0xe878BccA052579C9061566Cec154B783Fc5b9fF1
```
But this could take too long, so you can pass by parameter the block from and block to (the block from being the creation block of the contract)
```
python3 poorSKeme -ct 0xe878BccA052579C9061566Cec154B783Fc5b9fF1 -bf 14040726 -bt 15552901
```
This will result in a file named contract-[CONTRACT].json, for our example it will be called contract-0xe878BccA052579C9061566Cec154B783Fc5b9fF1.json

## Process data and visualization
After obtaining the data file you can process the information and visualize it by executing
```
python3 poorSKeme.py -f F/contract-0xe878BccA052579C9061566Cec154B783Fc5b9fF1.json -w
```
The above command will turn on two services, an internal API on port 5000 and the webi visualization on port 4200. Just open the browser and enter the address http://127.0.0.1:4200

<div style="display: flex">
  <div align="center" style="width: 50%; margin: 10px;">
      <a href=""><img src="https://kennbroorg.gitlab.io/poorskeme-page/img/resume.png"></a>
  </div>
  <div align="center" style="width: 50%; margin: 10px;">
      <a href=""><img src="https://kennbroorg.gitlab.io/poorskeme-page/img/detail.png"></a>
  </div>
</div>
<div style="display: flex">
  <div align="center" style="width: 50%; margin: 10px;">
      <a href=""><img src="https://kennbroorg.gitlab.io/poorskeme-page/img/code.png"></a>
  </div>
  <div align="center" style="width: 50%; margin: 10px;">
      <a href=""><img src="https://kennbroorg.gitlab.io/poorskeme-page/img/diagram.png"></a>
  </div>
</div>

<div align="center">
    <a href=""><img src="https://kennbroorg.gitlab.io/poorskeme-page/img/bkg_poorSKeme.png"></a>
</div>

# Disclaimer
This is a young project, started in mid-March 2022, so it may contain errors.
For now, it only works with the Binance blockchain.
Over time, and with feedback, the project will grow and bugs will be fixed, but it is a personal project and the time dedicated to it is undetermined.

# Disclaimer
This is a young project, started in mid-March 2022, so it may contain errors.
For now, it only works with the Binance blockchain.
Over time, and with feedback, the project will grow and bugs will be fixed, but it is a personal project and the time dedicated to it is undetermined.

# Disclaimer
This is a young project, started in mid-March 2022, so it may contain errors.
For now, it only works with the Binance blockchain.
Over time, and with feedback, the project will grow and bugs will be fixed, but it is a personal project and the time dedicated to it is undetermined.

> I posted the disclaimer three times, maybe you will read it even once

# Simple Roadmap
- [X] Binance Blockchain support
- [X] Data collect
- [X] Visualization
- [ ] Ethereum Blockchain support
- [ ] Automatic anomaly detection
- [X] Early detection of scams

...
...
...

- [ ] Traceability
- [ ] Wallet identification

These last two points of the roadmap are subject to a lot of research, but nothing is impossible.
