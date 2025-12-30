import copy
import random
from collections import defaultdict

from check_code import check_wk_ma, check_machines_to_workstations, check_adjust_workstation
from examine_encoding import examine_workstation_machines_code, examine_workstation_code

# def adjust_machine_in_workstation_machines(individual,num):



def adjust_crossover_workstation_machines(individual,num):
    new_machine = copy.deepcopy(individual['machine_code'])  # 新的机器编码
    old_workstation_code=individual['workstation_code']  # 旧的工作站编码
    old_workstation_machine = copy.deepcopy(individual['workstation_machines'])  # 旧的工作站：机器匹配编码

    need_machine_unique = set(new_machine) #新的机器列表
    print(f"need_machine_unique{need_machine_unique}")
    old_machine = set(old_workstation_machine.values()) #原来的机器列表

    new_has_old_hasnt = need_machine_unique - old_machine #需要添加的机器
    old_has_new_hasnt = old_machine - need_machine_unique #需要删除的机器

    # 遍历 old_workstation_machine 字典，按机器类型分类
    machines_to_workstations = defaultdict(list)
    for station, machine in old_workstation_machine.items():
        machines_to_workstations[machine].append(station)

    # 调整机器和workstation_machines
    if need_machine_unique == old_machine and new_has_old_hasnt==set() and old_has_new_hasnt == set():
        # 如果需要的机器和旧的机器一致，即new_has_old_hasnt和old_has_new_hasnt都为空
        print(f"说明新旧编码需要的机器都一致")
        # # 根据人力平衡取调整workstation_machines即可
        # individual=adjust_crossover_workstation_machines_according_balance(individual,23)
    elif need_machine_unique != old_machine and new_has_old_hasnt==set() and old_has_new_hasnt != set():
        # 如果新旧机器不一样，且旧的机器包含新的机器，就需要将旧机器中的工作站分给别的工作站，之后把这个多余的机器删除
        print(f"新旧编码不相同，没有新的机器出现，旧的编码有多余的机器需要剔除")

        new_value = []
        # 合并需要踢掉的机器所分配的工作站
        for key in old_has_new_hasnt:
            if key in machines_to_workstations:
                new_value.extend(machines_to_workstations[key])  # 合并值
        # 删除多余的机器
        for key in list(old_has_new_hasnt):
            print(f"key{key}")
            machines_to_workstations.pop(key, None)  # 避免 KeyError
            old_has_new_hasnt.remove(key)

        # # 按照已有的工作站数量排序，获取最少的键(机器)
        sorted_keys = sorted(machines_to_workstations.keys(), key=lambda k: len(machines_to_workstations[k]))
        # 先找到所有值为空的键
        empty_keys = [key for key in sorted_keys if not machines_to_workstations[key]]

        # 将未分配的工作站分配到新的机器上
        for workstation in new_value:
            if empty_keys:
                k = empty_keys.pop(0)  # 先从空的键里取一个
            else:
                k = sorted_keys.pop(0)  # 选择当前值最少的键
                sorted_keys = sorted(machines_to_workstations.keys(),key=lambda k: len(machines_to_workstations[k]))  # 重新排序
            machines_to_workstations[k].append(workstation)  # 分配工作站

        # 检查工作站是否齐全
        check_machines_to_workstations(machines_to_workstations,num)
    elif need_machine_unique != old_machine and new_has_old_hasnt!=set() and old_has_new_hasnt == set():
        # 新旧机器不一样，新的机器包含旧的机器，即出现了新的机器，需要添加这个机器，并且把别的工作站分过来
        print(f"新旧编码不相同，有新的机器出现，但是没有需要剔除的机器")
        for wk in new_has_old_hasnt:
            machines_to_workstations[wk]=[]
        # 检查工作站是否齐全
        check_machines_to_workstations(machines_to_workstations,num)
    elif need_machine_unique != old_machine and new_has_old_hasnt!=set() and old_has_new_hasnt != set():
        # 新旧机器不一致，且新旧机器交叉，先把新的添加上，再把旧的剔除
        print(f"有新的机器出现，且旧的机器中有用不上需要剔除的")
        # 添加新的机器
        for wk in list(new_has_old_hasnt):
            machines_to_workstations[wk]=[]
            new_has_old_hasnt.remove(wk)
        # 合并旧的多余的机器的工作站，即这些工作站是要分配到别的工作站上的
        new_value=[]
        for key in old_has_new_hasnt:
            if key in machines_to_workstations:
                new_value.extend(machines_to_workstations[key])

        # 删除多余的机器
        for key in list(old_has_new_hasnt):
            print(f"key{key}")
            machines_to_workstations.pop(key, None)  # 避免 KeyError
            old_has_new_hasnt.remove(key)

        # 如果键对应的值是None或者是空列表，就取出来
        empty_keys = [k for k, v in machines_to_workstations.items() if not v]

        # 将未分配的工作站分配到新的机器上
        for workstation in new_value:
            if empty_keys:
                k = empty_keys.pop(0)
                machines_to_workstations[k].append(workstation)  # 分配工作站
            else:
                k = random.choice(list(machines_to_workstations.keys()))
                machines_to_workstations[k].append(workstation)  # 分配工作站

        # 检查工作站是否齐全
        check_machines_to_workstations(machines_to_workstations,num)
    else:
        print(f"我看看还有什么情况")
        raise ValueError("其他情况")

    print(f'检查检查检查检查检查检查检查')
    print(f"machines_to_workstations{machines_to_workstations}")
    print(f'检查检查检查检查检查检查检查')

    # 检查调整后的机器是否正确
    tem_modified_machine=set(machines_to_workstations.keys())
    print(f"168168")
    print(f"tem_modified_machine{tem_modified_machine}")
    tem_new_has_old_hasnt=need_machine_unique-tem_modified_machine
    tem_old_has_new_hasnt=tem_modified_machine- need_machine_unique
    print(f"tem_new_has_old_hasnt{tem_new_has_old_hasnt}")
    print(f"tem_old_has_new_hasnt{tem_old_has_new_hasnt}")
    if need_machine_unique == tem_modified_machine and tem_new_has_old_hasnt==set() and tem_old_has_new_hasnt == set():
        tem_array_wk_ma = {v: k for k, values in machines_to_workstations.items() for v in values}
        print(f"workstation_machines转化成tem_array_wk_ma{tem_array_wk_ma}")
        individual['workstation_machines']=tem_array_wk_ma
        individual=adjust_crossover_workstation_machines_according_balance(individual,machines_to_workstations,num)
        # print(f"修改完的个体的workstation_machines值是{}")
    else:
        raise ValueError(f"报错，但不是不知道具体原因，再改下")

    examine_workstation_machines_code(individual['workstation_machines'],individual['machine_code'],num)

    return tem_array_wk_ma
