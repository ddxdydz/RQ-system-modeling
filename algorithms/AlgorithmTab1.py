from time import time
from math import inf

from algorithms.Algorithm import Algorithm
from algorithms.support.get_time import get_time
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


class AlgorithmTab1(Algorithm):
    def __init__(self, signal_to_change_progress_value=None):
        super().__init__(signal_to_change_progress_value)

    def set_parameters(self, application_count, lm, mu, sg):
        self.app_count = application_count
        self.lm = lm
        self.mu1 = mu
        self.sg = sg

        # Статус обработчика:
        self.handler_status = FREE

        # Счётчики заявок:
        self.not_received_app_count = application_count
        self.orbit_app_count = 0
        self.active_app_count = 0
        self.processed_app_count = 0

        self.event_manager = EventManager()
        self.init_collected_data()

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

    def from_orbit(self, event_time):
        self.orbit_app_count -= 1

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

    def get_results(self, application_count, lm, mu, sg):
        """
        :param app_count:
        :param lm: интенсивность прихода заявок
        :param mu: интенсивность обслуживания
        :param sg: время на орбите
        :return:
        """
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
