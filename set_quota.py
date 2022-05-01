import os
import sys
import time
import subprocess


def run_offline_app():
    """Run offline application."""
    os.system('cgcreate -g cpu:czh_cgroup_test')
    os.system('cgset -r cpuset.cpus=0-103 czh_cgroup_test')
    os.system('cgset -r cpuset.mems=0-1 czh_cgroup_test')
    cmd_cfs_period_us   = "cgset -r cpu.cfs_period_us=1000000 czh_cgroup_test"
    cmd_cfs_quota_us    = "cgset -r cpu.cfs_quota_us=-1 czh_cgroup_test"
    cmd_run_offline_app = "cgexec -g cpu:czh_cgroup_test /home/changzhihao.czh/ali-online/run_composite_offline.sh"
    os.system(cmd_cfs_period_us)
    os.system(cmd_cfs_quota_us)
    os.system(cmd_run_offline_app)


def init_offline_app():
    print('Begin to run offline app..')
    run_offline_app()
    print('Wait 60 seconds...')
    time.sleep(60)
    print('Offline app running!!!')


def set_quota(quota):
    print(f'Set quota to {quota}')
    quota_value = quota * 1000000
    cmd_change_quota = "cgset -r cpu.cfs_quota_us=" + str(int(quota_value)) + " czh_cgroup_test"
    os.system(cmd_change_quota)


def exit_offline_app():
    cmd_kill2 = "ps aux | grep statistics_app.py | grep -v grep | cut -c 9-15 | xargs kill -9"
    os.system(cmd_kill2)

    cmd_kill_offline = "ps aux | grep specjbb2015.jar | grep -v grep | cut -c 9-15 | xargs kill -9"
    os.system(cmd_kill_offline)


if __name__ == "__main__":
    init_offline_app()
    set_quota(quota=70)
    time.sleep(200)
    set_quota(quota=30)
    time.sleep(200)
    set_quota(quota=50)
    time.sleep(200)
    print('complete!')
    exit_offline_app()
