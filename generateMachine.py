import pandas as pd
import string

import generateOR
import generateOperation

# file_path = 'data/operation_data.xlsx'
# operation_data = pd.read_excel(file_path, sheet_name='final')
# data=operation_data.copy()

def generate_machine_codes(operation_codes,data):
    machine_codes=[]
    constraint=[]
    tem_data=data[['工序','机器']]
    # 遍历每个操作编码，查找对应的机器编码
    for code in operation_codes:
        # 提取工序编号 j
        op_num = int(code.split(',')[1])  # 获取操作编码中的工序编号
        # print(op_num)
        # 查找工序编号对应的机器编码
        machine_code = tem_data[tem_data['工序'] == op_num]['机器'].values[0]

        # 创建操作编码与机器编码的映射关系
        constraint.append(f"{code}->{machine_code}")
        machine_codes.append(machine_code)
    # print(machine_codes)
    return data,machine_codes,constraint


# final_data,_=generateOR.generateOR(data)
# op_final_data,op_code=generateOperation.generate_operation_codes(final_data)
# generate_machine_codes(op_code,op_final_data)


