from datetime import date
from ast import literal_eval
import os

from dotenv import load_dotenv
load_dotenv()

import entry_points
import snapshots


if __name__ == '__main__':
    PERMIT_IDS = literal_eval(os.getenv('PERMIT_IDS'))
    today = date.today()

    for permit_id in PERMIT_IDS:
        entry_points.run_pipeline(permit_id)
        snapshots.run_pipeline(permit_id, today)