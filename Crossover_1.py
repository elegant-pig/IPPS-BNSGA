import copy
import random
from collections import OrderedDict, defaultdict
from itertools import chain

import pandas as pd

import adjust_workstation_machine_code
# import calculate
import generateOperation
import init
import selection
from check_code import check_adjust_workstation, check_wk_ma, check_adjust_employ, \
    check_result_employ_allocation, check_wk_ma2, check_machines_to_workstations
from generateBalance import  generate_new_balance

file_path = 'data/operation_data.xlsx'
operation_data = pd.read_excel(file_path, sheet_name='final')
data = operation_data.copy()
def crossover_choose_parent(elite_individuals):
    # print(f"交叉之前的个体")
    print(elite_individuals)
    Child=[]
    # print(f"choose_parent")
    # copy_elite_individuals=elite_individuals.copy()
    # old_best_individul=elite_individuals[0]
    # 将原本最优的个体保留下来
    # Child.append(old_best_individul)

    while len(elite_individuals) > 1:
        # 随机选择两个父代
        # P1, P2 = random.sample(elite_individuals, 2)

        # # P1选择最优秀的个体
        # P1=elite_individuals[0]
        # print(f"P1!!!!!!!!!!!!!")
        # check_adjust_employ(P1['individual']['employ_code'], 23)
        # elite_individuals.remove(P1)
        # P2采用轮盘赌选择个体
        # P2= selection.roulette_wheel_selection(elite_individuals, 1)
        select_child=selection.roulette_wheel_selection(elite_individuals, 2)
        # print(P2)

        # child1,child2=crossover(P1,P2[0])
        child1,child2=crossover(select_child[0],select_child[1])

        print(f"5555555555555555555")
        # print(f"检查检查{child1['individual']['workstation_code']}")
        check_adjust_workstation(child1['individual']['workstation_code'], 23)
        # check_adjust_workstation(child2['individual']['workstation_code'], 23)
        # print(f"负责检查交叉后的编码有没有问题")
        print(f"检查检查{child1['individual']['result_employ_allocation']}")
        check_result_employ_allocation(child1['individual']['result_employ_allocation'], 23)
        # check_result_employ_allocation(child2['individual']['result_employ_allocation'], 23)

        # check_adjust_employ(child2['individual']['employ_code'], 23)
        print(f"检查检查{child1['individual']['workstation_machines']}")
        check_wk_ma(child1['individual']['workstation_machines'], 23)
        # check_wk_ma(child2['individual']['workstation_machines'], 23)

        print(f"检查检查{child1['individual']['employ_code']}")
        check_adjust_employ(child1['individual']['employ_code'], 23)

        print(f"结束了！！！！！")

        Child.append(child1)
        Child.append(child2)
        # 在轮盘赌的时候就已经删除了
        # # 从 elite_individuals 中移除 P2
        # elite_individuals.remove(P2)

    # # 如果还有剩余的个体（即只有一个未配对的个体），与 P1 进行交叉
    # if elite_individuals:
    #     last_individual = elite_individuals.pop()  # 移除最后一个未配对的个体
    #     child1, child2 = crossover(old_best_individul, last_individual)
    #     Child.append(child1)
    #     Child.append(child2)
    o=0
    for j in Child:
        print(f"%%%%%{o}")
        check_wk_ma(j['individual']['workstation_machines'], 23)
        check_adjust_workstation(j['individual']['workstation_code'], 23)
        check_result_employ_allocation(j['individual']['result_employ_allocation'], 23)
        check_adjust_employ(j['individual']['employ_code'], 23)
        o+=1
    return Child

    # return Child,old_best_individul

def crossover(P1,P2):

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
    # replace_op、result_employ_allocation、workstation_machines这三个变量不交叉，因为他们是用来辅助帮忙调整编码的
    C1['individual']['replace_op']=P1['individual']['replace_op']
    C1['individual']['workstation_machines']=P1['individual']['workstation_machines']
    C1['individual']['result_employ_allocation']=P1['individual']['result_employ_allocation']
    C2['individual']['replace_op']=P2['individual']['replace_op']
    C2['individual']['workstation_machines']=P2['individual']['workstation_machines']
    C2['individual']['result_employ_allocation']=P2['individual']['result_employ_allocation']
    # print(f"888888")
    # print(C1['individual']['result_employ_allocation'])
    # print(C2['individual']['result_employ_allocation'])
    # print(f"负责检查继承自P1和P2的编码有没有问题")
    # check_result_employ_allocation(C1['individual']['result_employ_allocation'],23)
    # check_result_employ_allocation(C2['individual']['result_employ_allocation'],23)


    C1,C2=crossover_OR_FMX_ONE_POINT(P1,P2,C1,C2)
    # C1,C2=adjust_op(C1,C2,replace_op)
    C1,C2=crossover_other_FMX_two_point(P1,P2,C1,C2)



    # 调整不符合约束的编码,单个编码调整
    C1=adjust_individual(C1,data)

    check_wk_ma(C1['individual']['workstation_machines'], 23)
    check_adjust_workstation(C1['individual']['workstation_code'], 23)
    check_result_employ_allocation(C1['individual']['result_employ_allocation'], 23)
    check_adjust_employ(C1['individual']['employ_code'], 23)

    C2=adjust_individual(C2,data)
    check_wk_ma(C2['individual']['workstation_machines'], 23)
    check_adjust_workstation(C2['individual']['workstation_code'], 23)
    check_result_employ_allocation(C2['individual']['result_employ_allocation'], 23)
    check_adjust_employ(C2['individual']['employ_code'], 23)

    return C1,C2

