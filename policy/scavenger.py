import sys
import os
import time
import math
import numpy as np

from util.control_spark_bench import add_spark_bench_jobs
from util.control_hi_bench import add_hi_bench_jobs


# 主要用来转换时间格式
def change_time_to_seconds(curr_time):
    time_array = time.strptime(curr_time, "%Y-%m-%d %H:%M:%S")
    time_stamp = int(time.mktime(time_array))
    return time_stamp


def change_seconds_to_time(seconds):
    time_array = time.localtime(seconds)
    other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    return other_style_time


def get_steady_interval(out_file):
    f_out = open(out_file)
    line = f_out.readline()
    while line:
        if "0%" in line:
            begin_second = int(line.split("s:")[0])
        if "quiescence" in line:
            end_second = int(line.split("s:")[0])
        line = f_out.readline()
    f_out.close()
    
    words = out_file.split("/")[5]
    curr_date = words.split("_")[0]
    curr_time = words.split("_")[1]
    curr_time = curr_date + " " + curr_time
    begin_time = change_seconds_to_time(change_time_to_seconds(curr_time) + begin_second)
    end_time = change_seconds_to_time(change_time_to_seconds(curr_time) + end_second)
    return begin_second, end_second, begin_time, end_time


def test_steady(out_file):
    f_out = open(out_file)
    line = f_out.readline()
    begin_flag = 0
    end_flag = 0
    while line:
        if "0%" in line:
            begin_second = int(line.split("s:")[0])
            begin_flag = 1
        if "quiescence....." in line:
            end_second = int(line.split("s:")[0])
            end_flag = 1
        line = f_out.readline()
    f_out.close()

    if begin_flag == 0:
        return 0
    elif begin_flag == 1 and end_flag == 0:
        return 1
    else:
        return 2


def get_begin_second(out_file, second):
    f_out = open(out_file)
    line = f_out.readline()
    begin_flag = 0
    end_flag = 0
    while line:
        if "0%" in line:
            begin_second = int(line.split("s:")[0])
            break
        line = f_out.readline()
    f_out.close()

    words = out_file.split("/")[5]
    curr_date = words.split("_")[0]
    curr_time = words.split("_")[1]
    curr_time = curr_date + " " + curr_time

    time.sleep(2)
    return begin_second, begin_second + second


# 这个函数主要是读取perf文件得到的底层ipc数据监测值
# 可以根据begin_time和end_time设置读取得到的数据时间范围
def get_ipc_data(file_path, begin_second = None, end_second = None):
    # 首先读取perf记录的数据
    # 包括cache_misses\instructions\cpu_cycles
    cache_misses = [[], []]
    instructions = [[], []]
    cpu_cycles   = [[], []]
    f = open(file_path)
    line = f.readline()
    while line:
        if "<not counted>" in line:
            break
        if "cache-misses" in line:
            if begin_second == None:
                cache_misses[0].append(int(float(line[:15])))
                cache_misses[1].append(int(line[16:36].replace(",", "")))
            else:
                time_stamp = int(float(line[:15]))
                if time_stamp >= begin_second and time_stamp <= end_second:
                    
                    cache_misses[0].append(int(float(line[:15])))
                    cache_misses[1].append(int(line[16:36].replace(",", "")))
        if "instructions" in line:
            if begin_second == None:
                instructions[0].append(int(float(line[:15])))
                instructions[1].append(int(line[16:36].replace(",", "")))
            else:
                time_stamp = int(float(line[:15]))
                if time_stamp >= begin_second and time_stamp <= end_second:
                    instructions[0].append(int(float(line[:15])))
                    instructions[1].append(int(line[16:36].replace(",", "")))
        if "cpu-cycles" in line:
            if begin_second == None:
                cpu_cycles[0].append(int(float(line[:15])))
                cpu_cycles[1].append(int(line[16:36].replace(",", "")))
            else:
                time_stamp = int(float(line[:15]))
                if time_stamp >= begin_second and time_stamp <= end_second:
                    cpu_cycles[0].append(int(float(line[:15])))
                    cpu_cycles[1].append(int(line[16:36].replace(",", "")))
        line = f.readline()
    f.close()
        
    # 通过instructions\cpu_cycles来计算ipc
    ipc = [[], []]
    for i in range(len(cpu_cycles[0])):
        time_stamp  = cpu_cycles[0][i]
        cpu_cycle   = cpu_cycles[1][i]
        instruction = instructions[1][i]
        ipc[0].append(time_stamp)
        ipc[1].append(instruction / cpu_cycle)
    return ipc[1]


