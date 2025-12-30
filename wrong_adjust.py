from check_code import check_wk_ma, check_adjust_workstation, check_result_employ_allocation, check_adjust_employ


def check_adjust_wrong_individual(individual,num):
    print(individual)
    workstation_machines=individual['individual']['workstation_machines']
    workstation_codes=individual['individual']['workstation_code']
    result_employ_allocation=individual['individual']['result_employ_allocation']
    employ_code=individual['individual']['employ_code']
    if check_wk_ma(workstation_machines,num):
        if check_adjust_workstation(workstation_codes,num):
            if check_result_employ_allocation(result_employ_allocation,num):
                if check_adjust_employ(employ_code,num):
                    print(f"个体调整没有问题")
                else:
                    # 工作站其他的都没问题,但是员工有问题
                    print(f"工作站其他的都没问题,但是员工有问题,重新调整")
                    for e_wk_list,wk_list  in zip(individual['individual']['employ_code'], individual['individual']['workstation_code']):
                        for e_wk,wk in zip(e_wk_list,wk_list):
                            workstation_dict = {entry['workstation']: entry['employ'] for entry in individual['individual']['result_employ_allocation']}
                            if e_wk['workstation']==wk:
                                # 转换成字典
                                try:
                                    print(workstation_dict[e_wk['workstation']])  # 如果键不存在，会抛出 KeyError
                                except KeyError:
                                    raise KeyError(f"工作站 {e_wk['workstation']} 不存在！")
                                if e_wk['employ']==workstation_dict.get(e_wk['workstation']):
                                    print(f"成功")
                                else:
                                    e_wk['employ']=workstation_dict.get(e_wk['workstation'],"未找到")
                            else:
                                print(f"工作站不对")
                                e_wk['workstation'] = wk
                                try:
                                    print(workstation_dict[e_wk['workstation']])  # 如果键不存在，会抛出 KeyError
                                except KeyError:
                                    raise KeyError(f"工作站 {e_wk['workstation']} 不存在！")
                                e_wk['employ']=workstation_dict.get(e_wk['workstation'],"未找到")

            else:
                print(f"工作站都分配了，但是员工与工作站匹配不对，即有员工重复了")
                # for e in individual['individual']['employ_code']:
                raise ValueError("也有问题，但是暂时不知道怎么解决")

        else:
            print(f"工作站缺失")
            raise ValueError('有工作站没有分配！！')
    else:
        print(f"工作站和机器匹配都不对")
        raise ValueError('严重问题！！！')

    return individual