def crossover_OR_FMX_ONE_POINT(P1,P2,C1,C2):
    """"
    单点交叉
    -P1:父代1
    -P2:父代2
    """

    # 随机选择交叉点，确保选择一个有效的索引
    cross_point = random.randint(0, len(P1['individual']['OR_CODE']))  # 选择0到2之间的一个位置

    # 进行单点交叉
    C1['individual']['OR_CODE']=P1['individual']['OR_CODE'][:cross_point]+P2['individual']['OR_CODE'][cross_point:]
    C2['individual']['OR_CODE']=P2['individual']['OR_CODE'][:cross_point]+P1['individual']['OR_CODE'][cross_point:]

    return C1,C2

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
            C1['individual'][key] = P1['individual'][key][:cross_point2] + P2['individual'][key][cross_point2:cross_point1] + P1['individual'][key][cross_point1:]
            C2['individual'][key] = P2['individual'][key][:cross_point2] + P1['individual'][key][cross_point2:cross_point1] + P2['individual'][key][cross_point1:]

        # C1['individual']['operation_code']=P1['individual']['operation_code'][:cross_point2]+P2['individual']['operation_code'][cross_point2:cross_point1]+P1['individual']['operation_code'][cross_point1:]
        # C1['individual']['machine_code']=P1['individual']['machine_code'][:cross_point2]+P2['individual']['machine_code'][cross_point2:cross_point1]+P1['individual']['machine_code'][cross_point1:]
        # C1['individual']['balance_code']=P1['individual']['balance_code'][:cross_point2]+P2['individual']['balance_code'][cross_point2:cross_point1]+P1['individual']['balance_code'][cross_point1:]
        # C1['individual']['operation_code']=P1['individual']['operation_code'][:cross_point2]+P2['individual']['operation_code'][cross_point2:cross_point1]+P1['individual']['operation_code'][cross_point1:]
        # C1['individual']['workstation_code']=P1['individual']['workstation_code'][:cross_point2]+P2['individual']['workstation_code'][cross_point2:cross_point1]+P1['individual']['workstation_code'][cross_point1:]
        # C1['individual']['employ_code']=P1['individual']['employ_code'][:cross_point2]+P2['individual']['employ_code'][cross_point2:cross_point1]+P1['individual']['employ_code'][cross_point1:]

    else:
        # print("else")
        for key in keys:
            C1['individual'][key] = P1['individual'][key][:cross_point1] + P2['individual'][key][cross_point1:cross_point2] + P1['individual'][key][cross_point2:]
            C2['individual'][key] = P2['individual'][key][:cross_point1] + P1['individual'][key][cross_point1:cross_point2] + P2['individual'][key][cross_point2:]
        # C1=P1['individual'][:cross_point1]+P2['individual'][cross_point1:cross_point2]+P1['individual'][cross_point2:]
        # C2=P2['individual'][:cross_point1]+P1['individual'][cross_point1:cross_point2]+P2['individual'][cross_point2:]

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

