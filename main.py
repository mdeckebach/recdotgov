from datetime import date
import src.entry_points as entry_points
import src.snapshots as snapshots


# Globals
INYO_ID = '233262'
TODAY = date.today()

if __name__ == '__main__':
    entry_points.run_pipeline(INYO_ID)
    snapshots.run_pipeline(INYO_ID, TODAY)