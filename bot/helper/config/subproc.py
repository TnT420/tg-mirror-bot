import logging
import os
import subprocess
import time

LOGGER = logging.getLogger(__name__)

aria2c: subprocess.Popen


def ariaDaemonStart():
    global aria2c
    trackerslistName = 'trackerslist.txt'
    dl(os.environ['TRACKERSLIST'], trackerslistName)
    scriptName = 'aria.sh'
    LOGGER.info(f"Generating '{scriptName}'...")
    dat = (
        f'#!/bin/bash' '\n' '\n'
        f'aria2c \\' '\n'
        f'   --enable-rpc \\' '\n'
        f'   --rpc-listen-all=false \\' '\n'
        f'   --rpc-listen-port=6800 \\' '\n'
        f'   --check-certificate=false \\' '\n'
        f'   --daemon=true \\' '\n'
        f'   --max-connection-per-server=10 \\' '\n'
        f'   --rpc-max-request-size=1024M \\' '\n'
        f'   --min-split-size=10M \\' '\n'
        f'   --allow-overwrite=true \\' '\n'
        f'   --bt-tracker=$(cat {trackerslistName}) \\' '\n'
        f'   --bt-max-peers=0 \\' '\n'
        f'   --seed-time=0.01 \\' '\n'
        f'   --follow-torrent=mem \\' '\n'
        f'   --split=10 \\' '\n'
        f'   --max-overall-upload-limit=1K \\' '\n'
        f'   --max-overall-download-limit={os.environ["MAX_DOWNLOAD_SPEED"]} \\' '\n'
        f'   --max-concurrent-downloads={os.environ["MAX_CONCURRENT_DOWNLOADS"]}' '\n' '\n'
    )
    open(scriptName, 'w').write(dat)
    if open(scriptName, 'r').read() == dat:
        LOGGER.info(subprocess.run(['chmod', '+x', scriptName, '-v'], stdout=subprocess.PIPE).stdout.decode('utf-8'))
        aria2c = subprocess.Popen(f'./{scriptName}')
        LOGGER.info(f"{scriptName} started (pid {aria2c.pid})")
        return
    else:
        exit(1)


def killAll():
    global aria2c
    aria2c.terminate()
    LOGGER.info(f"aria.sh killed (pid {aria2c.pid})")
    LOGGER.info(subprocess.run(['pkill', 'aria2c', '-e'], stdout=subprocess.PIPE).stdout.decode('utf-8'))


def dl(url: str, fileName):
    DL_WAIT_TIME = int(os.environ['DL_WAIT_TIME'])
    subprocess.run(['aria2c', url, '--quiet=true', '--out=' + fileName])
    time_lapsed = 0
    while time_lapsed != DL_WAIT_TIME:
        if os.path.exists(fileName):
            break
        else:
            time.sleep(0.1)
            time_lapsed += 0.1
