# poorSKeme

OSINT - Data Visualization - Blockchain - Awareness - Scam

# Install

Go to release section. Download the ZIP file called poorSKeme.zip and unzip it, install requeriments and execute it.

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

# Disclaimer
This is a young project, started in mid-March 2022, so it may contain errors.
Over time, and with feedback, the project will grow and bugs will be fixed, but it is a personal project and the time dedicated to it is uncertain.