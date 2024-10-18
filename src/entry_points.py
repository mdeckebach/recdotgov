from datetime import datetime
from time import sleep

from dotenv import dotenv_values
import pymysql
import requests

from setup_logger import setup_logger
import sql


logger = setup_logger(__name__)

# Get environmental variables for db connection
env = dotenv_values('.env')
HOST = env['HOST']
USER = env['USER']
PASSWORD = env['PASSWORD']
DATABASE = env['DATABASE']
MAX_RETRIES = int(env['MAX_RETRIES'])
RETRY_DELAY = int(env['RETRY_DELAY'])
HEADERS = {'User-Agent': env['USER_AGENT']}

def extract(permit_id):
    url = f'https://www.recreation.gov/api/permitcontent/{permit_id}'
    
    for attempt in range(1, MAX_RETRIES + 1):
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 200:
            data = response.json()
            logger.info('Payload received (Attempt %s)', attempt)
            return data
        else:
            logger.warning('Payload failed with status code: %s (Attempt %s)', response.status_code, attempt)
            if attempt < MAX_RETRIES:
                sleep(RETRY_DELAY)
            else:
                raise Exception('Max retries reached. Failed to extract data.')

def transform(data):
    '''Converts nested dictionary into list of tuples for easier database upserting'''
    transformed_data = []
    for d in data['payload']['divisions'].values():

        # Get modified_time into a datetime format
        modified_ts = datetime.fromisoformat(d['modified_time'].replace('Z', '+00:00'))
        if modified_ts.year == 1: # catch default 0001-01-01 00:00:00 values
            modified_ts = None

        transformed_data.append((d['code'], d['description'], d['district'], d['id'], d['latitude'], d['longitude'], modified_ts, d['name'], d['permit_id'], d['version']))

    return transformed_data

def load(data):
    '''Updates DB with latest metadata for each entry_point'''
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            connection = pymysql.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
            cursor = connection.cursor()
            logger.info('DB connection established (Attempt %s)', attempt)
            cursor.execute(sql.CREATE_DIM_ENTRY_POINTS_IF_NOT_EXISTS)
            cursor.executemany(sql.REPLACE_ENTRY_POINTS, data)
            connection.commit()
            connection.close()
            return len(data)
        except Exception as e:
            if attempt < MAX_RETRIES:
                logger.warning('Load failed with error: %s (Attempt %s)', e, attempt)
                sleep(RETRY_DELAY)
            else:
                raise Exception('Max retries reached. Failed to load data to database.')

def run_pipeline(permit_id):
    try:
        raw_data = extract(permit_id)
        transformed_data = transform(raw_data)
        rows_affected = load(transformed_data)
        logger.info('ENTRY_POINTS pipeline complete. %s rows upserted', rows_affected)
    except Exception as e:
        logger.error('Terminal Error: %s', e)
