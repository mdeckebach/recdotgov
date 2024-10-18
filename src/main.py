from datetime import date
from ast import literal_eval

from dotenv import dotenv_values

import entry_points
import snapshots


if __name__ == '__main__':
    # Get environmental variables for db connection
    env = dotenv_values('.env')
    PERMIT_IDS = literal_eval(env['PERMIT_IDS'])
    today = date.today()

    for permit_id in PERMIT_IDS:
        entry_points.run_pipeline(permit_id)
        snapshots.run_pipeline(permit_id, today)