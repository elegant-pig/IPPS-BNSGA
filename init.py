import math
import random

import pandas as pd

import generateOR
import generateOperation
import generateMachine
import generateBalance
import generateEmploy
import generateWorkstation_simple
from check_code import check_adjust_workstation, check_result_employ_allocation, check_wk_ma, check_adjust_employ
from generate_Workstation import generate_workstation_code


# population_size=5 #种群大小
# num_workstations=23
# piece_num=50 #一共生产多少件
# batch=10 #一批次生产多少件
# Pr=0.8
# elite_size=math.ceil(population_size*Pr)
# file_path = 'data/operation_data.xlsx'
# operation_data = pd.read_excel(file_path, sheet_name='final')
# data=operation_data.copy()

def initialize_population(op_data,id_data,population_size, num_workstations):
    """
    初始化种群函数。

    参数:
        population_size (int): 种群大小。
        num_workstations (int): 工作站数量。

    返回:
        population (list of list): 初始种群，每个个体表示一个工序分配方案。
    """
    population = []
    result_constraint=[]
    workstation_assignment_machines=[]
    # constraint={}

    # 为每个个体生成一个随机的工序分配
    for _ in range(population_size):
        individual,constraint, = generate_individual(op_data,id_data,num_workstations)
        population.append(individual)
        result_constraint.append(constraint)
    # print(f"result_constraint{result_constraint}")
    # print(f"population{population}")
    return population,result_constraint

def generate_individual(op_data,id_data,num_workstations):
    """
    初始化个体

    参数:
        num_workstations(int):工作站数量

    返回:
        individual（list）:个体
        constraint(list)：个体约束
    """
    tem_data,or_code,replace_op=generateOR.generateOR(op_data)
    _,operation_code=generateOperation.generate_operation_codes(tem_data)
    _,machine_code, constraint=generateMachine.generate_machine_codes(operation_code,tem_data)
    _,balance_code,tem_generate_workstation=generateBalance.generate_balance_codes(tem_data,constraint,num_workstations)
    # _,workstation_code,workstation_assignments,result_constraint,workstation_machines=generateWorkstation_simple.assignment_operation(tem_data,tem_generate_workstation,num_workstations)
    workstation_code,workstation_machines,workstation_assignments=generate_workstation_code(operation_code,machine_code,balance_code,num_workstations,tem_data)
    result_employ_allocation, employ_code=generateEmploy.generateEmploy(tem_data,id_data,workstation_code,workstation_assignments,num_workstations)


    individual={
        'OR_CODE':or_code,
        'operation_code': operation_code,
        'machine_code': machine_code,
        'balance_code': balance_code,
        'workstation_code': workstation_code,
        'employ_code': employ_code,
        'replace_op':replace_op,
        'workstation_machines':workstation_machines,
        'result_employ_allocation':result_employ_allocation
    }
    # print(f"初始化时的employ_code")
    # print(individual['employ_code'])
    check_adjust_workstation(individual['workstation_code'], num_workstations)
    check_result_employ_allocation(individual['result_employ_allocation'], num_workstations)
    check_wk_ma(individual['workstation_machines'], num_workstations)
    check_adjust_employ(individual['employ_code'], num_workstations)


    return individual,constraint



# population,result_constraint=initialize_population(population_size,num_workstations)

