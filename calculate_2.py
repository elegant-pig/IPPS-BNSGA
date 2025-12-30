import copy
import math
from collections import defaultdict
from copy import deepcopy
import random


from examine_encoding import examine_individual, examine_employ_code
from generate_Workstation import generate_workstation


# batch=10

def calculate(populations,batch_time,num_station,data,staff_data):
    result_goal=[]
    for index,individual in enumerate(populations):
        workstation_available_time = {station: {"free_intervals": [(float(0.0), float('inf'))], 'assigned_jobs': []} for station in generate_workstation(num_station)}
        if 'individual' in individual:
            individual = deepcopy(individual['individual'])
            # individual=individual['individual']
        else:
            individual = deepcopy(individual)
        print(f"开始计算时的工作站！！{individual['workstation_code']}")
        workstation_available_time=calculate_time(individual,workstation_available_time,batch_time,num_station,data,staff_data,num_station)

        # 计算makespan
        # 提取所有工作站的 assigned_jobs 列表
        all_jobs = [job for station in workstation_available_time.values() for job in station['assigned_jobs']]
        # 找到 end_time 最大的 job，即计算当前个体的最大完工时间
        job_with_max_end_time = max(all_jobs, key=lambda job: job['end_time'])
        makespan = job_with_max_end_time['end_time']

        # 计算workload
        # 计算该个体每个工作站的负荷
        workload_list,variance, variance_unbiased = calculate_workload(workstation_available_time)
        # 工作负荷最大的工作站
        max_station = max(workload_list, key=workload_list.get)

        # 最大值
        max_value = workload_list[max_station]

        # 计算空闲时间
        total_free_time = calculate_freetime(workstation_available_time)
        result_goal.append({'individual': individual, 'makespan': makespan, 'workload_variance':variance,'workload': max_value, 'total_free_time': total_free_time})


    return result_goal