def adjust_crossover_workstation_machines_according_balance(individual,machines_to_workstations,num):
    print(f"根据人力平衡调整workstation_machines，传进来的值保证机器、人力平衡都是准确的，只是分配的工作站不对")
    tem_give_wk=[] #这是可以分一部分工作站出去的机器
    tem_need_wk=[] #这是要补一部分工作站进来的机器
    p_tem_need_wk=[]#这是要补一部分工作站进来的机器,且现在值为0
    b_tem_wk=[]#这个平衡了
    balance_code=individual['balance_code']
    machine_code=individual['machine_code']
    # machines_to_workstations = defaultdict(list)
    # # 遍历 old_workstation_machine 字典，按机器类型分类
    # for station, machine in individual['workstation_machines'].items():
    #     machines_to_workstations[machine].append(station)
    print(f"182182")
    print(f"机器编码{individual['machine_code']}")
    print(f"machines_to_workstations{machines_to_workstations}")
    # 计算差值
    tem_give_wk,tem_need_wk,b_tem_wk,p_tem_need_wk=calculate_crossover_balance(machine_code,balance_code,machines_to_workstations)

    # 开始调整
    for dictionary in tem_need_wk:
        # k1是机器,v1是这个机器需要补充多少个工作站
        for k1,v1 in dictionary.items():
            if any(k1 in d for d in p_tem_need_wk):
                # 优先处理这个机器
                if tem_give_wk:
                    # 选择一个工作站
                    selected_item = random.choice(tem_give_wk)
                    # k2是可以分出去的机器，v2是可以分出去的值
                    for k2,v2 in selected_item.items():
                        # 从这个机器中随机选一个工作站分出去
                        select_wk=random.choice(machines_to_workstations[k2])
                        # 添加到machines_to_workstations中
                        machines_to_workstations[k1].append(select_wk)
                        # 将这个原来工作站所在的机器的位置中删掉
                        machines_to_workstations[k2].remove(select_wk)
                        # tem_give_wk,tem_need_wk,b_tem_wk,p_tem_need_wk=calculate_crossover_balance(machine_code, balance_code, machines_to_workstations)
                else:
                    # 从别的地方给他补充
                    max_key = max(machines_to_workstations, key=lambda k: len(machines_to_workstations[k]))
                    max_value = machines_to_workstations[max_key]
                    c_wk = random.choice(max_value)
                    machines_to_workstations[k1].append(c_wk)  # 添加到这个机器中
                    machines_to_workstations[max_key].remove(c_wk)  # 从原来的机器中删除
                    # tem_give_wk, tem_need_wk, b_tem_wk, p_tem_need_wk = calculate_crossover_balance(machine_code, balance_code,machines_to_workstations)
            else:
                # 随机选择一个策略 0表示不添加了，之后过，1表示从别的工作站中拿一个过来
                strategy = random.choice([0, 1])
                max_key = max(machines_to_workstations, key=lambda k: len(machines_to_workstations[k]))
                max_value = machines_to_workstations[max_key]
                if strategy==0:
                    print(f"不做更改")
                else:
                    c_wk=random.choice(max_value)
                    machines_to_workstations[k1].append(c_wk)  # 添加到这个机器中
                    machines_to_workstations[max_key].remove(c_wk)  # 从原来的机器中删除
                # tem_give_wk,tem_need_wk,b_tem_wk,p_tem_need_wk=calculate_crossover_balance(machine_code, balance_code, machines_to_workstations)

    _,_,_,check_p_tem_need_wk=calculate_crossover_balance(machine_code,balance_code,machines_to_workstations)
    print(f"227227")
    print(f"机器编码{individual['machine_code']}")
    print(f"machines_to_workstations{machines_to_workstations}")

    for machine, stations in machines_to_workstations.items():
        if not stations:  # 如果列表为空
            raise ValueError(f"机器 {machine} 没有对应的工作站，无法反转！")

    reversed_dict = {station: machine for machine, stations in machines_to_workstations.items() for station in stations}

    # # 反转键值
    # reversed_dict = {station: machine for machine, stations in machines_to_workstations.items() for station in stations}
    # 按键排序
    sorted_reversed_dict = dict(sorted(reversed_dict.items(), key=lambda x: x[0]))
    individual['workstation_machines'] = sorted_reversed_dict

    if check_p_tem_need_wk:
        individual=adjust_crossover_workstation_machines_according_balance(individual,machines_to_workstations,num)
        # raise ValueError("还有问题，有机器没分配到工作站")

    result_wk,sign=examine_workstation_machines_code(individual['workstation_machines'],individual['machine_code'],num)

    if result_wk:
        print(f"正确")
        return individual
    else:
        print(sign)
        raise ValueError("workstation_machines编码不对")
