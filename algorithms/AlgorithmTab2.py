from time import time
from math import inf

from algorithms.Algorithm import Algorithm
from algorithms.support.get_time import get_time
from algorithms.support.extra_plotting_data.get_probability_of_processing_data import *
from algorithms.support.extra_plotting_data.get_probability_of_orbit_data import *
from algorithms.support.extra_plotting_data.get_probability_of_orbit_data_from_orbit import *
from basic.constants.algorithm_working import *

# Типы событий
APP_RECEIVING_EVENT = 0
HANDLER_COMPLETION_EVENT = 1
ORBIT_RECEIVING_EVENT = 2
HANDLER_FREE_BROKEN_EVENT = 3
HANDLER_PROCESSING_BROKEN_EVENT = 4
HANDLER_RECOVER_EVENT = 5

# Статусы обработчика
FREE = 0  # Свободно
PROCESSING = 1  # В обработке / занято
BROKEN = 2  # В обработке / занято


class EventManager:
    def __init__(self):
        # Времена наступления событий по их ID типа:
        self.events_times = [inf, inf, inf, inf, inf, inf]

        # Предыдущий момент времени:
        self.T_last = 0

        # Модальное время:
        self.T_mod = 0

    def change_event_time(self, event_type, event_delta_time):
        self.events_times[event_type] = self.T_mod + event_delta_time

    def get_event_time(self, event_type):
        return self.events_times[event_type]

    def get_nearest_event(self):
        return min(
            [0, 1, 2, 3, 4, 5],
            key=lambda event_id: self.events_times[event_id]
        )


