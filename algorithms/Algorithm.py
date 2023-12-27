from algorithms.support.managers.ApplicationManager import ApplicationManager
from algorithms.support.managers.ProgressIndicator import ProgressIndicator
from algorithms.support.managers.EventsManager import EventManager
from algorithms.support.get_time import get_time
from basic.constants.algorithm_working import *


class Algorithm:
    def __init__(self, signal_to_change_progress_value=None):
        self.progress_indicator = \
            ProgressIndicator(signal_to_change_progress_value)

        self.lm, self.mu, self.sg = 0, 0, 0
        self.app_manager = None
        self.event_manager = None

        self.handler_status = FREE
        self.handler_app_id = None

        self.collected_data = dict()

    def set(self, application_count, lm, mu, sg):

        self.lm, self.mu, self.sg = lm, mu, sg
        self.app_manager = ApplicationManager(application_count)

        self.event_manager = EventManager()
        for i in range(application_count):
            self.event_manager.add_event(
                self.get_arrival_delta_time(), APPLICATION_EVENT, i)

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

    def get_arrival_delta_time(self) -> float:
        return get_time(self.lm)

    def get_handler_delta_time(self) -> float:
        return get_time(self.mu)

    def get_orbit_delta_time(self) -> float:
        return get_time(self.sg)

    def add_data_to_application_count_graphic(self, time: int, value: int):
        self.collected_data["data_for_plotting"]["application_count_graphic"]["time"].append(time)
        self.collected_data["data_for_plotting"]["application_count_graphic"]["value"].append(value)

    def add_data_to_handler_status_graphic(self, time: int, value: int):
        self.collected_data["data_for_plotting"]["handler_status_graphic"]["time"].append(time)
        self.collected_data["data_for_plotting"]["handler_status_graphic"]["value"].append(value)

    def to_active_app(self, event_time, app_id: int):
        self.app_manager.to_active(app_id)
        self.add_data_to_application_count_graphic(
            event_time, self.app_manager.active_applications_count)

    def to_process_handler(self, event_time, app_id: int):
        self.handler_status = PROCESSING
        self.handler_app_id = app_id
        self.event_manager.add_event(
            event_time + self.get_handler_delta_time(),
            HANDLER_COMPLETED_EVENT,
            0
        )
        self.add_data_to_handler_status_graphic(event_time, self.handler_status)

    def to_finish_handler(self, event_time):
        self.app_manager.to_completed(self.handler_app_id)
        self.handler_status = FREE
        self.handler_app_id = None
        self.add_data_to_application_count_graphic(
            event_time, self.app_manager.active_applications_count)
        self.add_data_to_handler_status_graphic(event_time, self.handler_status)
        self.progress_indicator.update(self.app_manager.get_progress())

    def to_orbit(self, event_time, app_id: int):
        self.event_manager.add_event(
            event_time + self.get_orbit_delta_time(),
            APPLICATION_EVENT,
            app_id
        )
