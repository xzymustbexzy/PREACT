import os
import re
import subprocess
from datetime import datetime


def get_system_info():
    """返回一个dict，key为cpu的id，value为当前cpu的利用率。
    其中比较特殊的cpu id是ALL，表示所有CPU的均值"""
    current_cpu_info = {}
    p = subprocess.Popen('top -b -n 1', shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    line = out.splitlines()[2]
    line = line.decode('utf8')
    line = line[8:].strip()
    m = re.match(r'([\d\.]+)', line)
    usage= float(m.group(1))
    info = {
        'time': str(datetime.now()),
        'cpu_util': usage
    }
    return info


if __name__ == '__main__':
    current_cpu_info = get_system_info()
    print(current_cpu_info)


