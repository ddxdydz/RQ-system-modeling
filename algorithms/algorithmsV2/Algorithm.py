from interface.support.controllers.StatusBarUpdater import StatusBarUpdater


class Algorithm:
    def __init__(self, signal_to_change_progress_value=None):
        self.progress_indicator = StatusBarUpdater(signal_to_change_progress_value)
        self.collected_data = dict()

    def init_collected_data(self):
        self.collected_data = {
            "data_for_plotting":
                {
                    "application_count_graphic": {"time": [0], "value": [0]},
                    "handler_status_graphic": {"time": [0], "value": [0]}
                },
            "algorithm_working_time": None,
            "status": 0
        }

    def add_data_to_application_count_graphic(self, time: int, value: int):
        self.collected_data["data_for_plotting"]["application_count_graphic"]["time"].append(time)
        self.collected_data["data_for_plotting"]["application_count_graphic"]["value"].append(value)

    def add_data_to_handler_status_graphic(self, time: int, value: int):
        self.collected_data["data_for_plotting"]["handler_status_graphic"]["time"].append(time)
        self.collected_data["data_for_plotting"]["handler_status_graphic"]["value"].append(value)
