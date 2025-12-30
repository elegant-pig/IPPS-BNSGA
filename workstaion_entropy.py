from collections import defaultdict

import pandas as pd
import numpy as np


def entropy(probs):
    probs = np.array(probs)
    probs = probs[probs > 0]
    return -np.sum(probs * np.log2(probs)) if len(probs) > 0 else 0.0

def compute_predecessor_entropy(df, op_col='工序', pred_col='前继工序'):
    entropy_scores = {}
    for _, row in df.iterrows():
        op = str(row[op_col]).strip()
        preds_str = str(row[pred_col]).strip()
        if preds_str == '' or preds_str.lower() in ['nan', '0']:
            entropy_scores[op] = 0.0
            continue
        preds = [x.strip() for x in preds_str.replace('，', ',').replace('、', ',').split(',') if x.strip()]
        n = len(preds)
        p = [1 / n] * n
        entropy_scores[op] = entropy(p)
    return entropy_scores


def get_workstation_priority(ws):
    side = 0 if ws[0] == 'L' else 1
    num = int(ws[1:])
    return num * 2 + side  # L1=2, R1=3, L2=4, R2=5, ...

def sort_ws_by_proximity(ws_pool):
    return sorted(ws_pool, key=get_workstation_priority)

def parse_operation_index(op_str):
    """从'O3,4'提取出工序编号 4"""
    return str(int(op_str.split(',')[1]))  # 提取 '4'

def get_nearby_workstations(center, ws_pool):
    if center not in ws_pool:
        return []

    side, idx = center[0], int(center[1:])
    opposite = 'R' if side == 'L' else 'L'

    candidates = {
        f'{side}{idx - 1}': 1.0,
        f'{side}{idx + 1}': 1.0,
        f'{opposite}{idx}': 0.8,
        f'{opposite}{idx - 1}': 0.6,
        f'{opposite}{idx + 1}': 0.4
    }

    nearby = [(ws, w) for ws, w in candidates.items() if ws in ws_pool]
    nearby.sort(key=lambda x: -x[1])
    return [ws for ws, _ in nearby]

def assign_workstations(operation_code, balance_code, machine_code, workstation_list, df):
    entropy_scores = compute_predecessor_entropy(df)
    assert len(operation_code) == len(balance_code) == len(machine_code)

    op_data = []
    for op, bal, mac in zip(operation_code, balance_code, machine_code):
        op_id = parse_operation_index(op)
        ent = entropy_scores.get(op_id, 0.0)
        op_data.append((op, bal, ent, mac, op_id))

    machine_clusters = defaultdict(list)
    for item in op_data:
        machine_clusters[item[3]].append(item)

    ws_pool = sort_ws_by_proximity(workstation_list)
    ws_used = set()
    allocation = {}

    for machine, ops in machine_clusters.items():
        ops.sort(key=lambda x: (x[2], x[1]))

        group_ws_pool = [ws for ws in ws_pool if ws not in ws_used]
        if len(group_ws_pool) == 0:
            print(f"无可用工作站供机器 ")
            # raise ValueError("无可用工作站供机器 {} 分配".format(machine))

        total_needed = sum([item[1] for item in ops])
        if total_needed > len(group_ws_pool):
            print(f"⚠ 警告：机器 {machine} 所需工作站数 {total_needed} 超出剩余可用数 {len(group_ws_pool)}，将部分重叠使用")

        group_ws_sorted = sort_ws_by_proximity(group_ws_pool)
        best_start = 0
        best_score = float('inf')
        for i in range(len(group_ws_sorted) - total_needed + 1):
            window = group_ws_sorted[i:i + total_needed]
            score = sum([get_workstation_priority(ws) for ws in window])
            if score < best_score:
                best_start = i
                best_score = score
        local_ws = group_ws_sorted[best_start: best_start + total_needed]

        idx = 0
        for op, bal, ent, mac, opid in ops:
            assigned = local_ws[idx: idx + bal]
            allocation[op] = {
                '机器': mac,
                '工序编号': opid,
                '信息熵': ent,
                '工作站': assigned
            }
            ws_used.update(assigned)
            idx += bal

    # 检查是否有工序未成功分配
    for op, info in allocation.items():
        if not info['工作站']:
            print(f"{op}（机器:{info['机器']} 熵:{info['信息熵']:.2f}） → {info['工作站']}")
            raise ValueError(f"工序 {op} 分配的工作站为空！请检查 balance_code 是否合理，或工作站数量是否足够。")

    print("【最终工作站分配结果】")
    for op, info in allocation.items():
        print(f"{op}（机器:{info['机器']} 熵:{info['信息熵']:.2f}） → {info['工作站']}")

    return allocation



