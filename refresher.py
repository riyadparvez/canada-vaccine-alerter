from loguru import logger
from random import randint
import os
import sys
import time

logger.remove()
logger.add(sys.stdout, level="DEBUG", colorize=True, format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> <blue>|{level: ^8}|</blue> <cyan>{module: ^10}:{function: ^15}:{line: >3}</cyan> - <level>{message}</level>", backtrace=True)

REFRESH_TIME = 60

def refresher(seconds):
    logger.info("Starting refersher script")
    while True:
        mainDir = os.path.dirname(__file__)
        filePath = os.path.join(mainDir, 'dummy.py')
        with open(filePath, 'w') as f:
            rand_num = randint(0, 10000)
            f.write(f'# {rand_num}')
            logger.info(f"Wrote {rand_num} to file. Sleep for {seconds} seconds.")
        time.sleep(seconds)

refresher(REFRESH_TIME)
