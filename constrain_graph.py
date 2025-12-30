import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

file_path = 'data/operation_data.xlsx'
operation_data = pd.read_excel(file_path, sheet_name='final')
data=operation_data.copy()
predecessors=data[['工序','可替代工序','前继工序']]
# 创建有向图
G = nx.DiGraph()

# 处理数据：将前继工序和可替代工序转换为图中的边
for idx, row in data.iterrows():
    task = row['工序']
    # 获取前继工序
    predecessors = row['前继工序']
    if predecessors:
        predecessors = [int(x) for x in predecessors.split(',')]  # 将字符串转为列表
        print("1111111111111111")
        print(predecessors)
        for pred in predecessors:
            G.add_edge(pred, task)

    # 处理可替代工序
    if row['可替代工序']:
        alternatives = [int(x) for x in str(row['可替代工序']).split('、')]  # 处理可替代工序
        for alt in alternatives:
            # 为可替代工序添加双向连接
            G.add_edge(task, alt)
            G.add_edge(alt, task)

# 绘制图
plt.figure(figsize=(12, 12))
pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos, with_labels=True, node_size=2000, node_color='skyblue', font_size=10, font_weight='bold', arrows=True)
plt.title("工序依赖关系图")
plt.show()

# 拓扑排序
topological_order = list(nx.topological_sort(G))
print("拓扑排序结果:", topological_order)