# 方法D：机器工序聚类 + 局部贪婪 + 跨组轮转分配
def allocate_workstations(operation_code, machine_code, balance_code, workstation):
    # Step 1: 聚类：将工序按机器分类
    machine_to_ops = defaultdict(list)
    for op, m, b in zip(operation_code, machine_code, balance_code):
        machine_to_ops[m].append((op, b))

    # Step 2: 对每个机器组内进行 balance 排序（熵也可替代）
    machine_groups = []
    for machine, ops in machine_to_ops.items():
        print(f"ops{ops}")
        sorted_ops = sorted(ops, key=lambda x: -x[1])  # balance越大优先级越高
        machine_groups.append((machine, sorted_ops))

    # Step 3: 准备工作站状态
    ws_assigned = {w: None for w in workstation}  # 哪些工作站被占用
    ws_result = defaultdict(list)  # 工序 -> 工作站的映射

    # 辅助函数：寻找某个中心点附近的空工作站（权重高的先）
    def find_local_station(center_idx, side):
        directions = [
            (0, 1.0),  # 当前
            (-1, 0.8),  # 前
            (1, 0.8),  # 后
            (0.1 if side == 'L' else -0.1, 0.6),  # 侧（对面）
            (-1 if side == 'L' else 1, 0.4),  # 斜前
            (1 if side == 'L' else -1, 0.4)  # 斜后
        ]
        candidates = []
        for delta, weight in directions:
            idx = center_idx + int(delta)
            if 0 <= idx < len(workstation):
                w = workstation[idx]
                if ws_assigned[w] is None:
                    candidates.append((weight, w))
        candidates.sort(reverse=True)  # 权重高优先
        return [w for _, w in candidates]

    # Step 4: 跨组轮转式公平分配
    group_iters = [iter(group) for _, group in machine_groups]
    remaining = True
    while remaining:
        remaining = False
        for group_idx, group_iter in enumerate(group_iters):
            try:
                op, _ = next(group_iter)
                remaining = True
                # 分配工作站
                for i, w in enumerate(workstation):
                    if ws_assigned[w] is None:
                        center_idx = i
                        side = 'L' if 'L' in w else 'R'
                        candidates = find_local_station(center_idx, side)
                        if candidates:
                            chosen = candidates[0]
                            ws_assigned[chosen] = op
                            ws_result[op].append(chosen)
                            break
                else:
                    raise ValueError(f"工序 {op} 分配的工作站为空！请检查 balance_code 是否合理，或工作站数量是否足够。")
            except StopIteration:
                continue

    return ws_result

