from algorithms.support.get_time import get_time
from algorithms.support.dih_search import dih_search
from basic.constants.algorithm_working import *


class ApplicationManager:
    def __init__(self, application_count, lm):
        self.application_count = application_count
        self.completed_applications_count = 0
        self.active_applications_count = 0

        # Статусы заявок по их индексам:
        self.applications_statuses = [NOT_RECEIVED] * self.application_count
        # Изначально в системе нет заявок, поэтому у всех заявок статусы "NOT_RECEIVED".

        # Список, содержащий время наступления ближайшего необработанного события для каждой заявки по её индексу:
        self.times_of_unprocessed_events_by_application_indexes = \
            [get_time(lm) for _ in range(self.application_count)]
        # Изначально у каждой заявки ближайшим событием является поступление в систему.

        # Индексы отсортированных заявок по временам наступления их необработанных ближайших событий
        self.sorted_app_ids = list(range(self.application_count))
        self.sorted_app_ids.sort(key=lambda app_i: self.times_of_unprocessed_events_by_application_indexes[app_i])

        self.is_valid = True

    def get_insert_id(self, app_event_time):
        insert_id = dih_search(
            app_event_time, 0, len(self.sorted_app_ids) - 1,
            key=lambda i: self.times_of_unprocessed_events_by_application_indexes[
                self.sorted_app_ids[i]]
        )
        return insert_id

    def update_sorted_app_ids_list(self, updated_app_id):
        next_nearest_event_time = self.get_time(updated_app_id)
        if len(self.sorted_app_ids) > 1:
            self.sorted_app_ids.pop(0)
            if self.applications_statuses[updated_app_id] != COMPLETED:
                insert_id = self.get_insert_id(next_nearest_event_time)
                self.sorted_app_ids.insert(insert_id, updated_app_id)
        self.is_valid = True

    def get_nearest_app_id(self):
        if not self.is_valid:
            raise Exception("Invalid call get_nearest_app_id. Do update_sorted_app_ids_list")
        return self.sorted_app_ids[0]

    def get_time(self, app_id):
        return self.times_of_unprocessed_events_by_application_indexes[app_id]

    def get_status(self, app_id):
        return self.applications_statuses[app_id]

    def add_delta_time(self, app_id, delta):
        self.times_of_unprocessed_events_by_application_indexes[app_id] += delta

    def to_completed(self, app_id):
        self.applications_statuses[app_id] = COMPLETED
        self.completed_applications_count += 1
        self.active_applications_count -= 1

    def to_active(self, app_id):
        self.applications_statuses[app_id] = ACTIVE
        self.active_applications_count += 1

    def get_progress(self):
        return int(self.completed_applications_count * 100 / self.application_count)

    def is_all_completed(self):
        return self.completed_applications_count == self.application_count
