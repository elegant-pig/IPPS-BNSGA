import math
import random
from decimal import Decimal, getcontext

import pandas as pd
import openpyxl as op

import Gantt
import init
from collections import defaultdict
import numpy as np
import generateWorkstation_simple

file_path = 'data/operation_data.xlsx'
operation_data = pd.read_excel(file_path, sheet_name='use')
schedule=operation_data[['部件','工序','机器','标准工时','难易度']]
current_time=0
batch_time = math.ceil(main.piece_num / main.batch)  # 一共生产多少批次
workstation_available_time = {station: {"free_intervals": [(float(0.0),float('inf'))], 'assigned_jobs':[]} for station in generateWorkstation_simple.generate_workstation(generateWorkstation_simple.num_stations)}
getcontext().prec = 28  # 设置全局精度
getcontext().rounding = "ROUND_HALF_UP"  # 普通四舍五入

# 将工序按照部件分组
def categorize(individual):
    categorized = defaultdict(list)
    operation = individual['operation_code']
    # 遍历每个操作码
    for code in operation:
        first_num = code.split(',')[0][1:]  # 取 'O' 后面的数字部分
        categorized[first_num].append(code)
    return categorized

def calculate(individuals,num_workstations,constraints):
    for individual in individuals:
        print(individual)
        calculate_time(individual)
        # Gantt.plot_gantt_chart(calculate_time(individual))
        # 提取所有工作站的 assigned_jobs 列表
        all_jobs = [job for station in workstation_available_time.values() for job in station['assigned_jobs']]
        # 找到 end_time 最大的 job
        job_with_max_end_time = max(all_jobs, key=lambda job: job['end_time'])
        print("Job with maximum end_time:", job_with_max_end_time)
    return job_with_max_end_time

def find_earliest_available_workstation(individual,target_operation_code,start_time,process_time):
    tem_workstation = []
    min_start_time_data=[]
    for idx, code in enumerate(individual['operation_code']):
        if code == target_operation_code:
            # 该工序对应的可选工作站
            workstations = individual['workstation_code'][idx]
            # 如果有多个可选的工作站
            if len(workstations)>1:
                # 遍历可选工作站
                for i,wk in enumerate(workstations):
                    # 遍历工作站的空闲时间段
                    for k,interval in enumerate(workstation_available_time[wk]['free_intervals']):
                        # 如果区间的开始时间小于等于该工序最早的开始时间，且该区间能满足该工序的加工时间,即按照该工序的最早开始加工时间加上加工时间小于等于该区间的最后时间节点
                        if math.isinf(interval[1]): #如果区间上界是无穷大
                            if start_time >= interval[0]:
                                tem_workstation.append((wk,start_time, round(start_time + process_time), k))
                            else:
                                tem_workstation.append((wk,interval[0], round(interval[0] + process_time), k))
                        else: #区间上界是无穷大
                            if start_time>=interval[0] and round(start_time+process_time)<interval[1]:
                                tem_workstation.append((wk,start_time,round(start_time+process_time),k))
                            elif start_time<interval[0] and process_time<round(interval[1]-interval[0]):
                                tem_workstation.append((wk,interval[0],round(interval[0]+process_time),k))
                            else:
                                continue
                # print(f'有多个可选工作站，某一工作站的可选区间tem_workstation{tem_workstation}')
                # 找到该工作站最早的开始制作时间
                sort_workstation=sorted(tem_workstation, key=lambda  x:(x[1], int(x[0][1:])))
                # min_start_time_data.append(min(tem_workstation, key=lambda  x:x[1]))
                # print(f"min_start_time_data{min_start_time_data}")
                # 比较所有工作站中最早开始的制作时间，即分配到该工作站上,如果出现开始制作时间一样的工作站，则按照工作站编号最小的工作站来选择
                # min_start_time_workstation_data=min(min_start_time_data,key=lambda  x: (x[1],int(x[0][1:])))
                # print(min_start_time_workstation_data)

                tem_result=sort_workstation[0]
                earliest_workstation=tem_result[0]
                # work_info(开始时间，结束时间，idx)
                work_info=(tem_result[1],tem_result[2],tem_result[3])
                return earliest_workstation,work_info,sort_workstation

            else:
                # 只有一个可选工作站时
                for k,interval in enumerate(workstation_available_time[workstations[0]]['free_intervals']):
                    if math.isinf(interval[1]):
                        if start_time >= interval[0]:
                            tem_workstation.append((workstations[0],start_time,round(start_time+process_time),k))
                        else:
                            tem_workstation.append((workstations[0],interval[0],round(interval[0]+process_time),k))
                    else:
                        if start_time>=interval[0] and round(start_time+process_time)<interval[1]:
                            tem_workstation.append((workstations[0],start_time,round(start_time+process_time),k))
                        elif start_time<interval[0] and process_time<round(interval[1]-interval[0]):
                            tem_workstation.append((workstations[0],interval[0],round(interval[0]+process_time),k))
                        else:
                            continue
                # 找到该工作站最早的开始制作时间)
                sort_workstation = sorted(tem_workstation, key=lambda x:x[1])
                tem_result = sort_workstation[0]
                # min_start_time_data.append(min(tem_workstation, key=lambda  x:x[1]))
                # work_info(开始时间，结束时间，idx)
                work_info = (tem_result[1], tem_result[2],tem_result[3])
                return workstations[0],work_info,sort_workstation