# def adjust_workstation_machine(child):
#     # print(f"170170")
#     # print(child)
#     # print("----------------------------------------------")
#     # 这个编码可能有缺失，所以要调整
#     wk=child['individual']['workstation_code']
#
#     # check_num,tem_wk_num=check_adjust_workstation(wk,23)
#
#     # 获取每个工作站对应的机器：{'R1': 'A', 'R7': 'A'}
#     workstation_machines = child['individual']['workstation_machines']
#     print(f"开始检查")
#     check_wk_ma(workstation_machines,23)
#     # print(f"workstation_machines{workstation_machines}")
#
#     # 将所有工作站从嵌套列表中提取出来，变成一个一维列表 提取出交叉后子代的工作站编码，这时候的工作站编码会缺失一些
#     # 获取交叉后的wk编码（有缺失），将其提取出来，看是否会有缺失
#     # {'L2', 'R10', 'L9', 'L6', 'R3', 'L7', 'R4', 'R9', 'L1', 'R8', 'R5', 'R2', 'L10', 'L11', 'L3', 'L8', 'R11', 'R12', 'L5', 'R6'}
#     assigned_workstations = set(workstation for sublist in wk for workstation in sublist)
#
#     # 获取所有的工作站，workstation_machines中出现的工作站
#     all_workstations = set(workstation_machines.keys())
#
#
#     # 获取没有分配的工作站
#     missing_workstations = list(all_workstations - assigned_workstations)
#     print(f"190190")
#     print(f"workstation_machines{workstation_machines}")
#     print(f"获取所有的工作站{all_workstations}")
#     print(f"现有的工作站，即交叉后子代的编码，这时候有缺失{assigned_workstations}")
#     # print(tem_wk_num)
#     print(f"没有分配的工作站{missing_workstations}")
#
#     # 当前个体需要的机器
#     machine_codes = child['individual']['machine_code']
#     machine_codes_set = set(machine_codes)
#     print(f"当前个体需要的机器{machine_codes_set}")
#     # print(f"当前个体需要的机器machine_codes{machine_codes_set}")
#
#     # 获取 workstation_machines 中所有的机器类型
#     workstation_machines_values = set(workstation_machines.values())
#     print(f"原编码中的机器类型{workstation_machines_values}")
#
#     # 找出 workstation_machines 中出现，但 machine_codes 中没有的机器类型
#     # 有五种可能！！！
#     unused_machines = workstation_machines_values - machine_codes_set
#     print(f"原编码中的机器类型-先编码的机器类型，{unused_machines}")
#
#
#     # 获取所有机器类型的工作站
#     stations_using_machine = {}
#     for machine in set(machine_codes):
#         stations_using_machine[machine] = [station for station, m in workstation_machines.items() if m == machine]
#     print(f"获取该编码所有机器类型对应的工作站stations_using_machine{stations_using_machine}")
#
#     # 检查哪些机器类型已经分配到工作站
#     assigned_machines = set(m for station in assigned_workstations for station, m in workstation_machines.items() if station in assigned_workstations)
#     print(f"检查该编码哪些机器分配到工作站了{assigned_machines}")
#     # print(f"assigned_machines{assigned_machines}")
#
#     # 找出当前个体缺失的机器，即调整后该编码需要的机器-当前未调整的编码中已经分配了工作站的机器
#     missing_machines = set(machine_codes) - assigned_machines
#     print(f"当前缺失的机器{missing_machines}")
#     # print(f"当前缺失的机器！！！")
#     if missing_machines==set():
#         print(f"当前没有缺失机器")
#
#     # 处理交叉后没有的机器，即占用别的机器位置的机器
#     if unused_machines:
#         print("有问题，但是有时跑不出来！！！！！！")
#         print(f"215hang")
#         for i in unused_machines:
#             if i in stations_using_machine:
#                 tem_unused_wk=stations_using_machine[unused_machines]
#                 # 将这些工作站添加到 missing_workstations 中
#                 missing_workstations.extend(stations_using_machine)
#             # 删除 stations_using_machine 中对应机器的工作站数据
#             for station in stations_using_machine:
#                 if station in workstation_machines:
#                     del workstation_machines[station]  # 删除工作站对应的机器
#
#
#     # 用来记录跳过的工作站，稍后进行处理
#     pending_workstations = []
#
#     for i in range(len(wk)):
#         machine=machine_codes[i]
#         tem_balance=child['individual']['balance_code'][i]
#         op=child['individual']['operation_code'][i]
#
#         # 如果当前机器属于未分配的机器
#         if machine in missing_machines:
#             # 遍历当前个体原来的工作站
#             for j in range(len(wk[i])):
#                 tem_workstation=wk[i][j] #当前工作站
#                 # print(f"tem_workstation{tem_workstation}")
#                 # 如果当前个体工作站配对的机器不等于该工序所需要的机器
#                 if workstation_machines.get(tem_workstation) != machine:
#                     # 如果 tem_workstation 不匹配，随机选择一个替代
#                     # print(f"工作站 {tem_workstation} 的机器类型与 {machine} 不匹配，随机选择一个替换...")
#                     # 如果当前存在未分配的工作站
#                     if missing_workstations:
#                         tem_arr = wk[i][j]
#                         chosen_station=random.choice(missing_workstations)
#                         # 修改workstation_code的值
#                         child['individual']['workstation_code'][i][j]=chosen_station
#                         # 这个工作站分配完后就从未分配中删除
#                         missing_workstations.remove(chosen_station)
#                         # print(f"missing_workstations{missing_workstations}")
#                         # 修改workstation_machines中该工作站对应机器的值
#                         child['individual']['workstation_machines'][chosen_station]=machine
#                         # 判断原本的工作站是否还有分配给别的工序，如果没有的话就加入未分配中
#                         # 将所有工作站从嵌套列表中提取出来，变成一个一维列表
#                         # assigned_workstations_tem = set(workstation for sublist in child['individual']['workstation_code'] for workstation in sublist)
#                         assigned_workstations_tem = set()
#                         for sublist in child['individual']['workstation_code']:
#
#                             for workstation in sublist:
#                                 print(f"276276")
#                                 print(workstation)
#                                 assigned_workstations_tem.add(workstation)
#
#                         if tem_arr not in assigned_workstations_tem:
#                             missing_workstations.append(tem_arr)
#                     else:
#                         # 如果没有缺失工作站，记录下当前需要处理的工作站，稍后处理
#                         # print("!!!!!!!!!!!!!!!!!!!!!!")
#                         # print(f"当前工作站是{tem_workstation}")
#                         # 将当前工作站的值赋为空
#                         child['individual']['workstation_code'][i][j]=[]
#                         print("assigned_workstations_tem")
#                         # 之后判断tem_workstation是否有分配到其他工序，即是否还有在workstation_code中出现，没有的话就加入missing_workstations
#
#                         assigned_workstations_tem = set()
#                         # for sublist in child['individual']['workstation_code']:
#                         #     for workstation in sublist:
#                         #         if isinstance(workstation, list):
#                         #             print(f"workstation{workstation}")
#                         #
#                         #             assigned_workstations_tem.add(workstation)
#                         #         else:
#                         #             assigned_workstations_tem = set( workstation for sublist in child['individual']['workstation_code'] for workstation in sublist)
#
#                         # assigned_workstations_tem = set()
#                         for sublist in child['individual']['workstation_code']:
#                             for workstation in sublist:
#                                 # print("assigned_workstations_tem")
#                                 # print(f"workstation{workstation}")
#                                 if not workstation:
#                                     continue
#                                 else:
#                                     assigned_workstations_tem.add(workstation)
#
#                         if tem_workstation not in assigned_workstations_tem:
#                             missing_workstations.append(tem_workstation)
#                         # print(f"工序{op}机器 {machine} 对应的工作站暂时未分配，跳过该工序，该工序的人力平衡是{tem_balance}")
#                         pending_workstations.append({'op': op, 'machine': machine, 'tem_balance': tem_balance})
#         else:
#             # 当前机器已经分配过了，即没有未分配的机器
#             for j in range(len(wk[i])):
#                 # print(f"wk[i][j]{wk[i][j]}")
#                 if wk[i][j] not in stations_using_machine[machine]:
#                     # print("说明机器跟工作站不匹配")
#                     # print(f"stations_using_machine[machine]{stations_using_machine[machine]}")
#                     if missing_workstations:
#                         # print(f"还有未分配的工作站")
#                         tem_arr=wk[i][j]
#                         chosen_station = random.choice(missing_workstations)
#                         # 修改workstation_code的值
#                         child['individual']['workstation_code'][i][j]=chosen_station
#                         # 删除已经选中的工作站
#                         missing_workstations.remove(chosen_station)
#                         # 修改workstation_machines中的值
#                         child['individual']['workstation_machines'][chosen_station] = machine
#                         # assigned_workstations_tem = set(workstation for sublist in child['individual']['workstation_code'] for workstation in sublist)
#                         assigned_workstations_tem = set()
#                         for sublist in child['individual']['workstation_code']:
#                             for workstation in sublist:
#                                 assigned_workstations_tem.add(workstation)
#
#                         if tem_arr not in assigned_workstations_tem:
#                             missing_workstations.append(tem_arr)
#                     else:
#                         # print(f"没有未分配的机器")
#                         wk[i][j]=random.choice(stations_using_machine[machine])
#                         child['individual']['workstation_code'][i][j] = wk[i][j]
#
#
#     if pending_workstations:
#         current_workstations=[]
#         # print(f"有未处理的工序{pending_workstations}！！！！！！！！！！！！！！！！！！！！！！！！")
#         for pending in pending_workstations:
#             op = pending['op']
#             machine = pending['machine']
#             tem_balance = pending['tem_balance']
#             # 确认当前机器是否存在于 stations_using_machine 中
#             if machine in stations_using_machine:
#                 # 找到所有机器对应的工作站列表长度大于等于 tem_balance 的机器
#                 machines_with_sufficient_workstations = [machine for machine, workstations in stations_using_machine.items() if len(workstations) >= tem_balance]
#
#                 for i in range(tem_balance):
#                     # print(f"机器对应长度大于{tem_balance}的数据{machines_with_sufficient_workstations}")
#                     # 随机选择一个机器其工作站的值大于tem_balance
#                     selected_machine = random.choice(machines_with_sufficient_workstations)
#                     # print(f"selected_machine{selected_machine}")
#                     # print(f"这个机器对应的工作站值是{stations_using_machine[selected_machine]}")
#
#                     # 随机从这个机器对应的工作站中选择一个
#                     selected_wk=random.choice(stations_using_machine[selected_machine])
#                     # 将选择的工作站添加到现在机器对应的值中
#                     stations_using_machine[machine].append(selected_wk)
#                     # 添加到current_workstations，后面将current_workstations赋值给该位置的工序
#                     current_workstations.append(selected_wk)
#                     # 将选择的工作站从原来的机器中溢出
#                     stations_using_machine[selected_machine].remove(selected_wk)
#                     # 修改workstation_machines中的值
#                     child['individual']['workstation_machines'][selected_wk] = machine
#
#                     # 找到该工序对应的索引
#                 op_index = child['individual']['operation_code'].index(op)
#                 # 将原来交叉后的工作站值修改
#                 child['individual']['workstation_code'][op_index] = current_workstations
#                 # print(child['individual']['workstation_code'][op_index])
#                 # child['individual']['workstation_machine']=
#
#
#     # 如果还有未分配的工作站
#     if missing_workstations:
#         # 提取出所有工作站，展平嵌套列表
#         workstations_in_code = set(workstation for sublist in child['individual']['workstation_code'] for workstation in sublist)
#         # 获取 workstation_machines 中的所有工作站
#         workstations_in_machines = set(workstation_machines.keys())
#
#         # print(f"workstations_in_code{workstations_in_code}")
#         # print(f"workstations_in_machines{workstations_in_machines}")
#
#
#         # 比较两个集合，确保工作站都存在
#         if workstations_in_code == workstations_in_machines:
#             print("所有工作站都匹配")
#             print(f"383")
#             print(f"workstations_in_code{workstations_in_code}")
#             print(f"workstations_in_machines{workstations_in_machines}")
#
#         else:
#             print("有工作站未匹配")
#             print(f"缺失的工作站{workstations_in_code - workstations_in_machines}")
#     # print("--------------------------------")
#     # print("最后调整的结果是：")
#     # print(child['individual']['workstation_code'])
#     # print("--------------------------------")

