import math

import pandas as pd
import itertools
import pandas as pd

from main_2 import main_2
from main_3 import main_3


# population_size=8#种群大小

# piece_num=10 #一共生产多少件

# Pr=0.6
# Px=0.4  #变异率


# max_iterations=200 #迭代次数


def iteration():
    file_path = 'data/operation_data.xlsx'
    operation_data = pd.read_excel(file_path, sheet_name='final')
    employ_data = pd.read_excel(file_path, sheet_name='staff')
    data = operation_data.copy()
    staff_data = employ_data.copy()
    # 结果记录列表
    all_results = []

    # population_sizes = [8, 10, 12, 15]
    # population_sizes = [8, 10]
    population_sizes = [100]  # 种群大小

    # piece_nums = [10, 100, 1000]
    piece_nums = [1000]  # 生产多少件
    # Px_values = [0.4,0.5,0.6,0.7,0.8]
    Px_values = [0.1,0.3,0.5]
    # Px_values = [0.5]

    Pr_values = [0.8]

    # 固定参数
    max_iterations = 30  # 迭代次数
    num_workstations = 25  # 工作站数量
    batch = 10  # 一批次生产多少件

    for population_size, piece_num, Px, Pr in itertools.product(population_sizes, piece_nums, Px_values, Pr_values):
        batch_time = math.ceil(piece_num / batch)  # 一共生产多少批次
        elite_size = round(population_size * Pr / 2) * 2
        # population_size, num_workstations, max_iterations, batch_time, elite_size, Px
        result,pareto_front = main_3(data,staff_data,population_size,num_workstations,max_iterations,batch_time,elite_size,Px)
        result['population_sizes']=population_size
        result['piece_nums']=piece_num
        result['Px_values']=Px
        result['Pr_values']=Pr
        result['elite_size']=elite_size
        result['batch_time']=batch_time
        result['num_workstations']=num_workstations
        result['batch']=batch
        result['pareto_front']=pareto_front

        all_results.append(result)
    # 存入表格
    df = pd.DataFrame(all_results)
    df.to_excel("NSGA3_10_1000_25_10'.xlsx", index=False)

    # # 可选同时保存为 CSV
    # df.to_csv(filename.replace(".xlsx", ".csv"), index=False, encoding='utf-8-sig')
    # print(f"结果也保存为 CSV：{filename.replace('.xlsx', '.csv')}")

# 只有当脚本作为主程序运行时，才会执行以下代码
if __name__ == "__main__":
    iteration()