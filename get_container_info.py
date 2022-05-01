import re
import os
import subprocess


def get_container_info(history_window=60):
    """从容器的nginx中读取流量信息
    
    返回一个dict，key为容器的id，value为一个list，记录了历史一小时的datetime、qps和rt"""
    container_ids = []
    p = subprocess.Popen('pouch ps | grep main',shell=True,stdout=subprocess.PIPE)
    out, err = p.communicate()
    for line in out.splitlines():
        line = line.decode('utf8')
        for s in line.split(' ')[1:]:
            if s != '':
                container_ids.append(s)
                break

    # print(container_ids)


    containers_info = {}

    for container_id in container_ids:
        cmd = 'pouch exec -u 0 ' + container_id + f' tsar --nginx -i 1 -w {history_window}'
        p = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE)
        out, err = p.communicate()
        history_info = []
        for line in out.splitlines():
            line = line.decode('utf8')
            if re.match(r'(\d+)/(\d+)/(\d+)\-(\d+):(\d+)', line):
                line = re.sub('\s+',' ',line)
                line = line.split(' ')
                line = [s for s in line if s != '']
                datetime, accept, handle, reqs, active, read, write, wait, qps, rt, sslqps, spdyps, sslf, sslv3f, h2qps, sslhds, sslk = line
                qps = qps.strip()
                rt = rt.strip()
                if qps.endswith('K'):
                    qps = float(qps[:-1]) * 1000
                if rt.endswith('K'):
                    rt = float(rt[:-1]) * 1000
                history_info.append({
                    'datetime': datetime,
                    'qps': float(qps), 
                    'rt': float(rt)
                })
        containers_info[container_id] = history_info

    return containers_info


if __name__ == '__main__':
    containers_info = get_container_info()
    print(f'Number of containers: {len(containers_info)}')
    for container_id, info in containers_info.items():
        print(container_id, f'(qps={info[-1]["qps"]}, rt={info[-1]["rt"]})')
    max_rt = max([float(info[-1]['rt']) for info in containers_info.values()])
    mean_rt = sum([float(info[-1]['rt']) for info in containers_info.values()]) / len(containers_info)
    print(f'max rt = {max_rt}')
    print(f'mean rt = {mean_rt}')
    total_qps = sum([float(info[-1]['qps']) for info in containers_info.values()])
    mean_qps = sum([float(info[-1]['qps']) for info in containers_info.values()]) / len(containers_info)
    print(f'mean qps = {mean_qps}')
    print(f'total qps = {total_qps}')

