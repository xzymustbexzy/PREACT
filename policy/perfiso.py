

def perfiso_policy(state, RUNNING_CORES=104):
    # 设置buffer_cores时，如果在8个核上运行，设置为2；之后类比
    buffer_cores = 2 / 8 * RUNNING_CORES

    online_app_cpu_util = state['online_app_cpu_util']
    total_cpu_core = online_app_cpu_util / 100 + buffer_cores
    # 设置在线任务需要多少core时，如果计算出来需要的core大于总核数，将离线任务的quota设置为0.1
    if total_cpu_core >= RUNNING_CORES:
        future_quota = 0.1
    else:
        future_quota = RUNNING_CORES - total_cpu_core

    return future_quota


if __name__ == '__main__':
    state = {'online_app_cpu_util': 1000}
    quota = perfiso_policy(state)
    print(quota)


