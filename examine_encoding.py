
def examine_workstation_code(code,num):
    print(f"工作站编码是{code}")
    print(f"总共的工作站是{num}")
    # 使用集合去重
    workstations = set(w for sublist in code for w in sublist)

    if len(workstations)!=num:
        print(f"去重后的数量是{len(workstations)}")
        print(f"去重后的工作站是{workstations}")
        return False
    else:
        print(f"工作站编码数量正确")
        return True

def examine_workstation_machines_code(workstation_machines,machines,num):
    """
    workstation_machines:个体的workstation_machines编码
    machines：个体的machine_code编码
    num:工作站数量
    """
    sign =None
    print(f"机器编码是{machines}")
    print(f"工作站机器匹配编码是{workstation_machines}")

    keys_wk=set(workstation_machines.keys())
    values_m=set(workstation_machines.values())

    machines=set(machines)
    print(f"machines{machines}")
    print(f"values_m{values_m}")
    print(f"keys_wk{keys_wk}")

    if len(keys_wk)==num and values_m==machines:
        print(f"工作站数量正确，且出现的机器都对")
        return True,sign
    elif len(keys_wk)!=num and values_m==machines:
        print(f"机器没问题,但是工作站缺失了！")
        print(f"工作站数量{keys_wk}")
        print(f"工作站列表：{keys_wk}")
        sign=1
        return False,sign
    elif len(keys_wk)!=num and values_m!=machines:
        print(f"工作站缺失，机器对不上")
        print(f"工作站数量{keys_wk}")
        print(f"工作站列表：{keys_wk}")
        print(f"机器列表：{values_m}")
        print(f"原来机器列表：{machines}")
        sign=2
        return False,sign
    elif len(keys_wk)==num and values_m!=machines:
        print(f"工作站没问题，但是机器对不上")
        print(f"机器列表：{values_m}")
        print(f"原来机器列表：{machines}")
        sign = 3
        return False,sign
    else:
        print(f"我看看这是什么情况")
        print(f"工作站数量{keys_wk}")
        print(f"工作站列表：{keys_wk}")
        print(f"机器列表：{values_m}")
        print(f"原来机器列表：{machines}")
        sign = 0
        return False,sign

def examine_employ_code(code,num):
    sign=None
    print(f"员工编码是：{code}")
    # 使用集合去重
    workstations = {item['workstation'] for sublist in code for item in sublist}

    employ={item['employ'] for sublist in code for item in sublist}

    # 转换成列表（如果需要）
    workstations_list = list(workstations)

    employ_list=list(employ)

    if len(workstations)!=num and len(employ)!=num:
        print(f"工作站和员工的数量都不对")
        print(f"去重后工作站数量：{len(workstations)}，员工数量{len(employ)}")
        print(f"去重后的工作站是{workstations_list}")
        print(f'去重后员工编码是{employ}')
        sign=1
        return False,sign
    elif len(workstations)==num and len(employ)!=num:
        print(f"工作站数量对，为{len(workstations)}")
        print(f"但是员工数量不对，为{len(employ)}")
        print(f"员工列表是{employ_list}")
        sign=2
        return False,sign
    elif len(workstations)==num and len(employ)==num:
        print(f"工作站和员工的数量都对")
        return True,sign
    elif len(workstations)!=num and len(employ)==num:
        print(f"工作站数量不对，为{len(workstations)}")
        print(f"工作站列表是{workstations_list}")
        print(f"但是员工数量正确，有问题，说明有工作站分了两个员工，也要修改")
        sign=3
        return False,sign
    else:
        print(f"还有别的情况")
        sign=0
        return False,sign

def examine_result_employ_allocation(code,num):
    sign=None
    print(f"员工和工作站配对编码{code}")
    # 提取出所有workstation对应的值
    workstations = [entry['workstation'] for entry in code]
    # 去重
    workstations = list(set(workstations))

    employ=[entry['employ'] for entry in code]

    employ=list(set(employ))

    if len(workstations)==num and len(employ)==num:
        print(f"工作站和员工数量匹配")
        return True,sign
    elif len(workstations)==num and len(employ)!=num:
        print(f"工作站数量没问题，但是员工数量不对！")
        print(f"员工数量是{len(employ)}")
        print(f"员工列表是{employ}")
        sign=1
        return False,sign
    elif len(workstations)!=num and len(employ)==num:
        print(f"工作站数量不对，但是员工数量对了，说明有多个员工分到一个工作站")
        print(f"工作站数量是{len(workstations)}")
        print(f"工作站列表{workstations}")
        sign=2
        return False,sign
    elif len(workstations)!=num and len(employ)!=num:
        print(f"工作站和员工数量都不对")
        print(f'工作站数量是{len(workstations)}，员工数量是{len(employ)}')
        print(f"工作站列表{workstations}")
        print(f"员工列表{employ}")
        sign=3
        return False,sign
    else:
        print(f"还有别的情况？？")
        sign = 0
        return False,sign

def examine_individual(individual,num):
    print(f"进来的数据是{individual}")
    if 'individual' in individual:
        individual=individual['individual']

    result_wm,sign_wm=examine_workstation_machines_code(individual['workstation_machines'], individual['machine_code'], num)
    result_wk= examine_workstation_code(individual['workstation_code'],num)
    result_rec,sign_rec=examine_result_employ_allocation(individual['result_employ_allocation'],num)
    result_e,sign_e=examine_employ_code(individual['employ_code'],num)

    if result_wm:
        print(f"机器和工作站数量正确")
        if result_wk:
            print(f"工作站分配数量也正确")
            if result_rec:
                print(f"工作站员工分配正确")
                if result_e:
                    print(f"员工编码正确")
                    return True
                else:
                    print(f"sign_e{sign_e}")
                    raise ValueError(f"员工编码不正确")
            else:
                print(f"sign_rec{sign_rec}")
                raise ValueError("工作站员工分配不正确")
        else:
            raise ValueError("工作站数量不正确")
    else:
        print(f"sign_wm{sign_wm}")
        raise ValueError(f"机器工作站不正确")


# # 只有当脚本作为主程序运行时，才会执行以下代码
# if __name__ == "__examine_individual__":
#     examine_individual()