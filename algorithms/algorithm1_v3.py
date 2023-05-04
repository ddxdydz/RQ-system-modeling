from math import log
from random import random
from time import time

from algorithms.algorithm1_settings import *
from constants import *

# Статусы заявок
NOT_RECEIVED = 1352  # Не принято в обработку
ACTIVE = 1536  # Находится в системе / активно
COMPLETED = 1435  # Завершено / обработано
# Статусы обработчика
FREE = 2643  # Свободно
PROCESSING = 2366  # В обработке / занято


class Algorithm1:
    def __init__(self, application_count=None, lm=None, mu=None, sg=None):
        self.application_count = application_count
        self.lm, self.mu, self.sg = lm, mu, sg
        self.signal_to_change_progress_value = None

        self.sum_time_processing = 0
        self.last_progress_value = 0
        self.handler_time_to_sum = 0  # Время после которого, время работы не учтено
        self.collected_data = dict()

        self.completed_applications_count = 0  # Количество обработанных заявок
        self.active_applications_count = 0  # Количество заявок, находящихся в системе

        self.handler_status = FREE
        self.handler_app_id = None  # Индекс заявки, находящейся в обработке

        self.applications_statuses = list()
        self.times_of_unprocessed_events_by_application_indexes = list()
        self.sorted_app_ids = list()

    def clear_collected_data(self):
        self.collected_data = {
            "events_data": [
                {
                    "time": 0,
                    "values":
                        {
                            "application_count_graphic": 0,
                            "handler_status_graphic": 0,
                            "handler_percent_graphic": 0
                        }
                }
            ],
            "algorithm_working_time": None,
            "number_of_iterations": 0,
            "status": 0
        }

    def update_alg_iteration_values(self):
        self.sum_time_processing = 0
        self.last_progress_value = 0
        self.handler_time_to_sum = 0
        self.clear_collected_data()

        self.completed_applications_count = 0
        self.active_applications_count = 0
        self.sum_time_processing = 0

        self.handler_status = FREE
        self.handler_app_id = None

        # Статусы заявок по их индексам:
        self.applications_statuses = [NOT_RECEIVED] * self.application_count
        # Изначально в системе нет заявок, поэтому у всех заявок статусы "NOT_RECEIVED".

        # Список, содержащий время наступления ближайшего необработанного события для каждой заявки по её индексу:
        self.times_of_unprocessed_events_by_application_indexes = \
            [self.get_arrival_time() for _ in range(self.application_count)]
        # Изначально у каждой заявки ближайшим событием является поступление в систему.

        # Индексы отсортированных заявок по временам наступления их необработанных ближайших событий
        self.sorted_app_ids = sorted(
            list(range(self.application_count)),
            key=lambda app_i: self.times_of_unprocessed_events_by_application_indexes[app_i]
        )

    def set_parameters(self, application_count=None, lm=None, mu=None, sg=None):
        self.application_count = application_count
        self.lm, self.mu, self.sg = lm, mu, sg

    def set_signal_to_change_progress_value(self, signal):
        self.signal_to_change_progress_value = signal

    def get_arrival_time(self) -> float:
        return -log(random()) / self.lm

    def get_handler_time(self) -> float:
        return -log(random()) / self.mu

    def get_orbit_time(self) -> float:
        return -log(random()) / self.sg

    def to_active_app(self, app_id):
        self.applications_statuses[app_id] = ACTIVE
        self.active_applications_count += 1

    def to_process_handler(self, app_id):
        self.handler_status = PROCESSING
        self.handler_app_id = app_id
        self.handler_time_to_sum = self.times_of_unprocessed_events_by_application_indexes[app_id]
        self.times_of_unprocessed_events_by_application_indexes[app_id] += self.get_handler_time()

    def to_free_handler(self):
        self.handler_status = FREE
        self.applications_statuses[self.handler_app_id] = COMPLETED
        self.handler_app_id = None
        self.completed_applications_count += 1
        self.active_applications_count -= 1

    def to_orbit(self, app_id):
        self.times_of_unprocessed_events_by_application_indexes[app_id] += self.get_orbit_time()

    def dih_search(self, value, left: int, right: int, key):
        self.collected_data["number_of_iterations"] += 1
        average = (left + right) // 2
        if key(average) == value:
            return average
        elif right - left == 1:
            if key(left) < value <= key(right):
                return right
            elif key(left) == value:
                return left
            elif key(right) < value:
                return right + 1
            elif key(left) > value:
                return left
        elif left == right:
            if value <= key(left):
                return left
            return right + 1
        else:
            if key(average) < value:
                return self.dih_search(value, average, right, key=key)
            return self.dih_search(value, left, average, key=key)

    def get_insert_id(self, app_event_time):
        insert_id = self.dih_search(
            app_event_time, 0, len(self.sorted_app_ids) - 1,
            key=lambda i: self.times_of_unprocessed_events_by_application_indexes[
                self.sorted_app_ids[i]]
        )
        return insert_id

    def update_sorted_app_ids_list(self, nearest_app_id):
        next_nearest_event_time = \
            self.times_of_unprocessed_events_by_application_indexes[nearest_app_id]
        if len(self.sorted_app_ids) > 1:
            self.sorted_app_ids.pop(0)
            if self.applications_statuses[nearest_app_id] != COMPLETED:
                self.sorted_app_ids.insert(
                    self.get_insert_id(next_nearest_event_time), nearest_app_id)

    def collect_data(self, nearest_event_time):
        if self.handler_status == PROCESSING and self.handler_app_id != nearest_event_time:
            self.sum_time_processing += nearest_event_time - self.handler_time_to_sum
            self.handler_time_to_sum = nearest_event_time

        self.collected_data["events_data"].append(
            {
                "time": nearest_event_time,
                "values":
                    {
                        "application_count_graphic": self.active_applications_count,
                        "handler_status_graphic": int(self.handler_status == PROCESSING),
                        "handler_percent_graphic": int(self.sum_time_processing * 100 / nearest_event_time)
                    }
            }
        )

    def update_indicator(self, completed_applications_count):
        if self.signal_to_change_progress_value is not None:
            progress = int(completed_applications_count * 100 / self.application_count)
            if progress != self.last_progress_value and progress % 5 == 0:
                self.signal_to_change_progress_value.emit(progress)
                self.last_progress_value = progress
                print(progress)
            if self.collected_data["number_of_iterations"] > ITERATION_LIMIT_COUNT and progress < 5:
                self.collected_data["status"] = ITERATION_LIMIT
                return True
        return False

    def run(self):
        completed_applications_count = 0

        while completed_applications_count != self.application_count:

            # Находим индекс заявки, участвующей в необработанном событии, которое наступает раньше остальных:
            nearest_app_id = self.sorted_app_ids[0]
            nearest_app_time = self.times_of_unprocessed_events_by_application_indexes[nearest_app_id]

            # Поступление заявки в систему:
            if self.applications_statuses[nearest_app_id] == NOT_RECEIVED:
                self.to_active_app(nearest_app_id)
            # Если прибор свободен, то занимаем его ближайшей заявкой:
            if self.handler_status == FREE:
                self.to_process_handler(nearest_app_id)
            # Если прибор был занят текущей заявкой, то освобождаем его:
            elif self.handler_app_id == nearest_app_id:
                completed_applications_count += 1
                self.to_free_handler()
            else:  # на орбиту
                self.to_orbit(nearest_app_id)

            # Обновление отсортированного списка индексов sorted_app_ids:
            self.update_sorted_app_ids_list(nearest_app_id)

            # Сбор данных на текущей итерации:
            self.collect_data(nearest_app_time)

            # Обновление индикаторов выполнения:
            if self.update_indicator(completed_applications_count):
                break

    def get_results(self):
        start_algorithm_working_time = time()
        self.update_alg_iteration_values()
        self.run()
        if self.collected_data["status"] != ITERATION_LIMIT:
            self.collected_data["algorithm_working_time"] = time() - start_algorithm_working_time
            self.collected_data["status"] = -1
        return self.collected_data


def main(application_count, lm, mu, sg, signal_to_change_progress_value=None):
    alg = Algorithm1(application_count, lm, mu, sg)
    alg.set_signal_to_change_progress_value(signal_to_change_progress_value)
    return alg.get_results()


if __name__ == '__main__':
    result = main(application_count=200, lm=3, mu=1, sg=1)
    print(result["algorithm_working_time"], result["number_of_iterations"])
