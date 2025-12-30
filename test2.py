import random


import numpy as np
import random

def round_balance_probabilistic(tem_balance, k=10):
    decimal_part = tem_balance - int(tem_balance)
    base = int(tem_balance)
    # 用 sigmoid 平滑决定进位概率
    prob_up = 1 / (1 + np.exp(-k * (decimal_part - 0.5)))
    if random.random() < prob_up:
        base += 1
    # 避免为0
    return max(1, base)


a=round_balance_probabilistic(3.3)
b=round_balance_probabilistic(3.2)
c=round_balance_probabilistic(3.1)
d=round_balance_probabilistic(3.5)
print(a)
print(b)
print(c)
print(d)

