## Package Imports
import requests
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize
import json

## Input my previously uncovered user id
user_id = r'##user_id##'

## Connect Session to Peloton API
## Input user email and password
s = requests.Session()
payload = {'username_or_email':'##email_address##', 'password':'##password###'}
s.post('https://api.onepeloton.com/auth/login', json=payload)

## Query API for my followers
follower_string = r"https://api.onepeloton.com/api/user/{}/followers?limit=50".format(user_id)
q_followers = s.get(follower_string)
# Refine query to get a df of ids and usernames
follower_ids = json_normalize(q_followers.json()['data'])
#follower_ids = follower_ids[['id','username']]

## Query API for my personal workouts
pw_query_string = r"https://api.onepeloton.com/api/user/{}/workouts?joins=ride&limit=100".format(user_id)
q_personal_workouts = s.get(pw_query_string)

df_my_id = json_normalize(q_personal_workouts.json()['data'])
df_my_id = df_my_id[df_my_id['fitness_discipline'] == 'cycling']
df_my_id = df_my_id[['id','peloton_id','end_time']]

## Use list of personal workouts from workout ids to query lists of performance stats from API
q_pw_idL = []       ## personal workout id list
q_pw_pgL = []       ## personal workout performance graph list
q_pw_peltonid = []  ## personal workout id list
q_pw_time=[]
for w in df_my_id['id']:
    
    pgs = r'https://api.onepeloton.com/api/workout/{}/performance_graph?every_n=30'.format(w)
    wo_pg = s.get(pgs).json()
    q_pw_pgL.append(wo_pg)

#close the API request item
s.close()

## Refine performance stats into lists of the metric/data that I am interested in
DurL=[]     # Duration
TOL=[]      # Total Output
MOL=[]      # Max Output
AOL=[]      # Average Output
MCL=[]      # Max Cadence
ACL=[]      # Average Cadence
MRL=[]      # Max Resistance
ARL=[]      # Average Resistance
MHRL=[]     # Max Heart Rate
AHRL=[]     # Average Heart Rate

for data in q_pw_pgL:
    
    DurL.append(data['duration'])
    TOL.append(data['summaries'][0]['value'])
    MOL.append(data['metrics'][0]['max_value'])
    AOL.append(data['metrics'][0]['average_value'])
    MCL.append(data['metrics'][1]['max_value'])
    ACL.append(data['metrics'][1]['average_value'])
    MRL.append(data['metrics'][2]['max_value'])
    ARL.append(data['metrics'][2]['average_value'])
    try:
        MHRL.append(data['metrics'][4]['max_value'])
    except:
        MHRL.append(np.nan)
    try:
        AHRL.append(data['metrics'][4]['average_value'])
    except:
        AHRL.append(np.nan)

## Finally zip all of the data together into a dataframe tibble
pelo_stats = pd.DataFrame(zip(df_my_id['id'],df_my_id['peloton_id'],df_my_id['end_time'],DurL,TOL,MOL,AOL,ACL,MRL,ARL,AHRL,MHRL))
# Name the columns
pelo_stats = pelo_stats.rename(columns={0: 'workout_id', 1: 'peloton_id', 2: 'date', 3: 'duration (s)', 4: 'total_output (kJ)',
5: 'max_power (W)', 6: 'average_power (W)', 7: 'average_cadence (RPM)', 8: 'max_resistance (%)',9: 'average_resistence (%)', 10: 'average_heart_rate (BPM)', 11: 'max_heart_rate (BPM)'})
## Convert the data from UNIX time to datetime
pelo_stats['date'] = pd.to_datetime(pelo_stats['date'], unit='s').apply(lambda x: x.to_datetime64())

## Export the data to a CSV
pelo_stats.to_csv(path_or_buf=r'C:\\Users\\####\\Dropbox\\Data\\Projects\\Peloton\\pelo.csv')