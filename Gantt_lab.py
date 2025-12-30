import matplotlib.pyplot as plt
import pandas as pd
import random
import os

# # 实验室电脑环境
# os.environ['TCL_LIBRARY'] = r'C:\Users\elegant_pigg\AppData\Local\Programs\Python\Python313\tcl\tcl8.6'
# os.environ['TK_LIBRARY'] = r'C:\Users\elegant_pigg\AppData\Local\Programs\Python\Python313\tcl\tk8.6'

# # 自己的电脑环境
# os.environ['TCL_LIBRARY'] = r'D:\Users\tanin\AppData\Local\Programs\Python\Python310\tcl\tcl8.6'
# os.environ['TK_LIBRARY'] = r'D:\Users\tanin\AppData\Local\Programs\Python\Python310\tcl\tk8.6'
#
# # import matplotlib.pyplot as plt
# matplotlib.use('TkAgg')  # 设置后端为 TkAgg，兼容大多数环境

# 定义绘图函数
def plot_gantt_chart(workstation_available_time):
    # 准备数据
    data = []
    for workstation, details in workstation_available_time.items():
        for job in details['assigned_jobs']:
            data.append({
                'Workstation': workstation,
                'Batch': job['batch'],
                'Operation': job['operation'],
                'Start': job['start_time'],
                'End': job['end_time']
            })

    df = pd.DataFrame(data)

    # 生成颜色映射，每个批次一种颜色
    unique_batches = df['Batch'].unique()
    colors = {batch: f'#{random.randint(0, 0xFFFFFF):06x}' for batch in unique_batches}

    # 创建绘图
    fig, ax = plt.subplots(figsize=(30, 8))  # 增加宽度，原先是 (12, 8)

    for index, row in df.iterrows():
        batch = row['Batch']
        operation = row['Operation']

        # 提取工序编号的 y 部分（例如 'O1,1' 提取 '1'）
        operation_y = operation.split(',')[1]  # 获取工序编号（'y' 部分）

        color = colors[row['Batch']]
        ax.barh(
            row['Workstation'],
            row['End'] - row['Start'],
            left=row['Start'],
            height=0.8,
            color=color,
            edgecolor='black'
        )
        # 在条形图中间标注工序编号
        ax.text(
            x=(row['Start'] + row['End']) / 2,
            y=row['Workstation'],
            s=operation_y,
            ha='center',
            va='center',
            color='white',
            fontsize=9,
            fontweight='bold'
        )

    # 设置轴标签和标题
    plt.xlabel('Time (in seconds)')
    plt.ylabel('Workstation')
    plt.title('Gantt Chart for Workstation and Process Allocation')

    # 添加批次图例
    legend_labels = [f'Batch {batch}' for batch in unique_batches]
    legend_colors = [plt.Rectangle((0, 0), 1, 1, color=colors[batch]) for batch in unique_batches]
    ax.legend(legend_colors, legend_labels, title="Batches", loc='upper right')

    plt.tight_layout()
    # plt.savefig("C:/Users/YourName/Desktop/plot.png")

    plt.show(block=False)

# 调用绘图函数
# plot_gantt_chart(workstation_available_time)