# def adjust_employ(child):
#     check_adjust_workstation(child['individual']['workstation_code'],23)
#     print(f"交叉后的员工编码")
#     # print(child['individual']['result_employ_allocation'])
#     print(child['individual']['workstation_code'])
#
#     for i,wk in enumerate(child['individual']['workstation_code']):
#         current_workstation = child['individual']['workstation_code'][i]
#         op=child['individual']['operation_code'][i]
#         tem_employ=child['individual']['employ_code'][i]
#         # print(f"tem_employ{tem_employ}")
#         if len(tem_employ)>1:
#             # print(f"该工序分配给多个工作站")
#             for j in range(len(tem_employ)):
#                 current_workstation=child['individual']['workstation_code'][i][j]
#                 if tem_employ[j]['employ']:
#                     current_employ=tem_employ[j]['employ']
#                 else:
#                     print(f"这个工作站是新分配上去的，需要补充员工")
#                 # 查找 result_employ_allocation 中匹配的工作站数据
#                 allocation = next((item for item in child['individual']['result_employ_allocation'] if item['workstation'] == current_workstation), None)
#                 print(f"allocation{allocation}")
#                 if allocation:
#                     # 获取 result_employ_allocation 中该工作站的正确员工编号
#                     correct_employ = allocation['employ']
#                     print(f"correct_employ{correct_employ}")
#
#                     # 如果员工编号不匹配，修改 employ_code 数据
#                     if current_employ != correct_employ:
#
#                         child['individual']['employ_code'][i][j]['employ'] = correct_employ
#
#                 else:
#                     # print(f"")
#                     print(f"未找到工作站 {wk} 的分配数据，跳过处理。")
#                     continue
#
#         else:
#             # print(f"该工序只分配给1个工作站")
#             current_employ=tem_employ[0]['employ']
#             # 查找 result_employ_allocation 中匹配的工作站数据
#             allocation = next((item for item in child['individual']['result_employ_allocation'] if item['workstation'] == current_workstation), None)
#             print(f"allocation{allocation}")
#             if allocation:
#                 # 获取 result_employ_allocation 中该工作站的正确员工编号
#                 correct_employ = allocation['employ']
#                 # print(f"correct_employ{correct_employ}")
#
#                 # 如果员工编号不匹配，修改 employ_code 数据
#                 if current_employ != correct_employ:
#                     child['individual']['employ_code'][i] = correct_employ
#                     print(f"434")
#                     print(child['individual']['employ_code'][i])
#     # print(f"439最后输出看看child")
#     # print(child)

def adjust_employ_code(individual):
    print(f"482482")
    print(f"individual{individual}")
    check_wk_ma(individual['individual']['workstation_machines'],23)
    check_adjust_workstation(individual['individual']['workstation_code'],23)
    # workstation_code = individual['individual']['workstation_code']
    # employ_code = individual['individual']['employ_code']
    result_employ_allocation = individual['individual']['result_employ_allocation']
    check_result_employ_allocation(result_employ_allocation,23)
    # print(f"当前的result_employ_allocation is:{result_employ_allocation}")
    # check_result_employ_allocation(result_employ_allocation,23)
    # 将 result_employ_allocation 处理成字典 {workstation: employ}
    # employ_mapping = {entry['workstation']: entry['employ'] for entry in result_employ_allocation}

    # 使用字典来存储每个 workstation 最后的 employ 值
    employ_mapping = {}
    unique_entries1=set()
    # 记录已分配的 workstations 和 employs
    workstation_to_employ = {}  # 记录每个工作站对应的 employ
    employ_to_workstations = {}  # 记录每个 employ 分配的工作站

    # 这里有问题
    for entry in result_employ_allocation:
        workstation_code=entry['workstation']
        employ=employ = entry['employ']
        entry_tuple = (entry['workstation'], entry['employ'])

        # **检测冲突1：同一工作站不能分配不同的 employ**
        if workstation_code in workstation_to_employ and workstation_to_employ[workstation_code] != employ:
            raise ValueError(
                f"冲突❌: 工作站 {workstation_code} 已分配给 employ {workstation_to_employ[workstation_code]}，不能再分配给 {employ}")

        # **检测冲突2：同一个 employ 不能分配到不同的工作站**
        if employ in employ_to_workstations and workstation_code not in employ_to_workstations[employ]:
            raise ValueError(
                f"冲突❌: employ {employ} 已分配到 {employ_to_workstations[employ]}，不能再分配到 {workstation_code}")

        # **记录数据**
        unique_entries1.add(entry_tuple)
        employ_mapping[workstation_code] = employ

        # 更新映射
        workstation_to_employ[workstation_code] = employ
        if employ not in employ_to_workstations:
            employ_to_workstations[employ] = set()
        employ_to_workstations[employ].add(workstation_code)

        # if entry_tuple not in unique_entries1:
        #     unique_entries1.add(entry_tuple)
        # employ_mapping[workstation_code]=employ

    print(f"111employ_mapping{employ_mapping}")
    print(f"workstation_code{individual['individual']['workstation_code']}")
    for i,wk_list in enumerate(individual['individual']['workstation_code']):
        # print(f"workstation_code{individual['individual']['workstation_code']}")
        print(f"wk_list{wk_list}")
        wk_len=len(wk_list)
        employ_len=len(individual['individual']['employ_code'][i])
        print(f"wk_len{wk_len}")
        print(f"employ_len{employ_len}")
        print(f"需要补充：")
        print(wk_len - employ_len)
        # 修改长度
        if wk_len>employ_len:
            print(f"修改长度，增加")
            # 说明employ_code这个位置需要补充的
            individual['individual']['employ_code'][i].extend([{'workstation': '', 'employ': ''}] * (wk_len - employ_len))
            print(individual['individual']['employ_code'][i])
        elif wk_len<employ_len:
            print(f"修改长度，减少")
            individual['individual']['employ_code'][i] = individual['individual']['employ_code'][i][:wk_len]
            print(individual['individual']['employ_code'][i])

        for j,wk in enumerate(wk_list):
            print(f"开始遍历")
            print(wk)
            print(individual['individual']['employ_code'][i][j])
            if wk == individual['individual']['employ_code'][i][j]['workstation']:
                print(f"557557")
                # 如果员工编号也对上的话
                if wk in employ_mapping and employ_mapping[wk] == individual['individual']['employ_code'][i][j]['employ']:
                    print(f"*******111111")
                    print(f"查找wk对应的员工{employ_mapping[wk]}")
                    print(f"当前编码对应的员工{individual['individual']['employ_code'][i][j]['employ']}")
                    print(f'配对成功')
                else:
                    # print(f"+++++++++")
                    print(f"*******111222")

                    print(f"查找wk对应的员工{employ_mapping[wk]}")
                    print(f"当前编码对应的员工{individual['individual']['employ_code'][i][j]['employ']}")
                    individual['individual']['employ_code'][i][j]['employ'] = employ_mapping[wk]
                    print(individual['individual']['employ_code'][i][j])
                    print(f"564564")
            else:
                print(f"*******222222")
                print(f'当前编码的工作站错误')
                print(f"563563")
                # print(f"查找wk对应的员工{employ_mapping[wk]}")
                # print(f"当前编码对应的员工{individual['individual']['employ_code'][i][j]['employ']}")
                print(f"workstation_code中的工作站是{wk}")
                print(f"当前employ_code编码的工作站是{individual['individual']['employ_code'][i][j]['workstation']}")
                # 说明工作站不匹配
                current_wk = wk
                current_employ = employ_mapping[wk]
                individual['individual']['employ_code'][i][j] = {'workstation': current_wk, 'employ': current_employ}
                print(f"当前工序对应的员工编码{employ_mapping[wk]}")
                print(individual['individual']['employ_code'][i])
                print(wk_list)

    print(f"workstation_code{individual['individual']['workstation_code']}")
    print(f"employ_code{individual['individual']['employ_code']}")
    print(f"222employ_mapping{employ_mapping}")
    check_adjust_employ(individual['individual']['employ_code'],23)
    check_result_employ_allocation(individual['individual']['result_employ_allocation'],23)
    return individual

