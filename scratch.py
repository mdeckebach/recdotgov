import pandas as pd
import requests


def get_permit_metadata(permit_id):
    url = f'https://www.recreation.gov/api/permitcontent/{permit_id}'
    headers = {'User-Agent': 'Mozilla/5.0'} # rec.gov's API rejects python-requests User-Agent
    return requests.get(url, headers=headers)

def get_availability(permit_id, start_date, end_date, commercial_acct='false'):
    params = {'start_date': start_date, 'end_date': end_date, 'commercial_acct': commercial_acct}
    headers = {'User-Agent': 'Mozilla/5.0'} # rec.gov's API rejects python-requests User-Agent
    url = f'https://www.recreation.gov/api/permitinyo/{permit_id}/availabilityv2'
    return requests.get(url, headers=headers, params=params)



inyo_id = '233262'
start_date = '2024-09-01'
end_date = '2024-09-30'


r = get_permit_metadata(inyo_id)

# TODO: make this a function w/ retries before short-circuiting
r.raise_for_status() # will raise error if request fails


data = r.json()
df = pd.DataFrame(data['payload']['campsites'])
pd.set_option('display.max_columns', None)
print(df.head())