def calculate_crossover_balance(machine_code,balance_code,machines_to_workstations):
    tem_give_wk=[]
    p_tem_need_wk=[]
    tem_need_wk=[]
    b_tem_wk=[]

    # 创建一个字典来存储 machine 对应的 balance 之和
    new_machine_balance_sum = defaultdict(int)
    # 遍历 machine 和 balance，累加对应 machine 的 balance 值

    # 这是调整后的编码新的人力平衡（新的），‘机器’：数量，
    for m, b in zip(machine_code, balance_code):
        new_machine_balance_sum[m] += b
    print(f"每个机器对应的人力平衡{new_machine_balance_sum}")

    # 这是旧的人力平衡的编码，将其变成‘机器’：数量的方式
    old_machine_balance_sum = {key: sum(1 for item in value if item) for key, value in machines_to_workstations.items()}

    # # 找出‘值’不相等的键  Eg:{'B': (3, 4), 'D': (2, 1)}前面的是需要的，后面是现有的
    # differences = {key: (new_machine_balance_sum[key], old_machine_balance_sum[key]) for key in new_machine_balance_sum
    #                if new_machine_balance_sum.get(key) != old_machine_balance_sum.get(key)}

    # 找出‘值’不相等的键
    differences = {
        key: (new_machine_balance_sum[key], old_machine_balance_sum[key])
        for key in new_machine_balance_sum
        if key in old_machine_balance_sum and new_machine_balance_sum[key] != old_machine_balance_sum[key]
    }

    # 记录差值
    for key, value in differences.items():
        if value[1] > value[0]:
            # 如果现有的比需要的多，说明可以给出去
            tem_b = value[1] - value[0]
            tem_give_wk.append({key: tem_b})  # 机器:可以给出去的数量
        elif value[1] < value[0]:
            tem_b = value[0] - value[1]
            tem_need_wk.append({key: tem_b})
            if value[1] == 0:
                p_tem_need_wk.append({key})
        elif value[1] == value[0] == 0:
            raise ValueError("出错了，怎么可能需求为0，且。。。")
        else:
            print(f"这个值平衡了，先不动")
            b_tem_wk.append({key: value[1]})
    return tem_give_wk,tem_need_wk,b_tem_wk,p_tem_need_wk

