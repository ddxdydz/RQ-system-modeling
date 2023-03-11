# Имитационное моделирование систем массового обслуживания
from random import random
from math import log
from time import time

APPLICATION_COUNT = 350
LM = 3
MU = 1
SG = 1

# Статусы заявок
NOT_RECEIVED = 1352  # Не принято в обработку
ACTIVE = 2536  # Находится в системе / активно
COMPLETED = 7435  # Завершено / обработано
# Статусы обработчика
PROCESSING = 6366  # В обработке / занято
FREE = 9643  # Свободно


def get_arrival_time() -> float:
    return -log(random()) / LM


def get_handler_time() -> float:
    return -log(random()) / MU


def get_orbit_time() -> float:
    return -log(random()) / SG


def main():
    # события, относящиеся к заявке по номерам
    applications_events_times = [get_arrival_time() for _ in range(APPLICATION_COUNT)]
    applications_indicators = [NOT_RECEIVED] * APPLICATION_COUNT
    handler_status = FREE
    handler_elem_id = None
    completed_applications_count = 0
    active_applications_count = 0

    while APPLICATION_COUNT != completed_applications_count:

        # Находим индекс заявки, учавтсующей в ближайшем событии
        nearest_event_applications_index = None
        min_time = None
        for i in range(APPLICATION_COUNT):
            if applications_indicators[i] != COMPLETED:
                if min_time is None or applications_events_times[i] < min_time:
                    min_time = applications_events_times[i]
                    nearest_event_applications_index = i

        # поступление в систему
        if applications_indicators[nearest_event_applications_index] == NOT_RECEIVED:
            applications_indicators[nearest_event_applications_index] = ACTIVE
            active_applications_count += 1

        # если прибор свободен, то занимаем его ближайшей заявкой
        if handler_status == FREE:
            handler_status = PROCESSING
            handler_elem_id = nearest_event_applications_index
            applications_events_times[nearest_event_applications_index] += get_handler_time()
        # если прибор был занят текущей заявкой, то освобождаем его
        elif handler_status == PROCESSING and handler_elem_id == nearest_event_applications_index:
            handler_status = FREE
            handler_elem_id = None
            applications_indicators[nearest_event_applications_index] = COMPLETED
            completed_applications_count += 1
            active_applications_count -= 1
        else:  # на орбиту
            applications_events_times[nearest_event_applications_index] += get_orbit_time()


if __name__ == '__main__':
    st = time()
    main()
    print(time() - st)
