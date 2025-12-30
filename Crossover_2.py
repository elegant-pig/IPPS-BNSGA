import copy
import random
from collections import OrderedDict, defaultdict
from itertools import chain

import pandas as pd

import adjust_workstation_machine_code
import calculate
import generateOperation
import init
import selection

from check_code import check_adjust_workstation, check_wk_ma, check_adjust_employ, \
    check_result_employ_allocation, check_wk_ma2, check_machines_to_workstations
from examine_encoding import examine_workstation_code, examine_result_employ_allocation, \
    examine_workstation_machines_code, examine_employ_code, examine_individual
from generateBalance import  generate_new_balance

file_path = 'data/operation_data.xlsx'
operation_data = pd.read_excel(file_path, sheet_name='final')
data = operation_data.copy()
def Crossover(elite_individuals):
    Child=[]

    # while len(elite_individuals) > 1:
    #     # 随机选择两个父代
    #     # P1, P2 = random.sample(elite_individuals, 2)
    #
    #     # # P1选择最优秀的个体
    #     # P1=elite_individuals[0]
    #     # print(f"P1!!!!!!!!!!!!!")
    #     # check_adjust_employ(P1['individual']['employ_code'], 23)
    #     # elite_individuals.remove(P1)
    #     # P2采用轮盘赌选择个体
    #     # P2= selection.roulette_wheel_selection(elite_individuals, 1)
    #
    #
    #     select_child=selection.roulette_wheel_selection(elite_individuals, 2)
    #
    #
    #     child1,child2=crossover_two_child(copy.deepcopy(select_child[0]),copy.deepcopy(select_child[1]))
    #
    #
    #     Child.append(child1)
    #     Child.append(child2)
    #     # 在轮盘赌的时候就已经删除了

    for times in range(len(elite_individuals)//2):
    # 轮盘赌选择后不删除选择过的个体
        select_parent= selection.roulette_selection_by_rank_and_crowding(elite_individuals, 2)
        # 交叉后得到子代
        C1,C2=crossover_two_child(select_parent[0],select_parent[1])
        Child.append(C1)
        Child.append(C2)

    return Child

    # return Child,old_best_individul

def crossover_two_child(P1,P2):

    C1 = {'individual': {
        'OR_CODE': [],
        'operation_code': [],
        'machine_code': [],
        'balance_code': [],
        'workstation_code': [],
        'employ_code': [],
        'replace_op':[],
        'workstation_machines':{},
        'result_employ_allocation':[]

    }}
    C2 = {'individual': {
        'OR_CODE': [],
        'operation_code': [],
        'machine_code': [],
        'balance_code': [],
        'workstation_code': [],
        'employ_code': [],
        'workstation_machines':{},
        'result_employ_allocation': []
    }}

    C1['individual']['replace_op'] = copy.deepcopy(P1['individual']['replace_op'])
    C1['individual']['workstation_machines'] = copy.deepcopy(P1['individual']['workstation_machines'])
    C1['individual']['result_employ_allocation'] = copy.deepcopy(P1['individual']['result_employ_allocation'])

    C2['individual']['replace_op'] = copy.deepcopy(P2['individual']['replace_op'])
    C2['individual']['workstation_machines'] = copy.deepcopy(P2['individual']['workstation_machines'])
    C2['individual']['result_employ_allocation'] = copy.deepcopy(P2['individual']['result_employ_allocation'])

    temC1,temC2=crossover_OR_FMX_ONE_POINT(copy.deepcopy(P1),copy.deepcopy(P2))
    C1['individual']['OR_CODE'] = copy.deepcopy(temC1)
    C2['individual']['OR_CODE'] = copy.deepcopy(temC2)
    C1,C2=crossover_other_FMX_two_point(copy.deepcopy(P1),copy.deepcopy(P2),copy.deepcopy(C1),copy.deepcopy(C2))

    # # 调整个体以满足约束条件
    # # 深拷贝是关键，确保调整过程中没有共享引用
    # # before_C1 = copy.deepcopy(C1)
    # C1 = adjust_individual(C1, data)
    # before_C1=copy.deepcopy(C1)
    # print(f"检查C1的值{C1}")
    # examine_individual(C1, 23)
    #
    # # 深拷贝是关键，确保调整过程中没有共享引用
    # # before_C2 = copy.deepcopy(C2)
    # C2 = adjust_individual(C2, data)
    # print(f"检查C2的值{C2}")
    # examine_individual(C2, 23)
    #
    # # 检查C1是否被污染
    # print(f"二次检查C1的值{C1}")
    # print("是否被污染：", before_C1['individual']['employ_code'] == C1['individual']['employ_code'])
    # # if before_C1['individual']['employ_code'] == C1['individual']['employ_code']:
    # #     print("C1 没有被污染")
    # # else:
    # #     print(f"C1 被污染了")
    # #     C1=copy.deepcopy(before_C1)
    # #     # raise ValueError("C1 被污染")
    # if before_C1==C1:
    #     print(f"未被污染")
    # else:
    #     print(f"被污染了")
    #     C1=copy.deepcopy(before_C1)

    return copy.deepcopy(C1), copy.deepcopy(C2)

def crossover_OR_FMX_ONE_POINT(P1, P2):
    """"
        单点交叉
        -P1:父代1
        -P2:父代2
        """

    # 随机选择交叉点，确保选择一个有效的索引
    cross_point = random.randint(0, len(P1['individual']['OR_CODE']))  # 选择0到2之间的一个位置

    # 进行单点交叉
    tem1_or= P1['individual']['OR_CODE'][:cross_point] + P2['individual']['OR_CODE'][cross_point:]
    tem2_or = P2['individual']['OR_CODE'][:cross_point] + P1['individual']['OR_CODE'][cross_point:]

    return tem1_or, tem2_or
# def crossover_OR_FMX_ONE_POINT(P1,P2,C1,C2):
#     """"
#     单点交叉
#     -P1:父代1
#     -P2:父代2
#     """
#
#     # 随机选择交叉点，确保选择一个有效的索引
#     cross_point = random.randint(0, len(P1['individual']['OR_CODE']))  # 选择0到2之间的一个位置
#
#     # 进行单点交叉
#     C1['individual']['OR_CODE']=P1['individual']['OR_CODE'][:cross_point]+P2['individual']['OR_CODE'][cross_point:]
#     C2['individual']['OR_CODE']=P2['individual']['OR_CODE'][:cross_point]+P1['individual']['OR_CODE'][cross_point:]
#
#     return C1,C2

def crossover_other_FMX_two_point(P1,P2,C1,C2):
    """"
        两点交叉
        -P1:父代1
        -P2:父代2
    """
    # 要处理的键列表
    keys = ['operation_code', 'machine_code', 'balance_code', 'workstation_code', 'employ_code']

    cross_point1 = random.randint(0, len(P1['individual']['operation_code']))
    cross_point2 = random.randint(0, len(P1['individual']['operation_code']))

    # 如果两个交叉点相同，继续生成第二个交叉点
    while cross_point1 == cross_point2:
        cross_point2 = random.randint(0, len(P1['individual']['OR_CODE']) - 1)

    if cross_point1>cross_point2:
        for key in keys:
            C1['individual'][key] = copy.deepcopy(P1['individual'][key][:cross_point2] + P2['individual'][key][cross_point2:cross_point1] + P1['individual'][key][cross_point1:])
            C2['individual'][key] = copy.deepcopy(P2['individual'][key][:cross_point2] + P1['individual'][key][cross_point2:cross_point1] + P2['individual'][key][cross_point1:])


    else:
        for key in keys:
            C1['individual'][key] = copy.deepcopy(
                P1['individual'][key][:cross_point1] + P2['individual'][key][cross_point1:cross_point2] +
                P1['individual'][key][cross_point2:])
            C2['individual'][key] = copy.deepcopy(
                P2['individual'][key][:cross_point1] + P1['individual'][key][cross_point1:cross_point2] +
                P2['individual'][key][cross_point2:])


    return C1,C2

def adjust_op(Child,data):
    # 创建一个空列表用于存储 C1 未选择的替换工序
    non_selected_operations = []

    # 从 C1_OR_CODE 提取已选择的工序编号
    selected_operations = [list(item.values())[0] for item in Child['individual']['OR_CODE']]  # 提取工序编号，比如 [6, 12]

    # 遍历 tem_array，提取未选择的工序
    for operation_pair in Child['individual']['replace_op']:
        for operation in operation_pair:
            if operation not in selected_operations:
                non_selected_operations.append(operation)
    data = data[~data['工序'].isin(non_selected_operations)]
    tem_data = data[['部件', '工序', '机器', '标准工时', '难易度', '前继工序','前继工序数量']]
    print(f"166166166")
    print(f"data{tem_data}")
    _,operation_codes=generateOperation.generate_operation_codes(tem_data)

    return tem_data,operation_codes

# def adjust_individual(child,data):
#     # 单个编码调整
#
#     # 调整工序和机器编码
#     child,tem_data=adjust_operation_machine(child,data)
#
#     # 调整人力平衡
#     child=generate_new_balance(child,tem_data)
#
#
#     # 根据人力平衡调整工作站编码
#     child= adjust_workstation_machine_code.adjust_crossover_workstation_machines(child, 23)
#
#     child= adjust_workstation_machine_code.adjust_crossover_workstation_code(child,23)
#
#     examine_workstation_code(child['individual']['workstation_code'],23)
#     # 根据调整员工编码
#     child=adjust_crossover_employ_code(child,23)
#     examine_employ_code(child['individual']['employ_code'],23)
#
#     return child

def adjust_operation_machine(child,data):
    # 先调整or_code和op_code
    tem_data, right_operation_codes = adjust_op(child, data)
    current_operation_codes = child['individual']['operation_code'].copy()

    # 调整工序和机器编码
    # 如果去重后的工序编码跟正确的工序编码长度不一致，则有重复工序
    if len(current_operation_codes) != len(set(current_operation_codes)):
        # print("有重复的工序")
        # 使用 OrderedDict 来保持顺序并去重
        ordered_dict = OrderedDict()
        # 记录去重掉的元素的位置
        removed_positions = []

        # 遍历原始列表并创建一个有序字典
        for idx, op in enumerate(current_operation_codes):
            if op not in ordered_dict:
                ordered_dict[op] = None  # 在字典中添加该元素
            else:
                removed_positions.append({'idx': idx, 'op': op})  # 如果元素重复，记录它的索引

        # 获取去重后的工序列表
        unique_operations = list(ordered_dict.keys())

        # 找出 right_operation_codes 中那些不在 C1['individual']['operation_code'] 中的工序
        missing_operations = [op for op in right_operation_codes if op not in unique_operations]
        # print(f"missing_operations{missing_operations}")

        if int(len(missing_operations)) + int(len(unique_operations)) != int(len(right_operation_codes)):
            # print("不仅重复，还出现了占用工序")
            for missing_op in missing_operations:
                replaced = False
                op_num = int(missing_op.split(',')[1])  # 获取操作编码中的工序

                for operation_pair in child['individual']['replace_op']:
                    if op_num in operation_pair:
                        # print("缺失的工序有替代工序")
                        # 缺失工序的替代工序
                        repalce_tem_op = [op for op in operation_pair if op != op_num]
                        for op in repalce_tem_op:
                            for i, current_op in enumerate(current_operation_codes):
                                # 找到了替换工序所在位置
                                if op == int(current_op.split(',')[1]):
                                    # 调整工序
                                    current_operation_codes[i] = missing_op
                                    # child['individual']['workstation_code'][]
                                    # 调整机器
                                    child['individual']['machine_code'][i] = data[data['工序'] == int(op)]['机器'].values[0]
                                    replaced = True
                                    missing_operations.remove(missing_op)  # 删除已替换的工序
                                    break

                            if replaced:
                                break
                if replaced:
                    # print(f"missing_operations{missing_operations}")
                    break  # 跳出当前循环，处理下一个缺失工序

            if missing_operations:
                # print("还有工序没有添加进去，这些是没有可替换工序的工序")
                # 调整工序
                current_operation_codes[removed_positions[0]['idx']] = missing_operations[0]
                child['individual']['operation_code'] = current_operation_codes

                # 调整工序对应机器
                child['individual']['machine_code'][removed_positions[0]['idx']] = \
                data[data['工序'] == int(missing_operations[0].split(',')[1])]['机器'].values[0]

                # 调整工序对应工作站
                tem_balance = child['individual']['balance_code'][removed_positions[0]['idx']]
            else:
                # 直接赋值，无须调整
                child['individual']['operation_code'] = current_operation_codes


        else:
            # 调整工序
            current_operation_codes[removed_positions[0]['idx']] = missing_operations[0]
            child['individual']['operation_code'] = current_operation_codes

            # 调整对应机器
            child['individual']['machine_code'][removed_positions[0]['idx']] = \
            data[data['工序'] == int(missing_operations[0].split(',')[1])]['机器'].values[0]
            tem_balance = child['individual']['balance_code'][removed_positions[0]['idx']]
            # process_time = tem_data[tem_data['工序'] == op_num]['标准工时'].values[0]
    elif set(child['individual']['operation_code']) == set(right_operation_codes):
        # 如果 operation_codes 中的工序与 C1 的工序完全一致，则无需调整
        print("生成的工序与 C1 的工序一致，无需调整。")
    else:
        # print("长度相等，但是工序对不上，说明有工序错误")
        # 找出 right_operation_codes 中那些不在 C1['individual']['operation_code'] 中的工序
        missing_operations = [op for op in right_operation_codes if op not in current_operation_codes]

        for missing_op in missing_operations:
            replaced = False
            op_num = int(missing_op.split(',')[1])  # 获取操作编码中的工序

            for operation_pair in child['individual']['replace_op']:
                if op_num in operation_pair:
                    # print("缺失的工序有替代工序")
                    # 缺失工序的替代工序
                    repalce_tem_op = [op for op in operation_pair if op != op_num]

                    for op in repalce_tem_op:
                        for i, current_op in enumerate(current_operation_codes):

                            # 找到了替换工序所在位置
                            if op == int(current_op.split(',')[1]):
                                current_operation_codes[i] = missing_op
                                replaced = True
                                missing_operations.remove(missing_op)  # 删除已替换的工序
                                # 调整机器编码
                                child['individual']['machine_code'][i] = data[data['工序'] == int(op)]['机器'].values[0]
                                break

                        if replaced:
                            break
            if replaced:
                break
        child['individual']['operation_code'] = current_operation_codes

    return child,tem_data













