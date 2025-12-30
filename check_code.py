from collections import defaultdict
from itertools import chain


def check_employ_efficiency(code,num):
    print(f"check_workstation")
    print(code)
    unique_workstations = set()
    unique_ids = set()

    # 遍历 wk_staff 结构，提取唯一的 workstation 和 id
    for group in code:
        for entry in group:
            unique_workstations.add(entry['workstation'])
            unique_ids.add(entry['employ'])

    # 获取去重后的数量
    workstation_count = len(unique_workstations)
    id_count = len(unique_ids)

    # 检查是否都等于 num
    if workstation_count == id_count == num:
        print(f"Workstation 去重后数量: {workstation_count}")
        print(f"ID 去重后数量: {id_count}")
        return True
    else:
        print(f"Workstation 去重后数量: {workstation_count}")
        print(f"ID 去重后数量: {id_count}")
        print(f"预期数量 (num): {num}")
        return False

def check_generateWorkstation(code,num):
    print(f"check_generateWorkstation")
    print(code)
    unique_items = set()

    # 遍历列表，将所有元素添加到集合中
    for sublist in code:
        unique_items.update(sublist)

    # 计算去重后的元素个数
    unique_count = len(unique_items)
    print(f"unique_items{unique_items}")
    # print(f"去重后的个数是{unique_count}")
    # print(f"是否等于num{unique_count == num, unique_count}")

    if unique_count != num:
        raise ValueError("生成的工作站数量不对")
    # else:
    #     return unique_count == num

def check_adjust_workstation(code,num):
    print(f"check_adjust_workstation")
    print(code)
    unique_stations=set(station for sublist in code for station in sublist)
    print(f"去重后的工作站{unique_stations}")
    unique_count = len(unique_stations)
    print(f"去重后的工作站数量{unique_count}")
    if unique_count != num:
        # raise ValueError("工作站数量不对")
        print(f"工作站数量不对{unique_count}")
        print(f"工作站是{unique_stations}")
        return False
    else:
        return True

    # # 将所有工作站从嵌套列表中提取出来，变成一个一维列表
    # assigned_workstations = set(workstation for sublist in wk for workstation in sublist)

def check_wk_ma(code,num):
    print(f"check_wk_ma")
    # {'L7': 'A', 'R3': 'A', 'L8': 'A', ……}
    print(code)
    unique_key_count = len(set(code.keys()))
    print(f"unique_key_count{unique_key_count}")
    # 检查数量是否等于 num
    is_equal = (unique_key_count == num)
    print(f"is_equal{is_equal}")
    if unique_key_count != num:
        # raise ValueError("工作站数量不对")
        return False
    else:
        return True

    # return is_equal

def check_wk_ma2(code,num):
    print(code)
    print(code.values())
    # 提取所有键的值并去重
    unique_workstations = set(chain.from_iterable(code.values()))
    # 计算去重后的数量
    unique_count = len(unique_workstations)
    if unique_count != num:
        print(unique_count)
        raise ValueError("工作站数量不对")

def check_out_generate_employ_code(code,num):
    print(f"check_out_generate_employ_code")
    print(code)
    # 展平列表并提取所有 employ 值
    employ_values = {entry['employ'] for sublist in code for entry in sublist}

    # 计算去重后 employ 数量
    num_employ = len(employ_values)

    # 判断是否等于 23
    if num_employ == num:
        print(f"员工数量符合要求: {num_employ} == num")
    else:
        print(f"员工数量不符合要求: {num_employ} != num")
        raise ValueError("员工数量不对")

def check_machines_to_workstations(code,num):
    print(code)
    # 取出所有值并去重
    all_workstations = set()
    for workstations in code.values():
        all_workstations.update(workstations)  # 使用 update 添加并去重

    # 计算唯一工作站数量
    num_unique_workstations = len(all_workstations)
    # 判断是否等于 23
    if num_unique_workstations == num:
        print("工作站数量等于 23")
    else:
        print(f"现在的工作站有：{all_workstations}")
        raise ValueError("缺少工作站")

def check_adjust_employ(code,num):
    sign=0
    print(f"check_adjust_employ")
    print(f"code{code}")
    # 提取所有 id 并去重
    unique_ids = {emp['employ'] for sublist in code for emp in sublist}
    print(f"unique_ids_check_adjust_employ{unique_ids}")

    if check_employ_code_workstation(code,num):
        print(f"工作站数量正确")
    else:
        print(f"工作站数量不正确")
        # raise ValueError("工作站数量不正确，进行调整")
        return False,sign

    # 判断去重后的 id 数量是否等于 23
    if len(unique_ids) == num:
        print("ID 数量正确，去重后的数量为 23")
        return True,None
    else:
        print(f"ID 数量不正确，去重后的数量为 {len(unique_ids)}")
        sign=1
        # raise ValueError('员工数量不对')
        return False,sign

def check_employ_code_workstation(code,num):
    # 提取所有的 workstation 并去重
    unique_wk = list(set(i['workstation'] for sublist in code for i in sublist))
    # unique_wk={emp['workstation'] for sublist in code for emp in sublist}
    print(f"&&&&&!!!!!!")
    print(f"unique_wk{unique_wk}")
    if len(unique_wk)==num:
        print(f"工作站数量齐全")
        return True
    else:
        print(f"工作站数量不齐全")
        print(f"unique_wk{unique_wk}")
        print(len(unique_wk))
        # raise ValueError("!!!!!!")
        return False

def check_result_employ_allocation(code,num):
    print(f"check_result_employ_allocation")
    print(code)

    # 使用字典的方式按 `workstation` 去重
    unique_data_workstation = {entry['workstation']: entry for entry in code}.values()
    print(f"unique_data_workstation{unique_data_workstation}")

    # 按 `employ` 去重
    unique_data_employ = {entry['employ']: entry for entry in code}.values()
    print(f"unique_data_employ{unique_data_employ}")

    # 按 `workstation` 和 `employ` 同时去重
    unique_data_both = {f"{entry['workstation']}_{entry['employ']}": entry for entry in code}.values()
    print(f"unique_data_both{unique_data_both}")

    # 获取去重后的数量
    len_workstation = len(unique_data_workstation)
    len_employ = len(unique_data_employ)
    len_both = len(unique_data_both)

    # 断言三个去重方式的结果数量必须相同，否则报错
    assert len_workstation == len_employ == len_both ==num, f"去重后数量不一致: workstation={len_workstation}, employ={len_employ}, both={len_both}"

    print(f"去重后数量一致")

def check_employ_allocation_conflicts(result_employ_allocation):
    # 记录工作站对应的员工
    station_to_employ = defaultdict(set)
    # 记录员工对应的工作站
    employ_to_stations = defaultdict(set)

    # 遍历数据，分别填充两个字典
    for item in result_employ_allocation:
        station = item['workstation']
        employ = item['employ']
        station_to_employ[station].add(employ)
        employ_to_stations[employ].add(station)

    # 检查是否有同一工作站分配了不同 employ
    conflicts_same_station = {
        station: employs
        for station, employs in station_to_employ.items()
        if len(employs) > 1  # 一个工作站有多个员工编号
    }

    # 检查是否有同一 employ 被分配到多个工作站
    conflicts_same_employ = {
        employ: stations
        for employ, stations in employ_to_stations.items()
        if len(stations) > 1  # 一个 employ 出现在多个工作站
    }

    return conflicts_same_station, conflicts_same_employ
