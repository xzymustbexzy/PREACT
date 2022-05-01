import pandas as pd


rt_threshold = 156
policy = 'perfiso'

def calc_violate_rate(df):
    df_time = df.groupby('datetime').mean()
    num_violate = len(df_time[df_time.rt > rt_threshold])
    total_epochs = len(df_time)
    violate_rate = num_violate / total_epochs * 100
    print(f'Violate rate {num_violate} / {total_epochs} = {violate_rate:.2f}%')
    return violate_rate


def calc_cpu_utilization(df):
    mean_cpu_util = df.cpu_utils.mean()
    print(f'CPU utilization = {mean_cpu_util:.2f}%')
    return mean_cpu_util


if __name__ == '__main__':
    policy = 'autopilot'
    df_rt = pd.read_csv(f'{policy}/rt_result.csv')
    calc_violate_rate(df_rt)
    df_cpu = pd.read_csv(f'{policy}/cpu_utils_result.csv')
    calc_cpu_utilization(df_cpu)

