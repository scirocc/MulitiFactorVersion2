# -*- coding: utf-8 -*-
import time
import numpy as np
import multiprocessing as mp

y = list(np.arange(1, 77777))


def fun(x):
    global y
    if x in y:
        result = True
    else:
        result = False
    return result


check_list = list(
    np.arange(1, 20000)
)
if __name__=='__main__':
    print(1)
# 方法1：map
    time1 = time.time()
    A = list(map(fun, check_list))

    # 方法2：for循环
    time2 = time.time()
    B = []
    for check_str in check_list:
        if check_str in y:
            B.append(True)
        else:
            B.append(False)

    # 方法3：map+多进程
    time3 = time.time()
    pool = mp.Pool()
    C = list(
        pool.map(fun, check_list)
    )
    time4 = time.time()

    cost1 = time2-time1
    cost2 = time3-time2
    cost3 = time4-time3
    print(cost1,cost2,cost3)
