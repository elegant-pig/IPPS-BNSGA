import copy
import random
from collections import OrderedDict, defaultdict, Counter

from adjust_workstation_machine_code import adjust_crossover_workstation_machines, adjust_crossover_workstation_code
from check_code import check_employ_allocation_conflicts
from examine_encoding import examine_workstation_machines_code, examine_workstation_code, examine_employ_code, \
    examine_result_employ_allocation, examine_individual
from generateBalance import generate_new_balance
from generateOperation import generate_operation_codes
from generate_Workstation import reverse_workstation_to_machines


def adjust_individual(populations,data,num):
    # print(populations)
    print(f"进来的编码都是没有调整的")
    modified_Child=[]

    for individual in populations:
        if 'individual' in individual:
            individual=individual['individual']
        # 调整or\op\ma
        child_op_ma, tem_data = adjust_operation_machine_codes(individual, data)
        # 调整人力平衡
        new_balance_codes,_ = generate_new_balance(copy.deepcopy(child_op_ma), tem_data)
        child_op_ma['balance_codes'] = new_balance_codes
        # 调整机器工作站：机器匹配
        new_wk_ma=adjust_workstation_machines(copy.deepcopy(child_op_ma),num)
        child_op_ma['workstation_machines']=copy.deepcopy(new_wk_ma)
        print(f'000child_op_ma00000{child_op_ma}')
        r,s=examine_workstation_machines_code(new_wk_ma,child_op_ma['machine_code'],num)
        if r:
            print(f"ok")
        else:
            raise ValueError(f"错误")
        print(f'----------point--------------')
        # 调整工作站编码
        new_wk=adjust_workstation_code(copy.deepcopy(child_op_ma),num)
        child_op_ma['workstation_code'] = copy.deepcopy(new_wk)
        # 调整员工编码
        staff_code=adjust_employ_code(copy.deepcopy(child_op_ma),num)
        child_op_ma['employ_code']=copy.deepcopy(staff_code)

        examine_individual(child_op_ma,num)

        modified_Child.append(child_op_ma)
    return modified_Child

def adjust_operation_code(offspring,data):

    # 创建一个空列表用于存储 C1 未选择的替换工序
    non_selected_operations = []
    # 从 C1_OR_CODE 提取已选择的工序编号
    selected_operations = [list(item.values())[0] for item in offspring['OR_CODE']]  # 提取工序编号，比如 [6, 12]

    # 遍历 tem_array，提取未选择的工序
    for operation_pair in offspring['replace_op']:
        for operation in operation_pair:
            if operation not in selected_operations:
                non_selected_operations.append(operation)
    data = data[~data['工序'].isin(non_selected_operations)]
    tem_data = data[['部件', '工序', '机器', '标准工时', '难易度', '前继工序', '前继工序数量']]

    _, operation_codes = generate_operation_codes(tem_data)
    # print(f"&&&&&&&&&&&&&&&&&")
    # print(f"正确的工序有！{operation_codes}")
    return tem_data,operation_codes
