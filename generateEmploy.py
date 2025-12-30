import math
import random

import generateOR
import generateWorkstation_simple

import pandas as pd
import generateBalance
import generateOperation
import generateMachine
from check_code import check_result_employ_allocation, check_out_generate_employ_code

# file_path = 'data/operation_data.xlsx'
# staff_data = pd.read_excel(file_path, sheet_name='staff')
# operation_data = pd.read_excel(file_path, sheet_name='final')
# data=operation_data.copy()
# num_station=23

difficulty_weight={
    'A':1,
    'B':0.8,
    'C':0.6,
    'D':0.4
}
# 反向创建一个字典，方便根据权重查找对应的难易度字母
weight_to_difficulty = {v: k for k, v in difficulty_weight.items()}
def generateEmploy(op_data,staff_data,workstation_codes,workstation_assignments,numstation):
    employ_data = staff_data[['员工', 'A', 'B', 'C', 'D']]
    difficulty_data=op_data[['工序','难易度']]
    result_employ_allocation = []
    max_difficulties={}
    workstation_employ=[]
    tem_employ_data=employ_data.copy()
    print(f"workstation_assignments{workstation_assignments}")
    # 获取工作站分配的工序
    for workstation,op in workstation_assignments.items():
        diff_coll = []
        # print(op)
        # print(f"workstation_assignments: {workstation_assignments}")
        for number in op:
            # 获取当前工序
            code = int(number.split(",")[1])
            # 当前工序的难易度
            diff = difficulty_data[difficulty_data['工序'] == code]['难易度'].values[0]
            # 根据难易度赋予权值
            weight=difficulty_weight[diff]
            diff_coll.append(weight)

        # 获取当前工作站的最大难易度
        if diff_coll:
            # 找到当前工作站中所有工序，并找到难易度最大的工序
            max_difficulty = max(diff_coll)
            max_difficulty_letter=weight_to_difficulty[max_difficulty] #根据权重找到其对应的难易度的字母
            # 将 max_difficulty_letter 添加到 max_difficulties 字典中
            # 该工作站分配的难易度按照难易度最高的分配
            max_difficulties[workstation] = max_difficulty_letter

        # 按照工序难易度排序，找出完成该难易度效率最高的员工
        employ_data_sorted = tem_employ_data.sort_values(by=max_difficulty_letter, ascending=False)
        # 员工编号
        top_employ=int(employ_data_sorted.iloc[0]['员工'])

        # 添加到result_employ_allocation
        # result_employ_allocation.append({'workstation':workstation,'employ':top_employ,'difficulty': diff,'operation':op[0]})
        result_employ_allocation.append({'workstation':workstation,'employ':top_employ})


        # 从 tem_employ_data 中删除该员工
        tem_employ_data = tem_employ_data.drop(tem_employ_data[tem_employ_data['员工'] == top_employ].index)
        # # 从 tem_employ_data 中删除该员工
        # tem_employ_data = tem_employ_data.drop(tem_employ_data[tem_employ_data['员工'] == top_employ].index)

    result_employ_allocation,employ_code=workstation_assignments_employ(result_employ_allocation,workstation_codes)
    print(f"result_employ_allocation{result_employ_allocation}")
    print(f"employ_code{employ_code}")
    check_out_generate_employ_code(employ_code, numstation)
    check_result_employ_allocation(result_employ_allocation, numstation)
    return result_employ_allocation,employ_code
    # return result_employ_allocation


def workstation_assignments_employ(result_employ_allocation,workstation):
    # 创建一个空字典来存储工作站与员工的匹配
    workstation_employees = {}
    # 生成最终的分配结果
    employ_code = []
    for entry in result_employ_allocation:
        # print(f"entry{entry}")
        workstation_name = entry['workstation']
        employee_id = entry['employ']
        # op=entry['operation']
        # employee_eff=entry['efficiency']
        if workstation_name not in workstation_employees:
            workstation_employees[workstation_name] = []
        workstation_employees[workstation_name].append({'workstation':workstation_name,'employ':employee_id})
    # print(f"workstation_employees{workstation_employees}")

    # print(f"100100")
    # 遍历 workstation_code，根据每个工作站的名称找到对应的员工
    for workstation_list in workstation:
        print(workstation_list)
        # 为每个子列表（工作站位置）创建一个员工编号的列表
        employee_ids = []
        for station in workstation_list:
            # print(f"station")
            # 获取对应工作站的员工编号
            if station in workstation_employees:
                # print(f"workstation_employees{workstation_employees}")
                # print(f"workstation_employees[station]{workstation_employees[station]}")

                employee_ids.extend(workstation_employees[station])
                # print(f"employee_ids{employee_ids}")

        # 将员工信息（员工ID和效率）添加到分配结果中
        employ_code.append(employee_ids)

    # # 输出结果
    # print(f"result_employ_allocation{result_employ_allocation}")
    # check_result_employ_allocation(result_employ_allocation,23)
    return result_employ_allocation,employ_code


# # data, OR_codes, tem_array
# final_data,_,_=generateOR.generateOR(data)
# op_final_data,op_code=generateOperation.generate_operation_codes(final_data)
# data,mchine_codes,constraint1=generateMachine.generate_machine_codes(op_code,op_final_data)
# tem_data,balance_codes,constraint2= generateBalance.generate_balance_codes(final_data, constraint1, num_station)
# # workstation=generateWorkstation_simple.generate_workstation(num_station)
# # data,workstation_codes,workstation_assignments,result_constraint,workstation_machines
# _,workstation_codes,workstation_assignments,result_constraint,_=generateWorkstation_simple.assignment_operation(tem_data,constraint2,num_station)
# generateEmploy(tem_data,workstation_codes,workstation_assignments)
# # data,workstation_codes,workstation_assignments
# # workstation_assignments_employ(generateEmploy(tem_data,workstation_assignments))