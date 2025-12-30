import matplotlib.pyplot as plt


def plot_pareto_fronts(solutions):
    # 目标列表
    objectives = ['makespan', 'workload_variance', 'workload', 'total_free_time']

    # 创建一个 2x2 的子图布局
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # 平铺每个子图
    axes = axes.flatten()

    for i in range(4):
        for j in range(i + 1, 4):
            ax = axes[i * 3 + j - ((i + 1) * (i + 2)) // 2]
            obj1 = objectives[i]
            obj2 = objectives[j]


            # 目标1和目标2的值
            x = [sol[obj1] for sol in solutions]
            y = [sol[obj2] for sol in solutions]

            # 绘制散点图
            ax.scatter(x, y, c='blue', s=40, alpha=0.7)
            ax.set_xlabel(obj1.replace('_', ' ').title())
            ax.set_ylabel(obj2.replace('_', ' ').title())
            ax.set_title(f'{obj1.replace("_", " ").title()} vs {obj2.replace("_", " ").title()}')
            ax.grid(True)

    # 调整布局，避免重叠
    plt.tight_layout()
    plt.show()


def plot_pareto_fronts2(solutions):
    # 如果是单个解，转为列表
    if isinstance(solutions, dict):
        solutions = [solutions]

    # 目标列表（只要存在于解中的即可）
    # objectives = ['makespan', 'workload_variance', 'workload', 'total_free_time']
    objectives = ['makespan', 'workload_variance', 'total_free_time']

    available_objectives = [obj for obj in objectives if obj in solutions[0]]

    num_objs = len(available_objectives)
    total_plots = (num_objs * (num_objs - 1)) // 2
    cols = 2
    rows = (total_plots + 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 5 * rows))
    axes = axes.flatten()

    plot_idx = 0
    for i in range(num_objs):
        for j in range(i + 1, num_objs):
            obj1 = available_objectives[i]
            obj2 = available_objectives[j]

            ax = axes[plot_idx]
            x = [sol[obj1] for sol in solutions]
            y = [sol[obj2] for sol in solutions]

            ax.scatter(x, y, c='blue', s=40, alpha=0.7)
            ax.set_xlabel(obj1.replace('_', ' ').title())
            ax.set_ylabel(obj2.replace('_', ' ').title())
            ax.set_title(f'{obj1.replace("_", " ").title()} vs {obj2.replace("_", " ").title()}')
            ax.grid(True)

            plot_idx += 1

    # 删除多余的子图
    for k in range(plot_idx, len(axes)):
        fig.delaxes(axes[k])

    plt.tight_layout()
    plt.show()


import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def plot_pareto_3d(solutions, obj1='makespan', obj2='workload_variance', obj3='total_free_time'):
    # 如果传入的是单个解，转为列表
    if isinstance(solutions, dict):
        solutions = [solutions]

    # 提取对应的三个目标值
    x = [sol[obj1] for sol in solutions]
    y = [sol[obj2] for sol in solutions]
    z = [sol[obj3] for sol in solutions]

    # 画 3D 图
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, c='blue', s=50, alpha=0.7)

    # 设置标签
    ax.set_xlabel(obj1.replace('_', ' ').title())
    ax.set_ylabel(obj2.replace('_', ' ').title())
    ax.set_zlabel(obj3.replace('_', ' ').title())
    ax.set_title('3D Pareto Front')

    plt.tight_layout()
    plt.show()