def adjust_operation_machine_codes(child,data):
    # 先调整or_code和op_code
    tem_data, right_operation_codes = adjust_operation_code(child, data)
    # 旧的编码可能有错误，且重复
    old_operation_codes = copy.deepcopy(child['operation_code'])


    # 调整工序和机器编码
    # 如果去重后的工序编码跟正确的工序编码长度不一致，则有重复工序
    if len(old_operation_codes) != len(set(old_operation_codes)):
        # print("有重复的工序")
        # 使用 OrderedDict 来保持顺序并去重
        ordered_dict = OrderedDict()
        # 记录去重掉的元素的位置
        removed_positions = []

        # 遍历原始列表并创建一个有序字典
        for idx, op in enumerate(old_operation_codes):
            if op not in ordered_dict:
                ordered_dict[op] = None  # 在字典中添加该元素
            else:
                removed_positions.append({'idx': idx, 'op': op})  # 如果元素重复，记录它的索引

        # 获取去重后的工序列表
        unique_operations = list(ordered_dict.keys())

        # 找出 right_operation_codes 中那些不在 C1['operation_code'] 中的工序
        missing_operations = [op for op in right_operation_codes if op not in unique_operations]
        # print(f"missing_operations{missing_operations}")

        if int(len(missing_operations)) + int(len(unique_operations)) != int(len(right_operation_codes)):
            # print("不仅重复，还出现了占用工序")
            for missing_op in missing_operations:
                replaced = False
                op_num = int(missing_op.split(',')[1])  # 获取操作编码中的工序

                for operation_pair in child['replace_op']:
                    if op_num in operation_pair:
                        # print("缺失的工序有替代工序")
                        # 缺失工序的替代工序
                        repalce_tem_op = [op for op in operation_pair if op != op_num]
                        for op in repalce_tem_op:
                            for i, current_op in enumerate(old_operation_codes):
                                # 找到了替换工序所在位置
                                if op == int(current_op.split(',')[1]):
                                    # 调整工序
                                    old_operation_codes[i] = missing_op
                                    # 调整机器
                                    child['machine_code'][i] = data[data['工序'] == int(op)]['机器'].values[0]
                                    replaced = True
                                    missing_operations.remove(missing_op)  # 删除已替换的工序
                                    break

                            if replaced:
                                break
                if replaced:
                    # print(f"missing_operations{missing_operations}")
                    break  # 跳出当前循环，处理下一个缺失工序

            if missing_operations:
                # print("还有工序没有添加进去，这些是没有可替换工序的工序")
                # 调整工序
                old_operation_codes[removed_positions[0]['idx']] = missing_operations[0]
                child['operation_code'] = old_operation_codes

                # 调整工序对应机器
                child['machine_code'][removed_positions[0]['idx']] =data[data['工序'] == int(missing_operations[0].split(',')[1])]['机器'].values[0]

            else:
                # 直接赋值，无须调整
                child['operation_code'] = old_operation_codes


        else:
            # 调整工序
            old_operation_codes[removed_positions[0]['idx']] = missing_operations[0]
            child['operation_code'] = old_operation_codes

            # 调整对应机器
            child['machine_code'][removed_positions[0]['idx']] = \
            data[data['工序'] == int(missing_operations[0].split(',')[1])]['机器'].values[0]

    elif set(child['operation_code']) == set(right_operation_codes):
        # 如果 operation_codes 中的工序与 C1 的工序完全一致，则无需调整
        print("生成的工序与 C1 的工序一致，无需调整。")
    else:
        # print("长度相等，但是工序对不上，说明有工序错误")
        # 找出 right_operation_codes 中那些不在 C1['operation_code'] 中的工序
        missing_operations = [op for op in right_operation_codes if op not in old_operation_codes]

        for missing_op in missing_operations:
            replaced = False
            op_num = int(missing_op.split(',')[1])  # 获取操作编码中的工序

            for operation_pair in child['replace_op']:
                if op_num in operation_pair:
                    # print("缺失的工序有替代工序")
                    # 缺失工序的替代工序
                    repalce_tem_op = [op for op in operation_pair if op != op_num]

                    for op in repalce_tem_op:
                        for i, current_op in enumerate(old_operation_codes):

                            # 找到了替换工序所在位置
                            if op == int(current_op.split(',')[1]):
                                old_operation_codes[i] = missing_op
                                replaced = True
                                missing_operations.remove(missing_op)  # 删除已替换的工序
                                # 调整机器编码
                                child['machine_code'][i] = data[data['工序'] == int(op)]['机器'].values[0]
                                break

                        if replaced:
                            break
            if replaced:
                break
        child['operation_code'] = old_operation_codes

    return child,tem_data
