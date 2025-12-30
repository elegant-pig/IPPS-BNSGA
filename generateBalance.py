import random
from decimal import getcontext, Decimal

import numpy as np
import pandas as pd

import generateOR
import generateOperation
import generateMachine


# file_path = 'data/operation_data.xlsx'
# operation_data = pd.read_excel(file_path, sheet_name='final')
# data=operation_data.copy()
# num_station=23
def generate_balance_codes(data,constraint_code,num_station):
    constraint=[]
    balance_codes=[]
    # tem_data = data[['工序', '标准工时','机器']]
    # data=data[['工序', '标准工时','机器']]
    tem_data=index_calculation(data,num_station)

    total_balance=0 #用于计算总的人力平衡
    # 遍历每个操作编码，查找对应的机器编码
    for entry in constraint_code:
        code, machine = entry.split("->")
        # 提取工序编号 j
        op_num = int(code.split(',')[1])  # 获取操作编码中的工序编号
        # print(op_num)
        # 查找工序编号对应的机器编码

        tem_balance = tem_data[tem_data['工序'] == op_num]['人力平衡'].values[0]

        decimal_part = tem_balance - int(tem_balance)
        if decimal_part <= 0.3:
            tem_balance=int(tem_balance)
        else:
            tem_balance=int(tem_balance) + 1  # 向上取整
        if tem_balance==0:
            tem_balance=1

        # 创建操作编码与机器编码的映射关系
        constraint.append(f"{code}->{machine}->{tem_balance}")
        balance_codes.append(tem_balance)
        # 计算总平衡值
        total_balance += tem_balance
        # print(f"total_balance{total_balance}")
        # print(f"constraint{constraint}")
    if total_balance<num_station:
        print("!!!!!!!!!!!!!!!!wrong")
        raise ValueError("数量不对！！！")


        # balance_layer.append(f"{code} -> {balance}")
        # balance_codes.append(constraint)
    print(f"!!!!!!!!!!!!!!!!!!")
    print(balance_codes)
    print(sum(balance_codes))
    return data,balance_codes,constraint

def index_calculation(data,num_station):
    # 添加一列新数据列并初始化为 None
    data['人力平衡'] = None
    # 计算所有工序的加工时间
    total_standard_time = data['标准工时'].sum().round(2)
    # print(f"总标准工时: {total_standard_time}")

    # 遍历data，填充新列
    for i, row in data.iterrows():
        # 按顺序给新列添加数据
        # 假设我们想用随机值填充新列
        new_value=((row['标准工时'] / total_standard_time) * num_station).round(5)
        # print(f"new_value{new_value}")
        data.loc[i, '人力平衡'] =new_value
    # print(data)
    return data

def generate_new_balance(individual,data):
    print(individual)
    new_balance_codes = []
    float_balance_codes=[]
    # unique_len = len({tuple(sorted(item)) for item in individual['individual']['workstation_code']})
    # 提取所有的键
    unique_len = len(list(individual['workstation_machines'].keys()))
    print(f"unique_len{unique_len}")
    # tem_data = data[['工序', '标准工时','机器']]
    # data=data[['工序', '标准工时','机器']]
    tem_data = index_calculation(data, unique_len)
    total_balance = 0  # 用于计算总的人力平衡
    for op in individual['operation_code']:
        # print(f"854854")
        op_num = int(op.split(',')[1])
        print(f"op_num{op_num}")
        try:
            tem_balance = tem_data[tem_data['工序'] == op_num]['人力平衡'].values[0]
            float_balance_codes.append(round(tem_balance,5))

            decimal_part = tem_balance - int(tem_balance)

            tem_balance = round_balance_probabilistic(tem_balance)

            # if decimal_part <= 0.3:
            #     tem_balance = int(tem_balance)
            # else:
            #     tem_balance = int(tem_balance) + 1  # 向上取整
            if tem_balance == 0:
                tem_balance = 1

            # # 创建操作编码与机器编码的映射关系
            # constraint.append(f"{code}->{machine}->{tem_balance}")
            new_balance_codes.append(tem_balance)
            # 计算总平衡值
            total_balance += tem_balance
        except IndexError:
            print(f"当前code没有这个工序，跳过")
            continue
    if total_balance < unique_len:
        diff_value=int(total_balance-unique_len)
        print(f"diff_value{diff_value}")
        modified_balance=adjust_balance_by_difference(float_balance_codes,new_balance_codes,diff_value)
        return modified_balance,float_balance_codes
    else:
        return new_balance_codes,float_balance_codes

def round_balance_probabilistic(tem_balance, k=10):
    decimal_part = tem_balance - int(tem_balance)
    base = int(tem_balance)
    # 用 sigmoid 平滑决定进位概率
    prob_up = 1 / (1 + np.exp(-k * (decimal_part - 0.5)))
    if random.random() < prob_up:
        base += 1
    # 避免为0
    return max(1, base)


def adjust_balance_by_difference(float_balance_codes, tem_balance, diff_balance):
    used_indices = set()

    for _ in range(diff_balance):
        # 计算差值（只考虑未被修改的位置）
        residuals = [
            (i, float_balance_codes[i] - tem_balance[i])
            for i in range(len(float_balance_codes))
            if i not in used_indices
        ]

        if not residuals:
            break  # 所有位置都修改过了

        # 找差值最大的索引
        max_i = max(residuals, key=lambda x: x[1])[0]

        # 加 1 并记录
        tem_balance[max_i] += 1
        used_indices.add(max_i)

    return tem_balance


# def adjust_balance_by_difference(float_balance_codes, tem_balance, diff_balance):
#     used_indices = set()
#     residuals = []
#
#     for i in range(len(float_balance_codes)):
#         diff = float_balance_codes[i] - tem_balance[i]
#         residuals.append((i, diff))
#
#     # 优先处理误差大的
#     sorted_residuals = sorted(residuals, key=lambda x: -x[1])  # 按 float-整数 从大到小
#
#     for _ in range(diff_balance):
#         # 先找误差最大的，误差大于某个阈值才修改
#         modified = False
#         for i, diff in sorted_residuals:
#             if i in used_indices:
#                 continue
#             if diff > 0.25:  # 阈值可以调整
#                 tem_balance[i] += 1
#                 used_indices.add(i)
#                 modified = True
#                 break
#         # 如果所有误差都很小，就找 tem_balance 最大的那个加一
#         if not modified:
#             max_index = max(
#                 [(i, val) for i, val in enumerate(tem_balance) if i not in used_indices],
#                 key=lambda x: x[1],
#                 default=(None, None)
#             )[0]
#             if max_index is not None:
#                 tem_balance[max_index] += 1
#                 used_indices.add(max_index)
#     return tem_balance

# final_data,_=generateOR.generateOR(data)
# op_final_data,op_code=generateOperation.generate_operation_codes(final_data)
# data,mchine_codes,constraint=generateMachine.generate_machine_codes(op_code,op_final_data)
# generate_balance_codes(final_data,constraint,num_station)