class AlgorithmTab2(Algorithm):
    def __init__(self, signal_to_change_progress_value=None):
        super().__init__(signal_to_change_progress_value)

    def set_parameters(self, application_count, lm, mu1, mu2, sg, dt1, dt2):
        self.app_count = application_count
        self.lm = lm
        self.mu1 = mu1
        self.mu2 = mu2
        self.sg = sg
        self.dt1 = dt1
        self.dt2 = dt2

        # Статус обработчика:
        self.handler_status = FREE

        # Счётчики заявок:
        self.not_received_app_count = application_count
        self.orbit_app_count = 0
        self.active_app_count = 0
        self.processed_app_count = 0

        self.event_manager = EventManager()
        self.init_collected_data()
        self.collected_data["data_for_plotting"]["orbit_status_graphic"] = {"time": [0], "value": [0]}

    def add_data_to_orbit_status_graphic(self, time: int, value: int):
        self.collected_data["data_for_plotting"]["orbit_status_graphic"]["time"].append(time)
        self.collected_data["data_for_plotting"]["orbit_status_graphic"]["value"].append(value)

    def update_time_events(self):
        # Генерируется момент времени поступления заявки в систему
        if self.not_received_app_count != 0:
            self.event_manager.change_event_time(APP_RECEIVING_EVENT, get_time(self.lm))
        else:
            self.event_manager.change_event_time(APP_RECEIVING_EVENT, inf)

        # Определяем момент времени завершения обслуживания
        if self.handler_status == PROCESSING:
            self.event_manager.change_event_time(HANDLER_COMPLETION_EVENT, get_time(self.mu1))
        else:
            self.event_manager.change_event_time(HANDLER_COMPLETION_EVENT, inf)

        # Определяем момент времени обращения заявки с орбиты
        if self.orbit_app_count == 0:
            self.event_manager.change_event_time(ORBIT_RECEIVING_EVENT, inf)
        else:
            self.event_manager.change_event_time(ORBIT_RECEIVING_EVENT, get_time(self.sg) / self.orbit_app_count)

        # Определяем моменты времени выхода прибора из строя и завершения восстановления
        if self.handler_status != BROKEN:
            self.event_manager.change_event_time(HANDLER_RECOVER_EVENT, inf)
            if self.handler_status == FREE:
                self.event_manager.change_event_time(HANDLER_FREE_BROKEN_EVENT, get_time(self.dt1))
                self.event_manager.change_event_time(HANDLER_PROCESSING_BROKEN_EVENT, inf)
            else:
                self.event_manager.change_event_time(HANDLER_FREE_BROKEN_EVENT, inf)
                self.event_manager.change_event_time(HANDLER_PROCESSING_BROKEN_EVENT, get_time(self.dt2))
        else:
            self.event_manager.change_event_time(HANDLER_FREE_BROKEN_EVENT, inf)
            self.event_manager.change_event_time(HANDLER_PROCESSING_BROKEN_EVENT, inf)
            self.event_manager.change_event_time(HANDLER_RECOVER_EVENT, get_time(self.mu2))

    def is_all_completed(self):
        return self.app_count == self.processed_app_count

    def get_progress(self):
        return int(self.processed_app_count * 100 / self.app_count)

    def to_active_app(self, event_time):  # поступление заявки в систему
        self.not_received_app_count -= 1
        self.active_app_count += 1

        self.add_data_to_application_count_graphic(event_time, self.active_app_count)

    def to_orbit(self, event_time):
        self.orbit_app_count += 1

        self.add_data_to_orbit_status_graphic(event_time, self.orbit_app_count)

    def from_orbit(self, event_time):
        self.orbit_app_count -= 1

        self.add_data_to_orbit_status_graphic(event_time, self.orbit_app_count)

    def to_process_in_handler(self, event_time):  # начало обработки заявки
        self.handler_status = PROCESSING

        self.add_data_to_handler_status_graphic(event_time, self.handler_status)
        self.progress_indicator.update(self.get_progress())

    def to_finish_handler(self, event_time):  # конец обработки заявки
        self.handler_status = FREE

        self.active_app_count -= 1
        self.processed_app_count += 1

        self.add_data_to_application_count_graphic(event_time, self.active_app_count)
        self.add_data_to_handler_status_graphic(event_time, self.handler_status)

    def to_broken_free_handler(self, event_time):
        self.handler_status = BROKEN

        self.add_data_to_handler_status_graphic(event_time, self.handler_status)

    def to_broken_processing_handler(self, event_time):
        self.handler_status = BROKEN

        self.to_orbit(event_time)

        self.add_data_to_handler_status_graphic(event_time, self.handler_status)

    def to_recover_handler(self, event_time):
        self.handler_status = FREE

        self.add_data_to_handler_status_graphic(event_time, self.handler_status)

    def run(self):
        while not self.is_all_completed():
            # Шаг 3: моделирование моментов времени наступления всех видов событий
            self.update_time_events()

            # Шаг 4: Определяем момент времени наступления ближайшего события
            nearest_event = self.event_manager.get_nearest_event()
            event_time = self.event_manager.get_event_time(nearest_event)
            self.event_manager.T_last = self.event_manager.T_mod
            self.event_manager.T_mod = event_time

            # Шаг 5: формирование статистики (в шаге 6)

            # Шаг 6: Определяем изменения состояний системы

            # Поступление заявки из входящего потока
            if nearest_event == APP_RECEIVING_EVENT:  # поступление заявки из входящего потока
                self.to_active_app(event_time)
                if self.handler_status == FREE:
                    self.to_process_in_handler(event_time)
                else:
                    self.to_orbit(event_time)
            # Завершение обслуживания заявки
            elif nearest_event == HANDLER_COMPLETION_EVENT:
                self.to_finish_handler(event_time)
            # Обращение заявки с орбиты к прибору
            elif nearest_event == ORBIT_RECEIVING_EVENT:
                if self.handler_status == FREE:
                    self.from_orbit(event_time)
                    self.to_process_in_handler(event_time)
            # Выход из строя прибора, когда он свободен
            elif nearest_event == HANDLER_FREE_BROKEN_EVENT:
                self.to_broken_free_handler(event_time)
            # Выход из строя прибора, когда он занят
            elif nearest_event == HANDLER_PROCESSING_BROKEN_EVENT:
                self.to_broken_processing_handler(event_time)
            # Восстановление прибора
            elif nearest_event == HANDLER_RECOVER_EVENT:
                self.to_recover_handler(event_time)

    def get_results(self, application_count, lm, mu1, mu2, sg, dt1, dt2):
        """
        :param app_count:
        :param lm: интенсивность прихода заявок
        :param mu1: интенсивность обслуживания
        :param mu2: время восстановления
        :param sg: время на орбите
        :param dt1: время выхода из строя если свободен
        :param dt2: время выхода из строя если занят
        :return:
        """
        start_algorithm_working_time = time()
        self.set_parameters(application_count, lm, mu1, mu2, sg, dt1, dt2)
        self.run()
        self.collected_data["data_for_plotting"]["probability_distribution_processed"] = \
            get_probability_of_processing_data(
                self.collected_data["data_for_plotting"]["handler_status_graphic"]["time"].copy(),
                self.collected_data["data_for_plotting"]["handler_status_graphic"]["value"].copy()
            )
        self.collected_data["data_for_plotting"]["probability_distribution_orbit"] = \
            get_probability_of_orbit_data(
                self.collected_data["data_for_plotting"]["application_count_graphic"]["time"].copy(),
                self.collected_data["data_for_plotting"]["application_count_graphic"]["value"].copy(),
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


def main(application_count, lm, mu, mu2, sg, dt1, dt2):
    return AlgorithmTab2().get_results(application_count, lm, mu, mu2, sg, dt1, dt2)


if __name__ == '__main__':
    result = main(application_count=4, lm=3, mu=1, mu2=1, sg=1, dt1=0.5, dt2=0.5)
    for name, data in result["data_for_plotting"].items():
        print("\t", name)
        for time, value in zip(*data.values()):
            print(time, value)
    print(result["algorithm_working_time"])