def adjust_workstation_machines(individual,num):
    new_machine = copy.deepcopy(individual['machine_code'])  # 新的机器编码
    old_workstation_machine = copy.deepcopy(individual['workstation_machines'])  # 旧的工作站：机器匹配编码
    new_balance=copy.deepcopy(individual['balance_code'])

    need_machine_unique = set(new_machine)  # 新的机器列表
    old_machine = set(old_workstation_machine.values())  # 原来的机器列表
    print(f"新的机器列表{need_machine_unique}")
    print(f"旧的机器列表{old_machine}")


    new_has_old_hasnt = need_machine_unique - old_machine  # 需要添加的机器
    old_has_new_hasnt = old_machine - need_machine_unique  # 需要删除的机器

    # # 遍历 old_workstation_machine 字典，按机器类型分类
    # machines_to_workstations = defaultdict(list)
    # for station, machine in old_workstation_machine.items():
    #     machines_to_workstations[machine].append(station)

    for station, machine in old_workstation_machine.items():
        if machine in old_has_new_hasnt:
            old_workstation_machine[station] = ''

    new_machine_balance=get_machine_balance_target(new_machine,new_balance)
    old_machine_balance=get_old_machine_count(old_workstation_machine)
    print(f"-----old_machine_balance----{old_machine_balance}")
    # 构造空位列表
    empty_stations = [s for s, m in old_workstation_machine.items() if m == '']
    print(f"empty_stations{empty_stations}")

    # 获取所有机器种类全集
    all_machines = set(new_machine_balance.keys())
    adjusted_machines = set()  # 存储已经被处理（调整）过的机器
    print(f"=====old_machine_balance====={old_machine_balance}")
    # 处理每个机器的差值
    for machine in all_machines:
        print(f"machines{machine}")
        need = new_machine_balance.get(machine, 0)
        current = old_machine_balance.get(machine, 0)
        print(f"need{need}")
        print(f"current{current}")

        # 如果这个机器是新添加的，就先加入
        if machine not in old_machine_balance:
            old_machine_balance[machine] = 0

        # delta = need - current
        try:
            delta = need - int(current)
        except ValueError:
            print(f"当前字段 current={current} 无法转换为整数，跳过或报错")
            print(f"++++old_machine_balance++++{old_machine_balance}")

            raise

        if delta > 0:
            # 需要新增 delta 个
            for _ in range(delta):
                if empty_stations:
                    # 从最后选一个空的工作站
                    chosen = empty_stations.pop()
                    print(f"chosen{chosen}")
                    old_workstation_machine[chosen] = machine
                else:
                    # 无空位，随机从其他机器中替换一个
                    # candidates = [
                    #     s for s, m in old_machine_balance.items()
                    #     if m != machine and m not in adjusted_machines
                    # ]

                    # candidates = [
                    #     s for s, m in old_machine_balance.items()
                    #     if m != machine and s not in adjusted_machines and m > 1
                    # ]

                    candidates = [
                        s for s in old_machine_balance.keys()
                        if s != machine and s not in adjusted_machines and old_machine_balance[s] > 1
                    ]

                    print(f"----candidates----{candidates}")
                    if candidates:
                        chosen = find_closest_candidate_without_current_idx(machine, candidates, new_machine)
                        # chosen = random.choice(candidates)
                        print(f"222chosen{chosen}")
                        old_machine_balance[chosen]-=1
                        old_machine_balance[machine]+=1
                        print(f"3333old_machine_balance3333{old_machine_balance}")
                    else:
                        candidates = [
                            s for s, m in old_machine_balance.items()
                            if m != machine and m not in adjusted_machines
                        ]
                        chosen = find_closest_candidate_without_current_idx(machine, candidates, new_machine)

                        # chosen = random.choice(candidates)
                        print(f"222chosen{chosen}")
                        # print(type(old_machine_balance[chosen]))
                        old_machine_balance[chosen] -= 1
                        old_machine_balance[machine] += 1
                        print(f"11111111adjusted_machines11111111111{adjusted_machines}")
                        # raise ValueError(f'youwenti')
        elif delta < 0:
            # 需要删除 |delta| 个
            machine_stations = [s for s, m in old_machine_balance.items() if m == machine]
            for _ in range(abs(delta)):
                if machine_stations:
                    chosen = random.choice(machine_stations)
                    old_machine_balance[chosen] =''
                    empty_stations.append(chosen)
            print(f"4444old_machine_balance4444{old_machine_balance}")

        adjusted_machines.add(machine)

        # 第二次 pass：分配剩余的 new_has_old_hasnt（新增但未出现在原分配中的机器）
    for machine in new_has_old_hasnt:
        # 优先补空位
        if empty_stations:
            chosen = empty_stations.pop()
            old_workstation_machine[chosen] = machine
        else:
            # 无空位则尝试替换未调整机器
            candidates = [
                s for s, m in old_workstation_machine.items()
                if m not in adjusted_machines
            ]
            if candidates:
                # chosen = random.choice(candidates)
                chosen = find_closest_candidate_without_current_idx(machine, candidates, new_machine)

                old_workstation_machine[chosen] = machine
            else:
                # 统计每个机器在 old_workstation_machine 中的出现次数
                machine_counter = Counter(old_workstation_machine.values())

                # 找出出现次数最多的机器（可能有多个并列最多）
                max_count = max(machine_counter.values())
                most_common_machines = [m for m, c in machine_counter.items() if c == max_count]

                # 从出现最多的机器中任选一个
                target_machine = random.choice(most_common_machines)

                # 找出使用该机器的所有工作站
                target_workstations = [s for s, m in old_workstation_machine.items() if m == target_machine]

                # 从这些工作站中任选一个进行替换
                chosen = random.choice(target_workstations)
                # chosen = find_closest_candidate_without_current_idx(machine, target_workstations, new_machine)

                # 替换为当前的 machine（即你希望分配的新机器）
                old_workstation_machine[chosen] = machine
                # raise ValueError(f"机器 {machine} 没有空位也无法替换其他未调整机器")

        adjusted_machines.add(machine)

        # 最后 pass：确保没有空位
    for station, machine in old_workstation_machine.items():
        if machine == '':
            raise ValueError(f"最终仍有空工作站 {station} 未被分配，请检查逻辑")

        # 最终确保 machine 的分布精确匹配 machine_code 中出现的机器
    final_machines = set(old_workstation_machine.values())
    if final_machines != need_machine_unique:
        raise ValueError(f"最终机器种类不一致，分配中包含 {final_machines}，但只应包含 {need_machine_unique}")

    # 更新结果回到个体中
    r,s=examine_workstation_machines_code(old_workstation_machine,new_machine,num)
    if r:
        return old_workstation_machine
    else:
        print(f"问题是{r}")
        raise ValueError(f"有问题")


