import random
import pandas as pd
import itertools
import openpyxl
from sympy import flatten

# file_path = 'data/operation_data.xlsx'
# operation_data = pd.read_excel(file_path, sheet_name='final')
# data = operation_data.copy()

def generateOR(data):
    OR_codes = []
    tem_data = data[['部件', '工序', '可替代工序']]  # 提取数据
    # 筛选出"可替代工序"列有值的行
    filtered_df = tem_data[tem_data['可替代工序'].notna()]

    tem_array = []  # 用于存储替代工序的列表
    existing_ops = []  # 用于存储已选择的工序，避免重复

    for index, row in filtered_df.iterrows():
        part = row['部件']
        op = int(row['工序'])

        # 处理替代工序
        replacement_operations = row['可替代工序']

        if isinstance(replacement_operations, str):  # 如果替代工序是字符串
            if '、' in replacement_operations:
                # 如果替代工序是多个工序（中文逗号分隔）
                replacement_operations = replacement_operations.split('、')  # 使用中文逗号分隔工序
                replacement_operations = [list(map(int, ops.split('+'))) if '+' in ops else [int(ops)] for ops in replacement_operations]
            elif '+' in replacement_operations:
                # 如果替代工序是多个工序的组合（加号分隔）
                replacement_operations = [list(map(int, replacement_operations.split('+')))]
            else:
                # 单一工序
                replacement_operations = [int(replacement_operations)]
        else:
            # 如果替代工序已经是单个工序
            replacement_operations = [int(replacement_operations)]

        # 检查是否已经存储该工序及其替代工序
        existing = False
        for item in tem_array:
            if item[0] == op:
                existing = True
                # 将替代工序添加到已有工序的列表中
                for replacement in replacement_operations:
                    if replacement not in item:
                        item.append(replacement)
                break

        if not existing:
            # 如果该工序没有存储过，创建新的记录
            tem_array.append([op] + replacement_operations)


    # 存储未被选择的工序
    remaining_codes=[]

    # 修改
    for i, item in enumerate(tem_array, start=1):
        # print(len(tem_array))
        # 随机选择一个替代组合
        selected_combination = random.choice(item)  # 选择工序
        # 获取未被选择的工序
        remaining = [op for op in item if op != selected_combination]
        remaining_codes.append(remaining)
        OR_codes.append({'OR' + str(i): selected_combination})

    # 展平 remaining_codes
    remaining_codes_flat = flatten(remaining_codes)

    data = data[~data['工序'].isin(remaining_codes_flat)]
    data = data[['部件', '工序', '机器', '标准工时', '难易度', '前继工序','前继工序数量']]
    # print(f"remaining_codes{remaining_codes}")
    # print(OR_codes)
    # print(f"tem_array: {tem_array}")  # 打印 tem_array 内容，帮助调试
    # print(data)
    return data, OR_codes,tem_array

# 假设你已经加载了数据并传递给 generateOR 函数
# data = pd.read_excel('path_to_data.xlsx')
# generateOR(data)
