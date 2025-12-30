import copy
import json
import math
from datetime import datetime

# from copy import copy

import pandas as pd

# import Crossover_1
import Gantt_lab
import Mutation
import calculate
import Crossover_2
import calculate_2
import init
import selection
from adjust_individual import adjust_individual
from check_code import check_adjust_workstation, check_result_employ_allocation, check_adjust_employ, check_wk_ma
from examine_encoding import examine_individual
from fitness_nonDominated import nsga2_fitness
from generate_Workstation import generate_workstation
from goal_chart import plot_results
from plot_pareto_fronts import plot_pareto_3d
from wrong_adjust import check_adjust_wrong_individual

# from goal_chart import plot_makespan_over_iterations, plot_all_metrics_over_iterations

def main_2(data,staff_data,population_size,num_workstations,max_iterations,batch_time,elite_size,Px):
    print(f"main函数")

    best_solution = None  # 存储全局最佳解
    best_fitness = float('-inf')  # 或使用负无穷来初始化最差的适应度
    each_best_result=[] #记录每代的最有个体的适应度
    each_best_result_pareto_front=None
    # 初始化种群
    #返回：population,result_constraint
    population,_=init.initialize_population(data,staff_data,population_size,num_workstations)
    for generation in range(max_iterations):
        print(f"迭代第{generation}次")
        # 适应度评估
        # solutions,current_best_solution = calculate(copy.deepcopy(population), batch_time, num_workstations)
        solutions,current_best_individual,pareto_front=nsga2_fitness(copy.deepcopy(population),batch_time,num_workstations,data,staff_data)
        print(f"solutions{solutions}")
        print(len(solutions))
        if best_solution is None :
            best_solution=current_best_individual
        elif best_solution['rank']<current_best_individual['rank']: #说明上一迭代最好的值比这次迭代最好的值都要好
            print(f"不修改")
        elif best_solution['rank']==current_best_individual['rank']: #说明上一迭代最好的值跟这次迭代最好的值在同一解集范围内，那就比拥挤度
            if best_solution['crowding_distance']>current_best_individual['crowding_distance']:
                print(f"依旧不修改")
            elif best_solution['crowding_distance']==current_best_individual['crowding_distance']:
                if best_solution['makespan']<=current_best_individual['makespan']:
                    print(f"不作修改")
                else:
                    best_solution=current_best_individual
            else:
                best_solution=current_best_individual
        else: #说明上次迭代最好的值比这次的差，则替换
            best_solution = current_best_individual

        print(f"each_best_result{each_best_result}")
        # 记录最优解
        each_best_result.append(best_solution)
        # each_best_result_pareto_front.append(pareto_front)
        each_best_result_pareto_front=pareto_front

        print(f"222solutions{solutions}")
        print(len(solutions))
        #  选择进入迭代的父代，选择的都是偶数，这是精英策略
        # parent=selection.elitism_selection(copy.deepcopy(solutions),elite_size)
        parent=selection.tournament_selection_NSGA2(copy.deepcopy(solutions),elite_size)

        # 进行交叉,交叉之后是没有调整的
        # # crossover_child,old_best=Crossover.crossover_choose_parent(parents)
        # # crossover_child=Crossover.crossover_choose_parent(parents)
        crossover_child=Crossover_2.Crossover(copy.deepcopy(parent))

        # 调整个体
        modified_crossover_Child=adjust_individual(copy.deepcopy(crossover_child),data,num_workstations)


        # # # 进行变异
        mutation_child=Mutation.mutation(copy.deepcopy(modified_crossover_Child),data,Px,num_workstations)
        # individual, operation_data, mutation_rate, num

        next_generation = select_next_generation(copy.deepcopy(mutation_child), batch_time, num_workstations, data, staff_data,
                                                 population_size)

        population = copy.deepcopy(next_generation)

    # # 存储数据
    save_each_best_results_to_excel(each_best_result,Px,each_best_result_pareto_front)

    # # 画最后结果的甘特图
    # draw(best_solution, num_workstations, data, staff_data, batch_time)
    #
    # # 调用画图函数,画最后结果的散点图
    # # plot_pareto_fronts2(each_best_results)
    # plot_pareto_3d(each_best_results)
    # plot_individual_pareto_fronts(each_best_results)
    return best_solution,pareto_front

def draw(best_solution,num_workstations, data, staff_data,batch_time):
    workstation_available_time = {station: {"free_intervals": [(float(0.0), float('inf'))], 'assigned_jobs': []} for station in generate_workstation(num_workstations)}
    tem_time= calculate_2.calculate_time(best_solution['individual'], workstation_available_time, batch_time, num_workstations, data, staff_data)
    examine_individual(best_solution, 23)
    # 画图，画出当前迭代最优解
    Gantt_lab.plot_gantt_chart(tem_time)

def select_next_generation(populations, batch_time, num_station, data, staff_data, pop_size):
    # 计算父代和子代的适应度
    sorted_solutions, best_solution,_ = nsga2_fitness(populations, batch_time, num_station, data, staff_data)

    # 选择适应度最优的 `pop_size` 个个体作为下一代
    selected_next_gen = sorted_solutions[:pop_size]

    # 返回选择后的下一代种群
    next_generation = [sol['individual'] for sol in selected_next_gen]

    return next_generation



def save_each_best_results_to_excel(each_best_results, Px,pareto_front,label="0707"):
    # 生成唯一文件名
    # timestamp = datetime.now()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"NSGA2_each_best_results_0711{timestamp}.xlsx"

    records = []
    for i, result in enumerate(each_best_results):
        ind = result['individual']

        record = {
            "Generation": i + 1,
            "Makespan": result.get("makespan"),
            "Workload": result.get("workload"),
            "Workload Variance": result.get("workload_variance"),
            "Total Free Time": result.get("total_free_time"),
            # "pareto_solutions":result.get(),
            "Rank": result.get("rank"),
            "Crowding Distance": result.get("crowding_distance"),
            # 编码信息（字符串表示）
            "Operation Codes": ", ".join(ind.get("operation_code", [])),
            "Machine Codes": ", ".join(ind.get("machine_code", [])),
            "Workstation Codes": json.dumps(ind.get("workstation_code", []), ensure_ascii=False),
            "Employ Codes": json.dumps(ind.get("employ_code", []), ensure_ascii=False),
            "Replace Ops": str(ind.get("replace_op", [])),
            'Px':Px,
            # 'pareto_front': pareto_front,

        }

        records.append(record)

    df = pd.DataFrame(records)
    df.to_excel(filename, index=False)
    print(f"结果已保存到 Excel：{filename}")

    # 可选同时保存为 CSV
    df.to_csv(filename.replace(".xlsx", ".csv"), index=False, encoding='utf-8-sig')
    print(f"结果也保存为 CSV：{filename.replace('.xlsx', '.csv')}")



#
#
# # 只有当脚本作为主程序运行时，才会执行以下代码
# if __name__ == "__main__":
#     main_2()