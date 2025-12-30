import copy
import random
from collections import defaultdict

import pandas as pd

from adjust_individual import adjust_workstation_and_workstation_machine_code, adjust_workstation_machines, \
    adjust_workstation_code, adjust_employ_code
from check_code import check_adjust_workstation
from examine_encoding import examine_workstation_machines_code, examine_individual
from generateBalance import generate_new_balance
from generateOperation import generate_operation_codes
from mutation_strategy_balance import SubLlist_Swap, Gaussian_perturbation
from mutation_strategy_employ import change_staff_to_workstation, swap_random_employ
from mutation_strategy_operation_machine import mutation_or_operation_machine1, mutation_or_operation_machine2
from mutation_strategy_workstation import SubLlist_Swap_wk


def mutation(individuals,operation_data,mutation_rate,num):
    modified_Child = []
    for c in individuals:
        if 'individual' in c:
            c=c['individual']
        or_node, operation_codes, machine_code = mutation_or_operation_machine(operation_data, mutation_rate,copy.deepcopy(c))
        c['OR_CODE'] = copy.deepcopy(or_node)
        c['operation_code'] = copy.deepcopy(operation_codes)
        c['machine_code'] = copy.deepcopy(machine_code)

        # 因为调整了机器和工序，所以先把人力平衡、工作站编码、机器工作站匹配编码和员工编码调整了
        new_balance_codes,float_balance_codes = generate_new_balance(copy.deepcopy(c), operation_data)
        modified_workstation_machines_code = adjust_workstation_machines(copy.deepcopy(c), num)
        c['workstation_machines'] = modified_workstation_machines_code
        r, s = examine_workstation_machines_code(modified_workstation_machines_code, copy.deepcopy(c['machine_code']), num)
        if r:
            # 调整工作站编码
            new_wk = adjust_workstation_code(copy.deepcopy(c), num)
            c['workstation_code'] = new_wk

        else:
            raise ValueError(f"错误")
        print(f'----------point--------------')
        # 调整员工编码
        staff_code = adjust_employ_code(copy.deepcopy(c), num)
        c['employ_code'] = copy.deepcopy(staff_code)

        # 对人力平衡编码进行变异
        balance_code=mutate_balance_code(mutation_rate,new_balance_codes,float_balance_codes,num)
        c['balance_codes'] = balance_code


        modified_workstation_code = mutate_workstation_code(mutation_rate, copy.deepcopy(c),num)
        c['workstation_code'] = copy.deepcopy(modified_workstation_code)

        modified_employ,modified_employ_allocate=mutate_employ_code(mutation_rate, copy.deepcopy(c),num)
        c['employ_code'] =copy.deepcopy(modified_employ)
        c['result_employ_allocation']=copy.deepcopy(modified_employ_allocate)

        modified_Child.append(c)

        if examine_individual(c,num):
            print(f"正确")
        else:
            raise ValueError(f"调整错误")

    return modified_Child

def mutation_or_operation_machine(operation_data,mutation_rate,i):
    # operation_data, mutation_rate, copy.deepcopy(c)
    # data=copy.deepcopy(operation_data)
    mutate_num = int(round((mutation_rate * len(i['workstation_code']))))  # 变异的基因个数
    individual=copy.deepcopy(i)
    if mutate_num == 0 or mutate_num % 2 != 0:
        mutate_num += 1
    for _ in range(mutate_num):
        strategy=random.choice([0,1])
        if strategy==0:
            print(f"选择第一个策略")
            or_node,operation_code,machine_code=mutation_or_operation_machine1(copy.deepcopy(operation_data),individual)
            i['operation_code']=operation_code
            i['machine_code']=machine_code
            i['OR_CODE']=or_node
            # data=tem_ddate
        else:
            print(f"选择第二个策略")
            peration_code_new,machine_code=mutation_or_operation_machine2(i['operation_code'],copy.deepcopy(operation_data))
            i['operation_code']=peration_code_new
            i['machine_code']=machine_code
            # data = tem_data

    return individual['OR_CODE'], individual['operation_code'], individual['machine_code']

def mutate_workstation_code(mutation_rate,i,num):
    # old_workstation = copy.deepcopy(i['workstation_code'])
    # machine_code = copy.deepcopy(i['machine_code'])
    # old_workstation_machine = copy.deepcopy(i['workstation_machines'])

    mutate_num = int(round((mutation_rate * len(i['workstation_code']))))  # 变异的基因个数
    if mutate_num == 0 or mutate_num % 2 != 0:
        mutate_num += 1

    # 使用子列表交换策略
    tem_workstation= SubLlist_Swap_wk(mutate_num, i,num)


    return tem_workstation


def mutate_balance_code(mutation_rate,i,float_i,num_station):
    # mutate_num = int(round((mutation_rate * len(i['balance_code']))))  # 变异的基因个数
    # if mutate_num == 0 or mutate_num % 2 != 0:
    #     mutate_num += 1

    # 使用子列表交换策略
    tem_balance = Gaussian_perturbation(mutation_rate,i,float_i,num_station)

    return tem_balance

def mutate_employ_code(mutation_rate,i,num):

    mutate_num = int(round((mutation_rate * len(i['employ_code']))))  # 变异的基因个数
    if mutate_num == 0 or mutate_num % 2 != 0:
        mutate_num += 1

    # tem_employ_code,staff_to_workstation=change_staff_to_workstation(mutate_num,copy.deepcopy(i))
    result=swap_random_employ(mutate_num,copy.deepcopy(i))
    i['result_employ_allocation']=copy.deepcopy(result)
    employ_code=adjust_employ_code(i,num)

    return employ_code,result



