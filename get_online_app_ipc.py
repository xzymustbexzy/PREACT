import subprocess

from utils import get_online_app_pid_list


def get_online_app_ipc():
    pid_list = get_online_app_pid_list()
    pid_list_str = ','.join([str(pid) for pid in pid_list])
    p = subprocess.Popen(f'perf stat -p {pid_list_str} sleep 1', shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    for line in out.splitlines():
        line = line.decode('utf8')
        if 'instructions' in line:
            print('hhhhh')
            line = [s for s in line.split(' ') if s != '']
            print(line)
            i = line.index('#')
            ipc = float(line[i + 1])
            return ipc
    raise NotImplementedError


if __name__ == '__main__':
    ipc = get_online_app_ipc()
    print(ipc)

