import copy
import random

import pandas as pd

from generateOperation import generate_operation_codes


def mutation_or_operation_machine2(operation_data, mutation_rate, i):
    """
    工序编码变异函数：直接修改 operation_code 中 y 值（即工序编号），而不操作 or_node。
    """
    replace_ops = i['replace_op']  # 替代工序列表，例如 [[5, 6, 7], [10, 11]]
    operation_code = i['operation_code']  # 当前操作编码，如 ['O0,6', 'O0,7', ...]
    print(f"replace_ops{replace_ops}")
    print(f"修改前的编码: {operation_code}")

    data = operation_data.copy()
    machine_code = []

    # 计算要变异的次数
    mutate_num = int(round(mutation_rate * len(operation_code)))
    if mutate_num == 0:
        mutate_num = 1
    print(f"变异个数: {mutate_num}")

    # 执行若干次变异
    for _ in range(mutate_num):
        kk = random.choice(replace_ops)  # 随机选一个替换组
        current_op = random.choice(kk)   # 从该组中随机选一个作为当前值

        # 在 operation_code 中找到等于 current_op 的 y 值（即工序编号）
        for idx, code in enumerate(operation_code):
            part, op = code.split(',')
            op = int(op)
            if op == current_op:
                # 替换成该组中除当前值以外的另一个随机编号
                new_op = random.choice([x for x in kk if x != current_op])
                operation_code[idx] = f"{part},{new_op}"  # 保持原位置和 part 不变，只改 op
                break  # 一次只替换一个

    print(f"修改后的编码: {operation_code}")

    # 更新 machine_code
    for code in operation_code:
        op_num = int(code.split(',')[1])
        current_machine_code = data[data['工序'] == op_num]['机器'].values[0]
        machine_code.append(current_machine_code)

    # 生成 tem_data（用于后续处理）
    tem_data = data[data['工序'].isin([int(code.split(',')[1]) for code in operation_code])]
    tem_data = tem_data[['部件', '工序', '机器', '标准工时', '难易度', '前继工序', '前继工序数量']]

    return i['OR_CODE'], operation_code, machine_code, tem_data

def mutation_or_operation_machine(operation_data,mutation_rate,i):
    replace_ops = i['replace_op']
    or_node = i['OR_CODE']
    operation_code=copy.deepcopy(i['operation_code'])
    print(f"修改前的编码{i['operation_code']}")
    data = operation_data.copy()
    machine_code = []
    mutate_num = int(round((mutation_rate * len(or_node))))  # 变异的基因个数
    if mutate_num == 0:
        mutate_num = 1

    for i in range(mutate_num):
        kk = random.choice(replace_ops)
        print(f"kk{kk}")
        # 遍历 or_node 并替换符合条件的值
        for node in or_node:
            print(f"node{node}")
            for key, value in node.items():
                if value in kk:
                    # 选择 kk 中的另一个随机值（排除当前值）
                    new_value = random.choice([x for x in kk if x != value])
                    node[key] = new_value  # 替换值
                    print(f"替换的值{node[key]}")

                    for idx,code in enumerate(operation_code):
                        part,op =code.split(',')
                        if int(op)==value:
                            operation_code[idx]=f"{part},{new_value}"
                            break
    # 创建一个空列表用于存储 C1 未选择的替换工序
    non_selected_operations = []

    # 从 OR_CODE 提取已选择的工序编号
    selected_operations = [list(item.values())[0] for item in or_node]  # 提取工序编号，比如 [6, 12]
    print(f"selected_operations{selected_operations}")
    # 遍历 tem_array，提取未选择的工序
    for operation_pair in replace_ops:
        for operation in operation_pair:
            if operation not in selected_operations:
                non_selected_operations.append(operation)
    print(f"non_selected_operations{non_selected_operations}")
    data = data[~data['工序'].isin(non_selected_operations)]
    tem_data = data[['部件', '工序', '机器', '标准工时', '难易度', '前继工序', '前继工序数量']]

    tem_ddate, _ = generate_operation_codes(tem_data)
    print(tem_ddate)
    # print(f"修改后的编码{operation_codes}")
    for code in copy.deepcopy(operation_code):
        op_num = int(code.split(',')[1])  # 获取操作编码中的工序编号
        print(f"op_num{op_num}")
        current_machine_code = data[data['工序'] == op_num]['机器'].values[0]
        machine_code.append(current_machine_code)

    return or_node,operation_code,machine_code,tem_ddate