def adjust_workstation_code(individual,num):
    print(f"-----------进入adjust_workstation_code")
    r, s = examine_workstation_machines_code(individual['workstation_machines'], individual['machine_code'], num)
    if r:
        print(f"正确")
    else:
        print(f"问题是{r}")
        raise ValueError(f"有问题")

    new_workstaion_code=adjust_crossover_workstation_code(individual,num)

    if examine_workstation_code(new_workstaion_code,num):
        return new_workstaion_code
    else:
        raise ValueError(f"！！！！！！！！！！！！！！！！！！！")

# def adjust_workstation_code(individual,num):
#     all_wk=list(individual['workstation_machines'].keys())
#     old_machine=list(set(list(individual['workstation_machines'].values())))
#     new_machine=list(individual['machine_code'])
#     # 扁平化 + 去重
#     all_stations = set()  # 用集合自动去重
#
#     for sublist in copy.deepcopy(individual['workstation_code']):
#         for station in sublist:
#             all_stations.add(station)
#
#     # 转成列表（如果需要排序可以加sorted）
#     old_wk = sorted(all_stations, key=station_sort_key)



def station_sort_key(s):
    # 先按字母排序，再按数字排序
    return (s[0], int(s[1:]))


def adjust_employ_code(individual,num):
    print(f"-----进入adjust_employ_code")
    result_employ_allocation = individual['result_employ_allocation']
    staff_code=copy.deepcopy(individual['employ_code'])
    workstation_code=copy.deepcopy(individual['workstation_code'])
    r, s = examine_result_employ_allocation(result_employ_allocation, num)
    if r:
        print(f"成功")
    else:
        print(f"问题是{s}")
        raise ValueError("问题")

    r1=examine_workstation_code(individual['workstation_code'],num)
    if r1:
        print(f"成功")
    else:
        raise ValueError('工作站不对')

    conflicts_same_station, conflicts_same_employ = check_employ_allocation_conflicts(result_employ_allocation)
    if conflicts_same_station or conflicts_same_employ:
        print(f"说明result_employ_allocation有问题，需要调整")
        raise ValueError(f"@@@@@@@")
        # individual = adjust_crossover_result_employ_allocation(individual, num)

    # 使用字典来存储每个 workstation 最后的 employ 值
    employ_mapping = {item['workstation']: item['employ'] for item in result_employ_allocation}
    print(f"employ_mapping{employ_mapping}")

    # 看下员工分配跟工作站分配是否数量上对的上
    for i,wk_list in enumerate(workstation_code):
        wk_len=len(wk_list)
        employ_len=len(staff_code[i])
        print(f'工作站长度{wk_len},员工分配长度{employ_len}')
        # 调整员工编码长度
        if wk_len<employ_len:
            individual['employ_code'][i]=individual['employ_code'][i][:wk_len]
            print(f"这个位置的员工编码是{ individual['employ_code'][i]}")
        elif wk_len>employ_len:
            individual['employ_code'][i].extend([{'workstation': '', 'employ': 0} for _ in range((wk_len) - employ_len)])
        else:
            print(wk_len==employ_len)
            print(f"长度一致")
    staff_code=copy.deepcopy(individual['employ_code'])
    print(f"staff_code{staff_code}")
    modified_staff_code=[]
    # 修改employ_code
    print(f"----workstation_code------{workstation_code}")
    print(f"------staff_code------{staff_code}")
    for i,(wk_list,employ_list) in enumerate(zip(workstation_code,staff_code)):
        print(f"employ_list{employ_list}")
        print(f"wk_list{wk_list}")

        # 初始化当前这一行（即一个工序的多工作站员工分配）
        current_op_staff_list = []

        if len(wk_list)!=len(employ_list):
            raise ValueError(f"长度不相等")
        for j,(w,e) in enumerate(zip(wk_list,employ_list)):
            print(f"373737")
            # if isinstance()
            expected_employ=employ_mapping[w]
            # actual_workstation = e.get('workstation')
            # actual_employ = e.get('employ')
            # 将一个 {'workstation': w, 'employ': expected_employ} 放入当前工序的员工分配中
            current_op_staff_list.append({'workstation': w, 'employ': expected_employ})
            # modified_staff_code[i][j]['workstation']=w
            # modified_staff_code[i][j]['employ'] = expected_employ
        # 每个工序的员工分配是一个列表，添加到最终结果中
        modified_staff_code.append(current_op_staff_list)
                # if actual_workstation == w and actual_employ == expected_employ:
                #     print(f"未修改时的值{modified_staff_code}")
                #     print(f"这个位置的是{modified_staff_code[i][j]}")
                #     print(f"配对成功")
                # else:
                #     print(f"未修改时的值{modified_staff_code}")
                #     print(f"这个位置的是{modified_staff_code[i][j]}")
                #     modified_staff_code[i][j]['workstation']=w
                #     modified_staff_code[i][j]['employ'] = expected_employ
                #     print(f"修改成功")
    print(f"修改完后立马查看{modified_staff_code}")
    individual['employ_code']=modified_staff_code
    r2,s2=examine_employ_code(modified_staff_code,num)
    if r2:
        print(f"成功")
        return modified_staff_code
    else:
        print(f"result_employ_allocation{result_employ_allocation}")
        print(f"问题是{s2}")
        raise ValueError

