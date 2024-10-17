from datetime import date

from dotenv import dotenv_values

import entry_points
import snapshots


if __name__ == '__main__':
    # Get environmental variables for db connection
    env = dotenv_values('.env')
    PERMIT_ID = env['PERMIT_ID']
    today = date.today()

    entry_points.run_pipeline(PERMIT_ID)
    snapshots.run_pipeline(PERMIT_ID, today)