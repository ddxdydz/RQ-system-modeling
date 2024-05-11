import math
import random
from bisect import bisect_right
import time
import numpy as np

from algorithms.support.get_exponent_time import get_time as get_exponent_time


def choose_index(probabilities):
    cumulative_probabilities = [sum(probabilities[:i + 1]) for i in range(len(probabilities))]
    random_number = random.uniform(0.0, 1.0)

    # bisect_right находит первый элемент, который больше заданного значения:
    index = bisect_right(cumulative_probabilities, random_number)

    return index


def simulate_rq_system():
    """
    Основная функция имитационной модели RQ-системы с ненадежным прибором.
    """

    # Параметры RQ-системы
    Q = np.array([[-0.4, 0.1, 0.3], [0.3, -0.5, 0.2], [0.1, 0.1, -0.2]])  # Матрица интенсивностей, матрица инфинитезимальных характеристик

    LAMBDA = [1.0, 2.0, 3.0]  # Вектор условных интенсивностей
    # для простейшего входящего потока задается одно значение лямбды для всего вектора
    # для MMPP потока задаются различные значения

    sigma = 0.02  # Параметр времени ожидания заявки на орбите
    mu1 = 3.0  # Параметр времени обслуживания заявок
    mu2 = 2.0  # Параметр времени восстановления прибора
    gamma1 = 0.4  # Параметр времени бесперебойной работы прибора в свободном состоянии
    gamma2 = 0.2  # Параметр времени бесперебойной работы прибора в занятом состоянии

    # Начальные условия
    k = 0  # Состояние прибора (0 - свободен, 1 - занят, 2 - неисправен)
    i = 0  # Количество заявок на орбите

    # Вычисление вероятностей состояний цепи Маркова
    A = np.array([[Q[0][0], Q[1][0], Q[2][0]],
                  [Q[0][1], Q[1][1], Q[2][1]],
                  [Q[0][2], Q[1][2], Q[2][2]],
                  [1, 1, 1]])
    b = np.array([0, 0, 0, 1])
    r = np.linalg.solve(A.T @ A, A.T @ b)  # решает систему линейных уравнений (решение системы - r)

    # Выбор интенсивности входящего потока
    n = choose_index(r)  # Начальное состояние цепи Маркова
    lambda_selected = LAMBDA[n]  # параметр интенсивности прихода заявок
    q_selected = Q[n][n]  # параметр интенсивности смены состояния цепи Маркова

    # Вычисление переходных вероятностей
    Perehod0 = [0, Q[0][1] / (-Q[0][0]), Q[0][2] / (-Q[0][0])]
    Perehod1 = [Q[1][0] / (-Q[1][1]), 0, Q[1][2] / (-Q[1][1])]
    Perehod2 = [Q[2][0] / (-Q[2][2]), Q[2][1] / (-Q[2][2]), 0]

    # остальной код имитационной модели
    t = 0  # время начинается с нуля

    # Имитация по единицам времени
    for _ in range(10000000):  # цикл по единице времени (сек., мин., часы и т.д.)

        # ... (вывод графиков - закомментировано)

        # Генерация случайных времен событий:
        M = get_exponent_time(q_selected)  # Время смены состояния цепи Маркова
        X = get_exponent_time(lambda_selected)  # Время поступления заявки
        Y = math.inf if k in (0, 2) else get_exponent_time(mu1)  # Время обслуживания заявки
        Z = math.inf if i == 0 else get_exponent_time(sigma * i)  # Время ожидания на орбите
        # Генерация времен для событий, зависящих от состояния прибора
        B, W, S = math.inf, math.inf, math.inf  # Время бесперебойной работы и восстановления
        if k == 0:
            B = get_exponent_time(gamma1)  # Время бесперебойной работы в свободном состоянии
        elif k == 1:
            W = get_exponent_time(gamma2)  # Время бесперебойной работы в занятом состоянии
        else:
            S = get_exponent_time(mu2)  # Время завершения восстановления

        # Определение следующего события
        t_last, i_last = t, i
        next_event = min(M, X, Y, Z, B, W, S)
        t += next_event

        if next_event == M:  # Смена состояния цепи Маркова
            Perehod = Perehod0 if n == 0 else Perehod1 if n == 1 else Perehod2
            n = choose_index(Perehod)  # Начальное состояние цепи Маркова
            lambda_selected = LAMBDA[n]  # параметр интенсивности прихода заявок
            q_selected = Q[n][n]  # параметр интенсивности смены состояния цепи Маркова

        elif next_event == X:  # Поступление заявки
            if k == 0:
                k += 1  # Заявка начинает обслуживание
            else:
                i += 1  # Заявка уходит на орбиту

        elif next_event == Y:  # Завершение обслуживания
            k -= 1

        elif next_event == Z:  # Завершение ожидания на орбите
            if k == 0:
                i -= 1
                k += 1

        elif next_event == B:  # Выход из строя в свободном состоянии
            k = 2

        elif next_event == W:  # Выход из строя в занятом состоянии
            k = 2
            i += 1

        elif next_event == S:  # Восстановление
            k = 0


# Запуск имитации
simulate_rq_system()
