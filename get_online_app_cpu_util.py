import subprocess

from utils import get_online_app_pid_list


def get_cpu_usage_of_process(pid):
    p = subprocess.Popen(f'top -b -p {pid} -n 1', shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    line = out.splitlines()[-1]
    line = line.decode('utf8')
    line = [s for s in line.split(' ') if s != '']
    # print(line)
    # PID, USER, PR, NI, VIRT, RES, SHR, S, CPU, MEM, TIME, COMMAND = line
    CPU = line[8]
    usage = float(CPU)
    return usage    


def total_cpu_usage_of_processes(pid_list):
    total = 0
    for pid in pid_list:
        total += get_cpu_usage_of_process(pid)
    return total


history_cpu_usage = []


def get_online_app_cpu_util():
    pid_list = get_online_app_pid_list()
    usage = total_cpu_usage_of_processes(pid_list)
    global history_cpu_usage
    history_cpu_usage.append(usage)
    return usage


def get_history_online_app_cpu_util():
    global history_cpu_usage
    return history_cpu_usage


if __name__ == '__main__':
    usage = get_online_app_cpu_util()
    print(f'online application cpu usage: {usage}')
    print(f'running cores: {usage / 100}')

