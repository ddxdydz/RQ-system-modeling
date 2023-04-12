from random import random
from math import log
from time import time


APPLICATION_COUNT = 100
LM = 3
MU = 1
SG = 1

# Статусы заявок
NOT_RECEIVED = 1352  # Не принято в обработку
ACTIVE = 2536  # Находится в системе / активно
COMPLETED = 7435  # Завершено / обработано
# Статусы обработчика
FREE = 9643  # Свободно
PROCESSING = 6366  # В обработке / занято


def get_arrival_time() -> float:
    return -log(random()) / LM


def get_handler_time() -> float:
    return -log(random()) / MU


def get_orbit_time() -> float:
    return -log(random()) / SG


def main():
    times_of_unprocessed_events_by_application_indexes = \
        [get_arrival_time() for _ in range(APPLICATION_COUNT)]
    applications_statuses = [NOT_RECEIVED] * APPLICATION_COUNT
    handler_status = FREE
    handler_elem_id = None
    completed_applications_count = 0
    active_applications_count = 0

    while completed_applications_count != APPLICATION_COUNT:

        # Находим индекс заявки, участвующей в ближайшем необработанном событии
        application_index_of_nearest_event = None
        nearest_event_time = None
        for i in range(APPLICATION_COUNT):
            if applications_statuses[i] != COMPLETED:
                if nearest_event_time is None or \
                        times_of_unprocessed_events_by_application_indexes[i] < nearest_event_time:
                    nearest_event_time = times_of_unprocessed_events_by_application_indexes[i]
                    application_index_of_nearest_event = i

        # поступление в систему
        if applications_statuses[application_index_of_nearest_event] == NOT_RECEIVED:
            applications_statuses[application_index_of_nearest_event] = ACTIVE
            active_applications_count += 1

        # если прибор свободен, то занимаем его ближайшей заявкой
        if handler_status == FREE:
            handler_status = PROCESSING
            handler_elem_id = application_index_of_nearest_event
            times_of_unprocessed_events_by_application_indexes[
                application_index_of_nearest_event] += get_handler_time()
        # если прибор был занят текущей заявкой, то освобождаем его
        elif handler_status == PROCESSING and \
                handler_elem_id == application_index_of_nearest_event:
            handler_status = FREE
            handler_elem_id = None
            applications_statuses[application_index_of_nearest_event] = COMPLETED
            completed_applications_count += 1
            active_applications_count -= 1
        else:  # на орбиту
            times_of_unprocessed_events_by_application_indexes[
                application_index_of_nearest_event] += get_orbit_time()


if __name__ == '__main__':
    st = time()
    main()
    print(time() - st)