def adjust_individual(child,data):
    # 单个编码调整
    # 先调整or_code和op_code
    tem_data,right_operation_codes=adjust_op(child,data)
    current_operation_codes=child['individual']['operation_code'].copy()

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
                removed_positions.append({'idx':idx, 'op':op})  # 如果元素重复，记录它的索引

        # 获取去重后的工序列表
        unique_operations = list(ordered_dict.keys())

        # 找出 right_operation_codes 中那些不在 C1['individual']['operation_code'] 中的工序
        missing_operations = [op for op in right_operation_codes if op not in unique_operations]
        # print(f"missing_operations{missing_operations}")

        if int(len(missing_operations))+int(len(unique_operations))!=int(len(right_operation_codes)):
            # print("不仅重复，还出现了占用工序")
            for missing_op in missing_operations:
                replaced=False
                op_num = int(missing_op.split(',')[1])  # 获取操作编码中的工序

                for operation_pair in child['individual']['replace_op']:
                    if op_num in operation_pair:
                        # print("缺失的工序有替代工序")
                        # 缺失工序的替代工序
                        repalce_tem_op=[op for op in operation_pair if op != op_num]
                        for op in repalce_tem_op:
                            for i, current_op in enumerate(current_operation_codes):
                                # 找到了替换工序所在位置
                                if op == int(current_op.split(',')[1]):
                                    # 调整工序
                                    current_operation_codes[i] = missing_op
                                    # child['individual']['workstation_code'][]
                                    # 调整机器
                                    child['individual']['machine_code'][i] = data[data['工序'] == int(op)]['机器'].values[0]
                                    replaced=True
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
                current_operation_codes[removed_positions[0]['idx']]=missing_operations[0]
                child['individual']['operation_code']=current_operation_codes

                # 调整工序对应机器
                child['individual']['machine_code'][removed_positions[0]['idx']] = data[data['工序'] == int(missing_operations[0].split(',')[1])]['机器'].values[0]

                # 调整工序对应工作站
                tem_balance=child['individual']['balance_code'][removed_positions[0]['idx']]
            else:
                # 直接赋值，无须调整
                child['individual']['operation_code']=current_operation_codes


        else:
            # 调整工序
            current_operation_codes[removed_positions[0]['idx']]=missing_operations[0]
            child['individual']['operation_code']=current_operation_codes

            # 调整对应机器
            child['individual']['machine_code'][removed_positions[0]['idx']]=data[data['工序']==int(missing_operations[0].split(',')[1])]['机器'].values[0]
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
        child['individual']['operation_code']=current_operation_codes

    # 调整人力平衡
    child=generate_new_balance(child,tem_data)

    # 根据人力平衡调整工作站编码
    child=adjust_workstation(child)

    check_adjust_workstation(child['individual']['workstation_code'], 23)

    # 调整员工编码
    # adjust_employ(child)

    child=adjust_employ_code(child)


    print("所有编码都调整好了")
    check_adjust_workstation(child['individual']['workstation_code'], 23)
    check_result_employ_allocation(child['individual']['result_employ_allocation'], 23)
    check_adjust_employ(child['individual']['employ_code'], 23)
    check_wk_ma(child['individual']['workstation_machines'], 23)

    return child

