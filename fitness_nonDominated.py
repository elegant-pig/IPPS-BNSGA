import numpy as np

from calculate_2 import calculate


# 非支配关系判断：如果 a 支配 b，返回 True
# 支配条件：所有目标值都不劣，且至少一个更优
def dominates(a, b):
    better_or_equal = (
        a['makespan'] <= b['makespan'] and
        # a['workload'] <= b['workload'] and
        a['workload_variance'] <= b['workload_variance'] and
        a['total_free_time'] <= b['total_free_time']
    )
    strictly_better = (
        a['makespan'] < b['makespan'] or
        # a['workload'] < b['workload'] or
        a['workload_variance'] < b['workload_variance'] or
        a['total_free_time'] < b['total_free_time']
    )
    return better_or_equal and strictly_better

# 快速非支配排序
def fast_non_dominated_sort(solutions):
    fronts = [[]]
    domination_count = {}
    dominated_solutions = {}

    for i, p in enumerate(solutions):
        domination_count[i] = 0
        dominated_solutions[i] = []
        for j, q in enumerate(solutions):
            if i == j:
                continue
            if dominates(p, q):
                dominated_solutions[i].append(j)
            elif dominates(q, p):
                domination_count[i] += 1
        if domination_count[i] == 0:
            p['rank'] = 0
            fronts[0].append(i)

    current_front = 0
    while len(fronts[current_front]) > 0:
        next_front = []
        for i in fronts[current_front]:
            for j in dominated_solutions[i]:
                domination_count[j] -= 1
                if domination_count[j] == 0:
                    solutions[j]['rank'] = current_front + 1
                    next_front.append(j)
        current_front += 1
        fronts.append(next_front)

    return fronts[:-1]  # 最后一层为空，去掉

# 拥挤度计算
def calculate_crowding_distance(front, solutions):
    l = len(front)
    if l == 0:
        return

    for i in front:
        solutions[i]['crowding_distance'] = 0

    # objectives = ['makespan', 'workload_variance', 'workload', 'total_free_time']
    objectives = ['makespan', 'workload_variance', 'total_free_time']

    for obj in objectives:
        front_sorted = sorted(front, key=lambda i: solutions[i][obj])
        min_val = solutions[front_sorted[0]][obj]
        max_val = solutions[front_sorted[-1]][obj]

        # 边界解设置为无穷大
        solutions[front_sorted[0]]['crowding_distance'] = float('inf')
        solutions[front_sorted[-1]]['crowding_distance'] = float('inf')

        if max_val - min_val == 0:
            continue

        for k in range(1, l - 1):
            prev = solutions[front_sorted[k - 1]][obj]
            next = solutions[front_sorted[k + 1]][obj]
            solutions[front_sorted[k]]['crowding_distance'] += (next - prev) / (max_val - min_val)

# 评估适应度并进行非支配排序和拥挤度计算
def nsga2_fitness(populations, batch_time, num_station, data, staff_data):
    result = calculate(populations, batch_time, num_station, data, staff_data)

    # 构造基础信息
    solutions = []
    for sol in result:
        solutions.append({
            'individual': sol['individual'],
            'makespan': sol['makespan'],
            'workload_variance': sol['workload_variance'],
            # 'workload': sol['workload'],
            'total_free_time': sol['total_free_time'],
        })

    # 非支配排序
    fronts = fast_non_dominated_sort(solutions)

    # 给 solutions 赋 rank 和 crowding_distance
    for front_id, front in enumerate(fronts):
        for idx in front:
            solutions[idx]['rank'] = front_id
            solutions[idx]['crowding_distance'] = solutions[idx].get('crowding_distance', 0.0)

    # # 拥挤度计算
    # for front in fronts:
    #     calculate_crowding_distance(front, solutions)

    # 排序方式：先按rank，再按拥挤度（越大越好）
    sorted_solutions = sorted(solutions, key=lambda x: (x['rank'], -x['crowding_distance']))
    print(f"sorted_solutions{sorted_solutions}")
    print(len(sorted_solutions))

    # 提取当前非支配前沿 (rank=0)
    pareto_front = [solutions[i] for i in fronts[0]]

    return sorted_solutions, sorted_solutions[0],pareto_front  #返回当前排序后的种群，和当前最好的结果
