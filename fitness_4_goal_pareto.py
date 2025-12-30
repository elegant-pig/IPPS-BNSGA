import numpy as np

import Gantt_lab
from calculate import calculate, calculate_time
from examine_encoding import examine_individual


# 2. 计算每个解与理想解的欧几里得距离
def calculate_distance(solution, ideal_solution):
    return np.linalg.norm([
        solution['makespan'] - ideal_solution['makespan'],
        solution['workload_variance'] - ideal_solution['workload_variance'],
        solution['workload'] - ideal_solution['workload'],
        solution['total_free_time'] - ideal_solution['total_free_time']
    ])

def fitness(populations,batch_time, num_station, data,staff_data):
    # 值越小适应度越好
    result = calculate(populations, batch_time, num_station, data, staff_data)
    # 3. 计算每个解与理想解的距离

    ideal_solution = {
        'makespan': min(solution['makespan'] for solution in result),
        'workload': min(solution['workload'] for solution in result),
        'workload_variance':min(solution['workload_variance'] for solution in result),
        'total_free_time': min(solution['total_free_time'] for solution in result),
    }

    # 3. 计算每个解与理想解的距离
    distances = []
    for solution in result:
        distance = calculate_distance(solution, ideal_solution)
        # distances.append((solution['index'], distance, solution))
        distances.append({'individual':solution['individual'],'fitness':distance,'makespan':solution['makespan'],'workload_variance':solution['workload_variance'],'workload':solution['workload'],'total_free_time':solution['total_free_time']})
    # print(distances)
    # # 4. 选择距离理想解最近的解
    all_solutions=sorted(distances,key=lambda x:x['fitness'])
    best_solution = distances[0]
    # 画出当前迭代的最好解的图
    # draw(best_solution, num_station, data, staff_data,batch_time)

    return all_solutions,best_solution