def calculate_time(individual,workstation_available_time,batch_time,num_station,data,staff_data,num):
    produce_process = {operation: {str(batch): [] for batch in range(1, batch_time + 1)} for operation in
                       individual['operation_code']}  # 工序每一批次分配的工作站
    categorized = categorize(individual)
    makespan_dict = {operation: {str(batch): 0.0 for batch in range(1, batch_time + 1)} for operation in
                     individual['operation_code']}  # 工序每一批次的完工时间
    start_time_dict = {operation: {str(batch): 0.0 for batch in range(1, batch_time + 1)} for operation in
                       individual['operation_code']}  # 工序每一批次的开始时间
    print(f"进入计算时间时的工作站{individual['workstation_code']}")
    # 按批次生产
    for index in range(1, batch_time + 1):
        # 按相同部件开始生产工序
        for key, value in categorized.items():
            # 不是组合工序
            if int(key) != 0:
                # 按各部件依次制作,v是该工序，idx是该工序对应的位置
                for idx, v in enumerate(value):
                    # 如果是各部件第一个工序
                    if idx == 0:
                        tem_start_time = float(0.0)
                        p_t = round(float(data[data['工序'] == int(value[idx].split(',')[1])]['标准工时'].values[0]) * batch_time,2)  # 工序的加工时间
                        # 各部件的第一个工序的开始时间不受约束，只考虑最早的开始时间即可，如果最早开始时间一致就按照工作站编号最小的加工
                        earliest_wk, work_info, _, individual = find_earliest_available_workstation(data,individual,
                                                                                                    value[idx],
                                                                                                    tem_start_time, p_t,
                                                                                                    workstation_available_time,staff_data,num_station)
                        # difficulty=data[data['工序'] == int(value[idx].split(',')[1])]['难易度'].values[0]
                        # 修改该工作站的可用区间
                        workstation_available_time = modify_free_intervals(earliest_wk, work_info,
                                                                           workstation_available_time)
                        # print(f"work_info{work_info}")
                        # 记录该批次该工序的开始时间
                        start_time_dict[value[idx]][str(index)] = work_info[0]
                        # 记录该批次该工序的完成时间
                        makespan_dict[value[idx]][str(index)] = work_info[1]
                        # 记录工序的信息
                        workstation_available_time[earliest_wk]['assigned_jobs'].append({
                            'batch': index,
                            'operation': value[idx],
                            'start_time': work_info[0],
                            'end_time': work_info[1],
                            'distance': 0
                        })
                        # 记录工作站的信息
                        produce_process[value[idx]][str(index)].append(earliest_wk)  # 将每个工序对应批次的分配到的工作站记录下来
                    else:
                        # print("各部件其他工序")
                        # # 各部件其他工序
                        tem_start_time = makespan_dict[value[idx - 1]][str(index)]  # 最早开始时间是该部件该工序的前一工序的完成时间
                        p_t = round(float(data[data['工序'] == int(value[idx].split(',')[1])]['标准工时'].values[0]) * batch_time,2)  # 工序的加工时间

                        _, _, earliest_sort_workstation, individual = find_earliest_available_workstation(data,individual, value[idx], tem_start_time, p_t, workstation_available_time,staff_data,num_station)
                        nearest_sort_workstation = find_nearest_workstation(individual,
                                                                            produce_process[value[idx - 1]][str(index)],
                                                                            value[idx])
                        # merged=merged_data(earliest_sort_workstation,nearest_sort_workstation)
                        ideal_result = ideal_point_distance_starttime(merged_data(earliest_sort_workstation, nearest_sort_workstation))
                        # print(ideal_result)
                        work_info = (ideal_result['start_time'], ideal_result['end_time'], ideal_result['idx'])
                        workstation_available_time = modify_free_intervals(ideal_result['wk'], work_info,
                                                                           workstation_available_time)
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
                # print("组合工序")
                # 组合工序
                for idx, v in enumerate(value):
                    tem_start_time = max(makespan_dict)
                    max_value_tem = {}
                    # 将组合工序之前的工序进行合并
                    for m in makespan_dict.items():
                        time = m[1][str(index)]
                        max_value_tem[m[0]] = time
                    # 找组合工序之前最后一个完工的工序
                    max_key, max_value = max(
                        ((k, v) for k, v in max_value_tem.items() if v),  # 只选非空值
                        key=lambda item: item[1]  # 按值进行比较
                    )
                    examine_individual(individual, num)
                    p_t = round(
                        float(data[data['工序'] == int(value[idx].split(',')[1])]['标准工时'].values[0]) * batch_time,2)  # 工序的加工时间

                    print(f"未传进去的工作站{individual['workstation_code']}")
                    _, _, earliest_sort_workstation, individual = find_earliest_available_workstation(data,individual,
                                                                                                      value[idx],
                                                                                                      max_value, p_t,
                                                                                                      workstation_available_time,staff_data,num_station)
                    nearest_sort_workstation = find_nearest_workstation(individual,
                                                                        produce_process[max_key][str(index)],
                                                                        value[idx])

                    ideal_result = ideal_point_distance_starttime(merged_data(earliest_sort_workstation, nearest_sort_workstation))
                    # print(f"ideal_result{ideal_result}")
                    work_info = (ideal_result['start_time'], ideal_result['end_time'], ideal_result['idx'])
                    workstation_available_time = modify_free_intervals(ideal_result['wk'], work_info,
                                                                       workstation_available_time)
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

def categorize(individual):
    """
    将工序按照部件分组

    参数:
    individuals (list): 初始化的所有个体。
    返回:
    collections.defaultdict: 按照部件分组的工序集合。
    """
    categorized = defaultdict(list)
    operation = individual['operation_code']
    # 遍历每个操作码
    for code in operation:
        first_num = code.split(',')[0][1:]  # 取 'O' 后面的数字部分
        categorized[first_num].append(code)

    # # 对每个部件的工序按数字排序
    # for key in categorized:
    #     categorized[key].sort(key=lambda x: int(x.split(',')[1]))  # 按数字排序

    return categorized

def calculate_workload(workstation_available_time):
    """
    计算每个工作站的工作负载。
    工作负载可以通过所有任务的占用时间来计算。

    参数:
    workstation_available_time (dict): 包含每个工作站空闲时间区间和已分配任务的字典。

    返回:
    dict: 包含每个工作站的总工作负载（单位：时间）。
    """
    workload = {}
    # 遍历每个工作站
    for station, station_data in workstation_available_time.items():
        # 初始化工作站的负载
        total_workload = 0.0

        # 遍历该工作站已分配的所有任务
        for job in station_data['assigned_jobs']:
            # 每个任务的持续时间
            job_duration = job['end_time'] - job['start_time']
            total_workload += job_duration

        # 存储该工作站的总工作负载
        workload[station] = total_workload

    # 计算方差
    loads = list(workload.values())
    m = len(loads)
    if m == 0:
        print(f"没有使用这个工作站！")
        return workload, 0.0, 0.0

    mean_load = sum(loads) / m

    # 总体方差（分母 m）
    variance = sum((w - mean_load) ** 2 for w in loads) / m

    # 样本方差（分母 m-1）
    if m > 1:
        variance_unbiased = sum((w - mean_load) ** 2 for w in loads) / (m - 1)
    else:
        variance_unbiased = 0.0
    return workload,variance, variance_unbiased