# def adjust_workstation(individual):
#     print(f'608608')
#     print(f"individual{individual}")
#     new_machine=individual['individual']['machine_code'] #新的机器编码
#     print(f"new_machine{new_machine}")
#     old_workstation_code=individual['individual']['workstation_code']  #旧的工作站编码
#     old_workstation_machine=individual['individual']['workstation_machines'] #旧的工作站：机器匹配编码
#     unique_need_machine=set(new_machine)
#     print(f"unique_need_machine{unique_need_machine}")
#
#     old_machine=set(old_workstation_machine.values())
#     print(f"old_machine{old_machine}")
#
#     print(f"old_workstation_code{old_workstation_code}")
#     print(f"old_workstation_machine{old_workstation_machine}")
#
#     new_has_old_hasnt=unique_need_machine-old_machine
#     old_has_new_hasnt=old_machine-unique_need_machine
#
#     # 如果新编码需要的机器跟旧的一样的话
#     if unique_need_machine==old_machine:
#         print(f"11111")
#         print(f"说明新旧编码需要的机器都一致")
#         print(f"new_has_old_hasnt{new_has_old_hasnt}")
#         print(f"old_has_new_hasnt{old_has_new_hasnt}")
#         # 但是不能保证工作站分配没问题哦！但是无需调整machines_workstations,因为需要的机器跟原来一样，说明工作站：机器匹配正确
#
#         machines_to_workstations = defaultdict(list)
#         # 遍历原字典，将键值对翻转
#         for workstation, machine in individual['individual']['workstation_machines'].items():
#         # for workstation, machine in old_workstation_machine.items():
#             machines_to_workstations[machine].append(workstation)
#
#         # 将 defaultdict 转换为普通字典（可选）
#         machines_to_workstations = dict(machines_to_workstations)
#         print(f"eeeeeeeeeeeeee")
#         # print()
#         check_machines_to_workstations(machines_to_workstations,23)
#         individual=choose_workstation(individual,machines_to_workstations)
#     else:
#         print(f"22222")
#         print(f"新旧编码不相同")
#         # 用 defaultdict 来按机器类型分类
#         machines_to_workstations = defaultdict(list)
#         # 遍历 old_workstation_machine 字典，按机器类型分类
#         for station, machine in old_workstation_machine.items():
#             machines_to_workstations[machine].append(station)
#         # print(f"dddddddddd")
#         # check_wk_ma2(machines_to_workstations,23)
#         # 说明新旧的机器编码有不同
#         # 如果新的编码有但是旧的编码没有，说明新增了机器
#         if new_has_old_hasnt!=set():
#             print(f"22222!11111")
#             print(f"640640")
#             print(f"new_has_old_hasnt{new_has_old_hasnt}")
#             # 检查旧的编码中有没有新的编码中没有的机器
#             # 说明旧的编码为空，没有新的编码没有的机器，这个只需要将新编码中多的机器添加进去
#             if old_has_new_hasnt==set():
#                 print(f"22222!11111!11111")
#                 print(f'650650')
#                 for wk in new_has_old_hasnt:
#                     machines_to_workstations[wk]=[]
#                 # machines_workstations=machines_workstations_code(individual,machines_workstations)
#                 print(f"cccccccccccc")
#                 check_machines_to_workstations(machines_to_workstations, 23)
#                 individual,machines_to_workstations=adjust_machines_workstations_code(individual, machines_to_workstations)
#                 individual=choose_workstation(individual,machines_to_workstations)
#                 # print(f"machines_workstations{machines_workstations}")
#             else:
#                 print(f"22222！11111！22222")
#                 # 说明旧的编码有新的编码没有的机器,即新编码和旧编码有交集,删除旧的，添加新的
#                 print(f"说明旧的编码有新的编码没有的机器")
#                 print(f"old_has_new_hasnt{old_has_new_hasnt}")
#                 print(f"1111****************")
#                 print(f"machines_to_workstations{machines_to_workstations}")
#                 for wk in new_has_old_hasnt:
#                     machines_to_workstations[wk]=[]
#                 new_value=[]
#                 for key in old_has_new_hasnt:
#                     if key in machines_to_workstations:
#                         new_value.extend(machines_to_workstations[key])
#                 for key in old_has_new_hasnt:
#                     machines_to_workstations.pop(key,None)
#                 empty_keys=[k for k, v in machines_to_workstations.items() if not v] #如果键对应的值是None或者是空列表，就取出来
#                 # sorted(machines_workstations.keys(), key=lambda k: len(machines_workstations[k]))
#                 print(f"2222****************")
#                 print(f"machines_to_workstations{machines_to_workstations}")
#                 # 2. 逐个分配 new_value
#                 for workstation in new_value:
#                     if empty_keys:
#                         key = empty_keys.pop(0)  # 先分配给空的键，按顺序取出
#                     else:
#                         key = random.choice(list(machines_to_workstations.keys()))  # 随机分配给已有的键
#                     machines_to_workstations[key].append(workstation)  # 进行分配
#                 print(f"bbbbbbbbbbbbb")
#                 individual,machines_to_workstations=adjust_machines_workstations_code(individual, machines_to_workstations)
#                 individual=choose_workstation(individual, machines_to_workstations)
#         else:
#             print(f"22222！22222")
#             # 旧的编码包含了新的编码
#             # 说明是旧的编码中有新的编码中没有的机器，因此需要去掉旧的编码中的机器，将其所分配的工作站分配给别人
#             print(f"645")
#             print(f"旧的编码包含了新的编码")
#             print(f"old_has_new_hasnt{old_has_new_hasnt}")
#             print(f"new_has_old_hasnt{new_has_old_hasnt}")
#             # 1. 先获取 H 和 C 的值并合并
#             new_value = []
#             for key in old_has_new_hasnt:
#                 if key in machines_to_workstations:
#                     new_value.extend(machines_to_workstations[key])  # 合并值
#
#             # 2. 删除 H 和 C
#             for key in old_has_new_hasnt:
#                 machines_to_workstations.pop(key, None)  # 避免 KeyError
#
#             # 1. 按照已有的工作站数量排序，获取最少的键
#             sorted_keys = sorted(machines_to_workstations.keys(), key=lambda k: len(machines_to_workstations[k]))
#
#             for workstation in new_value:
#                 key = sorted_keys.pop(0)  # 选择当前值最少的键，并从列表移除
#                 machines_to_workstations[key].append(workstation)  # 分配工作站
#                 sorted_keys = sorted(machines_to_workstations.keys(), key=lambda k: len(machines_to_workstations[k]))  # 重新排序
#             print(f"aaaaaaaaaaa")
#             # 调整workstations_machines值以进行下一部调整工作站，但是调整完之后的workstation_machines还需要修改
#             individual,machines_to_workstations= adjust_machines_workstations_code(individual, machines_to_workstations)
#             individual=choose_workstation(individual, machines_to_workstations)
#     check_adjust_workstation(individual['individual']['workstation_code'],23)
#     check_wk_ma(individual['individual']['workstation_machines'],23)
#     return individual



