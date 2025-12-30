import random
import pandas as pd
import generateOR

file_path = 'data/operation_data.xlsx'
operation_data = pd.read_excel(file_path, sheet_name='final')
data = operation_data.copy()


def parse_predecessors(pred):
    """解析前继工序字符串为数字列表"""
    if pd.isna(pred):
        return []
    elif isinstance(pred,int):
        return [pred]
    else:
        return list(map(int, pred.split('、')))


def group_operations_by_predecessors(data):
    """根据前继工序将工序分组"""
    grouped = {}

    # 提取需要的列
    tem_data = data[['部件', '工序', '前继工序']]

    for _, row in tem_data.iterrows():
        pred_list = parse_predecessors(row['前继工序'])
        # print(f"前继工序{pred_list}")
        pred_tuple = tuple(pred_list)  # 使用元组作为字典的键
        # print(f"使用元组作为字典的键{pred_tuple}")

        if pred_tuple not in grouped:
            grouped[pred_tuple] = []

        # 将工序按前继工序分组
        grouped[pred_tuple].append(row)
        # print(f"grouped{grouped}")

    return grouped


def generate_operation_codes(data):
    """根据前继工序的一致性生成工序编码"""
    operation_codes = []

    # 将工序按前继工序进行分组
    grouped_operations = group_operations_by_predecessors(data)

    # 对每一组工序进行处理
    for pred_tuple, group in grouped_operations.items():
        # 在同一组内打乱工序顺序
        random.shuffle(group)

        # 遍历组内的工序，生成工序编码
        for row in group:
            part = row['部件']
            op = row['工序']

            # 生成工序编码
            i = part[1:]
            j = op
            operation_code = f"O{i},{j}"
            operation_codes.append(operation_code)

    # # 打印打乱后的工序代码顺序
    # print(f"operation_codes{operation_codes}")

    return data, operation_codes


# # 运行generateOR和生成工序代码
# final_data, _, _ = generateOR.generateOR(data)
# generate_operation_codes(final_data)
