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


def build_workstation_pool(num_stations=25):
    # L1-L12, R1-R12
    left = [f'L{i + 1}' for i in range(num_stations // 2)]
    right = [f'R{i + 1}' for i in range(num_stations // 2)]
    return left + right


def get_workstation_priority(ws):
    side = 0 if ws[0] == 'L' else 1
    num = int(ws[1:])
    return num * 2 + side  # L1=2, R1=3, L2=4, R2=5, ...


def parse_operation_index(op_str):
    """从'O3,4'提取出工序编号 4"""
    return str(int(op_str.split(',')[1]))  # 提取 '4'


def assign_workstations_entropy_with_machine_preference(operation_code, balance_code, entropy_scores, machine_code, total_stations=24):
    assert len(operation_code) == len(balance_code) == len(machine_code)
    op_ids = [parse_operation_index(op) for op in operation_code]
    op_entropy = [entropy_scores.get(op_id, 0.0) for op_id in op_ids]

    # 组成元组并排序：(op_code, balance, entropy, machine, 工序编号)
    op_data = list(zip(operation_code, balance_code, op_entropy, machine_code, op_ids))
    op_data.sort(key=lambda x: x[2])  # 熵升序排序

    ws_pool = build_workstation_pool(total_stations)
    ws_pool = sorted(ws_pool, key=get_workstation_priority)
    used_ws = set()
    allocation = {}
    ws_idx = 0

    for op_code, balance, entropy_val, machine, op_id in op_data:
        assigned = []
        while len(assigned) < balance and ws_idx < len(ws_pool):
            ws = ws_pool[ws_idx]
            if ws not in used_ws:
                assigned.append(ws)
                used_ws.add(ws)
            ws_idx += 1
        allocation[op_code] = {
            'entropy': entropy_val,
            'machine': machine,
            '工序编号': op_id,
            '工作站': assigned
        }

    # 补偿：处理未分配满的工序
    for op_code, info in allocation.items():
        required = balance_code[operation_code.index(op_code)]
        assigned = info['工作站']
        if len(assigned) >= required:
            continue  # 分配足够，无需补偿

        entropy_val = info['entropy']
        machine = info['machine']

        # 候选：已分配成功 & 相同机器
        candidates = [
            (oc, allocation[oc]['entropy'], allocation[oc]['工作站'])
            for oc in allocation
            if allocation[oc]['machine'] == machine and len(allocation[oc]['工作站']) > 0
        ]
        # 按熵值差异排序
        candidates.sort(key=lambda x: abs(x[1] - entropy_val))

        for _, _, cand_ws in candidates:
            for ws in cand_ws:
                if ws not in assigned:
                    assigned.append(ws)
                if len(assigned) >= required:
                    break
            if len(assigned) >= required:
                break

        allocation[op_code]['工作站'] = assigned

    return allocation

# _,workstation_code,workstation_assignments,result_constraint,workstation_machines=generateWorkstation_simple.assignment_operation(tem_data,tem_generate_workstation,num_workstations)
def generate_workstation_code(operation_code,machine_code,balance_code,assignment_result,num_station):
    """
    根据 operation_code 列表和工序工作站分配结果，生成 workstation_code 列表。

    :param operation_code: List[str]，例如 ['O3,4', 'O2,2', ...]
    :param assignment_result: Dict[str, List[str]]，例如 {'O2,2': ['L1', 'R1'], ...}
    :return: List[List[str]]，与 operation_code 等长的 workstation_code 列表。
    """
    assign_workstations_entropy_with_machine_preference(operation_code, balance_code, entropy_scores, machine_code, num_station)

    workstation_code = []
    for op in operation_code:
        workstation_code.append(assignment_result.get(op, []))
    return workstation_code

# # 示例数据
# operation_code = ['O2,2', 'O3,4', 'O1,1', 'O2,3', 'O0,5', 'O0,7', 'O0,8',
#                   'O0,9', 'O0,10', 'O0,11', 'O0,13', 'O0,14', 'O0,15', 'O0,16']
# balance_code = [2, 2, 2, 2, 3, 3, 2, 2, 3, 2, 2, 2, 3, 2]
# file_path = 'data/operation_data.xlsx'
# machine_code=['A','B','C','D','A','A','B','C','E','B','B','A','A','C']
#
# # 加载熵数据
# df = pd.read_excel(file_path, sheet_name='final')
# entropy_scores = compute_predecessor_entropy(df)
#
# # 分配
# allocation = assign_workstations_entropy_with_machine_preference(operation_code, balance_code, entropy_scores,machine_code)
#
# # 打印结果
# for op, info in allocation.items():
#     print(f"{op} (工序{info['工序编号']}，熵={info['entropy']:.4f}) → 工作站分配: {info['工作站']}")