def get_machine_balance_target(machine_code, balance_code):
    machine_balance = defaultdict(int)
    for m, b in zip(machine_code, balance_code):
        machine_balance[m] += b
    return dict(machine_balance)

def get_empty_workstations(workstation_machines):
    return [station for station, machine in workstation_machines.items() if machine == '']

def get_old_machine_count(old_workstation_machines):
    machine_count = defaultdict(int)
    for machine in old_workstation_machines.values():
        if machine != '':
            machine_count[machine] += 1
        # else:
            # raise ValueError(f"有空值，错误")
    return dict(machine_count)

def adjust_workstation_and_workstation_machine_code(child,num):
    workstation_code=[]
    print()
    workstation_to_machines=copy.deepcopy(child['workstation_machines'])
    machine_code=copy.deepcopy(child['machine_code'])
    correct_machine_list = list(set(machine_code))  # 正确的机器列表，去重
    r,s=examine_workstation_machines_code(workstation_to_machines,correct_machine_list,num)
    old_workstation_code = copy.deepcopy(child['workstation_code'])

    # 判断并修改workstation_to_machines值
    if r:
        print(f"说明机器都正确，但是工作站跟机器的关系不知道有没有要调整的")
    else:
        # 判断是哪种类型的不正确
        if s==1:
            raise ValueError(f'工作站缺少，原来的编码就有问题')
        elif s==2:
            raise ValueError(f'工作站和机器都缺失')
        elif s==3:
            print(f"***********************")
            print(f"唯一可以解决的问题，工作站没问题，机器对不上")
            tem=adjust_workstation_to_machines_code(workstation_to_machines,machine_code)
            workstation_to_machines=copy.deepcopy(tem)
            print(f"***********************")

        else:
            raise ValueError(f"特殊情况？？？？")

    # 接下来可以修改workstaion_code了
    tem_wk_code=adjust_workstation_code(workstation_to_machines,machine_code,old_workstation_code)


    return tem_wk_code,workstation_to_machines

