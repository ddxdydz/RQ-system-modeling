from algorithms.support.ApplicationManager import *
from algorithms.support.ProgressIndicator import *
from basic.constants.algorithm_working import *


class Algorithm:
    def __init__(self, signal_to_change_progress_value=None):
        self.progress_indicator = \
            ProgressIndicator(signal_to_change_progress_value)

        self.app_manager = None
        self.lm, self.mu, self.sg = 0, 0, 0
        self.handler_status = FREE
        self.handler_app_id = None
        self.collected_data = dict()

    def set_parameters(self, application_count, lm, mu, sg):
        self.app_manager = ApplicationManager(application_count, lm)
        self.lm, self.mu, self.sg = lm, mu, sg

        self.handler_status = FREE
        self.handler_app_id = None

        self.collected_data = {
            "data_for_plotting":
                {
                    "application_count_graphic": {"time": [0], "value": [0]},
                    "handler_status_graphic": {"time": [0], "value": [0]}
                },
            "algorithm_working_time": None,
            "status": 0
        }

    def get_arrival_time(self) -> float:
        return get_time(self.lm)

    def get_handler_time(self) -> float:
        return get_time(self.mu)

    def get_orbit_time(self) -> float:
        return get_time(self.sg)

    def add_data_to_application_count_graphic(self, time: int, value: int):
        self.collected_data["data_for_plotting"]["application_count_graphic"]["time"].append(time)
        self.collected_data["data_for_plotting"]["application_count_graphic"]["value"].append(value)

    def add_data_to_handler_status_graphic(self, time: int, value: int):
        self.collected_data["data_for_plotting"]["handler_status_graphic"]["time"].append(time)
        self.collected_data["data_for_plotting"]["handler_status_graphic"]["value"].append(value)

    def to_active_app(self, app_id: int):
        self.app_manager.to_active(app_id)
        self.add_data_to_application_count_graphic(
            self.app_manager.get_time(app_id),
            self.app_manager.active_applications_count
        )

    def to_process_handler(self, app_id: int):
        self.handler_status = PROCESSING
        self.handler_app_id = app_id
        self.add_data_to_handler_status_graphic(
            self.app_manager.get_time(app_id), self.handler_status
        )
        self.app_manager.add_delta_time(app_id, self.get_handler_time())

    def to_finish_handler(self, app_id: int):
        self.handler_status = FREE
        self.handler_app_id = None
        self.app_manager.to_completed(app_id)
        self.add_data_to_application_count_graphic(
            self.app_manager.get_time(app_id),
            self.app_manager.active_applications_count
        )
        self.add_data_to_handler_status_graphic(
            self.app_manager.get_time(app_id), self.handler_status
        )

    def to_orbit(self, app_id: int):
        self.app_manager.add_delta_time(app_id, self.get_handler_time())
