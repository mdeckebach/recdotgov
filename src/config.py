from datetime import date
import logging

MAX_RETRIES = 5
RETRY_DELAY = 2
HEADERS = {'User-Agent': 'Mozilla/5.0'} #rec.gov does not like python

def setup_logger(name):
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_name = f'logs/{date.today()}_recdotgov.log'
    file_handler = logging.FileHandler(file_name, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