def adjust_workstation_to_machines_code(workstation_to_machines,machine_code):
    wrong_machine = set(workstation_to_machines.values())  # workstation_to_machines中的机器列表去重
    correct_machine = list(set(machine_code))  # 正确的机器列表，去重
    correct_machine_list=copy.deepcopy(correct_machine)
    add_machine = set(correct_machine_list) - set(wrong_machine)  # 正确中有但错误中没有的
    del_machine = set(wrong_machine) - set(correct_machine_list)  # 错误中有但正确中没有的
    print(f"wrong_machine{wrong_machine}")
    print(f"correct_machine{correct_machine}")
    print(f"add_machine{add_machine}")
    print(f"del_machine{del_machine}")

    tem_workstation_to_machines=copy.deepcopy(workstation_to_machines)
    a_m=copy.deepcopy(list(add_machine))
    d_m=copy.deepcopy(list(del_machine))


    print(f'未修改的wk_ma{tem_workstation_to_machines}')
    # 先移除错误的机器
    while d_m and d_m != set():
        for wk, m in workstation_to_machines.items():
            if m in del_machine:
                tem_workstation_to_machines[wk] = ''
                if m in d_m:
                    d_m.remove(m)
                # d_m.remove(m) #不能删除，万一这个机器出现了两次，那么第二次就发现布料了，不型，要删除，因为出不了循环，但要换个形式
        print(f"170170调整下的wk_ma: {tem_workstation_to_machines}")

    # 再添加新的机器
    if not a_m and a_m==set():
        print(f'需要添加的机器{a_m}')
        # 要添加的机器为空，说明原来的机器列表包含或者大于新的机器列表，随机选择机器就可以了
        if '' in tem_workstation_to_machines.values():
            # 说明原来的机器分配跟新的一致，不需要调整
            print()
        else:
            raise ValueError(f"目前看来是不对的，因为不需要添加的话，旧的肯定要删除，不然无需调整")

        # 先找如果有删掉的机器
        for wk,m in tem_workstation_to_machines.items():
            if m=='':
                select_machine=random.choice(correct_machine_list)
                tem_workstation_to_machines[wk]=select_machine
        # 第一次检查出这里有问题
        print(f"1.....{tem_workstation_to_machines}")
    else:
        print(f"进来的工作站：机器={tem_workstation_to_machines}")
        # 说明原来的机器列表跟新的交叉，要不就是新的包含旧的
        if '' in tem_workstation_to_machines.values():
            print(f"①")
            # 说明新的机器跟旧的是交叉关系
            # 找出工作站对应机器为‘’的
            empty_stations = [k for k, v in tem_workstation_to_machines.items() if v == '']
            # print(empty_stations)  # 输出：['L2', 'L3']
            if len(empty_stations)==len(a_m):
                print(f"②")
                # for e_wk,machine in list(zip(empty_stations,a_m)):
                #     tem_workstation_to_machines[e_wk]=machine
                #     a_m.remove(machine)
                #     empty_stations.remove(e_wk)
                while empty_stations and a_m:
                    tem_workstation_to_machines[empty_stations.pop(0)] = a_m.pop(0)

            elif len(empty_stations)<len(a_m):
                # 说明可以匹配机器的工作站不够，要从其他的工作站中拿一点过来
                # 即要选择删掉一些其他机器，再分给新的机器，所以不会出现键为空的情况
                print(f"③")


                # 先将可以分配的都分配了
                # for machine in a_m:
                #     select_tem_wk=random.choice(empty_stations)
                #     tem_workstation_to_machines[select_tem_wk]=machine
                #     a_m.remove(machine)
                #     empty_stations.remove(select_tem_wk)
                while a_m and empty_stations:
                    machine = a_m.pop(0)
                    select_tem_wk = random.choice(empty_stations)
                    empty_stations.remove(select_tem_wk)
                    tem_workstation_to_machines[select_tem_wk] = machine
                machine_to_workstations = reverse_workstation_to_machines(tem_workstation_to_machines)
                #之后再从别的工作站拿一些来
                tem_workstation_to_machines=choose_other_wk_to_new_machine(machine_to_workstations, a_m, copy.deepcopy(tem_workstation_to_machines))
            elif len(empty_stations)>len(a_m):
                # 先将可以新机器分给工作站，剩下的再随机选一个新机器
                print(f"④")
                # for wk in list(empty_stations):
                #     if a_m and a_m!=set():
                #         select_tem_machine=random.choice(a_m)
                #         tem_workstation_to_machines[wk]=select_tem_machine
                #         a_m.remove(select_tem_machine)
                #         empty_stations.remove(wk)
                #     else:
                #         select_tem_machine=random.choice(list(machine_to_workstations.keys()))
                #         tem_workstation_to_machines[wk]=select_tem_machine
                while empty_stations:
                    wk = empty_stations.pop(0)  # 每次取第一个空工位

                    if a_m:
                        select_tem_machine = random.choice(list(a_m))
                        tem_workstation_to_machines[wk] = select_tem_machine
                        a_m.remove(select_tem_machine)
                    else:
                        machine_to_workstations = reverse_workstation_to_machines(tem_workstation_to_machines)
                        select_tem_machine = random.choice(list(machine_to_workstations.keys()))
                        tem_workstation_to_machines[wk] = select_tem_machine

            print(f"2.....{tem_workstation_to_machines}")

        else:
            print(f"⑤")
            # 说明新的机器包含旧的机器，那旧需要删掉一些机器，再将新的机器分配进去，这里machine_to_workstations不太可能出现键为空
            machine_to_workstations = reverse_workstation_to_machines(tem_workstation_to_machines)

            tem_workstation_to_machines=choose_other_wk_to_new_machine(machine_to_workstations, a_m, copy.deepcopy(tem_workstation_to_machines))
            print(f"3.....{tem_workstation_to_machines}")

    print(f"4.....{tem_workstation_to_machines}")
    # 检查是否都分配正确了
    r,s=examine_workstation_machines_code(tem_workstation_to_machines,correct_machine_list,num)
    if r:
        return tem_workstation_to_machines
    else:
        print(f"____________________")
        print(f"错误类型是{s}")
        print(f"____________________")
        print(f"correct_machine{correct_machine_list}")
        raise ValueError(f"有问题，不能传值回去")

