from datetime import datetime
from time import sleep

from dateutil.relativedelta import relativedelta
from dotenv import dotenv_values
import pymysql
import requests

from setup_logger import setup_logger
import sql


logger = setup_logger(__name__)

# Get environmental variables
env = dotenv_values('.env')
HOST = env['HOST']
USER = env['USER']
PASSWORD = env['PASSWORD']
DATABASE = env['DATABASE']
MAX_RETRIES = int(env['MAX_RETRIES'])
RETRY_DELAY = int(env['RETRY_DELAY'])
HEADERS = {'User-Agent': env['USER_AGENT']}

def extract(permit_id, start_date, num_months, commercial_acct='false'):
    raw_data = {'snapshot_ts': datetime.now(), 'permit_id': permit_id, 'payloads': {}}
    
    for i in range(num_months):
        date = start_date + relativedelta(months=i)
        start_of_month = date.replace(day=1)
        end_of_month = start_of_month + relativedelta(months=1, days=-1)
        payload = get_payload(permit_id, start_of_month, end_of_month, commercial_acct)
        raw_data['payloads'] = raw_data['payloads'] | payload['payload']
    
    return raw_data

def get_payload(permit_id, start_date, end_date, commercial_acct='false'):
    url = f'https://www.recreation.gov/api/permitinyo/{permit_id}/availabilityv2'
    params = {'start_date': start_date, 'end_date': end_date, 'commercial_acct': commercial_acct}

    for attempt in range(1, MAX_RETRIES + 1):
        response = requests.get(url, headers=HEADERS, params=params)

        if response.status_code == 200:
            data = response.json()
            logger.info('Payload %s - %s received (Attempt %s)', start_date, end_date, attempt)
            return data
        else:
            logger.warning('Payload %s - %s failed with status code: %s (Attempt %s)', start_date, end_date, response.status_code, attempt)
            if attempt < MAX_RETRIES:
                sleep(RETRY_DELAY)
            else:
                raise Exception('Max retries reached. Failed to extract data.')

def transform(data):
    '''Converts nested dictionaries into list of tuples for easier database upserting'''
    transformed_data = []

    # Construct tuples for each permit_id + entry_id + reservation_ds combo, which represents a new row of data
    permit_id = data['permit_id']
    snapshot_ts = data['snapshot_ts']
    for reservation_ds, date_data in data['payloads'].items():
        for entry_id, entry_data in date_data.items():
            available = entry_data['quota_usage_by_member_daily']['remaining']
            total = entry_data['quota_usage_by_member_daily']['total']
            reserved = total - available
            is_walkup = entry_data['is_walkup']
            not_yet_released = entry_data.get('not_yet_released', 0)
            release_ts = entry_data.get('release_date')
            transformed_data.append((entry_id, permit_id, reservation_ds, available, reserved, total, is_walkup, not_yet_released, release_ts, snapshot_ts))

    return transformed_data

def load(data):
    '''Appends records for any reservation_ds + entry_id combinations that have changed vs latest db record'''
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            connection = pymysql.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
            cursor = connection.cursor()
            logger.info('DB connection established (Attempt %s)', attempt)

            # Get latest snapshot in DB for each permit_id + entry_id + reservation_ds
            cursor.execute(sql.SELECT_LATEST_SNAPSHOTS)
            latest_snapshots = cursor.fetchall()
            latest_set = set(latest_snapshots) # For more efficient lookup
            records_to_insert = []

            # Isolate new records that differ from most recent record in DB (slicing ignores snapshot_ts)
            for record in data:
                if record[:-1] not in latest_set:
                    records_to_insert.append(record)
                
            if records_to_insert:
                cursor.executemany(sql.INSERT_SNAPSHOT, records_to_insert)
                connection.commit()

            connection.close()
            return len(records_to_insert)

        except Exception as e:
            if attempt < MAX_RETRIES:
                logger.warning('Load failed with error: %s (Attempt %s)', e, attempt)
                sleep(RETRY_DELAY)
            else:
                raise Exception('Max retries reached. Failed to load data to database.')


def run_pipeline(permit_id, date, num_months=7):
    try:
        raw_data = extract(permit_id, date, num_months)
        transformed_data = transform(raw_data)
        rows_affected = load(transformed_data)
        logger.info('SNAPSHOTS pipeline complete. %s rows inserted', rows_affected)
    except Exception as e:
        logger.error('Terminal Error: %s', e)