def find_nearest_workstation(individual,pre_workstation,target_operation_code):
    nearest_workstation = []
    for idx,code in enumerate(individual['operation_code']):
        if code == target_operation_code:
            # 该工序对应的可选工作站
            workstations = individual['workstation_code'][idx]
            if len(workstations) > 1:
                for i in workstations:
                    # 工作站如果在同一侧
                    if i[0]==pre_workstation[0][0]:
                        distance = abs(int(i[1:]) - int(pre_workstation[0][1])) #两工作站之间的距离
                        nearest_workstation.append({'distance': distance, 'wk': i, 'side': 0})
                    else:
                        # 工作站不同侧
                        distance = abs(int(i[1:]) - int(pre_workstation[0][1])) #两工作站之间的距离
                        nearest_workstation.append({'distance': distance, 'wk': i, 'side': 1})
                #升序排序,距离最近的优先，如果距离一样，就选择同一侧的
                nearest_workstation = sorted(nearest_workstation, key=lambda x: (x['distance'], x['side']))
                return nearest_workstation
            else:
                # 只有一个工作站
                # 如果工作站在同一侧
                if workstations[0] == pre_workstation[0][0]:
                    distance = abs(int(workstations[0][1]) - int(pre_workstation[0][1]))
                    nearest_workstation.append({'distance': distance, 'wk':workstations[0],'side':0})
                else:
                    # 如果不在同一侧
                    distance = abs(int(workstations[0][1]) - int(pre_workstation[0][1]))
                    nearest_workstation.append({'distance': distance, 'wk':workstations[0],'side':1})
                return nearest_workstation

def merged_data(earliest_array,nearest_array):
    # 创建一个字典，按照工作站（'wk'）来存储nearest_sort_workstation的数据
    nearest_data_dict={entry['wk']: entry for entry in nearest_array}
    # 合并数据
    merged_data = []
    for item in earliest_array:
        wk, start_time, end_time, idx = item
        if wk in nearest_data_dict:
            nearest_data = nearest_data_dict[wk]  # 获取相应的工作站数据
            # merged_item = (wk, start_time, end_time, idx, nearest_data['distance'], nearest_data['side'])
            merged_data.append({'wk':wk,'start_time':start_time,'end_time':end_time,'idx':idx,'distance':nearest_data['distance'],'side':nearest_data['side']})
    return merged_data

