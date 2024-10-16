from datetime import date
import src.entry_points as entry_points
import src.snapshots as snapshots


# Globals
inyo_id = '233262'
today = date.today()
num_months = 7 #permits only exist 6 months in advance, so looking out 7 months covers all records

if __name__ == '__main__':
    entry_points.run_pipeline(inyo_id)
    snapshots.run_pipeline(inyo_id, today, num_months)