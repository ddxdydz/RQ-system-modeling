from math import log
from random import random
from time import time

from constants import *

# Статусы заявок
NOT_RECEIVED = 1352  # Не принято в обработку
ACTIVE = 1536  # Находится в системе / активно
COMPLETED = 1435  # Завершено / обработано
# Статусы обработчика
FREE = 2643  # Свободно
PROCESSING = 2366  # В обработке / занято

PD_GRAPHIC_FREQUENCY = 1000


class Algorithm1:
    def __init__(self, application_count=None, lm=None, mu=None, sg=None):
        self.application_count = application_count
        self.lm, self.mu, self.sg = lm, mu, sg

        self.signal_to_change_progress_value = None
        self.last_progress_value_for_indicator = 0
        self.collected_data = dict()

        self.completed_applications_count = 0
        self.active_applications_count = 0

        self.handler_status = FREE
        self.handler_app_id = None

        self.applications_statuses = list()
        self.times_of_unprocessed_events_by_application_indexes = list()
        self.sorted_app_ids = list()

    def clear_collected_data(self):
        self.collected_data = {
            "data_for_plotting":
                {
                    "application_count_graphic": {"time": [0], "value": [0]},
                    "handler_status_graphic": {"time": [0], "value": [0]}
                },
            "algorithm_working_time": None,
            "number_of_iterations": 0,
            "status": 0
        }

    def update_alg_iteration_values(self):
        self.last_progress_value_for_indicator = 0
        self.clear_collected_data()

        self.completed_applications_count = 0  # Количество обработанных заявок
        self.active_applications_count = 0  # Количество заявок, находящихся в системе

        self.handler_status = FREE
        self.handler_app_id = None  # Индекс заявки, находящейся в обработке

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

    def collect_application_count_graphic_data(self, app_id):
        app_time = self.times_of_unprocessed_events_by_application_indexes[app_id]
        self.collected_data["data_for_plotting"]["application_count_graphic"]["time"].append(app_time)
        self.collected_data["data_for_plotting"]["application_count_graphic"]["value"].append(
            self.active_applications_count)

    def collect_handler_status_graphic_data(self, app_id):
        app_time = self.times_of_unprocessed_events_by_application_indexes[app_id]
        self.collected_data["data_for_plotting"]["handler_status_graphic"]["time"].append(app_time)
        self.collected_data["data_for_plotting"]["handler_status_graphic"]["value"].append(
            int(self.handler_status == PROCESSING))

    def to_active_app(self, app_id):
        self.applications_statuses[app_id] = ACTIVE
        self.active_applications_count += 1
        self.collect_application_count_graphic_data(app_id)

    def to_process_handler(self, app_id):
        self.handler_status = PROCESSING
        self.handler_app_id = app_id
        self.collect_handler_status_graphic_data(app_id)
        self.times_of_unprocessed_events_by_application_indexes[app_id] += self.get_handler_time()

    def to_free_handler(self, app_id):
        self.handler_status = FREE
        self.applications_statuses[self.handler_app_id] = COMPLETED
        self.handler_app_id = None
        self.completed_applications_count += 1
        self.active_applications_count -= 1
        self.collect_application_count_graphic_data(app_id)
        self.collect_handler_status_graphic_data(app_id)

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

    def update_indicator(self):
        if self.signal_to_change_progress_value is not None:
            progress = int(self.completed_applications_count * 100 / self.application_count)
            if progress != self.last_progress_value_for_indicator and progress % 5 == 0:
                self.signal_to_change_progress_value.emit(progress)
                self.last_progress_value_for_indicator = progress
                print(progress)
            if self.collected_data["number_of_iterations"] > ITERATION_LIMIT_COUNT and progress < 5:
                self.collected_data["status"] = ITERATION_LIMIT
                return True
        return False

    def run(self):

        while self.completed_applications_count != self.application_count:

            # Находим индекс заявки, участвующей в необработанном событии, которое наступает раньше остальных:
            nearest_app_id = self.sorted_app_ids[0]

            # Поступление заявки в систему:
            if self.applications_statuses[nearest_app_id] == NOT_RECEIVED:
                self.to_active_app(nearest_app_id)
            # Если прибор свободен, то занимаем его ближайшей заявкой:
            if self.handler_status == FREE:
                self.to_process_handler(nearest_app_id)
            # Если прибор был занят текущей заявкой, то освобождаем его:
            elif self.handler_app_id == nearest_app_id:
                self.to_free_handler(nearest_app_id)
            else:  # на орбиту
                self.to_orbit(nearest_app_id)

            # Обновление отсортированного списка индексов sorted_app_ids:
            self.update_sorted_app_ids_list(nearest_app_id)

            # Обновление индикаторов выполнения:
            if self.update_indicator():
                break

    def add_probability_distribution_data(self):
        hs_time_list = self.collected_data["data_for_plotting"]["handler_status_graphic"]["time"]
        hs_value_list = self.collected_data["data_for_plotting"]["handler_status_graphic"]["value"]

        # Добавление дополнительных значений для плавности графика:
        step = (hs_time_list[-1] - hs_time_list[0]) / PD_GRAPHIC_FREQUENCY
        time_for_adding = step * PD_GRAPHIC_FREQUENCY - step
        for id_time in range(len(hs_time_list) - 2, -1, -1):
            start_time_range = hs_time_list[id_time]
            end_time_range = hs_time_list[id_time + 1]
            hs_status_in_range = hs_value_list[id_time]
            while start_time_range < time_for_adding < end_time_range:
                hs_time_list.insert(id_time + 1, time_for_adding)
                hs_value_list.insert(id_time + 1, hs_status_in_range)
                time_for_adding -= step

        # Добавление данных для построения графика:
        probability_distribution_data = [0]
        working_time_sum = 0
        total_time_sum = 0
        for id_time in range(1, len(hs_time_list)):
            hs_status_in_range = hs_value_list[id_time - 1]
            start_time_range = hs_time_list[id_time - 1]
            end_time_range = hs_time_list[id_time]
            delta_time = end_time_range - start_time_range
            if hs_status_in_range == 1:
                working_time_sum += delta_time
            total_time_sum += delta_time
            probability_distribution_data.append(working_time_sum * 100 / total_time_sum)
        self.collected_data["data_for_plotting"]["probability_distribution_processed"] = \
            {"time": hs_time_list, "value": probability_distribution_data}

    def get_results(self):
        start_algorithm_working_time = time()
        self.update_alg_iteration_values()
        self.run()
        if self.collected_data["status"] != ITERATION_LIMIT:
            self.add_probability_distribution_data()
            self.collected_data["algorithm_working_time"] = time() - start_algorithm_working_time
            self.collected_data["status"] = -1
        return self.collected_data


def main(application_count, lm, mu, sg, signal_to_change_progress_value=None):
    alg = Algorithm1(application_count, lm, mu, sg)
    alg.set_signal_to_change_progress_value(signal_to_change_progress_value)
    return alg.get_results()


if __name__ == '__main__':
    result = main(application_count=4, lm=3, mu=1, sg=1)
    # print(result["data_for_plotting"])
    # print(result["algorithm_working_time"], result["number_of_iterations"])