def read_entry(root_path, query_num):
    while True:
        file_list = os.listdir(root_path)
        query_path_list = []
        for file in file_list:
            # 将Online应用筛选出来
            if "2022" in file:
                query_path_list.append(file)
        if len(query_path_list) < query_num:
            time.sleep(5)
        else:
            break
    query_path_list.sort()

    ipc = []
    for i in range(query_num):
        path = query_path_list[i]
        root_file = root_path + path
        perf_file = root_file + "/online_perf.txt"
        out_file  = root_file + "/composite.out"
        flag = test_steady(out_file)
        while flag != 2:
            time.sleep(5)
            flag = test_steady(out_file)
        begin_second, end_second, begin_time, end_time = get_steady_interval(out_file)
        temp_ipc = get_ipc_data(perf_file, begin_second, end_second)
        ipc.extend(temp_ipc)
    return ipc


def read_begin_entry(root_path, query_num, second):
    print("begin read begin entry", query_num)
    
    while True:
        file_list = os.listdir(root_path)
        query_path_list = []
        for file in file_list:
            # 将Online应用筛选出来
            if "2022" in file:
                query_path_list.append(file)
        if len(query_path_list) < query_num:
            time.sleep(5)
        else:
            break

    query_path_list.sort()
    ipc = []
    for i in range(query_num):
        path = query_path_list[i]
        root_file = root_path + path
        perf_file = root_file + "/online_perf.txt"
        out_file  = root_file + "/composite.out"
        flag = test_steady(out_file)
        while flag == 0:
            time.sleep(5)
            flag = test_steady(out_file)
        begin_time, end_time = get_begin_second(out_file, second)
        temp_ipc = get_ipc_data(perf_file, begin_time, end_time)
        ipc.extend(temp_ipc)
    print("end read entry", query_num)
    return ipc


def calcul_bound(value_list):
    mean = np.mean(value_list)
    tem_sum = 0
    for value in value_list:
        tem_sum += ((value - mean) ** 2)
    std_dev = math.sqrt(tem_sum / (len(value_list) - 1))
    return mean, std_dev


def scavenger_entry(root_path, RUNNING_CORES=104):
    # 这个是根据steady阶段的时间来设置的，单位为s
    steady_length  = 100
    window_size    = 30
    std_factor     = 1
    quota_increase = RUNNING_CORES * 0.1 * 1000000
    quota_decrease = 0.4
    minimum_quota  = 0.1 * 1000000

    future_quota = RUNNING_CORES / 8 * 5 * 1000000

    query_num = 1
    ipc_data = read_entry(root_path, query_num)
    query_num += 1

    mean, std_dev = calcul_bound(ipc_data[len(ipc_data) - window_size : ])
    lower_bound = mean - std_factor * std_dev
    lower_bound_2 = mean - 2 * std_factor * std_dev
    upper_bound = mean + std_factor * std_dev
    upper_bound_2 = mean + 2 * std_factor * std_dev
    
    update_bound_flag = 0
    plus_second = 2



    while True:
        if update_bound_flag == 1:
            ipc_data = read_entry(root_path, query_num)
            query_num += 1
            plus_second = 2
            mean, std_dev = calcul_bound(ipc_data[len(ipc_data) - window_size : ])
            lower_bound = mean - std_factor * std_dev
            lower_bound_2 = mean - 2 * std_factor * std_dev
            upper_bound = mean + std_factor * std_dev
            upper_bound_2 = mean + 2 * std_factor * std_dev
            update_bound_flag = 0

        ipc_data = read_begin_entry(root_path, query_num, plus_second)
        plus_second += 15
        if plus_second > steady_length:
            query_num += 1
            plus_second = 2
        current_ipc = ipc_data[-1]
        if current_ipc >= lower_bound and current_ipc <= upper_bound:
            future_quota += quota_increase
        elif current_ipc <= lower_bound and current_ipc >= lower_bound_2:
            future_quota -= quota_decrease * future_quota

        elif current_ipc <= lower_bound_2 or current_ipc >= upper_bound_2:
            future_quota = minimum_quota
            update_bound_flag = 1
        else:
            continue

        # 设置离线任务Quota时，保证Quota有一个最小值
        if future_quota <= 0.1 * 1000000:
            future_quota = 0.1 * 1000000
        if future_quota >= RUNNING_CORES * 1000000:
            future_quota = RUNNING_CORES * 1000000


if __name__ == "__main__":
    root_path    = str(sys.argv[1])
    offline_type = str(sys.argv[2])
    RUNNING_CORES = int(sys.argv[3])
    scavenger_entry(root_path, offline_type, RUNNING_CORES)
