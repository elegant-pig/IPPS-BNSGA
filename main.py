import copy
import math
import pandas as pd
import Gantt_lab
import init
import Crossover_2
import calculate_2
from examine_encoding import examine_individual

from fitness_nonDominated import nsga2_fitness
from adjust_individual import adjust_individual
from calculate import calculate, calculate_time

from fitness_4_goal_pareto import fitness

from goal_chart import plot_results

from selection import elitism_selection
# from utils import data, staff_data, population_size, num_workstations, max_iterations, batch_time, elite_size, Px


def main():
    best_solution=None
    best_fitness = float('-inf')  # 或使用负无穷来初始化最差的适应度
    each_best_results=[]
    # 初始化种群
    #返回：population,result_constraint
    population,_= init.initialize_population(data, staff_data, population_size, num_workstations)

    for generation in range(max_iterations):
        solutions,each_best_solution=fitness(copy.deepcopy(population),batch_time,num_workstations,data,staff_data)

        solutions, current_best_individual = nsga2_fitness(copy.deepcopy(population), batch_time, num_workstations,
                                                           data, staff_data)

        if best_solution is None:
            best_solution = current_best_individual
        elif best_solution['rank'] < current_best_individual['rank']:  # 说明上一迭代最好的值比这次迭代最好的值都要好
            print(f"不修改")
        elif best_solution['rank'] == current_best_individual['rank']:  # 说明上一迭代最好的值跟这次迭代最好的值在同一解集范围内，那就比拥挤度
            if best_solution['crowding_distance'] > current_best_individual['crowding_distance']:
                print(f"依旧不修改")
            elif best_solution['crowding_distance'] == current_best_individual['crowding_distance']:
                if best_solution['makespan'] <= current_best_individual['makespan']:
                    print(f"不作修改")
                else:
                    best_solution = current_best_individual
            else:
                best_solution = current_best_individual
        else:  # 说明上次迭代最好的值比这次的差，则替换
            best_solution = current_best_individual


        # # 首次初始化
        # if best_solution is None:
        #     best_solution=copy.deepcopy(each_best_solution)
        #     best_fitness=copy.deepcopy(each_best_solution['fitness'])
        # elif each_best_solution['fitness']<best_fitness: #这一轮最优解比上一轮的好
        #     last_solution = solutions.pop()
        #     if last_solution['fitness']>best_fitness: #说明这次迭代适应度值最差的解比上一次迭代的解还要差
        #         solutions.append(best_solution)
        #     else:
        #         solutions.append(last_solution)
        #     best_solution = copy.deepcopy(each_best_solution)
        #     best_fitness = copy.deepcopy(each_best_solution['fitness'])
        # elif each_best_solution['fitness']>=best_fitness: #说明当前最好的解比上一次迭代的还要差
        #     last_solution=solutions.pop()
        #     solutions.append(copy.deepcopy(best_solution))

        # 记录最优解
        each_best_results.append(best_solution)
        print(f"each_best_results{each_best_results}")
        # 画出最优解的图
        # draw(best_solution, num_workstations, data, staff_data,batch_time)

        #  选择进入迭代的父代，选择的都是偶数
        parent = elitism_selection(copy.deepcopy(solutions), elite_size)

        # 进行交叉，变异
        Child=Crossover_2.Crossover(parent)
        # 全部交叉后遍历修改
        modified_crossover_Child=adjust_individual(copy.deepcopy(Child),data,num_workstations)

        # 进行变异
        mutation_Child=mutation(copy.deepcopy(modified_crossover_Child),data,Px,num_workstations)



        population=copy.deepcopy(mutation_Child)
        # population = crossover_child

    draw(best_solution, num_workstations, data, staff_data, batch_time)
    makespan_values = [x['makespan'] for x in each_best_results]
    workload_values = [x['workload'] for x in each_best_results]
    workload_variance = [x['workload_variance'] for x in each_best_results]
    total_free_time_values = [x['total_free_time'] for x in each_best_results]


    # === 调用绘图函数 ===
    plot_results(makespan_values,workload_variance, workload_values, total_free_time_values)

def draw(best_solution,num_workstations, data, staff_data,batch_time):
    workstation_available_time = {station: {"free_intervals": [(float(0.0), float('inf'))], 'assigned_jobs': []} for station in generate_workstation(num_workstations)}
    tem_time=calculate_time(best_solution['individual'], workstation_available_time, batch_time, num_workstations, data, staff_data)
    # examine_individual(best_solution, 23)
    # 画图，画出当前迭代最优解
    Gantt_lab.plot_gantt_chart(tem_time)


# 只有当脚本作为主程序运行时，才会执行以下代码
if __name__ == "__main__":
    main()