def choose_other_wk_to_new_machine(machine_to_workstations,add_machine,tem_workstation_to_machines):
    # 提取出机器对应值的数量大于1的，即分配超过一个工作站的机器
    machine_to_workstations_filtered = {k: v for k, v in machine_to_workstations.items() if len(v) > 1}

    for v_m in list(add_machine):
        # select_tem_wk=random.choice(machine_to_workstations_filtered)
        random_m, random_wks = random.choice(list(machine_to_workstations_filtered.items()))
        final_wk = random.choice(random_wks)  # 从可选的机器列表中选择一个工作站
        tem_workstation_to_machines[final_wk] = v_m  # 往wk_ma中这个工作站填入新的机器类型
        add_machine.remove(v_m)  # 删除掉已经加入的新的机器类型
        del machine_to_workstations_filtered[random_m]

    return tem_workstation_to_machines


def find_closest_candidate_without_current_idx(machine, candidates, machine_code):
    """
    找 candidates 中距离 machine_code 中所有出现 machine 的位置最近的一个。
    这里用所有出现位置做基准，找到候选机器出现位置与基准最接近的机器。
    """
    # 找 machine 出现位置
    machine_positions = [i for i, m in enumerate(machine_code) if m == machine]
    if not machine_positions:
        # machine没出现过，随机返回一个
        return random.choice(candidates)

    best_candidate = None
    best_distance = float('inf')

    for c in candidates:
        positions = [i for i, m in enumerate(machine_code) if m == c]
        if not positions:
            continue
        # 计算最小距离：candidate所有位置和machine所有位置的距离的最小值
        min_dist = min(abs(p1 - p2) for p1 in machine_positions for p2 in positions)
        if min_dist < best_distance:
            best_distance = min_dist
            best_candidate = c

    return best_candidate