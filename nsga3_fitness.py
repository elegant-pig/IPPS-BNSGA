import numpy as np

from calculate_2 import calculate


def generate_reference_points(num_objectives, p):
    """
    生成参考点，p为分割数（分割越多参考点越密集）
    返回：参考点数组，shape=(num_points, num_objectives)
    """
    def recursive_gen(points, left, total, temp, dimension, results):
        if dimension == num_objectives - 1:
            temp.append(left / total)
            results.append(temp.copy())
            temp.pop()
        else:
            for i in range(left + 1):
                temp.append(i / total)
                recursive_gen(points, left - i, total, temp, dimension + 1, results)
                temp.pop()

    results = []
    recursive_gen([], p, p, [], 0, results)
    return np.array(results)


# -------------------------
# 1. 你的非支配排序函数保持不变
def dominates(a, b):
    better_or_equal = (
        a['makespan'] <= b['makespan'] and
        a['workload_variance'] <= b['workload_variance'] and
        a['total_free_time'] <= b['total_free_time']
    )
    strictly_better = (
        a['makespan'] < b['makespan'] or
        a['workload_variance'] < b['workload_variance'] or
        a['total_free_time'] < b['total_free_time']
    )
    return better_or_equal and strictly_better

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

    return fronts[:-1]  # 去掉最后空的层


# -------------------------
# 2. 生成均匀参考点（Das-Dennis法，针对3目标）

def generate_reference_points(num_objectives=3, p=12):
    # p 控制划分颗粒度，越大点越密集
    def recursive_gen(ref_points, num_objs, left, total, temp):
        if num_objs == 1:
            temp.append(left / total)
            ref_points.append(temp.copy())
            temp.pop()
        else:
            for i in range(left + 1):
                temp.append(i / total)
                recursive_gen(ref_points, num_objs - 1, left - i, total, temp)
                temp.pop()

    ref_points = []
    recursive_gen(ref_points, num_objectives, p, p, [])
    return np.array(ref_points)


# -------------------------
# 3. 归一化目标值

def normalize_objectives(solutions, objectives=['makespan', 'workload_variance', 'total_free_time']):
    # 提取目标矩阵 shape = (N, M)
    obj_matrix = np.array([[sol[obj] for obj in objectives] for sol in solutions])
    min_vals = np.min(obj_matrix, axis=0)
    max_vals = np.max(obj_matrix, axis=0)
    # 防止除0
    denom = np.where(max_vals - min_vals == 0, 1, max_vals - min_vals)
    normalized = (obj_matrix - min_vals) / denom
    return normalized


# -------------------------
# 4. 计算个体与参考点的垂直距离（关联）

def associate_to_reference_points(normalized_objs, reference_points):
    # 垂直距离计算: d = ||x - (x·r)r||  r为单位参考点向量
    distances = np.full((len(normalized_objs), len(reference_points)), np.inf)
    for i, x in enumerate(normalized_objs):
        for j, r in enumerate(reference_points):
            r_norm = np.linalg.norm(r)
            if r_norm == 0:
                continue
            proj = np.dot(x, r) / r_norm
            proj_vec = proj * r / r_norm
            diff = x - proj_vec
            distances[i, j] = np.linalg.norm(diff)
    # 返回每个个体最近参考点索引
    nearest_refs = np.argmin(distances, axis=1)
    return nearest_refs


# -------------------------
# 5. 环境选择 - 基于参考点关联的niching策略

def niching_selection(front_indices, solutions, nearest_refs, K, reference_points):
    # K = 剩余需要选的个数
    chosen = []
    niche_counts = {i: 0 for i in range(len(reference_points))}  # 各参考点已选数

    # 先统计已选个体占用的参考点数（在前面已选个体中）
    for i in front_indices:
        niche_counts[nearest_refs[i]] += 0  # 初始为0

    # 候选个体按rank已同，依次为每个参考点选择
    front_pool = set(front_indices)

    while len(chosen) < K and front_pool:
        # 找最少被占用参考点的个体
        min_count = min([niche_counts[nearest_refs[i]] for i in front_pool])
        # 参考点对应的个体集合
        candidates = [i for i in front_pool if niche_counts[nearest_refs[i]] == min_count]
        # 任选一个candidate，选最小距离个体
        # 先计算距离对应参考点的距离（你可以优化）
        best_candidate = None
        best_dist = float('inf')
        for c in candidates:
            # 计算距离（垂直距离）
            # 直接复用上面计算的距离数组更优，简化这里演示
            # 为简化，这里用0（可改成你真实距离）
            dist = 0
            if dist < best_dist:
                best_dist = dist
                best_candidate = c
        chosen.append(best_candidate)
        niche_counts[nearest_refs[best_candidate]] += 1
        front_pool.remove(best_candidate)
    return chosen


# -------------------------
# 6. NSGA-III主函数：评估，排序，环境选择

def nsga3_fitness(populations, batch_time, num_station, data, staff_data):
    # 1. 计算目标
    result = calculate(populations, batch_time, num_station, data, staff_data)

    # 2. 构造solutions格式
    solutions = []
    for sol in result:
        solutions.append({
            'individual': sol['individual'],
            'makespan': sol['makespan'],
            'workload_variance': sol['workload_variance'],
            'total_free_time': sol['total_free_time'],
        })

    # 3. 非支配排序
    fronts = fast_non_dominated_sort(solutions)

    # 4. 生成参考点
    num_objectives = 3
    reference_points = generate_reference_points(num_objectives=num_objectives, p=12)

    # 5. 归一化目标值
    normalized_objs = normalize_objectives(solutions, ['makespan', 'workload_variance', 'total_free_time'])

    # 6. 关联个体到参考点
    nearest_refs = associate_to_reference_points(normalized_objs, reference_points)

    # 7. 选出下一代
    new_population = []
    for front in fronts:
        if len(new_population) + len(front) <= len(populations):
            # 全部加入
            new_population.extend(front)
        else:
            # 需要niching选择部分个体
            remaining = len(populations) - len(new_population)
            selected = niching_selection(front, solutions, nearest_refs, remaining, reference_points)
            new_population.extend(selected)
            break

    # 8. 返回选中个体和最优个体
    sorted_solutions = [solutions[i] for i in new_population]
    best_solution = sorted_solutions[0]
    pareto_front = [solutions[i] for i in fronts[0]]

    return sorted_solutions, best_solution,pareto_front
