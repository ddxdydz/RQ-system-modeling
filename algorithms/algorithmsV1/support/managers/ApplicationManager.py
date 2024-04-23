from basic.constants.algorithm_working import *


class ApplicationManager:
    def __init__(self, application_count):
        self.application_count = application_count
        self.completed_applications_count = 0
        self.active_applications_count = 0

        # Статусы заявок по их индексам:
        self.applications_statuses = [NOT_RECEIVED] * self.application_count
        # Изначально в системе нет заявок, поэтому у всех заявок статусы "NOT_RECEIVED".

    def to_completed(self, app_id):
        self.completed_applications_count += 1
        self.active_applications_count -= 1
        self.applications_statuses[app_id] = COMPLETED

    def to_active(self, app_id):
        self.active_applications_count += 1
        self.applications_statuses[app_id] = ACTIVE

    def get_status(self, app_id):
        return self.applications_statuses[app_id]

    def get_progress(self):
        return int(self.completed_applications_count * 100 / self.application_count)

    def is_all_completed(self):
        return self.completed_applications_count == self.application_count
