import numpy as np

# 2. 计算每个解与理想解的欧几里得距离
def calculate_distance(solution, ideal_solution):
    return np.linalg.norm([
        solution['makespan'] - ideal_solution['makespan'],
        solution['workload'] - ideal_solution['workload'],
        solution['total_free_time'] - ideal_solution['total_free_time']
    ])

def fitness(solutions):
    # 3. 计算每个解与理想解的距离
    distances = []
    ideal_solution = {
        'makespan': min(solution['makespan'] for solution in solutions),
        'workload': min(solution['workload'] for solution in solutions),
        'total_free_time': min(solution['total_free_time'] for solution in solutions),
    }

    # 3. 计算每个解与理想解的距离
    distances = []
    for solution in solutions:
        distance = calculate_distance(solution, ideal_solution)
        # distances.append((solution['index'], distance, solution))
        distances.append({'individual':solution['individual'],'fitness':distance,'makespan':solution['makespan'],'workload':solution['workload'],'total_free_time':solution['total_free_time']})
    # print(distances)
    # # 4. 选择距离理想解最近的解
    all_solutions=sorted(distances,key=lambda x:x['fitness'])
    best_solution = distances[0]
    print(f"检验多少个个体")
    print(len(distances))
    return all_solutions,best_solution