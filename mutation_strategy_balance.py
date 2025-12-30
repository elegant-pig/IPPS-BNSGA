import copy
import random
from collections import defaultdict

from examine_encoding import examine_workstation_code, examine_result_employ_allocation, examine_employ_code
from generateBalance import adjust_balance_by_difference


def Gaussian_perturbation(mutation_rate,balance_code,float_balance_codes ,num):
    sigma=0.5
    new_code = []
    for val in balance_code:
        if random.random() < mutation_rate:
            mutated_val = val + random.gauss(0, sigma)
        else:
            mutated_val = val
        mutated_val = max(0, round(mutated_val))  # 避免为负数
        new_code.append(mutated_val)

    total = sum(new_code)
    is_valid = total >= num
    if is_valid:
        return new_code, is_valid
    else:
        diff_value = int(total - num)
        print(f"diff_value{diff_value}")
        modified_balance = adjust_balance_by_difference(float_balance_codes, new_code, diff_value)
        return modified_balance

# mutation_operators = [
#     swap_mutation,
#     inversion_mutation,
#     insertion_mutation,
#     scramble_mutation,
#     sublist_swap_mutation,
#     intra_sublist_mutation,
#     change_staff_to_workstation
# ]


# def hybrid_mutation(code, mutation_rate):
#     # 初始化的权重值
#     # 自动更新：在
#     # GA
#     # 主循环中，根据算子历史“奖励”定期重算
#     # operator_weights，放在每隔若干代的更新逻辑里。
#     operator_weights = [1, 1, 1, 1, 1, 1]
#
#     if random.random() > mutation_rate:
#         return code  # 不变异
#     # 随机选择一个变异算子
#     operator = random.choice(mutation_operators)
#
#     # 按照权重选择一个变异算子
#     operator = select_operator(operator_weights)
#     return operator(code)


def change_staff_to_workstation(rate,i,num):
    staff_to_workstation =copy.deepcopy(i['individual']['result_employ_allocation'])
    old_employ_code=copy.deepcopy(i['individual']['employ_code'])

    # print(f"员工编码是------{i['individual']['employ_code']}")

    for r in range(rate//2):
        # selected_two = random.sample(staff_to_workstation, 2) #选择该机器的两个位置交换.
        # 随机选取两个不同的索引
        idx1, idx2 = random.sample(range(len(staff_to_workstation)), 2)
        tem_id=staff_to_workstation[idx1]['employ']
        staff_to_workstation[idx1]['employ']=staff_to_workstation[idx2]['employ']
        staff_to_workstation[idx1]['employ']=tem_id
    print(f"这里的员工编码----{i['individual']['employ_code']}")
    employ_mapping = {item['workstation']: item['employ'] for item in staff_to_workstation}
    print(f"---------i{i}")
    # 修改employ_code
    for k,staff_list in enumerate(i['individual']['employ_code']):
        print(f"员工编码该位置{staff_list}")
        for j,e in enumerate(staff_list):
            print(f"这里的编码是{e}")
            wk_e=e['workstation']
            # print(employ_mapping[])
            if e['employ']==employ_mapping[wk_e]:
                print(f"正确，不修改")
            else:
                old_employ_code[k][j]['employ']=employ_mapping[staff_list['workstation']]
            # staff_list['employ'] = employ_mapping[staff_list['workstation']]

    r,s=examine_result_employ_allocation(staff_to_workstation,num)
    if r:
        r1,s1=examine_employ_code(old_employ_code,num)
        if r1:
            return old_employ_code,staff_to_workstation
        else:
            print(f"问题是{s}")
            raise ValueError('员工编码不对')
    else:
        print(f"问题是{s}")
        raise ValueError('员工分配到工作站不对')




def SubLlist_Swap(rate,i,num):
    old_wk=copy.deepcopy(i['individual']['workstation_code'])
    machine_code=copy.deepcopy(i['individual']['machine_code'])

    if rate<2:
        rate=2

    if rate % 2 != 0:
        rate += 1
    print(f"交换几次呢{rate}")
    mapping = defaultdict(list)
    for idx, mch in enumerate(machine_code):
        mapping[mch].append(idx)
    print(f"mapping{mapping}")

    # 先过滤出所有长度 ≥ 2 的 key 列表
    valid_keys = [mch for mch, pos in mapping.items() if len(pos) >= 2]

    if not valid_keys:
        # 没有满足条件的机器编码，进行相应处理
        # return
        print(f"做不了交换")
        return
    print(f"未修改之前old_wk{old_wk}")
    for i in range(int(rate/2)):
        # 从 valid_keys 中随机选一个
        mch = random.choice(valid_keys) #随机选择要变化的一个机器
        selected_two = random.sample(mapping[mch], 2) #选择该机器的两个位置交换
        tem_data=old_wk[selected_two[0]]
        old_wk[selected_two[0]]=old_wk[selected_two[1]]
        old_wk[selected_two[1]]=tem_data
    print(f'修改之后old_wk{old_wk}')

    if examine_workstation_code(old_wk,num):
        return old_wk
    else:
        raise ValueError('有问题')


def inversion_mutation(code):
    new_flat = sum(code, [])  # 简单展开
    # 随机选区间 [a, b)
    a, b = sorted(random.sample(range(len(new_flat)), 2))
    new_flat[a:b] = reversed(new_flat[a:b])
    # 按原子列表长度重构回嵌套列表
    return reconstruct(new_flat, code)

def insertion_mutation(code):
    new_flat = sum(code, [])
    idx_remove = random.randrange(len(new_flat))
    elem = new_flat.pop(idx_remove)
    idx_insert = random.randrange(len(new_flat) + 1)
    new_flat.insert(idx_insert, elem)
    return reconstruct(new_flat, code)

def scramble_mutation(code):
    new_flat = sum(code, [])
    a, b = sorted(random.sample(range(len(new_flat)), 2))
    segment = new_flat[a:b]
    random.shuffle(segment)
    new_flat[a:b] = segment
    return reconstruct(new_flat, code)

def sublist_swap_mutation(code):
    new_code = [sublist[:] for sublist in code]
    # 随机选两个子列表下标 i, j
    i, j = random.sample(range(len(new_code)), 2)
    new_code[i], new_code[j] = new_code[j], new_code[i]
    return new_code

def intra_sublist_mutation(code):
    new_code = [sublist[:] for sublist in code]
    # 随机选一个子列表
    i = random.randrange(len(new_code))
    sub = new_code[i]
    if len(sub) < 2:
        return new_code
    # 在子列表内做简单的 swap
    j1, j2 = random.sample(range(len(sub)), 2)
    sub[j1], sub[j2] = sub[j2], sub[j1]
    return new_code

# 辅助函数示例
def random_position_pairs(code):
    # 返回两个（子列表索引, 子列表内索引）对
    flat_positions = [(i, j) for i, sub in enumerate(code) for j in range(len(sub))]
    return random.sample(flat_positions, 2)

def reconstruct(flat_list, template):
    # 根据 template（原 code）的子列表长度信息，将 flat_list 重新分组
    new_code, idx = [], 0
    for sub in template:
        length = len(sub)
        new_code.append(flat_list[idx: idx+length])
        idx += length
    return new_code