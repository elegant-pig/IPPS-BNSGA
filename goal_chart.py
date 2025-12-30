import os

import matplotlib.pyplot as plt
# 实验室电脑环境
os.environ['TCL_LIBRARY'] = r'C:\Users\elegant_pigg\AppData\Local\Programs\Python\Python313\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\elegant_pigg\AppData\Local\Programs\Python\Python313\tcl\tk8.6'


# # 自己的电脑环境
# os.environ['TCL_LIBRARY'] = r'D:\Users\tanin\AppData\Local\Programs\Python\Python310\tcl\tcl8.6'
# os.environ['TK_LIBRARY'] = r'D:\Users\tanin\AppData\Local\Programs\Python\Python310\tcl\tk8.6'



def plot_results(makespan_values, workload_values, total_free_time_values):
    iterations = list(range(1, len(makespan_values) + 1))

    # 绘制 makespan 曲线
    plt.figure(figsize=(10, 6))
    plt.plot(iterations, makespan_values, label='Makespan', color='red', marker='o')
    plt.title('Convergence of Makespan')
    plt.xlabel('Iteration')
    plt.ylabel('Makespan')
    plt.legend()
    plt.grid(True)
    plt.show()

    # 绘制 workload 曲线
    plt.figure(figsize=(10, 6))
    plt.plot(iterations, workload_values, label='Workload', color='blue', marker='o')
    plt.title('Convergence of Workload')
    plt.xlabel('Iteration')
    plt.ylabel('Workload')
    plt.legend()
    plt.grid(True)
    plt.show()

    # 绘制 total_free_time 曲线
    plt.figure(figsize=(10, 6))
    plt.plot(iterations, total_free_time_values, label='Total Free Time', color='green', marker='o')
    plt.title('Convergence of Total Free Time')
    plt.xlabel('Iteration')
    plt.ylabel('Total Free Time')
    plt.legend()
    plt.grid(True)
    plt.show()


def main():
    global_best_solution = None  # 存储全局最佳解
    best_fitness = float('-inf')  # 负无穷初始化最差适应度
    each_best_result = []  # 记录每代的最优个体
    global_best_values = []  # 记录全局最优适应度变化

    # === 初始化种群 ===
    population, _ = init.initialize_population(data, population_size, num_workstations)

    # === 初始化时记录最优解 ===
    solution, current_best_solution = calculate.calculate(population, batch_time, num_workstations)
    each_best_result.append(current_best_solution)

    # 设置全局最优解
    global_best_solution = current_best_solution
    global_best_values.append(global_best_solution['fitness'])

    # === 开始迭代 ===
    for generation in range(max_iterations):
        print(f"第 {generation + 1} 代迭代")

        # 计算当前种群的适应度
        solution, current_best_solution = calculate.calculate(population, batch_time, num_workstations)
        each_best_result.append(current_best_solution)

        # 更新全局最优解
        if current_best_solution['fitness'] > global_best_solution['fitness']:
            global_best_solution = current_best_solution

        global_best_values.append(global_best_solution['fitness'])

        # === 选择父代 ===
        parents = selection.elitism_selection(solution, elite_size)

        # === 交叉 ===
        children, _ = Crossover.crossover_choose_parent(parents)

        # === 变异 ===
        mutation_child = Mutation.mutate(children, Px)

        # === 更新种群 ===
        # 加入变异后的个体 + 当前全局最优个体
        population = mutation_child
        if global_best_solution['individual'] not in population:
            population.append(global_best_solution['individual'])

        # 保持种群大小一致（按适应度排序，保留最优个体）
        if len(population) > population_size:
            population = sorted(population, key=lambda x: x['fitness'], reverse=True)[:population_size]

        # === 终止条件 ===
        if generation >= max_iterations:
            print("达到了最大迭代次数，停止算法")
            break

    # === 提取用于绘图的数据 ===
    makespan_values = [x['makespan'] for x in each_best_result]
    workload_values = [x['workload'] for x in each_best_result]
    total_free_time_values = [x['total_free_time'] for x in each_best_result]

    # === 调用绘图函数 ===
    plot_results(makespan_values, workload_values, total_free_time_values)


# 运行主函数
if __name__ == "__main__":
    main()
