import time
from datetime import datetime
import os
import threading

from set_quota import init_offline_app, set_quota, exit_offline_app
from policy.bursty import bursty_policy
from policy.perfiso import perfiso_policy
from policy.autopilot import autopilot_policy
from get_container_info import get_container_info
from get_system_info import get_system_info
from get_online_app_cpu_util import get_online_app_cpu_util, get_history_online_app_cpu_util


def run_cpu_util_collect_thread(policy):
    root = os.path.join('result', policy)
    filepath = os.path.join(root, 'cpu_every_second.csv')
    with open(filepath, 'w', encoding='utf8') as f:
        f.write('datetime,cpu_utils\n')
    while True:
        system_info = get_system_info()
        with open(filepath, 'a', encoding='utf8') as f:
            f.write(f'{datetime.now()},{system_info["cpu_util"]}\n')
        time.sleep(1)


def get_current_state():
    container_info = get_container_info()
    window_size = min([len(info) for info in list(container_info.values())])
    history_qps = [0] * window_size
    for cid, info_list in container_info.items():
        assert(len(info_list) == window_size, 'All container info must has the same window size!!')
        for i, info in enumerate(info_list[-window_size:]):
            history_qps[i] += info['qps']
    
    online_app_cpu_util = get_online_app_cpu_util()
    history_online_cpu_util = get_history_online_app_cpu_util()

    state = {
        'history_qps':  history_qps,
        'online_app_cpu_util': online_app_cpu_util,
        'history_online_cpu_util': history_online_cpu_util
    }
    return state


def get_current_rt():
    containers_info = get_container_info()
    window_size = min([len(info) for info in containers_info.values()])
    history_mean_rt = [0] * window_size
    history_max_rt = [0] * window_size
    for i in range(window_size):
        history_max_rt[-i] = max([float(info[-i]['rt']) for info in containers_info.values()])
        history_mean_rt[-i] = sum([float(info[-i]['rt']) for info in containers_info.values()]) / len(containers_info)
    return {
        'history_mean_rt': history_mean_rt,
        'history_max_rt': history_max_rt
    }


def run(policy, policy_time_interval=60):
    policy_func_table = {
        'bursty': bursty_policy,
        'perfiso': perfiso_policy,
        'autopilot': autopilot_policy
    }
    policy_func = policy_func_table[policy]
    print(f'Runing evaluate program (policy: {policy})')

    init_offline_app()
    history_system_info = []
    history_quota = []
    try:
        while True:
            begin_time = time.time()
            state = get_current_state()
            system_info = get_system_info()
            history_system_info.append(system_info)
            quota = policy_func(state)
            history_quota.append(quota)
            print('=' * 20)
            print(f'Current time: {datetime.now()}')
            print(f'Policy give quota: {quota}')
            performance = get_current_rt()
            print(f'max rt = {performance["history_max_rt"][-1]}')
            print(f'mean rt = {performance["history_mean_rt"][-1]}')
            print(f'cpu util = {system_info["cpu_util"]}')
            print()
            set_quota(quota)
            end_time = time.time()
            use_time = end_time - begin_time
            time.sleep(policy_time_interval - use_time)
    except KeyboardInterrupt:
        print('Finished!')

    state = get_container_info(history_window=80)
    print(state)
    root = os.path.join('result', policy)
    if not os.path.exists(root):
        os.mkdir(root)
    with open(os.path.join(root, 'rt_result.csv'), 'w', encoding='utf8') as f:
        f.write('container_id,datetime,qps,rt\n')
        for cid, info_list in state.items():
            for info in info_list:
                f.write(f'{cid},{info["datetime"]},{info["qps"]},{info["rt"]}\n')
    with open(os.path.join(root, 'cpu_utils_result.csv'), 'w', encoding='utf8') as f:
        f.write('time,cpu_utils\n')
        for system_info in history_system_info:
            f.write(f'{system_info["time"]},{system_info["cpu_util"]}\n')
    with open(os.path.join(root, 'quota_history.csv'), 'w', encoding='utf8') as f:
        f.write('quota\n')
        for quota in history_quota:
            f.write(f'{quota}\n')
    exit_offline_app()


if __name__ == '__main__':
    policy = 'autopilot'
    thread = threading.Thread(target=run_cpu_util_collect_thread, args=(policy,))
    thread.start()
    run(policy)



