import math
import random

import calculate
import init


# def selection_()

def elitism_selection(solution,elite_size):
    """
    使用精英策略选择最优个体并返回。

    参数:
    - solution: 个体的适应度值列表
    - elite_size: 保留的最优个体数量

    返回:
    - elite_individuals: 保留的最优个体
    """
    elite_individuals = solution[:elite_size]

    # print(elite_individuals)
    # print(len(elite_individuals))
    return elite_individuals



import random

def roulette_wheel_selection(population, elite_size):
    """
    使用归一化方法的轮盘赌选择算法，并将 max_fitness 设置为最大适应度值的两倍。
    :param population: 所有个体的列表
    :param elite_size: 选择的个体数量
    :return: 选择的个体
    """
    selected_individuals = []

    for _ in range(elite_size):
        # 1. 计算适应度，distance 越小适应度越高
        fitness_values = []
        valid_distances = [individual['fitness'] for individual in population if individual['fitness'] > 0]

        # 确保最小距离不是 0
        min_distance = min(valid_distances) if valid_distances else 1

        for individual in population:
            distance = individual['fitness']
            if distance == 0:
                # 如果 distance 为 0，适应度设置为最大适应度的两倍
                fitness_values.append(round((1 / min_distance) * 2, 4) if min_distance != 0 else 1)
            else:
                # 计算适应度
                fitness_values.append(round(1 / distance, 4))

        # 2. 归一化适应度
        total_fitness = sum(fitness_values)

        # 归一化过程：将适应度缩放到 [0, 1] 区间
        normalized_fitness_values = [fitness / total_fitness for fitness in fitness_values]

        # 3. 轮盘赌选择
        random_choice = random.random()  # 随机选择一个 [0, 1) 之间的数
        cumulative_probability = 0.0
        selected_idx = None
        for i, prob in enumerate(normalized_fitness_values):
            cumulative_probability += prob
            if random_choice <= cumulative_probability:
                selected_idx = i
                break

        # 如果没有选中任何个体，则处理错误
        if selected_idx is None:
            selected_idx=0

        # 将选择的个体添加到 selected_individuals 中
        selected_individuals.append(population[selected_idx])

        # 4. 从 population 中移除已选择的个体
        population.pop(selected_idx)
    print(f"选中的个体是{selected_individuals}")
    return selected_individuals

def roulette_selection_by_rank_and_crowding(population, elite_size):
    """
    使用 NSGA-II 风格的选择机制，按 rank 层次优先，拥挤距离轮盘赌。
    :param population: 包含 rank 和 crowding_distance 的个体列表
    :param elite_size: 要选择的个体数量
    :return: 选择的个体列表
    """
    selected_individuals = []

    # 1. 将个体按 rank 升序排序
    sorted_population = sorted(population, key=lambda x: x['rank'])

    current_rank = 0
    candidates = []

    # 2. 逐层选取 rank 层，直到满足 elite_size
    while len(candidates) < elite_size:
        current_layer = [ind for ind in sorted_population if ind['rank'] == current_rank]

        if len(candidates) + len(current_layer) <= elite_size:
            candidates.extend(current_layer)
            current_rank += 1
        else:
            # 3. 当前层人数超额，使用拥挤距离轮盘赌选择
            remaining_slots = elite_size - len(candidates)

            # 提取合法的 (ind, crowding_distance) 对
            valid_pairs = []
            for ind in current_layer:
                cd = ind.get('crowding_distance', 0.0)
                if not isinstance(cd, (int, float)) or not math.isfinite(cd) or cd < 0:
                    cd = 0.0
                valid_pairs.append((ind, cd))

            # 分离出处理后的列表
            current_layer = [pair[0] for pair in valid_pairs]
            crowding_values = [pair[1] for pair in valid_pairs]
            total_distance = sum(crowding_values)

            # 计算选择概率
            if total_distance == 0:
                probs = [1 / len(current_layer)] * len(current_layer)
            else:
                probs = [cd / total_distance for cd in crowding_values]

            # 执行带权选择，注意 random.choices 允许重复
            selected_indices = random.choices(range(len(current_layer)), weights=probs, k=remaining_slots)
            selected = [current_layer[i] for i in selected_indices]
            candidates.extend(selected)
            break

    return candidates

def tournament_selection_NSGA2(solutions, num_selected):
    print(f"种群数是{len(solutions)}")
    print(f"要选择成为父代的个数是{num_selected}")
    selected_parents = []
    tournament_size = 2
    for _ in range(num_selected):
        # 随机选择两个个体进行锦标赛
        candidates = random.sample(solutions, tournament_size)

        # 进行比较，选择更优的父代
        winner = candidates[0]
        for candidate in candidates[1:]:
            if candidate['rank'] < winner['rank']:  # Rank 优先
                winner = candidate
            elif candidate['rank'] == winner['rank']:  # Rank 相同，则比拥挤度
                if candidate['crowding_distance'] > winner['crowding_distance']:
                    winner = candidate
        # 选出的优胜者加入父代池
        selected_parents.append(winner)

    return selected_parents

def tournament_selection_NSGA3(population, elite_size):
    selected = []
    while len(selected) < elite_size:
        candidate1, candidate2 = random.sample(population, 2)

        # 优先比较 rank
        if candidate1['rank'] < candidate2['rank']:
            winner = candidate1
        elif candidate1['rank'] > candidate2['rank']:
            winner = candidate2
        else:
            # 如果 rank 相同，可以比较一个其他指标，比如 makespan（也可能是 reference_distance）
            if candidate1['workload_variance'] < candidate2['workload_variance']:
                winner = candidate1
            else:
                winner = candidate2

        selected.append(winner)
    return selected

