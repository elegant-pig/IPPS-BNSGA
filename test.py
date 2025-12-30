# 新的方法,先生成一个工作站-机器分配

import networkx as nx

def min_cost_max_flow_machine_assignment(machine_to_workstations: dict, balance_code: dict):
    """
    使用最小费用最大流算法，为机器分配工作站，尽量满足每个机器的 balance_code 需求。

    参数：
    - machine_to_workstations: dict
        机器可用的工作站集合，例如：
        {
            'M1': ['W1', 'W2'],
            'M2': ['W2', 'W3'],
            ...
        }
    - balance_code: dict
        每台机器希望分配的工作站数量，例如：
        {
            'M1': 2,
            'M2': 3,
            ...
        }

    返回：
    - workstation_to_machine: dict
        每个工作站被分配到的机器，例如：
        {
            'W1': 'M1',
            'W2': 'M2',
            ...
        }
    """

    G = nx.DiGraph()
    source = 'S'
    sink = 'T'

    machines = list(machine_to_workstations.keys())
    all_workstations = set(ws for wss in machine_to_workstations.values() for ws in wss)

    # 添加 source 到机器的边
    for m in machines:
        G.add_edge(source, m, capacity=balance_code[m], weight=0)

    # 添加机器到工作站的边
    for m, wss in machine_to_workstations.items():
        for w in wss:
            G.add_edge(m, w, capacity=1, weight=0)  # 可定制 weight，例如负距离

    # 添加工作站到 sink 的边
    for w in all_workstations:
        G.add_edge(w, sink, capacity=1, weight=0)

    # 求解最小费用最大流
    flow_dict = nx.max_flow_min_cost(G, source, sink)

    # 解析结果：找出哪些工作站被哪台机器占用
    workstation_to_machine = {}
    for m in machines:
        for w, f in flow_dict[m].items():
            if f > 0:
                workstation_to_machine[w] = m

    return workstation_to_machine


machine_to_workstations = {
    'M1': ['W1', 'W2', 'W9', 'W11'],
    'M2': ['W1', 'W4', 'W5', 'W8'],
    'M3': ['W2', 'W3', 'W6', 'W7', 'W10', 'W12'],
}

balance_code = {
    'M1': 2,
    'M2': 4,
    'M3': 6
}

result = min_cost_max_flow_machine_assignment(machine_to_workstations, balance_code)
print("分配结果:", result)