# def assign_workstations_with_proximity_push(operation_code, balance_code, machine_code, workstation_list, df):
#     entropy_scores = compute_predecessor_entropy(df)
#     assert len(operation_code) == len(balance_code) == len(machine_code)
#
#     op_data = []
#     for op, bal, mac in zip(operation_code, balance_code, machine_code):
#         op_id = parse_operation_index(op)
#         ent = entropy_scores.get(op_id, 0.0)
#         op_data.append((op, bal, ent, mac, op_id))
#
#     machine_clusters = defaultdict(list)
#     for item in op_data:
#         machine_clusters[item[3]].append(item)
#
#     ws_pool = sort_ws_by_proximity(workstation_list)
#     ws_used = set()
#     allocation = {}
#
#     def find_non_used_nearby(ws, required, ws_used, ws_pool):
#         """查找离当前 ws 最近的、尚未使用的工作站集合"""
#         candidates = [ws] + get_nearby_workstations(ws, ws_pool)
#         result = []
#         for cand in candidates:
#             if cand not in ws_used:
#                 result.append(cand)
#             if len(result) >= required:
#                 break
#         return result if len(result) == required else None
#
#     for machine, ops in machine_clusters.items():
#         ops.sort(key=lambda x: (x[2], x[1]))  # 先按熵，再按 balance_code 升序
#
#         total_needed = sum([item[1] for item in ops])
#         group_ws_pool = [ws for ws in ws_pool if ws not in ws_used]
#         group_ws_sorted = sort_ws_by_proximity(group_ws_pool)
#
#         if total_needed > len(group_ws_pool):
#             print(f"⚠ 警告：机器 {machine} 所需工作站数 {total_needed} 超出剩余可用数 {len(group_ws_pool)}，将部分重叠使用")
#
#         idx = 0
#         for op, bal, ent, mac, opid in ops:
#             found = False
#
#             # 尝试从当前位置及之后的位置滑窗查找满足要求的工作站组合
#             for start in range(idx, len(ws_pool)):
#                 if start + bal > len(ws_pool):
#                     break
#                 candidate_window = ws_pool[start:start + bal]
#                 if all(ws not in ws_used for ws in candidate_window):
#                     assigned = candidate_window
#                     found = True
#                     break
#
#                 # 尝试在当前主窗口中心周围找邻近空闲工作站
#                 neighbor_set = []
#                 for ws in candidate_window:
#                     nearby = find_non_used_nearby(ws, 1, ws_used, ws_pool)
#                     if nearby:
#                         neighbor_set += nearby
#                     if len(neighbor_set) >= bal:
#                         break
#                 if len(neighbor_set) >= bal:
#                     assigned = neighbor_set[:bal]
#                     found = True
#                     break
#
#             if not found:
#                 # 如果所有滑窗都找不到，则允许强行分配未完全空闲的窗口（重叠使用）
#                 assigned = []
#                 for ws in ws_pool:
#                     if ws not in ws_used:
#                         assigned.append(ws)
#                     if len(assigned) >= bal:
#                         break
#                 print(f"⚠ 警告：{op} 找不到完全空闲窗口，执行部分重叠分配 → {assigned}")
#
#             allocation[op] = {
#                 '机器': mac,
#                 '工序编号': opid,
#                 '信息熵': ent,
#                 '工作站': assigned
#             }
#             ws_used.update(assigned)
#
#     # 最终检查
#     for op, info in allocation.items():
#         if not info['工作站']:
#             raise ValueError(f"工序 {op} 分配失败，未找到工作站")
#
#     print("【最终工作站分配结果 - D方法】")
#     for op, info in allocation.items():
#         print(f"{op}（机器:{info['机器']} 熵:{info['信息熵']:.2f}） → {info['工作站']}")
#
#     return allocation


# def assign_workstations_with_proximity_push(operation_code, balance_code, machine_code, workstation_list, df):
#     entropy_scores = compute_predecessor_entropy(df)
#     assert len(operation_code) == len(balance_code) == len(machine_code)
#
#     op_data = []
#     for op, bal, mac in zip(operation_code, balance_code, machine_code):
#         op_id = parse_operation_index(op)
#         ent = entropy_scores.get(op_id, 0.0)
#         bal = int(float(bal))  # 强制转换为整数
#         op_data.append((op, bal, ent, mac, op_id))
#
#
#     machine_clusters = defaultdict(list)
#     for item in op_data:
#         machine_clusters[item[3]].append(item)
#     print(f"-----machine_clusters------{machine_clusters}")
#
#     ws_pool = sort_ws_by_proximity(workstation_list)
#     ws_used = set()
#     allocation = {}
#
#     def find_non_used_nearby(ws, required, ws_used, ws_pool):
#         """查找离当前 ws 最近的、尚未使用的工作站集合"""
#         candidates = [ws] + get_nearby_workstations(ws, ws_pool)
#         result = []
#         for cand in candidates:
#             if cand not in ws_used:
#                 result.append(cand)
#             if len(result) >= required:
#                 break
#         return result if len(result) == required else None
#
#     for machine, ops in machine_clusters.items():
#         ops.sort(key=lambda x: (x[2], x[1]))  # 先按熵，再按 balance_code 升序
#
#         total_needed = sum([item[1] for item in ops])
#         group_ws_pool = [ws for ws in ws_pool if ws not in ws_used]
#         group_ws_sorted = sort_ws_by_proximity(group_ws_pool)
#
#         if total_needed > len(group_ws_pool):
#             print(f"⚠ 警告：机器 {machine} 所需工作站数 {total_needed} 超出剩余可用数 {len(group_ws_pool)}，将部分重叠使用")
#
#         idx = 0
#         for op, bal, ent, mac, opid in ops:
#             found = False
#
#             # 尝试从当前位置及之后的位置滑窗查找满足要求的工作站组合
#             for start in range(idx, len(ws_pool)):
#                 if start + bal > len(ws_pool):
#                     break
#                 candidate_window = ws_pool[start:start + bal]
#                 if all(ws not in ws_used for ws in candidate_window):
#                     assigned = candidate_window
#                     found = True
#                     break
#
#                 # 尝试在当前主窗口中心周围找邻近空闲工作站
#                 neighbor_set = []
#                 for ws in candidate_window:
#                     nearby = find_non_used_nearby(ws, 1, ws_used, ws_pool)
#                     if nearby:
#                         neighbor_set += nearby
#                     if len(neighbor_set) >= bal:
#                         break
#                 if len(neighbor_set) >= bal:
#                     assigned = neighbor_set[:bal]
#                     found = True
#                     break
#
#             if not found:
#                 # 如果所有滑窗都找不到，则允许强行分配未完全空闲的窗口（重叠使用）
#                 assigned = []
#                 for ws in ws_pool:
#                     if ws not in ws_used:
#                         assigned.append(ws)
#                     if len(assigned) >= bal:
#                         break
#                 print(f"⚠ 警告：{op} 找不到完全空闲窗口，执行部分重叠分配 → {assigned}")
#
#             allocation[op] = {
#                 '机器': mac,
#                 '工序编号': opid,
#                 '信息熵': ent,
#                 '工作站': assigned
#             }
#             ws_used.update(assigned)
#
#     # 最终检查
#     for op, info in allocation.items():
#         if not info['工作站']:
#             raise ValueError(f"工序 {op} 分配失败，未找到工作站")
#
#     print("【最终工作站分配结果 - D方法】")
#     for op, info in allocation.items():
#         print(f"{op}（机器:{info['机器']} 熵:{info['信息熵']:.2f}） → {info['工作站']}")
#
#     return allocation