def adjust_machines_workstations_code(individual,machines_workstations):
    # 这里有问题！！！！！！！！！！！！！！ workstation_code不对的话就是这里有问题
    print(f"952952")
    print(f"machines_workstations{machines_workstations}")
    tem_give_wk=[] #这是可以分一部分工作站出去的机器
    tem_need_wk=[] #这是要补一部分工作站进来的机器
    # 调整machines_workstations这个编码，这个编码原来是直接继承了父代的，里面的机器不一定对，但是工作站的数量和值应该是没问题的
    # 根据balance_code进行调整，少的补，但是多的不减
    old_balance=individual['individual']['balance_code']
    machine=individual['individual']['machine_code']
    tem_workstation_machines = {}  # 存储更新后的工作站-机器映射

    # 创建一个字典来存储 machine 对应的 balance 之和
    balance_sum = defaultdict(int)
    # 遍历 machine 和 balance，累加对应 machine 的 balance 值
    # 这是调整后的编码新的人力平衡（新的），‘机器’：数量
    for m, b in zip(machine, old_balance):
        balance_sum[m] += b
    print(f"balance_sum")
    # print(dict(balance_sum))

    # 这是旧的人力平衡的编码，将其变成‘机器’：数量的方式
    machine_lengths={key: sum(1 for item in value if item) for key, value in machines_workstations.items()}
    # print(f"machine_lengths{machine_lengths}")
    # 找出‘值’不相等的键  Eg:{'B': (3, 4), 'D': (2, 1)}前面的是需要的，后面是现有的
    differences = {key: (balance_sum[key], machine_lengths[key]) for key in balance_sum if balance_sum.get(key) != machine_lengths.get(key)}
    print(f"differences{differences}")

    for key,value in differences.items():
        print(f"key{key}")
        print(f"value{value}")
        # 如果现有的比需要的多
        if value[1]>value[0]:
            tem_b=value[1]-value[0]
            tem_give_wk.append({key:tem_b}) #机器:可以给出去的数量
        elif value[1]<value[0]: #如果现有的比需要的少
            tem_b = value[0] - value[1]
            tem_need_wk.append({key:tem_b}) #机器:需要的数量
    print(f"tem_give_wk{tem_give_wk}")
    print(f"tem_need_wk{tem_need_wk}")

    # 如果需要补充的机器存在的话
    if tem_need_wk:
        print(tem_need_wk)
        for dictionary in tem_need_wk:
            for key ,value in dictionary.items():
                # print(f"742742")
                print(f"key{key}")
                print(f"value{value}")
                # 循环添加机器，
                for i in range(int(value)):
                    print(f"tem_give_wk{tem_give_wk}")
                    # 随机从可以提供的机器中补充，按照需要补充的次数遍历
                    if tem_give_wk:
                        selected_item=random.choice(tem_give_wk)
                        # 修改selected_item
                        # 在这里修改工作站！！！
                        for key1, value1 in selected_item.items():
                            # key1是机器，value1是它对应的工作站
                            # 在这里修改工作站！！！
                            # 在这个机器分配的工作站中选择一个工作站
                            select_wk = random.choice(machines_workstations[key1])
                            # 将选择的工作站赋给新的机器
                            machines_workstations[key].append(select_wk)
                            # 将这个原来工作站所在的机器的位置中删掉
                            machines_workstations[key1].remove(select_wk)
                            new_value = int(value1) - 1
                            # 将这个补充出去的机器先从原来的集合删除，修改它的可以供给的值，即减1，之后再放进去
                            tem_give_wk.remove(selected_item)
                            tem_give_wk.append({key1: new_value})
                            print(f'816816修改后的tem_give_wk{tem_give_wk}')
                            # 如果它的值小于等于0，说明它没有可供给的，那就
                            if new_value <= 0:
                                tem_give_wk = [item for item in tem_give_wk if item != {key1: new_value}]
                            # if tem_give_wk:
                            #     continue
                            # else:
                            #     break
                    else:
                        # 随机选择一个策略 0表示不添加了，之后过，1表示从别的工作站中拿一个过来
                        strategy=random.choice([0, 1])
                        has_empty = any(len(v) == 0 for v in machines_workstations.values())
                        max_key = max(machines_workstations, key=lambda k: len(machines_workstations[k]))
                        max_value = machines_workstations[max_key]
                        if has_empty:
                            # 必须从别的工作站中取出一个
                            c_wk=random.choice(max_value)
                            machines_workstations[key].append(c_wk) #添加到这个机器中
                            machines_workstations[max_key].remove(c_wk) #从原来的机器中删除
                        else:
                            if strategy==0:
                                print(f"不做更改")
                            elif strategy==1:
                                c_wk = random.choice(max_value)
                                machines_workstations[key].append(c_wk)  # 添加到这个机器中
                                machines_workstations[max_key].remove(c_wk)  # 从原来的机器中删除

    print(f"————————————————————————sign")

    has_empty = any(len(v) == 0 for v in machines_workstations.values())
    if has_empty:
        print("是否存在空值:", has_empty)
        raise ValueError("有空值")

    # 反转键值
    reversed_dict = {station: machine for machine, stations in machines_workstations.items() for station in stations}
    # 按键排序
    sorted_reversed_dict = dict(sorted(reversed_dict.items(), key=lambda x: x[0]))
    print(f"sorted_reversed_dict{sorted_reversed_dict}")
    individual['individual']['workstation_machines']=sorted_reversed_dict

    print(f"!!!!!!!!!!!!!!@@@@@@@@@@@@@@")
    check_wk_ma(individual['individual']['workstation_machines'],23)
    return individual,machines_workstations