def ideal_point(workstation_info):
    # ideal_result=[]
    # 确定理想点
    ideal_start_time = min(item['start_time'] for item in workstation_info)
    ideal_distance = min(item['distance'] for item in workstation_info)
    # print(f"workstation_info{workstation_info}")
    # print(f"ideal_start_time{ideal_start_time}")
    # print(f"ideal_distance{ideal_distance}")
    # 计算每个数据到理想点的距离
    for item in workstation_info:
        start_time_diff = item['start_time'] - ideal_start_time
        distance_diff = item['distance'] - ideal_distance
        item['ideal_distance'] = (start_time_diff ** 2 + distance_diff ** 2) ** 0.5
    # 找到最小的理想距离
    min_ideal_distance = min(item['ideal_distance'] for item in workstation_info)
    # print(f"min_ideal_distance{min_ideal_distance}")
    # 找到所有距离相等的点
    optimal_candidates = [item for item in workstation_info if item['ideal_distance'] == min_ideal_distance]
    # 随机选择一个点
    pareto_optimal = random.choice(optimal_candidates)

    # print(f"optimal_candidates{optimal_candidates}")
    # 按理想点距离排序，选择最优点
    # pareto_optimal = min(workstation_info, key=lambda x: x['ideal_distance'])
    # print(f"pareto_optimal{pareto_optimal}")
    # print(f"pareto_optimal{pareto_optimal}")
    print(pareto_optimal)
    return pareto_optimal

def modify_free_intervals(earliest_wk,work_info):
    if workstation_available_time[earliest_wk]['free_intervals'][work_info[2]] is not None:
        low = workstation_available_time[earliest_wk]['free_intervals'][work_info[2]][0]
        high = workstation_available_time[earliest_wk]['free_intervals'][work_info[2]][1]
        if work_info[0] > low:
            if work_info[1] < high:
                del workstation_available_time[earliest_wk]['free_intervals'][work_info[2]]
                workstation_available_time[earliest_wk]['free_intervals'].append((low, work_info[0]))
                workstation_available_time[earliest_wk]['free_intervals'].append((work_info[1], high))
            elif work_info[1] == high:
                del workstation_available_time[earliest_wk]['free_intervals'][work_info[2]]
                workstation_available_time[earliest_wk]['free_intervals'].append((low, work_info[0]))
        elif work_info[0] == low:
            if work_info[1] < high:
                del workstation_available_time[earliest_wk]['free_intervals'][work_info[2]]
                workstation_available_time[earliest_wk]['free_intervals'].append((work_info[1], high))
            elif work_info[1] == high:
                del workstation_available_time[earliest_wk]['free_intervals'][work_info[2]]
    else:
        workstation_available_time[earliest_wk]['free_intervals'].append((work_info[1],float('inf')))


