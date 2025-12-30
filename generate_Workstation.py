import math
import random
from collections import defaultdict

import numpy as np
# import nx
import pandas as pd
import generateBalance
import generateOR
import generateOperation
import generateMachine
import openpyxl


from check_code import  check_generateWorkstation
from examine_encoding import examine_workstation_machines_code, examine_workstation_code
from workstaion_entropy import assign_workstations, allocate_workstations, assign_workstations_with_proximity_push

# 会出现一个位置分配同一个工作站！！！！
# 有无必要！！！！

file_path = 'data/operation_data.xlsx'
operation_data = pd.read_excel(file_path, sheet_name='final')
data=operation_data.copy()
# num_station=23


def entropy(probs):
    probs = np.array(probs)
    probs = probs[probs > 0]
    return -np.sum(probs * np.log2(probs)) if len(probs) > 0 else 0.0

def compute_predecessor_entropy(df, op_col='工序', pred_col='前继工序'):
    #根据前继工序计算信息熵
    entropy_scores = {}
    for _, row in df.iterrows():
        op = str(row[op_col]).strip()
        preds_str = str(row[pred_col]).strip()
        if preds_str == '' or preds_str.lower() in ['nan', '0']:
            entropy_scores[op] = 0.0
            continue
        preds = [x.strip() for x in preds_str.replace('，', ',').replace('、', ',').split(',') if x.strip()]
        n = len(preds)
        p = [1 / n] * n
        entropy_scores[op] = entropy(p)
    return entropy_scores


def parse_constraint_item(item):
    # 从 "O3,4->B->1" 中提取：operation_code = "O3,4", machine = "B", balance = 1
    parts = item.split("->")
    op_code = parts[0]
    machine = parts[1]
    balance = int(parts[2])
    return op_code, machine, balance

def parse_operation_index(op_code):
    # 解析 O3,4 => "3,4"
    return op_code[1:]

def get_workstation_priority(ws):
    # 优先级排序用：先L后R，编号小优先
    side = 0 if ws[0] == 'L' else 1
    index = int(ws[1:])
    return (side, index)

def generate_workstation(num_station):
    left_count = num_station // 2  # 左边的数量
    right_count = num_station - left_count  # 右边的数量

    # 生成左边的编码
    left_side = [f"L{i + 1}" for i in range(left_count)]
    # 生成右边的编码
    right_side = [f"R{i + 1}" for i in range(right_count)]
    workstation = left_side + right_side
    return workstation

def generate_workstation_code(operation_code,machine_code,balance_code,num_workstations,data):
    op_ids = []
    op_entropy = []
    workstation_list = generate_workstation(num_workstations)

    # allocation=assign_workstations(operation_code,balance_code,machine_code,workstation_list,data)
    # allocation=allocate_workstations(operation_code,balance_code,machine_code,workstation_list)
    allocation=assign_workstations_with_proximity_push(operation_code,balance_code,machine_code,workstation_list,data)

    print(f"allocation{allocation}")
    workstation_code = []
    for op in operation_code:
        # allocation['O1,1']['工作站']
        workstation_code.append(allocation[op]['工作站'])
        print(f"workstation_code{workstation_code}")
    if examine_workstation_code(workstation_code,num_workstations):
        workstation_machines=generate_workstation_machines(workstation_code,machine_code)
    else:
        raise ValueError('缺少工作站')

    r,s=examine_workstation_machines_code(workstation_machines, machine_code, num_workstations)

    if r:
        left_count = num_workstations // 2  # 左边的数量
        right_count = num_workstations - left_count  # 右边的数量
        assignments = generate_workstation_assignments(workstation_code, operation_code, left_count, right_count)
        return workstation_code,workstation_machines,assignments
    # return workstation_code
    else:
        raise ValueError('——————数据不对——————')
def generate_workstation_machines(workstation_code, machine_code):
    workstation_machines = {}
    for op_idx, stations in enumerate(workstation_code):
        machine = machine_code[op_idx]
        for station in stations:
            if station not in workstation_machines:
                workstation_machines[station] = machine
    return workstation_machines


def generate_workstation_assignments(workstation_code, operation_code, left_count, right_count):
    # 初始化工作站分配字典
    workstation_assignments = {f"L{i + 1}": [] for i in range(left_count)}
    workstation_assignments.update({f"R{i + 1}": [] for i in range(right_count)})

    # 遍历所有工序的分配情况
    for op, stations in zip(operation_code, workstation_code):
        for station in stations:
            workstation_assignments[station].append(op)

    return workstation_assignments

def reverse_workstation_to_machines(workstation_to_machines):
    # 构建新的反向映射
    machine_to_workstations = defaultdict(list)

    for station, machine in workstation_to_machines.items():
        if not machine:  # 过滤 '', None, False
            continue
        machine_to_workstations[machine].append(station)

    # 转成普通字典（如果你不想用 defaultdict 的形式）
    machine_to_workstations = dict(machine_to_workstations)
    return machine_to_workstations