# def mutation_or_operation_machine(operation_data, mutation_rate, i):
#     replace_ops = i['replace_op']
#     or_node = i['OR_CODE']
#     operation_code = i['operation_code']
#     print(f"进来的编码: {operation_code}")
#
#     data = operation_data.copy()
#     machine_code = []
#
#     mutate_num = int(round((mutation_rate * len(or_node))))
#     if mutate_num == 0:
#         mutate_num = 1
#     print(f"变异个数: {mutate_num}")
#
#     # --------- 替换 OR_CODE 中的工序编号 ---------
#     for _ in range(mutate_num):
#         kk = random.choice(replace_ops)
#         for node in or_node:
#             for key, value in node.items():
#                 if value in kk:
#                     new_value = random.choice([x for x in kk if x != value])
#                     node[key] = new_value  # 替换 OR_CODE 的工序编号
#                     print(f"{node[key]}")
#                     print(new_value)
#                     # --------- 同步替换 operation_code 中的工序编码 ----------
#                     old_code = f"{key},{value}"
#                     new_code = f"{key},{new_value}"
#                     for idx, oc in enumerate(operation_code):
#                         if oc == old_code:
#                             operation_code[idx] = new_code
#                             print(f"将 {old_code} 替换为 {new_code}")
#                             break
#
#     # --------- 直接根据替换后的 operation_code 构建 machine_code ---------
#     for code in copy.deepcopy(operation_code):
#         part_id, op_num = code.split(',')
#         op_num = int(op_num)
#         current_machine_code = data[data['工序'] == op_num]['机器'].values[0]
#         machine_code.append(current_machine_code)
#
#     # print(f"修改后的编码: {operation_code}")
#     # print(f"对应机器: {machine_code}")
#
#     return or_node, operation_code, machine_code, data





file_path = 'data/operation_data.xlsx'

operation_data = pd.read_excel(file_path, sheet_name='final')
individual={'OR_CODE': [{'OR1': 6}, {'OR2': 12}], 'operation_code': ['O3,4', 'O2,2', 'O1,1', 'O2,3', 'O0,6', 'O0,7', 'O0,8', 'O0,9', 'O0,10', 'O0,12', 'O0,13', 'O0,14', 'O0,15', 'O0,16'], 'machine_code': ['B', 'A', 'A', 'B', 'H', 'C', 'A', 'B', 'B', 'G', 'D', 'E', 'A', 'F'], 'balance_code': [2, 2, 1, 2, 1, 1, 3, 3, 3, 2, 1, 2, 1, 1], 'workstation_code': [['L1', 'R1'], ['R6', 'L7'], ['L2'], ['R7', 'L8'], ['R2'], ['L3'], ['R8', 'L9', 'R9'], ['L10', 'R10', 'L11'], ['R11', 'R12', 'L1'], ['R3', 'L4'], ['R4'], ['L5', 'R5'], ['L1'], ['L6']], 'employ_code': [[{'workstation': 'L1', 'employ': 4}, {'workstation': 'R1', 'employ': 21}], [{'workstation': 'R6', 'employ': 3}, {'workstation': 'L7', 'employ': 22}], [{'workstation': 'L2', 'employ': 13}], [{'workstation': 'R7', 'employ': 17}, {'workstation': 'L8', 'employ': 23}], [{'workstation': 'R2', 'employ': 5}], [{'workstation': 'L3', 'employ': 1}], [{'workstation': 'R8', 'employ': 2}, {'workstation': 'L9', 'employ': 8}, {'workstation': 'R9', 'employ': 18}], [{'workstation': 'L10', 'employ': 20}, {'workstation': 'R10', 'employ': 9}, {'workstation': 'L11', 'employ': 15}], [{'workstation': 'R11', 'employ': 14}, {'workstation': 'R12', 'employ': 11}, {'workstation': 'L1', 'employ': 4}], [{'workstation': 'R3', 'employ': 10}, {'workstation': 'L4', 'employ': 6}], [{'workstation': 'R4', 'employ': 12}], [{'workstation': 'L5', 'employ': 19}, {'workstation': 'R5', 'employ': 7}], [{'workstation': 'L1', 'employ': 4}], [{'workstation': 'L6', 'employ': 16}]], 'replace_op': [[5, 6], [11, 12]], 'workstation_machines': {'L1': 'B', 'R1': 'B', 'R6': 'A', 'L7': 'A', 'L2': 'A', 'R7': 'B', 'L8': 'B', 'R2': 'H', 'L3': 'C', 'R8': 'A', 'L9': 'A', 'R9': 'A', 'L10': 'B', 'R10': 'B', 'L11': 'B', 'R11': 'B', 'R12': 'B', 'R3': 'G', 'L4': 'G', 'R4': 'D', 'L5': 'E', 'R5': 'E', 'L6': 'F'}, 'result_employ_allocation': [{'workstation': 'L1', 'employ': 4}, {'workstation': 'L2', 'employ': 13}, {'workstation': 'L3', 'employ': 1}, {'workstation': 'L4', 'employ': 6}, {'workstation': 'L5', 'employ': 19}, {'workstation': 'L6', 'employ': 16}, {'workstation': 'L7', 'employ': 22}, {'workstation': 'L8', 'employ': 23}, {'workstation': 'L9', 'employ': 8}, {'workstation': 'L10', 'employ': 20}, {'workstation': 'L11', 'employ': 15}, {'workstation': 'R1', 'employ': 21}, {'workstation': 'R2', 'employ': 5}, {'workstation': 'R3', 'employ': 10}, {'workstation': 'R4', 'employ': 12}, {'workstation': 'R5', 'employ': 7}, {'workstation': 'R6', 'employ': 3}, {'workstation': 'R7', 'employ': 17}, {'workstation': 'R8', 'employ': 2}, {'workstation': 'R9', 'employ': 18}, {'workstation': 'R10', 'employ': 9}, {'workstation': 'R11', 'employ': 14}, {'workstation': 'R12', 'employ': 11}]}
mutation_or_operation_machine(operation_data,0.2,individual)