def calculate_time(individual):
    # print(f"batch_time{batch_time}")
    # 不考虑搬运时间，将搬运的距离纳入奖励机制中进行优化
    produce_process = {operation: {str(batch): [] for batch in range(1, batch_time + 1)} for operation in individual['operation_code']} #工序每一批次分配的工作站
    categorized=categorize(individual)
    makespan_dict = {operation:{str(batch):0.0 for batch in range(1, batch_time + 1)} for operation in individual['operation_code']} #工序每一批次的完工时间
    start_time_dict={operation:{str(batch):0.0 for batch in range(1, batch_time + 1)} for operation in individual['operation_code']} #工序每一批次的开始时间
    # 按批次生产
    for index in range(1,batch_time+1):
        # 按相同部件开始生产工序
        for key, value in categorized.items():
            # 不是组合工序
            if int(key) != 0:
                # 按各部件依次制作
                for idx, v in enumerate(value):
                    # 如果是各部件第一个工序
                    if idx == 0:
                        print("各部件第一道工序")
                        tem_start_time=float(0.0)
                        p_t = float(schedule[schedule['工序'] == int(value[idx].split(',')[1])]['标准工时'].values[0])  # 工序的加工时间
                        # 各部件的第一个工序的开始时间不受约束，只考虑最早的开始时间即可，如果最早开始时间一致就按照工作站编号最小的加工
                        earliest_wk,work_info,_=find_earliest_available_workstation(individual,value[idx],tem_start_time,p_t)
                        # print(f"earliest_wk{earliest_wk}")
                        # 修改该工作站的可用区间
                        modify_free_intervals(earliest_wk,work_info)
                        # print(f"work_info{work_info}")
                        # 记录该批次该工序的开始时间
                        start_time_dict[value[idx]][str(index)]=work_info[0]
                        # 记录该批次该工序的完成时间
                        makespan_dict[value[idx]][str(index)]=work_info[1]
                        # 记录工序的信息
                        workstation_available_time[earliest_wk]['assigned_jobs'].append({
                            'batch': index,
                            'operation': value[idx],
                            'start_time': work_info[0],
                            'end_time': work_info[1],
                            'distance': 0
                        })
                        # 记录工作站的信息
                        produce_process[value[idx]][str(index)].append(earliest_wk) #将每个工序对应批次的分配到的工作站记录下来
                    else:
                        print("各部件其他工序")
                        # # 各部件其他工序
                        tem_start_time=makespan_dict[value[idx-1]][str(index)] #最早开始时间是该部件该工序的前一工序的完成时间
                        p_t = float(schedule[schedule['工序'] == int(value[idx].split(',')[1])]['标准工时'].values[0])  # 工序的加工时间
                        _,_,earliest_sort_workstation=find_earliest_available_workstation(individual,value[idx],tem_start_time,p_t)
                        nearest_sort_workstation=find_nearest_workstation(individual,produce_process[value[idx-1]][str(index)],value[idx])
                        # merged=merged_data(earliest_sort_workstation,nearest_sort_workstation)
                        ideal_result=ideal_point(merged_data(earliest_sort_workstation,nearest_sort_workstation))
                        # print(ideal_result)
                        work_info=(ideal_result['start_time'],ideal_result['end_time'],ideal_result['idx'])
                        modify_free_intervals(ideal_result['wk'], work_info)
                        # 记录该批次该工序的开始时间
                        start_time_dict[value[idx]][str(index)] = ideal_result['start_time']
                        # 记录该批次该工序的完成时间
                        makespan_dict[value[idx]][str(index)] = ideal_result['end_time']
                        # 记录工序的信息
                        workstation_available_time[ideal_result['wk']]['assigned_jobs'].append({
                            'batch': index,
                            'operation': value[idx],
                            'start_time': ideal_result['start_time'],
                            'end_time': ideal_result['end_time'],
                            'distance': ideal_result['distance']
                        })
                        # 记录工作站的信息
                        produce_process[value[idx]][str(index)].append(ideal_result['wk'])  # 将每个工序对应批次的分配到的工作站记录下来
            else:
                print("组合工序")
                #组合工序
                for idx,v in enumerate(value):
                    tem_start_time=max(makespan_dict)
                    max_value_tem={}
                    # 将组合工序之前的工序进行合并
                    for m in makespan_dict.items():
                        time=m[1][str(index)]
                        max_value_tem[m[0]]=time
                    # 找组合工序之前最后一个完工的工序
                    max_key, max_value = max(
                        ((k, v) for k, v in max_value_tem.items() if v),  # 只选非空值
                        key=lambda item: item[1]  # 按值进行比较
                    )
                    p_t = float(schedule[schedule['工序'] == int(value[idx].split(',')[1])]['标准工时'].values[0])  # 工序的加工时间
                    _, _, earliest_sort_workstation = find_earliest_available_workstation(individual, value[idx],max_value, p_t)
                    nearest_sort_workstation = find_nearest_workstation(individual,produce_process[max_key][str(index)],value[idx])
                    print(f"nearest_sort_workstation{nearest_sort_workstation}")
                    print(f"earliest_sort_workstation{earliest_sort_workstation}")

                    ideal_result = ideal_point(merged_data(earliest_sort_workstation, nearest_sort_workstation))
                    # print(f"ideal_result{ideal_result}")
                    work_info = (ideal_result['start_time'], ideal_result['end_time'], ideal_result['idx'])
                    modify_free_intervals(ideal_result['wk'], work_info)
                    # 记录该批次该工序的开始时间
                    start_time_dict[value[idx]][str(index)] = ideal_result['start_time']
                    # 记录该批次该工序的完成时间
                    makespan_dict[value[idx]][str(index)] = ideal_result['end_time']
                    # 记录工序的信息
                    workstation_available_time[ideal_result['wk']]['assigned_jobs'].append({
                        'batch': index,
                        'operation': value[idx],
                        'start_time': ideal_result['start_time'],
                        'end_time': ideal_result['end_time'],
                        'distance': ideal_result['distance']
                    })
                    # 记录工作站的信息
                    produce_process[value[idx]][str(index)].append(ideal_result['wk'])  # 将每个工序对应批次的分配到的工作站记录下来
    return workstation_available_time


#
# dwql=calculate(main.population,main.num_workstations,main.result_constraint)
# print(dwql)