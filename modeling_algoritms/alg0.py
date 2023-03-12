# Имитационное моделирование систем массового обслуживания

from random import random
from math import log
from time import time


count_elem = 100
lm = 3
sg = 1
mu = 1

s1 = time()

T = [-log(random()) / lm for _ in range(count_elem)]
active_elements = [0] * count_elem
finished_elements = [0] * count_elem

count = 0
handler_S = 0
handler_elem_id = None

while 0 in finished_elements:
    for i in range(count_elem):
        if T[i] == min(T) and not finished_elements[i]:
            # поступление в систему
            if not active_elements[i]:
                active_elements[i] = 1
                count += 1

            # если прибор свободен
            if handler_S == 0:
                handler_S = 1
                handler_elem_id = i
                T[i] += -log(random()) / mu

            # если прибор занят этой заявкой
            elif handler_S == 1 and handler_elem_id == i:
                handler_S = 0
                handler_elem_id = None
                count -= 1
                finished_elements[i] = 1
                T[i] = 9999
            else:  # на орбиту
                T[i] += -log(random()) / sg


print(time() - s1)