def choose_workstation(individual,machines_workstations):
    print(f"888888choose_workstation")
    print(f"machines_workstations{machines_workstations}")
    # 负责选择工作站的
    # 数字范围 1 到 5
    numbers = [1, 2, 3, 4, 5]
    # 权重，数字越小概率越大
    weights1 = [5, 4, 3, 2, 1]
    # 权重，数字越小概率越小
    weights1 = [1, 2, 3, 4, 5]
    workload_high = []
    workload_low = []
    workload_b=[]
    lose_wk = []
    # 使用集合去重并合并所有值
    unique_all_workstations = set()

    # 提取所有机器的值，去重,即提取所有工作站
    for values in machines_workstations.values():
        unique_all_workstations.update(values)  # 把每个键的值列表加入集合

    # 转换为列表（按字母顺序排序）
    unique_all_machines = sorted(unique_all_workstations)

    if len(unique_all_workstations)!=23:
        print(f"846846有问题有问题")
        print(len(unique_all_workstations))
        print(f"unique_workstations{unique_all_workstations}")
        raise ValueError("原本的工作站数量有问题")

    unique_current_workstations = sorted(set(wk for sublist in individual['individual']['workstation_code'] for wk in sublist))
    # print(f"unique_workstations{unique_current_workstations}")

    if set(unique_current_workstations) == set(unique_all_workstations):
        print("两个列表的值相同（忽略顺序）")
    else:
        print("现在的编码缺失了工作站")
        lose_wk=set(unique_all_workstations)-set(unique_current_workstations)
        print(f"else{lose_wk}")

    for i,ws_list in enumerate(individual['individual']['workstation_code']):
        # 获取当前工序需要的机器
        machine_needed=individual['individual']['machine_code'][i]

       # 获取该机器所有对应的工作站,即该机器可以选择的工作站
        valid_workstations=machines_workstations[machine_needed]
        # print(f"840840")
        print(f"valid_workstations{valid_workstations}")
        tem_valid=copy.deepcopy(valid_workstations)
        print(f"ws_list{ws_list}")
        # 检查并调整不对的
        for j,ws in enumerate(ws_list):
            if ws not in valid_workstations:
                # 如果当前工作站不符合机器的要求，则进行调整
                # 有问题！！会导致有工作站未选择
                # 在当前可选的机器中选择一个工作站
                preferred_ws=[wk for wk in lose_wk if wk in valid_workstations]
                print(f"preferred_ws{preferred_ws}")
                if preferred_ws:
                    # if len(preferred_ws)==1:
                    #     new_ws=preferred_ws
                    # else:
                    new_ws = random.choice(preferred_ws)
                    # lose_wk.remove(new_ws)
                else:
                    print(f"valid_workstations为空？？")
                    if valid_workstations:
                        print(f"valid_workstations{valid_workstations}")
                        new_ws=random.choice(valid_workstations)
                individual['individual']['workstation_code'][i][j]=new_ws

    # 通过balance去调整每个工序分配到的工作站数量
    for idx, (workstation, balance) in enumerate(zip(individual['individual']['workstation_code'], individual['individual']['balance_code'])):

        if int(len(workstation)) >= int(balance):
            diff = int(len(workstation)) - int(balance)
            print(f"该工作站的负载大于等于实际负载有差别,相差{diff}")
            chosen_number = random.choices(numbers, weights=weights1, k=1)[0]
            # if diff > chosen_number:
            if diff > 0:
                print(f"分配过多工作站！")
                workload_high.append((idx, diff))
            elif diff==0:
                workload_b.append((idx,diff))
        else:
            diff = int(len(workstation)) - int(balance)
            # print(f"该工序分配的工作站过少,相差{diff}")
            # 按照概率从1-5之间选择一个数，数字越小概率越大
            # 按照权重选择一个数字
            chosen_number = random.choices(numbers, weights=weights1, k=1)[0]
            if diff > chosen_number:
                workload_low.append((idx, diff))

        # 按照 diff 大小降序排序 (diff 越大越靠前),之后添加工作站
        workload_low.sort(key=lambda x: x[1], reverse=True)

        # 如果存在分配工作站少了的工序
        if workload_low:
            # print(f"workload_low{workload_low}")
            for idx, diff in workload_low:
                machine_type = individual['individual']['machine_code'][idx]  # 获取该工序对应的机器类型
                available_workstations = machines_workstations.get(machine_type, [])  # 获取该机器可用的工作站列表
                while diff>0:
                    found=False
                    for wk in lose_wk:
                        if wk in available_workstations and wk not in individual['individual']['workstation_code'][idx]:
                            individual['individual']['workstation_code'][idx].append(wk)
                            lose_wk.remove(wk)  # 从 lose_wk 中移除
                            found = True
                            break  # 只添加一个，跳出循环

                    if not found:
                        possible_wk = [wk for wk in available_workstations if wk not in individual['individual']['workstation_code'][idx]]
                        if possible_wk:
                            new_wk = random.choice(possible_wk)  # 随机选择一个符合条件的工作站
                            individual['individual']['workstation_code'][idx].append(new_wk)

                    diff = int(individual['individual']['balance_code'][idx]) - len( individual['individual']['workstation_code'][idx])
        else:
            # 说明没有工作站分配的工作站少了,但是有工作站分配多了
            # 有个问题，会不会每个工作站的人力平衡都刚刚好
            for i in lose_wk:
                # print(f"10211021")
                for ids in workload_b:
                    # print(ids)
                    current_ma=individual['individual']['machine_code'][ids[0]]
                    # print(f"current_ma{current_ma}")
                    lose_wk_machine_type = machines_workstations.get(i)
                    # print(f"lose_wk_machine_type{lose_wk_machine_type}")
                    # 如果机器类型与 current_ma 相同，则添加到对应工作站的列表中
                    if lose_wk_machine_type == current_ma:
                        individual['individual']['workstation_code'][ids[0]].append(i)
                        lose_wk.remove(i)
                        break  # 退出循环，假设只需匹配一次
            # print(f"lose_wk{lose_wk}")

    # 检查是否调整完了后有工作站没有分配到
    # 如果还有未分配的工作站

    new_unique_workstations = sorted(set(wk for sublist in individual['individual']['workstation_code'] for wk in sublist))
    print(f"new_unique_workstations{new_unique_workstations}")
    new_lose_wk=set(unique_all_workstations)-set(new_unique_workstations)
    print(f"还有没有分配的工作站")
    while new_lose_wk:
        # print(f"还有没有分配的工作站")
        print(f"new_lose_wk{new_lose_wk}")
        # if new_lose_wk:
        for i in list(new_lose_wk):
            print(f"遍历工作站{i}")
            for ids in workload_b:
                current_ma = individual['individual']['machine_code'][ids[0]]
                print(f"current_ma{current_ma}")
                # lose_wk_machine_type = machines_workstations.get(i)
                # print(f"lose_wk_machine_type{lose_wk_machine_type}")
                print(f"machines_workstations{machines_workstations}")
                if current_ma in machines_workstations:
                    individual['individual']['workstation_code'][ids[0]].append(i)
                    new_lose_wk.remove(i)
                    print(f"当前删除后的new_lose_wk{new_lose_wk}")
                    break  # 退出循环，假设只需匹配一次
                else:
                    # 说明机器不在这个machines_workstations
                    print(f"没在工作站编码中找到")
                    a=1
                    b=0
                    assert a==b,f"说明机器不在这个machines_workstations"
                    # raise ValueError("!!!!!!!!!!")
        print(f"判断是否结束")
        new_unique_workstations3 = sorted(set(wk for sublist in individual['individual']['workstation_code'] for wk in sublist))
        new_lose_wk = set(unique_all_workstations) - set(new_unique_workstations3)
        print(f"new_lose_wk{new_lose_wk}")

    new_unique_workstations2 = sorted( set(wk for sublist in individual['individual']['workstation_code'] for wk in sublist))
    new_lose_wk2 = set(unique_all_workstations) - set(new_unique_workstations2)
    if new_lose_wk2:
        print(f"new_lose_wk2{new_lose_wk2}")
        raise ValueError("有工作站没有分配")
    print(f"11581158")
    check_adjust_workstation(individual['individual']['workstation_code'],23)
    # 不需要修改individual['individual']['workstation_machines']，因为本身就修改好了，这里只是调整工作站编码，也是根据机器来的

    # # 需要修改workstation_machines
    # # 存储工作站到机器的映射
    # workstation_machine_dict = {}
    # # 遍历所有工作站和对应的 machine_code
    # for wks, mc in zip(individual['individual']['workstation_code'], individual['individual']['machine_code']):
    #     for wk in wks:
    #         if wk in workstation_machine_dict and workstation_machine_dict[wk] != mc:
    #             raise ValueError(f"工作站 {wk} 已经匹配到 {workstation_machine_dict[wk]}，但现在又匹配到 {mc}，数据冲突！")
    #         workstation_machine_dict[wk] = mc  # 存储键值对
    #
    # individual['individual']['workstation_machines']=workstation_machine_dict

    return individual















