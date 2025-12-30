import copy
import datetime
import json
import math
import pandas as pd
import Gantt_lab
import init
import Crossover_2

from adjust_individual import adjust_individual
from calculate_2 import calculate_time

from examine_encoding import examine_individual
from generate_Workstation import generate_workstation

import Mutation
from nsga3_fitness import generate_reference_points, nsga3_fitness
from selection import tournament_selection_NSGA3


def main_3(data,staff_data,population_size,num_workstations,max_iterations,batch_time,elite_size,Px):
    best_solution=None
    each_best_results=[]
    best_pareto_front=None

    num_objectives = 3
    p = 4  # 参考点分割数，可根据问题调整,3的话刚刚好
    reference_points = generate_reference_points(num_objectives, p)

    # 初始化种群
    #返回：population,result_constraint
    population,_= init.initialize_population(data, staff_data, population_size, num_workstations)

    for generation in range(max_iterations):
        solutions,current_best_individual,pareto_front=nsga3_fitness(copy.deepcopy(population),batch_time,num_workstations,data,staff_data)

        if best_solution is None:
            best_solution = current_best_individual

        elif best_solution['rank'] < current_best_individual['rank']:
            pass  # 当前 best 更好，不修改

        elif best_solution['rank'] == current_best_individual['rank']:
            # 比如选 makespan 小的（或者你可以换成其他目标）
            if best_solution['makespan'] <= current_best_individual['makespan']:
                pass  # 当前 best 更好，不修改
            else:
                best_solution = current_best_individual

        else:
            # 当前 best 的 rank 比 current 差，更新
            best_solution = current_best_individual

        # 记录最优解
        each_best_results.append(current_best_individual)
        best_pareto_front=pareto_front
        # print(f"-----each_best_results------{each_best_results}")

        # 挑选出参与“繁殖”的个体（父代池）
        parents=tournament_selection_NSGA3(copy.deepcopy(solutions),elite_size)

        # 进行交叉，变异
        Child= Crossover_2.Crossover(copy.deepcopy(parents))

        # 全部交叉后遍历修改
        modified_crossover_Child=adjust_individual(copy.deepcopy(Child),data,num_workstations)

        # 进行变异
        mutation_Child= Mutation.mutation(copy.deepcopy(modified_crossover_Child), data, Px, num_workstations)
        print(f"---mutation_Child{mutation_Child}")
        next_generation=select_next_generation(mutation_Child,batch_time,num_workstations,data,staff_data,population_size)

        population=copy.deepcopy(next_generation)

    # 存储数据
    save_each_best_results_to_excel(each_best_results,Px,best_pareto_front)
    # # 画最后结果的甘特图
    # draw(best_solution, num_workstations, data, staff_data, batch_time)
    #
    # # 调用画图函数,画最后结果的散点图
    # # plot_pareto_fronts2(each_best_results)
    # plot_pareto_3d(each_best_results)
    # plot_individual_pareto_fronts(each_best_results)
    return best_solution,pareto_front



    # makespan_values = [x['makespan'] for x in each_best_results]
    # workload_values = [x['workload'] for x in each_best_results]
    # workload_variance = [x['workload_variance'] for x in each_best_results]
    # total_free_time_values = [x['total_free_time'] for x in each_best_results]
    # # === 调用绘图函数 ===
    # plot_results(makespan_values,workload_variance, workload_values, total_free_time_values)

def draw(best_solution,num_workstations, data, staff_data,batch_time):
    workstation_available_time = {station: {"free_intervals": [(float(0.0), float('inf'))], 'assigned_jobs': []} for station in generate_workstation(num_workstations)}
    tem_time=calculate_time(best_solution['individual'], workstation_available_time, batch_time, num_workstations, data, staff_data)
    examine_individual(best_solution, 23)
    # 画图，画出当前迭代最优解
    Gantt_lab.plot_gantt_chart(tem_time)

def select_next_generation(populations, batch_time, num_station, data, staff_data, pop_size):
    print(f"-----select_next_generation")
    print(f"populations{populations}")
    # 计算父代和子代的适应度
    sorted_solutions, best_solution,_ = nsga3_fitness(populations, batch_time, num_station, data, staff_data)

    # 选择适应度最优的 `pop_size` 个个体作为下一代
    selected_next_gen = sorted_solutions[:pop_size]

    # 返回选择后的下一代种群
    next_generation = [sol['individual'] for sol in selected_next_gen]

    return next_generation

def save_each_best_results_to_excel(each_best_results,Px, pareto_front,label="0707"):
    # 生成唯一文件名
    # timestamp = datetime.datetime.now()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"NSGA3_each_best_resu lts_0710{timestamp}.xlsx"

    records = []
    for i, result in enumerate(each_best_results):
        ind = result['individual']

        record = {
            "Generation": i + 1,
            "Makespan": result.get("makespan"),
            "Workload": result.get("workload"),
            "Workload Variance": result.get("workload_variance"),
            "Total Free Time": result.get("total_free_time"),
            "Rank": result.get("rank"),
            "Crowding Distance": result.get("crowding_distance"),
            # 编码信息（字符串表示）
            "Operation Codes": ", ".join(ind.get("operation_code", [])),
            "Machine Codes": ", ".join(ind.get("machine_code", [])),
            "Workstation Codes": json.dumps(ind.get("workstation_code", []), ensure_ascii=False),
            "Employ Codes": json.dumps(ind.get("employ_code", []), ensure_ascii=False),
            "Replace Ops": str(ind.get("replace_op", [])),
            'PX':Px,
            # 'pareto_front':pareto_front
        }
        records.append(record)

    df = pd.DataFrame(records)
    df.to_excel(filename, index=False)
    print(f"结果已保存到 Excel：{filename}")

    # 可选同时保存为 CSV
    df.to_csv(filename.replace(".xlsx", ".csv"), index=False, encoding='utf-8-sig')
    print(f"结果也保存为 CSV：{filename.replace('.xlsx', '.csv')}")

# # 只有当脚本作为主程序运行时，才会执行以下代码
# if __name__ == "__main__":
#     main_2()