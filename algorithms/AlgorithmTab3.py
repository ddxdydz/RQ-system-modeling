from time import time
from math import inf
from bisect import bisect_right
from random import uniform
import numpy as np

from algorithms.Algorithm import Algorithm
from algorithms.support.get_exponent_time import get_exponent_time as get_time
from algorithms.support.extra_plotting_data.get_probability_of_processing_data import *
from algorithms.support.extra_plotting_data.get_probability_of_orbit_data_from_orbit import *

# Типы событий
APP_RECEIVING_EVENT = 0
HANDLER_COMPLETION_EVENT = 1
ORBIT_RECEIVING_EVENT = 2
HANDLER_FREE_BROKEN_EVENT = 3
HANDLER_PROCESSING_BROKEN_EVENT = 4
HANDLER_RECOVER_EVENT = 5
MARKOV_CHAIN_STATE_EVENT = 6

# Статусы обработчика
FREE = 0  # Свободно
PROCESSING = 1  # В обработке / занято
BROKEN = 2  # В обработке / занято


class AlgorithmTab3(Algorithm):
    def __init__(self, signal_to_change_progress_value=None):
        super().__init__(signal_to_change_progress_value)
        self.mu1 = self.mu2 = self.sigma = self.gamma1 = self.gamma2 = self.lambdas = self.q = self.v = None
        self.lambda_selected = self.q_selected = None
        self.handler_status = None
        self.orbit_app_count = self.not_received_app_count = self.active_app_count = self.processed_app_count = None
        self.T_mod = None
        self.times = None

    def set_parameters(self, mu1, mu2, sigma, gamma1, gamma2, lambdas, q, v):
        # Входные параметры системы:
        self.mu1 = mu1  # Параметр интенсивности прихода заявок с орибты
        self.mu2 = mu2  # Параметр интенсивности восстановления прибора
        self.sigma = sigma  # Параметр интенсивности обработки заявок
        self.gamma1 = gamma1  # Параметр интенсивности поломки прибора, когда он свободен
        self.gamma2 = gamma2  # Параметр интенсивности поломки прибора, когда он занят
        self.lambdas = lambdas[0]  # Вектор условных интенсивностей
        self.q = q  # Матрица инфинитезимальных характеристик
        self.v = v  # количество заявок

        # Параметры определяемые далее:
        self.lambda_selected = None  # параметр интенсивности прихода заявок
        self.q_selected = None  # параметр интенсивности смены состояния цепи Маркова

        # Начальное состояние системы:

        # Статус обработчика
        self.handler_status = FREE

        # Счётчики заявок
        self.orbit_app_count = 0  # количество заявок на орбите
        self.not_received_app_count = v  # заявки, ожидающие поступления в систему
        self.active_app_count = 0  # общее количество заявок в системе
        self.processed_app_count = 0

        self.T_mod = 0  # Модальное время
        self.times = [inf, inf, inf, inf, inf, inf, inf]  # Времена наступления событий

        # Для формирования статистики:
        self.init_collected_data()

    def update_time_events(self):
        self.times = [inf, inf, inf, inf, inf, inf, inf]

        # Генерируется момент смены состояния цепи Маркова
        self.times[MARKOV_CHAIN_STATE_EVENT] = self.T_mod + get_time(-self.q_selected)

        # Генерируется момент времени поступления заявки в систему
        if self.not_received_app_count != 0:
            self.times[APP_RECEIVING_EVENT] = self.T_mod + get_time(self.lambda_selected)

        # Определяем момент времени завершения обслуживания
        if self.handler_status == PROCESSING:
            self.times[HANDLER_COMPLETION_EVENT] = self.T_mod + get_time(self.mu1)

        # Определяем момент времени обращения заявки с орбиты
        if self.orbit_app_count != 0:  # если орбита не пуста
            self.times[ORBIT_RECEIVING_EVENT] = self.T_mod + get_time(self.sigma * self.orbit_app_count)

        # Определяем моменты времени выхода прибора из строя и завершения восстановления
        if self.handler_status == FREE:
            self.times[HANDLER_FREE_BROKEN_EVENT] = self.T_mod + get_time(self.gamma1)
        elif self.handler_status == PROCESSING:
            self.times[HANDLER_PROCESSING_BROKEN_EVENT] = self.T_mod + get_time(self.gamma2)
        else:
            self.times[HANDLER_RECOVER_EVENT] = self.T_mod + get_time(self.mu2)

    def get_nearest_event(self):
        return min(
            [0, 1, 2, 3, 4, 5, 6],
            key=lambda event_id: self.times[event_id]
        )

    def is_all_completed(self):
        return self.v == self.processed_app_count

    def get_progress(self):
        return int(self.processed_app_count * 100 / self.v)

    def add_to_system(self):  # учёт поступления заявки в систему
        self.not_received_app_count -= 1
        self.active_app_count += 1

        self.add_data_to_application_count_graphic(self.T_mod, self.active_app_count)

    def remove_from_system(self):  # учёт ухода обработанной заявки из системы
        self.active_app_count -= 1
        self.processed_app_count += 1

        self.add_data_to_application_count_graphic(self.T_mod, self.active_app_count)

    def add_to_orbit(self):  # учёт поступления заявки на орбиту
        self.orbit_app_count += 1

        self.add_data_to_orbit_status_graphic(self.T_mod, self.orbit_app_count)

    def deduct_from_orbit(self):  # учёт ухода заявки с орбиты
        self.orbit_app_count -= 1

        self.add_data_to_orbit_status_graphic(self.T_mod, self.orbit_app_count)

    def change_handler_status(self, new_status):  # учёт изменения статуса обработчика

        # Если прибор обработал заявку, то обновляем индикатор прогресса:
        if self.handler_status == PROCESSING and new_status == FREE:
            self.progress_indicator.update(self.get_progress())

        self.handler_status = new_status

        self.add_data_to_handler_status_graphic(self.T_mod, self.handler_status)

    @staticmethod
    def choose_index(probabilities):
        cumulative_probabilities = [sum(probabilities[:i + 1]) for i in range(len(probabilities))]
        random_number = uniform(0.0, 1.0)

        # bisect_right находит первый элемент, который больше заданного значения:
        index = bisect_right(cumulative_probabilities, random_number)

        return index

    def run(self):
        # Вычисление вероятностей состояний цепи Маркова
        size_q = len(self.q)
        matrix_q = np.array(self.q)
        string_of_ones = np.array([[1] * size_q])
        matrix_a = np.vstack([matrix_q.T, string_of_ones])
        b = np.array([0] * size_q + [1])
        r = np.linalg.solve(matrix_a.T @ matrix_a, matrix_a.T @ b)  # решение системы - r

        # Выбор интенсивности входящего потока
        n = self.choose_index(r)  # Начальное состояние цепи Маркова
        self.lambda_selected = self.lambdas[n]  # параметр интенсивности прихода заявок
        self.q_selected = self.q[n][n]  # параметр интенсивности смены состояния цепи Маркова

        # Вычисление переходных вероятностей
        perehod = []
        for row in range(size_q):
            perehod.append([])
            for col in range(size_q):
                if row == col:  # на диагонали нули
                    perehod[row].append(0)
                else:  # иначе отношение недиагонального элемента к диагональному элементу с минусом
                    perehod[row].append(self.q[row][col] / (-self.q[row][row]))

        # остальной код имитационной модели
        while self.v != self.processed_app_count:  # цикл по единице времени (сек., мин., часы и т.д.)
            # Шаг 3: моделирование моментов времени наступления всех видов событий
            self.update_time_events()

            # Шаг 4: Определяем момент времени наступления ближайшего события
            nearest_event = self.get_nearest_event()
            self.T_mod = self.times[self.get_nearest_event()]

            # Шаг 5: формирование статистики (в шаге 6)

            # Шаг 6: Определяем изменения состояний системы:
            if nearest_event == MARKOV_CHAIN_STATE_EVENT:  # Смена состояния цепи Маркова
                n = self.choose_index(perehod[n])  # Начальное состояние цепи Маркова
                self.lambda_selected = self.lambdas[n]  # параметр интенсивности прихода заявок
                self.q_selected = self.q[n][n]  # параметр интенсивности смены состояния цепи Маркова
            # Поступление заявки из входящего потока
            elif nearest_event == APP_RECEIVING_EVENT:
                self.add_to_system()
                if self.handler_status == FREE:
                    self.change_handler_status(PROCESSING)
                else:
                    self.add_to_orbit()
            # Завершение обслуживания заявки
            elif nearest_event == HANDLER_COMPLETION_EVENT:
                self.remove_from_system()
                self.change_handler_status(FREE)
            # Обращение заявки с орбиты к прибору
            elif nearest_event == ORBIT_RECEIVING_EVENT:
                if self.handler_status == FREE:
                    self.deduct_from_orbit()
                    self.change_handler_status(PROCESSING)
            # Выход из строя прибора, когда он свободен
            elif nearest_event == HANDLER_FREE_BROKEN_EVENT:
                self.change_handler_status(BROKEN)
            # Выход из строя прибора, когда он занят
            elif nearest_event == HANDLER_PROCESSING_BROKEN_EVENT:
                self.change_handler_status(BROKEN)
                self.add_to_orbit()
            # Восстановление прибора
            elif nearest_event == HANDLER_RECOVER_EVENT:
                self.change_handler_status(FREE)

    def get_results(self, mu1, mu2, sigma, gamma1, gamma2, lambdas, q, v):
        start_algorithm_working_time = time()

        self.set_parameters(mu1, mu2, sigma, gamma1, gamma2, lambdas, q, v)
        self.run()

        self.collected_data["data_for_plotting"]["probability_distribution_processed"] = \
            get_probability_of_processing_data(
                self.collected_data["data_for_plotting"]["handler_status_graphic"]["time"].copy(),
                self.collected_data["data_for_plotting"]["handler_status_graphic"]["value"].copy()
            )
        self.collected_data["data_for_plotting"]["probability_distribution_orbit"] = \
            get_probability_of_orbit_data_from_orbit(
                self.collected_data["data_for_plotting"]["orbit_status_graphic"]["time"].copy(),
                self.collected_data["data_for_plotting"]["orbit_status_graphic"]["value"].copy()
            )
        self.collected_data["algorithm_working_time"] = time() - start_algorithm_working_time
        self.collected_data["status"] = -1

        return self.collected_data


def main(mu1, mu2, sigma, gamma1, gamma2, lambdas, q, v):
    return AlgorithmTab3().get_results(mu1, mu2, sigma, gamma1, gamma2, lambdas, q, v)


if __name__ == '__main__':
    result = main(mu1=3, mu2=2, sigma=0.02, gamma1=0.4, gamma2=0.2, lambdas=[[2.0, 2.0, 2.0]],
                  q=[[-0.4, 0.1, 0.3], [0.3, -0.5, 0.2], [0.1, 0.1, -0.2]], v=4)
    for name, data in result["data_for_plotting"].items():
        print("\t", name)
        for time, value in zip(*data.values()):
            print(time, value)
    print(result["algorithm_working_time"])
