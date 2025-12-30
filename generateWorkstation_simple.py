import math
import random
from collections import defaultdict

import networkx as nx
# import nx
import pandas as pd
import generateBalance
import generateOR
import generateOperation
import generateMachine
import openpyxl


from check_code import  check_generateWorkstation
from examine_encoding import examine_workstation_machines_code

# 会出现一个位置分配同一个工作站！！！！
# 有无必要！！！！

file_path = 'data/operation_data.xlsx'
operation_data = pd.read_excel(file_path, sheet_name='final')
data=operation_data.copy()
# num_station=23

weight_rules={
    "front": 1,
    "back": 1,
    "side": 0.8,
    "diagonal_front": 0.6,
    "diagonal_back": 0.4
}


def generate_workstation(num_station):
    left_count = num_station // 2  # 左边的数量
    right_count = num_station - left_count  # 右边的数量

    # 生成左边的编码
    left_side = [f"L{i + 1}" for i in range(left_count)]
    # 生成右边的编码
    right_side = [f"R{i + 1}" for i in range(right_count)]
    workstation = left_side + right_side
    return workstation


# 新的方法,先生成一个工作站-机器分配
def min_cost_max_flow_machine_assignment(machine_to_workstations: dict, balance_code: dict):
    """
    使用最小费用最大流算法，为机器分配工作站，尽量满足每个机器的 balance_code 需求。

    参数：
    - machine_to_workstations: dict
        机器可用的工作站集合，例如：
        {
            'M1': ['W1', 'W2'],
            'M2': ['W2', 'W3'],
            ...
        }
    - balance_code: dict
        每台机器希望分配的工作站数量，例如：
        {
            'M1': 2,
            'M2': 3,
            ...
        }

    返回：
    - workstation_to_machine: dict
        每个工作站被分配到的机器，例如：
        {
            'W1': 'M1',
            'W2': 'M2',
            ...
        }
    """

    G = nx.DiGraph()
    source = 'S'
    sink = 'T'

    machines = list(machine_to_workstations.keys())
    all_workstations = set(ws for wss in machine_to_workstations.values() for ws in wss)

    # 添加 source 到机器的边
    for m in machines:
        G.add_edge(source, m, capacity=balance_code[m], weight=0)

    # 添加机器到工作站的边
    for m, wss in machine_to_workstations.items():
        for w in wss:
            G.add_edge(m, w, capacity=1, weight=0)  # 可定制 weight，例如负距离

    # 添加工作站到 sink 的边
    for w in all_workstations:
        G.add_edge(w, sink, capacity=1, weight=0)

    # 求解最小费用最大流
    flow_dict = nx.max_flow_min_cost(G, source, sink)

    # 解析结果：找出哪些工作站被哪台机器占用
    workstation_to_machine = {}
    for m in machines:
        for w, f in flow_dict[m].items():
            if f > 0:
                workstation_to_machine[w] = m

    return workstation_to_machine


