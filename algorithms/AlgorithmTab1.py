from time import time
from math import inf

from algorithms.Algorithm import Algorithm
from algorithms.support.get_exponent_time import get_exponent_time as get_time
from algorithms.support.extra_plotting_data.get_probability_of_processing_data import *
from basic.constants.algorithm_working import *

# Типы событий
APP_RECEIVING_EVENT = 0
HANDLER_COMPLETION_EVENT = 1
ORBIT_RECEIVING_EVENT = 2

# Статусы обработчика
FREE = 0  # Свободно
PROCESSING = 1  # В обработке / занято
BROKEN = 2  # В обработке / занято


class AlgorithmTab1(Algorithm):
    def __init__(self, signal_to_change_progress_value=None):
        super().__init__(signal_to_change_progress_value)
        self.app_count = self.lm = self.mu = self.sg = None
        self.handler_status = None
        self.orbit_app_count = self.not_received_app_count = self.active_app_count = self.processed_app_count = None
        self.T_mod = None
        self.times = None

    def set_parameters(self, application_count, lm, mu, sg):
        # Входные параметры системы:
        self.app_count = application_count  # Количество заявок
        self.lm = lm  # Параметр интенсивности входящего потока
        self.mu = mu  # Параметр интенсивности прихода заявок с орибты
        self.sg = sg  # Параметр интенсивности обработки заявок

        # Начальное состояние системы:

        # Статус обработчика
        self.handler_status = FREE

        # Счётчики заявок
        self.orbit_app_count = 0  # количество заявок на орбите
        self.not_received_app_count = application_count  # заявки, ожидающие поступления в систему
        self.active_app_count = 0  # общее количество заявок в системе
        self.processed_app_count = 0

        self.T_mod = 0  # Модальное время
        self.times = [inf, inf, inf]  # Времена наступления событий

        # Для формирования статистики:
        self.init_collected_data()

    def update_time_events(self):
        self.times = [inf, inf, inf]

        # Генерируется момент времени поступления заявки в систему
        if self.not_received_app_count != 0:
            self.times[APP_RECEIVING_EVENT] = self.T_mod + get_time(self.lm)

        # Определяем момент времени завершения обслуживания
        if self.handler_status == PROCESSING:
            self.times[HANDLER_COMPLETION_EVENT] = self.T_mod + get_time(self.mu)

        # Определяем момент времени обращения заявки с орбиты
        if self.orbit_app_count != 0:  # если орбита не пуста
            self.times[ORBIT_RECEIVING_EVENT] = self.T_mod + get_time(self.sg * self.orbit_app_count)

    def get_nearest_event(self):
        return min(
            [0, 1, 2],
            key=lambda event_id: self.times[event_id]
        )

    def is_all_completed(self):
        return self.app_count == self.processed_app_count

    def get_progress(self):
        return int(self.processed_app_count * 100 / self.app_count)

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

    def run(self):
        while not self.is_all_completed():
            # Шаг 3: моделирование моментов времени наступления всех видов событий
            self.update_time_events()

            # Шаг 4: Определяем момент времени наступления ближайшего события
            nearest_event = self.get_nearest_event()
            self.T_mod = self.times[self.get_nearest_event()]

            # Шаг 5: формирование статистики (в шаге 6)

            # Шаг 6: Определяем изменения состояний системы:
            # Поступление заявки из входящего потока
            if nearest_event == APP_RECEIVING_EVENT:
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

    def get_results(self, application_count, lm, mu, sg):
        start_algorithm_working_time = time()

        self.set_parameters(application_count, lm, mu, sg)
        self.run()

        self.collected_data["data_for_plotting"]["probability_distribution_processed"] = \
            get_probability_of_processing_data(
                self.collected_data["data_for_plotting"]["handler_status_graphic"]["time"].copy(),
                self.collected_data["data_for_plotting"]["handler_status_graphic"]["value"].copy()
            )
        self.collected_data["algorithm_working_time"] = time() - start_algorithm_working_time
        self.collected_data["status"] = -1

        return self.collected_data


def main(application_count, lm, mu, sg):
    return AlgorithmTab1().get_results(application_count, lm, mu, sg)


if __name__ == '__main__':
    result = main(application_count=4, lm=3, mu=1, sg=1)
    for name, data in result["data_for_plotting"].items():
        print("\t", name)
        for time, value in zip(*data.values()):
            print(time, value)
    print(result["algorithm_working_time"])