def calculate_freetime(workstation_available_time):
    """
    计算每个工作站的空闲时间

    参数:
    workstation_available_time (dict): 包含每个工作站空闲时间区间和已分配任务的字典。

    返回:
    dict: 包含每个工作站的总工作负载（单位：时间）。
    """
    free_times = {}
    total_free_time_all_stations = 0.0
    for station, data  in workstation_available_time.items():
        total_free_time = 0
        for interval in data['free_intervals']:
            if math.isinf(interval[1]):
                continue
            else:
                total_free_time += interval[1] - interval[0]  # 计算每个空闲区间的时间长度

        total_free_time_all_stations+=total_free_time
    # print(total_free_time_all_stations)
    return total_free_time_all_stations

def find_earliest_available_workstation(data,individual,target_operation_code,start_time,process_time,workstation_available_time,staff_data,num):
    """
    找最早能开始生产工序的工作站

    参数:
    individuals (list): 初始化的所有个体。
    target_operation_code(str):目标工序
    start_time(float):目标工序的开始最早可以开始工序的时间
    process_time(float):目标工序的操作时间

    返回:
    str: 最早开始生产的工作站
    list:work_info(start_time,end_time,index) 工序生产信息，index是该工作站上空闲时间区间集合里第几个空闲时间区间
    list:按照生产时间升序排序的工作站信息
    """
    examine_individual(individual,num)
    print(f"进来的工作站{individual['workstation_code']}")
    tem_workstation = []
    for idx, code in enumerate(individual['operation_code']):
        if code == target_operation_code:
            code = int(code.split(",")[1])
            # 该工序对应的可选工作站
            workstations = copy.deepcopy(individual['workstation_code'][idx])

            # 可选工作站对应分配员工
            employ=copy.deepcopy(individual['employ_code'][idx])
            # 如果有多个可选的工作站
            if len(workstations)>1:
                # 遍历可选工作站
                for i,wk in enumerate(workstations):
                    examine_individual(individual,num)
                    # 遍历工作站的空闲时间段
                    # 该工序的难易度
                    difficulty = data[data['工序'] == int(code)]['难易度'].values[0]

                    # 找员工的工作效率
                    efficiency = round(employ_efficiency(copy.deepcopy(individual['employ_code']), wk, difficulty,staff_data,num),2) #原数据类型计算效率

                    for k,interval in enumerate(workstation_available_time[wk]['free_intervals']):
                        # 如果区间的开始时间小于等于该工序最早的开始时间，且该区间能满足该工序的加工时间,即按照该工序的最早开始加工时间加上加工时间小于等于该区间的最后时间节点
                        if math.isinf(interval[1]): #如果区间上界是无穷大
                            if start_time >= interval[0]:
                                tem_workstation.append((wk,start_time, round((start_time + round(process_time*efficiency,2)),2), k))
                            else:
                                tem_workstation.append((wk,interval[0], round((interval[0] + round(process_time*efficiency,2)),2), k))
                        else: #区间上界是无穷大
                            if start_time>=interval[0] and round((start_time+round(process_time*efficiency,2)),2)<interval[1]:
                                tem_workstation.append((wk,start_time,round((start_time+round(process_time*efficiency,2)),2),k))
                            elif start_time<interval[0] and process_time<round((interval[1]-interval[0]),2):
                                tem_workstation.append((wk,interval[0],round((interval[0]+round(process_time*efficiency,2)),2),k))
                            else:
                                continue
                # 找到该工作站最早的开始制作时间
                sort_workstation=sorted(tem_workstation, key=lambda  x:(x[1], int(x[0][1:])))


                tem_result=copy.deepcopy(sort_workstation[0])
                earliest_workstation=copy.deepcopy(tem_result[0])
                # work_info(开始时间，结束时间，idx)
                work_info=(tem_result[1],tem_result[2],tem_result[3])
                return earliest_workstation,work_info,sort_workstation,individual
            elif len(workstations)==1:
                # 只有一个可选工作站时
                # 该工序的难易度
                difficulty = data[data['工序'] == int(code)]['难易度'].values[0]
                # 找员工的工作效率
                print(f"workstation{workstations}")
                print(f"!!!!!!!!!{workstations[0]}")

                examine_individual(individual,num)
                efficiency = round(employ_efficiency(copy.deepcopy(individual['employ_code']), workstations[0], difficulty,staff_data,num), 2)  # 原数据类型计算效率

                for k,interval in enumerate(workstation_available_time[workstations[0]]['free_intervals']):
                    if math.isinf(interval[1]):
                        if start_time >= interval[0]:
                            tem_workstation.append((workstations[0],start_time,round((start_time+round(process_time*efficiency,2)),2),k))
                        else:
                            tem_workstation.append((workstations[0],interval[0],round((interval[0]+round(process_time*efficiency,2)),2),k))
                    else:
                        if start_time>=interval[0] and round((start_time+round(process_time*efficiency,2)),2)<interval[1]:
                            tem_workstation.append((workstations[0],start_time,round((start_time+round(process_time*efficiency,2)),2),k))
                        elif start_time<interval[0] and round(process_time*efficiency,2)<round((interval[1]-interval[0]),2):
                            tem_workstation.append((workstations[0],interval[0],round((interval[0]+round(process_time*efficiency,2)),2),k))
                        else:
                            continue
                # 找到该工作站最早的开始制作时间
                sort_workstation = sorted(tem_workstation, key=lambda x:x[1])
                tem_result = copy.deepcopy(sort_workstation[0])

                work_info = (tem_result[1], tem_result[2],tem_result[3])
                return workstations[0],work_info,sort_workstation,individual
            else:
                raise ValueError(f"没有工作站！，有问题")
