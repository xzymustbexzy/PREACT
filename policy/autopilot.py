import math
import numpy as np


def get_w(half_life, time_stamp):
    return math.pow(2, -time_stamp / half_life)


def get_online_cpu_quota(cpu_util_list, sample_interval, bins, half_life, q):
    cpu_util_list = np.array(cpu_util_list)
    cpu_util_list = cpu_util_list / 100
    cpu_util_time_split = []
    for i in range(len(cpu_util_list) // sample_interval):
        end_index = len(cpu_util_list) - i * sample_interval
        begin_index = end_index - sample_interval
        hist, _ = np.histogram(cpu_util_list[begin_index:end_index], bins)
        hist = hist / hist.sum()
        cpu_util_time_split.append(hist)
    # cpu_util_time_split.shape = [N_intervals, num_bins]
    cpu_util_time_split = np.array(cpu_util_time_split)
    for i in range(cpu_util_time_split.shape[0]):
        w = get_w(half_life, i)
        cpu_util_time_split[i, :] = cpu_util_time_split[i, :] * w
    cpu_util_time_split = cpu_util_time_split.sum(axis=0)
    cpu_util_time_split = cpu_util_time_split / cpu_util_time_split.sum()
    acc_cpu_util_time_split = np.add.accumulate(cpu_util_time_split)
    q = q / 100
    for i in range(acc_cpu_util_time_split.shape[0]):
        if acc_cpu_util_time_split[i] > q:
            value = i
            break
    return value


def get_online_future_quota(next_qps, RUNNING_CORES):
    # 按照ir为6000，需要800%利用率设置
    return (next_qps / 650 * 100)


def autopilot_policy(state, RUNNING_CORES=104):
    perc_value = 90
    half_life = 2
    window_size = 60
    sample_interval = 5
    bins = list(range(RUNNING_CORES + 1))

    total_cpu_util_list = state['history_online_cpu_util'][-window_size:]
    qps_list = state['history_qps']

    if len(total_cpu_util_list) < sample_interval:
        current_qps = qps_list[-1]
        online_future_quota = get_online_future_quota(current_qps, RUNNING_CORES)
        if online_future_quota >= RUNNING_CORES:
            future_quota = 0.1
        else:
            future_quota = RUNNING_CORES - online_future_quota
            if future_quota >= RUNNING_CORES:
                future_quota = RUNNING_CORES
    else:
        online_cores = get_online_cpu_quota(total_cpu_util_list, sample_interval, bins, half_life, perc_value)
        future_quota = RUNNING_CORES - online_cores
    return future_quota
    

if __name__ == "__main__":
    state = {
        'history_online_cpu_util': [500, 600, 700, 800, 900, 5000, 5000, 5000, 5000, 5000, 200, 300, 400, 100],
        'history_qps': [30]
    }
    quota = autopilot_policy(state)
    print(quota)
    