def assign_workstations_with_proximity_push(operation_code, balance_code, machine_code, workstation_list, df):
    entropy_scores = compute_predecessor_entropy(df)
    assert len(operation_code) == len(balance_code) == len(machine_code)

    op_data = []
    for op, bal, mac in zip(operation_code, balance_code, machine_code):
        op_id = parse_operation_index(op)
        ent = entropy_scores.get(op_id, 0.0)
        bal = int(float(bal))
        op_data.append((op, bal, ent, mac, op_id))

    # 按机器聚类
    machine_clusters = defaultdict(list)
    for item in op_data:
        machine_clusters[item[3]].append(item)

    ws_pool = sort_ws_by_proximity(workstation_list)
    ws_used = set()
    allocation = {}

    # ========== 第一步：每个机器先分配一个balance最少的工序 ==========
    pre_assigned_ops = set()
    for machine, ops in machine_clusters.items():
        ops.sort(key=lambda x: x[1])  # 按 balance 升序
        op, bal, ent, mac, opid = ops[0]  # 取 balance 最小的

        unused_ws = sort_ws_by_proximity([ws for ws in ws_pool if ws not in ws_used])
        if len(unused_ws) >= bal:
            assigned = unused_ws[:bal]
        else:
            assigned = unused_ws
            still_need = bal - len(assigned)
            additional = [ws for ws in ws_pool if ws not in assigned][:still_need]
            assigned += additional
            print(f"⚠ 机器族预分配：{op} 工作站不足，使用部分已使用工作站补充 → {additional}")

        allocation[op] = {
            '机器': mac,
            '工序编号': opid,
            '信息熵': ent,
            '工作站': assigned
        }
        ws_used.update(assigned)
        pre_assigned_ops.add(op)

    # ========== 第二步：分配剩余所有工序（排除已分配） ==========
    remaining_ops = [item for item in op_data if item[0] not in pre_assigned_ops]
    remaining_ops.sort(key=lambda x: (x[2], x[1]))  # 熵 + balance 排序

    for op, bal, ent, mac, opid in remaining_ops:
        unused_ws = sort_ws_by_proximity([ws for ws in ws_pool if ws not in ws_used])
        if len(unused_ws) >= bal:
            assigned = unused_ws[:bal]
        else:
            assigned = unused_ws
            still_need = bal - len(assigned)
            additional = [ws for ws in ws_pool if ws not in assigned][:still_need]
            assigned += additional
            print(f"⚠ 工序后分配：{op} 工作站不足，使用部分已使用工作站补充 → {additional}")

        allocation[op] = {
            '机器': mac,
            '工序编号': opid,
            '信息熵': ent,
            '工作站': assigned
        }
        ws_used.update(assigned)

    # 最终检查
    for op, info in allocation.items():
        if not info['工作站']:
            raise ValueError(f"工序 {op} 分配失败，未找到工作站")

    print("【最终工作站分配结果 - 新策略】")
    for op, info in allocation.items():
        print(f"{op}（机器:{info['机器']} 熵:{info['信息熵']:.2f}） → {info['工作站']}")

    return allocation