def find_nearest_workstation(individual,pre_workstation,target_operation_code):
    """
    找距离前一工序工作站最近的工作站

    参数:
    individuals (list): 初始化的所有个体。
    pre_workstation(str):前一工序所在工作站
    target_operation_code(str):目标工序

    返回:
    list:nearest_workstation(distance,wk,side)  按照距离升序排序的工作站信息，距离一致就按照同侧优先的顺序排序
    """
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
                # return nearest_workstation
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
                # return nearest_workstation
    return nearest_workstation

def merged_data(earliest_array,nearest_array):
    """
    将找到的最早开始制作的工作站信息和距离最近的工作站信息进行合并
    两个数据中重合的部分进行数据合并，不重复的就舍去

    参数:
    earliest_array (list): 最早开始的工作站信息
    nearest_array(list):距离最近的工作站

    返回:
    list:符合条件的合并信息
    """
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

def ideal_point_distance_starttime(workstation_info):
    """
    使用基于理想点的帕累托最优法求解出最早开始且距离最近的工作站

    参数:
    workstation_info (list): merged_data函数返回的数据
    返回:
    list:最优解的信息
    """
    # ideal_result=[]
    # 确定理想点
    ideal_start_time = min(item['start_time'] for item in workstation_info)
    ideal_distance = min(item['distance'] for item in workstation_info)

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

    return pareto_optimal

def modify_free_intervals(earliest_wk,work_info,workstation_available_time):
    """
    修改workstation_available_time[earliest_wk]['free_intervals']里的空闲区间

    参数:
    earliest_wk (str):要修改的工作站
    work_info(str):占用的时间
    """
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

    return workstation_available_time

def employ_efficiency(employ_code,workstation,difficulty,staff_data,num):
    """
    查找员工完成该难易度工序的效率
    wk_staff-该工作站使用的员工
    """
    print(f"527527527")
    print(f"gggg{employ_code}")
    print(f"difficulty{difficulty}")

    employ_id=None
    print(f"workstation{workstation}")
    a,s=examine_employ_code(employ_code,num)
    if a:
        print('没问题')

    else:
        print(f'问题是{s}')
        raise ValueError("youwnti ")

    found = False  # 标志变量
    for id_list in employ_code:
        print(f"id_list{id_list}")
        for i in id_list:
            print(f"i{i}")
            if i['workstation']==workstation:
                employ_id=i['employ']
                found = True  # 记录找到
                break  # 跳出内层循环
            else:
                print(f"当前工作站是{i['workstation']}，要匹配的工作站是{workstation}")
        if found:
            break

    if not employ_id:
        raise ValueError("是找不到符合的工作站吗？？？")


    # print('employ_value')
    print(f"employ_id{employ_id}")
    if employ_id:
        print("--------------------")
        print(staff_data.loc[staff_data['员工']==employ_id,difficulty].values[0])
        efficiency = round(staff_data.loc[staff_data['员工'] == employ_id, difficulty].values[0], 2)

        print("--------------------")
    else:
        print(f"565")
        print(f"找不到员工号，说明有员工没有分配？？？？")
        raise ValueError("找不到员工？？？？why")

    return efficiency
