# from check_code import check_result_employ_allocation, check_employ_allocation_conflicts, check_adjust_employ
# from examine_encoding import examine_result_employ_allocation, examine_employ_code, examine_workstation_code
#
#
# def adjust_crossover_employ_code(individual,num):
#     r3=examine_workstation_code(individual['individual']['workstation_code'],23)
#     if r3:
#         print()
#     else:
#         # print(f"问题{s3}")
#         raise ValueError('s3')
#     result_employ_allocation = individual['individual']['result_employ_allocation']
#     examine_result_employ_allocation(individual['individual']['result_employ_allocation'],23)
#     check_result_employ_allocation(result_employ_allocation, 23)
#     conflicts_same_station, conflicts_same_employ=check_employ_allocation_conflicts(result_employ_allocation)
#     print("adjust_crossover_employ_code")
#     print(conflicts_same_station)
#     print(conflicts_same_employ)
#     if conflicts_same_station or conflicts_same_employ:
#         print(f"说明result_employ_allocation有问题，需要调整")
#         individual=adjust_crossover_result_employ_allocation(individual,num)
#
#
#     # 使用字典来存储每个 workstation 最后的 employ 值
#     employ_mapping = {item['workstation']: item['employ'] for item in result_employ_allocation}
#     print(f"employ_mapping{employ_mapping}")
#
#
#     for i,wk_list in enumerate(individual['individual']['workstation_code']):
#         wk_len=len(wk_list)
#         employ_len=len(individual['individual']['employ_code'][i])
#         # 调整员工编码长度
#         if wk_len<employ_len:
#             individual['individual']['employ_code'][i]=individual['individual']['employ_code'][i][:wk_len]
#             print(f"这个位置的员工编码是{ individual['individual']['employ_code'][i]}")
#         elif wk_len>employ_len:
#             individual['individual']['employ_code'][i].extend([{'workstation': '', 'employ': 0} for _ in range((wk_len) - employ_len)])
#         else:
#             print(wk_len==employ_len)
#             print(f"长度一致")
#
#     # 修改employ_code
#     for wk_list,employ_list in zip(individual['individual']['workstation_code'],individual['individual']['employ_code']):
#         print(f"employ_list{employ_list}")
#         print(f"wk_list{wk_list}")
#
#         for w,e in zip(wk_list,employ_list):
#             print(f"373737")
#             print(w)
#             print(e)
#             if w==e['workstation'] and e['employ']==employ_mapping[w]:
#                 print(f"配对成功")
#             else:
#                 e['workstation']=w
#                 e['employ'] = employ_mapping[w]
#                 print(e['workstation'])
#                 print(e['employ'] )
#     print(f"员工编码是{individual['individual']['employ_code']}")
#     print(f"individual是：{individual}")
#     r2,s2=examine_employ_code(individual['individual']['employ_code'],23)
#     if r2:
#         print(f"chenggong")
#         print(f"当前调整后的个体{individual}")
#         return individual
#     else:
#         print(f"问题是{s2}")
#         raise ValueError
#
#
#
