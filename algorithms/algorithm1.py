from random import random
from math import log
from time import time

from constants import *


# Статусы заявок
NOT_RECEIVED = 1352  # Не принято в обработку
ACTIVE = 1536  # Находится в системе / активно
COMPLETED = 1435  # Завершено / обработано
# Статусы обработчика
FREE = 2643  # Свободно
PROCESSING = 2366  # В обработке / занято


def main(application_count, lm, mu, sg, signal_to_change_progress_value=None):
    collected_data = {
        "events_data": [{"time": 0, "values": {"h_status": 0, "app_count": 0}}],
        "algorithm_working_time": None
    }
    start_algorithm_working_time = time()
    number_of_iterations = 0
    last_progress_value = 0

    def get_arrival_time() -> float:
        return -log(random()) / lm

    def get_handler_time() -> float:
        return -log(random()) / mu

    def get_orbit_time() -> float:
        return -log(random()) / sg

    completed_applications_count = 0  # Количество обработанных заявок
    active_applications_count = 0  # Количество заявок, находящихся в системе

    handler_status = FREE
    handler_application_id = None  # Индекс заявки, находящейся в обработке

    # Статусы заявок по их индексам:
    applications_statuses = [NOT_RECEIVED] * application_count
    # Изначально в системе нет заявок, поэтому у всех заявок статусы "NOT_RECEIVED".

    # Список, содержащий время наступления ближайшего необработанного события для каждой заявки по её индексу:
    times_of_unprocessed_events_by_application_indexes = \
        [get_arrival_time() for _ in range(application_count)]
    # Изначально у каждой заявки ближайшим событием является поступление в систему.

    # Индексы отсортированных заявок по временам наступления их необработанных ближайших событий
    sorted_app_ids = sorted(
        list(range(application_count)),
        key=lambda app_i: times_of_unprocessed_events_by_application_indexes[app_i]
    )

    while completed_applications_count != application_count:

        # Находим индекс заявки, участвующей в необработанном событии, которое наступает раньше остальных:
        application_index_of_nearest_event = sorted_app_ids[0]
        nearest_event_time = times_of_unprocessed_events_by_application_indexes[sorted_app_ids[0]]

        # Поступление заявки в систему
        if applications_statuses[application_index_of_nearest_event] == NOT_RECEIVED:
            applications_statuses[application_index_of_nearest_event] = ACTIVE
            active_applications_count += 1

        # Если прибор свободен, то занимаем его ближайшей заявкой
        if handler_status == FREE:
            handler_status = PROCESSING
            handler_application_id = application_index_of_nearest_event
            times_of_unprocessed_events_by_application_indexes[
                application_index_of_nearest_event] += get_handler_time()
        # Если прибор был занят текущей заявкой, то освобождаем его
        elif handler_status == PROCESSING and \
                handler_application_id == application_index_of_nearest_event:
            handler_status = FREE
            handler_application_id = None
            applications_statuses[application_index_of_nearest_event] = COMPLETED
            completed_applications_count += 1
            active_applications_count -= 1
        else:  # на орбиту
            times_of_unprocessed_events_by_application_indexes[
                application_index_of_nearest_event] += get_orbit_time()

        # Обновление отсортированного списка индексов sorted_app_ids:
        sorted_app_ids.pop(0)
        if applications_statuses[application_index_of_nearest_event] != COMPLETED:
            next_nearest_event_time = times_of_unprocessed_events_by_application_indexes[
                    application_index_of_nearest_event]
            for i in range(len(sorted_app_ids)):
                number_of_iterations += 1
                if next_nearest_event_time < times_of_unprocessed_events_by_application_indexes[sorted_app_ids[i]]:
                    sorted_app_ids.insert(i, application_index_of_nearest_event)
                    break
            else:
                sorted_app_ids.append(application_index_of_nearest_event)

        collected_data["events_data"].append(
            {
                "time": nearest_event_time,
                "values":
                    {
                        "h_status": int(handler_status == PROCESSING),
                        "app_count": active_applications_count
                    }
            }
        )

        if signal_to_change_progress_value is not None:
            progress = int(completed_applications_count * 100 / application_count)
            if progress != last_progress_value and progress % 5 == 0:
                signal_to_change_progress_value.emit(progress)
                last_progress_value = progress
                print(progress)
            if number_of_iterations > ITERATION_LIMIT_COUNT and progress < 5:
                print("ERR")
                collected_data["status"] = ITERATION_LIMIT
                return collected_data

    collected_data["number_of_iterations"] = number_of_iterations
    collected_data["algorithm_working_time"] = time() - start_algorithm_working_time
    collected_data["status"] = -1
    return collected_data


if __name__ == '__main__':
    result = main(application_count=200, lm=3, mu=1, sg=1)
    print(result["algorithm_working_time"], result["number_of_iterations"])