def adjust_crossover_workstation_code(individual,num):
    print(f">>>>>>>>>>>>>>>>>>>6")
    print(individual)
    print(f"进入adjust_crossover_workstation_code")
    print(individual['workstation_machines'])

    r,s=examine_workstation_machines_code(individual['workstation_machines'],individual['machine_code'],num)
    if r:
        print(f"成功")
    else:
        print(r)
        raise ValueError("错误")

    # 这里进来的workstation_machines都是正确的
    # 缺失的工作站
    lose_wk=[]
    # 将workstation_machines转化成机器：[工作站]
    machines_to_workstations = defaultdict(list)
    # 遍历 old_workstation_machine 字典，按机器类型分类
    for station, machine in individual['workstation_machines'].items():
        machines_to_workstations[machine].append(station)
    print(f"machines_to_workstations1{machines_to_workstations}")

    empty_keys = [k for k, v in machines_to_workstations.items() if not v]
    print(f"301301")
    print(f"empty_keys{empty_keys}")
    if empty_keys:
        print(f"302302")
        print(f"有机器完全没有分配工作站！！！，有问题")

    # 提取所有机器的值，去重,即提取所有工作站
    unique_all_workstations = set()
    for values in machines_to_workstations.values():
        unique_all_workstations.update(values)  # 把每个键的值列表加入集合


    if check_adjust_workstation(individual['workstation_code'],num):
        print("两个列表的值相同（忽略顺序）")
    else:
        print("现在的编码缺失了工作站")
        # 找到现在缺失的机器，优先在未选择的机器中选择


        unique_current_workstations_first = sorted(set(wk for sublist in individual['workstation_code'] for wk in sublist))
        lose_wk=set(unique_all_workstations)-set(unique_current_workstations_first)
        print(f"unique_workstations{unique_current_workstations_first}")
        print(f"检查原代码缺失的工作站{lose_wk}")
    print(f"machines_to_workstations2{machines_to_workstations}")

    # 调整每个工作站
    for i,wk_list in enumerate(individual['workstation_code']):
        print(f"输出一下编码长度")
        print(f"工作站的{len(individual['workstation_code'])}")
        print(f"人力平衡的{len(individual['balance_code'])}")
        # 获取当前工序需要的机器
        current_wk_ma=individual['machine_code'][i]
        # 当前工序需要分配的工作站数量
        print(f"人力平衡编码{individual['balance_code']}")
        print(f"当前的i是{i}")
        current_balance=individual['balance_code'][i]
        # 获取该机器所有对应的工作站,即该机器可以选择的工作站
        # current_valid_workstations = machines_to_workstations[current_wk_ma]
        # current_valid_workstations = machines_to_workstations.get(current_wk_ma, None)
        # print(f"current_valid_workstations333{current_valid_workstations}")
        current_valid_workstations = machines_to_workstations.get(current_wk_ma, None)
        if current_valid_workstations is not None:
            current_valid_workstations = current_valid_workstations[:]
        else:
            print(f"338338")
            print(f"Warning: {current_wk_ma} 不在 machines_to_workstations 中")
            print(f"机器编码{individual['machine_code']}")
            print(f"当前的机器是{individual['machine_code'][i]}")
            print(f"machines_to_workstations{machines_to_workstations}")
            raise ValueError("机器不在这个编码中，有问题")

        # 调整每个位置的长度
        if len(wk_list)>current_balance:
            wk_list=wk_list[:current_balance]
            individual['workstation_code'][i] = wk_list

            # 先检查有没有问题，再添加新的工作站
        elif len(wk_list)<current_balance:
            individual['workstation_code'][i].extend([""] * (current_balance - len(wk_list)))
            wk_list.extend([""] * (current_balance - len(wk_list)))
        else:
            print(f'长度没问题')
        print(f"machines_to_workstations3{machines_to_workstations}")

        # 修改每个位置中的工作站
        for j,w in enumerate(wk_list):
            tem_w=w
            print(f"wk_list{wk_list}")
            print(f"w{w}")
            print(f"current_valid_workstations444{current_valid_workstations}")
            print(f"machines_to_workstations4{machines_to_workstations}")

            if w not in current_valid_workstations:
                preferred_wk = [wk for wk in lose_wk if wk in current_valid_workstations]
                if preferred_wk:
                    new_wk = random.choice(preferred_wk)
                    lose_wk.remove(new_wk)
                    # 修改掉的工作站还有吗？？？？
                    print(f"现阶段缺失的工作站{lose_wk}")
                else:
                    if current_valid_workstations:
                        new_wk = random.choice(current_valid_workstations)
                    else:
                        print(f"current_valid_workstations555{current_valid_workstations}")
                        print(f"machines_to_workstations5{machines_to_workstations}")
                        print(f"当前的机器是{current_wk_ma}")
                        print(f"机器编码{individual['machine_code']}")
                        raise ValueError("该机器没有分配工作站有问题！")
                print(individual['workstation_code'][i][j])
                individual['workstation_code'][i][j] = new_wk
                # 检查 w 是否在任何一个子列表中
                exists = any(tem_w in sublist for sublist in individual['workstation_code'])
                if not exists and tem_w!='':
                    print(f"当前未更改前的工作站是{tem_w}")
                    print(type(lose_wk))
                    if type(lose_wk)==set:
                        lose_wk.add(tem_w)
                    else:
                        lose_wk.append(tem_w)
                    print(f"lose_wk{lose_wk}")
            else:
                print(f"这个工作站符合这个机器，不需要调整")
    # 检查确实工作站
    unique_current_workstations_after_modification = sorted(set(wk for sublist in individual['workstation_code'] for wk in sublist))
    tem_lose_wk = set(unique_all_workstations) - set(unique_current_workstations_after_modification)
    if not isinstance(lose_wk, set):
        lose_wk = set(lose_wk)
    if not isinstance(tem_lose_wk, set):
        tem_lose_wk = set(tem_lose_wk)

    result = lose_wk.union(tem_lose_wk)
    while result:
        # 取出工作站并打印
        k = result.pop()  # 从 lose_wk 中移除一个工作站
        print(f"重新调整未分配的工作站：{k}")

        # 取出这个工作站对应的机器
        current_m = individual['workstation_machines'].get(k, None)
        if current_m is None:
            print(f"工作站{k}没有对应的机器")
            raise ValueError("有问题，怎么会没有对应机器")

        # 使用 enumerate 来找到符合条件的索引
        indices = [index for index, value in enumerate(individual['machine_code']) if
                   value == current_m]
        print(f"符合该工作站的机器对应的工序的index是{indices}")

        # 随机从 indices 中取一个值
        if indices:
            random_index = random.choice(indices)
            print(f"随机选择的索引: {random_index}")
            print(individual['workstation_code'][random_index])

            # 将工作站添加到工序的工作站列表中
            individual['workstation_code'][random_index].append(k)
            print(f"更新后的工序工作站：{individual['workstation_code'][random_index]}")

        else:
            print("没有找到符合条件的索引")
            raise ValueError("怎么会没有符合条件的索引呢？")

        # 输出当前 lose_wk 的情况
        print(f"剩余未分配的工作站：{result}")


    result=examine_workstation_code(individual['workstation_code'],num)
    if result:
        print(f"成功")
        return individual['workstation_code']
    else:
        # print(sign_wk)
        raise ValueError(f"出问题")

def adjust_workstation_calculate(individual,num):
    if check_wk_ma(individual['workstation_machines'],num):
        print(f"起码工作站数据是全的，就是没有分配全")
        machines_to_workstations = defaultdict(list)
        # 遍历 old_workstation_machine 字典，按机器类型分类
        for station, machine in individual['workstation_machines'].items():
            machines_to_workstations[machine].append(station)
    else:
        print(f"工作站数量都不齐全！有问题")
        raise ValueError("这个需要好好解决下")

    # individual=adjust_crossover_workstation_machines_according_balance(individual,machines_to_workstations,num)

    if check_adjust_workstation(individual['workstation_code'],num):
        return individual
    else:
        raise ValueError('改改改！')

# def prio_crossovver_workstation_code(individual,num):








