import numpy as np


def dt_td_mvg(last_qps_list, Td, rt, RUNNING_CORES):
    total_l_t  = 0
    for qps in last_qps_list:
        total_l_t += qps
    average_l_t = total_l_t / len(last_qps_list)

    total_l_td = 0
    if len(last_qps_list) <= Td:
        total_l_td += np.sum(last_qps_list)
        average_l_td = total_l_td / len(last_qps_list)
    else:
        total_l_td += np.sum(last_qps_list[len(last_qps_list) - Td:])
        average_l_td = total_l_td / Td
    return average_l_td / average_l_t * cal_dt_mvg(last_qps_list, rt, RUNNING_CORES)


def cal_dt_mvg(last_qps_list, rt, RUNNING_CORES):
    lt = get_online_future_quota(last_qps_list[-1], RUNNING_CORES)
    dt = lt - rt
    return dt


def get_online_future_quota(next_qps, RUNNING_CORES):
    # 按照ir为6000，需要800%利用率设置
    return ((next_qps / 650 * 100)) * 1000000


def bursty_policy(state, RT_THRESHOLD=100, RUNNING_CORES=100):
    qps_list = state['history_qps']
    pos = 0
    last_qps_list = []
    last_quota_list = []
    # Initialize Td
    Td = 1
    # Initialize Buffer length
    K = 0
    for i in range(0, len(qps_list)):
        curr_qps = int(qps_list[i])
        if i != 0:
            if pos == Td:
                n_proactive = dt_td_mvg(last_qps_list, Td, last_quota_list[-1], RUNNING_CORES)
                pos = 0
            n_reactive = cal_dt_mvg(last_qps_list, last_quota_list[-1], RUNNING_CORES)
            # n_reactive大于k表示online需要增加资源
            # n_proactive大于0表示online需要增加资源
            # 即时和历史趋势都认为应该增加资源，则一下子增加很多
            if n_reactive > K and n_proactive > 0:
                online_future_quota = last_quota_list[-1] + n_proactive + n_reactive
                # print("!!!", online_future_quota, last_quota_list[-1], n_reactive, n_proactive)
            # 即时的认为需要增加资源，但是历史趋势认为不应该增加资源，则按照即时的来处理
            elif n_reactive > K and n_proactive <= 0:
                online_future_quota = last_quota_list[-1] + n_reactive
                # print("###", online_future_quota, last_quota_list[-1], n_reactive, n_proactive)
            # 即时的认为不用增加资源，则按照历史趋势的结论来处理
            else:
                online_future_quota = last_quota_list[-1] + n_proactive
                # print("***", online_future_quota, last_quota_list[-1], n_reactive, n_proactive)

            # online_future_quota = last_quota_list[-1] + n_reactive

            pos += 1
        else:
            online_future_quota = get_online_future_quota(curr_qps, RUNNING_CORES)
            n_proactive = 0

        # 设置在线任务需要多少core时，如果计算出来需要的core大于总核数，将离线任务的quota设置为0.1
        if online_future_quota >= RUNNING_CORES * 1000000:
            future_quota = 0.1 * 1000000
        else:
            future_quota = RUNNING_CORES * 1000000 - online_future_quota
            if future_quota >= RUNNING_CORES * 1000000:
                future_quota = RUNNING_CORES * 1000000

        last_quota_list.append(RUNNING_CORES * 1000000 - future_quota)
        last_qps_list.append(curr_qps)

    future_quota = future_quota / 1000000
    return future_quota


