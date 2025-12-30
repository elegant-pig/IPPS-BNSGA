import copy
import random

import pandas as pd

from generateOperation import generate_operation_codes


def mutation_or_operation_machine1(operation_data,i):
    replace_ops = i['replace_op']
    or_node = i['OR_CODE']
    operation_code=copy.deepcopy(i['operation_code'])
    data = operation_data.copy()
    machine_code = []

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
    # # 遍历 tem_array，提取未选择的工序
    # for operation_pair in replace_ops:
    #     for operation in operation_pair:
    #         if operation not in selected_operations:
    #             non_selected_operations.append(operation)
    # print(f"non_selected_operations{non_selected_operations}")
    # data = data[~data['工序'].isin(non_selected_operations)]
    # tem_data = data[['部件', '工序', '机器', '标准工时', '难易度', '前继工序', '前继工序数量']]
    #
    # tem_ddate, _ = generate_operation_codes(tem_data)
    # print(tem_ddate)
    # print(f"修改后的编码{operation_codes}")
    for code in copy.deepcopy(operation_code):
        op_num = int(code.split(',')[1])  # 获取操作编码中的工序编号
        print(f"op_num{op_num}")
        current_machine_code = data[data['工序'] == op_num]['机器'].values[0]
        machine_code.append(current_machine_code)

    return or_node,operation_code,machine_code


def mutation_or_operation_machine2(operation_code, data):
    """
    对 operation_code 做变异：交换当前部件为0的工序与其前面不属于前继的工序。

    参数：
    - operation_code: 当前工序编码列表，如 ['O1,1','O2,2','O0,5','O0,6']
    - tem_data: 包含 '工序' 与 '前继工序' 的 DataFrame

    返回：
    - operation_code_new: 变异后的 operation_code
    """
    operation_code_new = operation_code.copy()

    # 获取部件为0的工序位置
    idx_candidates = [idx for idx, code in enumerate(operation_code_new) if code.startswith('O0,')]
    if not idx_candidates:
        return operation_code_new  # 没有可变异工序，返回原值

    # 随机选一个位置
    select_idx = random.choice(idx_candidates)
    selected_code = operation_code_new[select_idx]
    selected_op = int(selected_code.split(',')[1])  # 提取工序编号

    # 获取它的前继工序
    pred_str = data[data['工序'] == selected_op]['前继工序'].values
    preds = str(pred_str[0]).split(',') if len(pred_str) > 0 and pd.notna(pred_str[0]) else []
    preds = [int(p.strip()) for p in preds if p.strip().isdigit()]

    # 查看它之前的所有工序（在 operation_code 中的位置）
    for idx in range(select_idx - 1, -1, -1):  # 从 select_idx 向前扫描
        code_before = operation_code_new[idx]
        part_id, op_id = code_before.split(',')
        op_id = int(op_id)

        # 如果这个不是前继，就可以交换
        if op_id not in preds:
            # 交换位置
            operation_code_new[select_idx], operation_code_new[idx] = operation_code_new[idx], operation_code_new[
                select_idx]
            break  # 一次变异就好
        # ===== 同步生成新的 machine_code =====
    machine_code = []
    for code in operation_code_new:
        op_num = int(code.split(',')[1])  # 工序编号
        machine = data[data['工序'] == op_num]['机器'].values[0]
        machine_code.append(machine)



    return operation_code_new,machine_code