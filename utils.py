import subprocess


def get_online_app_pid_list():
    pid_list = []
    p = subprocess.Popen('ps -Af | grep buy', shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    for line in out.splitlines():
        line = line.decode('utf8')
        line = [s for s in line.split(' ') if s != '']
        if line[0] == 'root':
            continue
        pid_list.append(int(line[1]))
    return pid_list


if __name__ == '__main__':
    pid_list = get_online_app_pid_list()
    print(len(pid_list))
    print(pid_list)