# 这个函数生成wk_ma和workstation_code,原来的方法
def assignment_operation(data,constraint,num_stations):
    """
    返回：
    -data(dataform):表格数据
    -workstation_codes(list):工序编码
    -workstation_assignments：工作站分配工序信息
    -result_constraint：总约束
    """
    workstation=generate_workstation(num_stations)
    # 合并左右两边的工作站编码
    left_count = num_stations // 2  # 左边的数量
    right_count = num_stations - left_count  # 右边的数量

    while True:
        assigned_workstations =set()#记录已经使用过的工作站
        avialable_stations = workstation.copy()
        workstation_assignments = {f"L{i + 1}": [] for i in range(left_count)}
        workstation_assignments.update({f"R{i + 1}": [] for i in range(right_count)})
        # operation_assignment = {f"{i+1}":[] for i in range(total_operations)}  # 工序分配记录
        operation_assignment={op:[] for op in data['工序']}
        # print(operation_assignment)
        workstation_machines={}
        workstation_codes=[]
        # result_operation_allocation=[]
        result_constraint=[]
        tem_data = data[['工序', '标准工时']]
        check_machine=[]
        machine_first_assignment={}
        first_list = []
        machine_op_detail=grouped_operation_to_machine(constraint)
        for machin,op_list in machine_op_detail.items():
            first_list.append(op_list[0])

        for list in first_list:
            first_op = list['op_num']
            first_machine = list['machine']
            first_code = list['code']
            first_balance=int(list['balance'])
            for i in range(first_balance):
                if len(avialable_stations)>0:
                    selected_station = random.choice(avialable_stations)
                    if selected_station in workstation_machines:
                        if workstation_machines[selected_station] == first_machine:
                            print(f"机器匹配成功")
                        else:
                            # 如果该工序与选择的工作站上所用的机器不一致时，就重新选择
                            while workstation_machines[selected_station] != first_machine:
                                selected_station = random.choice(avialable_stations)  # 继续随机选择
                    else:
                        workstation_machines[selected_station] = first_machine

                    workstation_assignments[selected_station].append(first_code)
                    operation_assignment[first_op].append(selected_station)
                    avialable_stations.remove(selected_station)
                else:
                    raise ValueError("xianbaocuo ")

        for entry in constraint:
            code, machine, balance = entry.split("->")
            check_machine.append(machine)
            op_num = int(code.split(',')[1])  # 获取操作编码中的工序
            process_time = tem_data[tem_data['工序'] == op_num]['标准工时'].values[0]
            balance = int(balance)

            if operation_assignment[op_num]:
                print(operation_assignment[op_num])
                print(f"已经分配了，跳过")
            else:
                for i in range(balance):
                    if len(avialable_stations) > 0:
                        selected_station = random.choice(avialable_stations)
                        if selected_station in workstation_machines:
                            if workstation_machines[selected_station] == machine:
                                print(f"机器匹配成功")
                            else:
                                # 如果该工序与选择的工作站上所用的机器不一致时，就重新选择
                                while workstation_machines[selected_station] != machine:
                                    selected_station = random.choice(avialable_stations)  # 继续随机选择
                        else:
                            workstation_machines[selected_station] = machine

                        workstation_assignments[selected_station].append(code)
                        operation_assignment[op_num].append(selected_station)
                        avialable_stations.remove(selected_station)
                    else:
                        avialable_stations = workstation.copy()
                        selected_station = random.choice(avialable_stations)
                        # 如果选择的工作站的机器与该工序需要的机器相同
                        if workstation_machines[selected_station] == machine:
                            workstation_assignments[selected_station].append(code)  # 分配工序
                            operation_assignment[op_num].append(selected_station)
                        else:
                            # 如果该工序与选择的工作站上所用的机器不一致时，就重新选择
                            while workstation_machines[selected_station] != machine:
                                selected_station = random.choice(avialable_stations)  # 继续随机选择
                            # 直到找到匹配的工作站后分配工序
                            workstation_assignments[selected_station].append(code)  # 分配工序
                            operation_assignment[op_num].append(selected_station)

            tem_workstation_data=operation_assignment[op_num].copy()
            # 将工序分配放入约束中
            workstation_codes.append(tem_workstation_data)
            result_constraint.append(f"{code}->{machine}->{balance}->{tem_workstation_data}->{process_time}")

        # check_generateWorkstation(workstation_codes, 23)
        # r,s=examine_workstation_machines_code(workstation_machines, check_machine, 23)
        if r:
            print(f"right")
            return data, workstation_codes, workstation_assignments, result_constraint, workstation_machines
        else:
            print(f"问题是{s}")
            raise ValueError("有问题")
        # return data,workstation_codes,workstation_assignments,result_constraint,workstation_machines


def grouped_operation_to_machine(constraint):
    machine_op_detail = defaultdict(list)

    for entry in constraint:
        code, machine, balance = entry.split("->")
        op_num = int(code.split(',')[1])
        machine_op_detail[machine].append({
            'code':code,
            'op_num': op_num,
            'machine':machine,
            'balance': int(balance)
        })

    # 对每台机器的工序列表按 op_num 升序排序
    for machine in machine_op_detail:
        machine_op_detail[machine].sort(key=lambda x: x['op_num'])

    return machine_op_detail

# final_data,_=generateOR.generateOR(data)
# op_final_data,op_code=generateOperation.generate_operation_codes(final_data)
# data,mchine_codes,constraint=generateMachine.generate_machine_codes(op_code,op_final_data)
# tem_data,balance_codes,constraint= generateBalance.generate_balance_codes(final_data, constraint, num_station)
# workstation=generate_workstation(num_station)
# assignment_operation(tem_data,constraint,num_station)
