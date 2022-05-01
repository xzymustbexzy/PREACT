import os
from datetime import datetime

import pandas as pd


df_list = []
profile_dir = 'profile文件'
for filename in os.listdir(profile_dir):
    df = pd.read_csv(os.path.join(profile_dir, filename), index_col=0)
    df_list.append(df)
df = pd.concat(df_list, axis=0)
df = df[df.throughput_type == 'HTTP']
print(df)


time_df = pd.read_csv('timestamp.txt')
begin_times = []
end_times = []
quotas = []
for i, row in time_df.iterrows():
    if i % 2 == 0:
        begin = datetime.strptime(row['timestamp'], '%Y-%m-%d_%H%M%S')
        begin_times.append(begin)
        quota = row['quota']
        quotas.append(quota)
    else:
        end = datetime.strptime(row['timestamp'], '%Y-%m-%d_%H%M%S')
        end_times.append(end)


def search_quota(timestamp):
    for begin, end, quota in zip(begin_times, end_times, quotas):
        if timestamp >= begin and timestamp <= end:
            return quota
    return None


with open('training_data.csv', 'w', encoding='utf8') as f:
    f.write('qps,quota,rt\n')
    for i, row in df.iterrows():
        qps = row['qps__Q_s']
        rt = row['rt__ms_Q']
        timestamp = datetime.strptime(row['sample_time__m'], '%Y-%m-%d %H:%M:%S')
        quota = search_quota(timestamp)
        if quota is not None:
            f.write(f'{qps},{quota},{rt}\n')
