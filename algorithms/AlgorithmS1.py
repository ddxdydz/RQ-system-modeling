from time import time

from algorithms.Algorithm import Algorithm
from algorithms.support.extra_plotting_data.get_probability_of_processing_data import *
from basic.constants.algorithm_working import *


class AlgorithmS1(Algorithm):
    def __init__(self, signal_to_change_progress_value=None):
        super().__init__(signal_to_change_progress_value)

    def run(self):
        while not self.app_manager.is_all_completed():
            event_time, event_type, app_id = self.event_manager.get_nearest_event()

            if event_type == APPLICATION_EVENT:
                # Поступление заявки в систему:
                if self.app_manager.get_status(app_id) == NOT_RECEIVED:
                    self.to_active_app(event_time, app_id)
                # Если прибор свободен, то занимаем его ближайшей заявкой:
                if self.handler_status == FREE:
                    self.to_process_handler(event_time, app_id)
                else:  # иначе на орбиту
                    self.to_orbit(event_time, app_id)
            # Если обработчик завершил обработку текущей заявки:
            elif event_type == HANDLER_COMPLETED_EVENT:
                self.to_finish_handler(event_time)

    def get_results(self, application_count, lm, mu, sg):
        start_algorithm_working_time = time()
        self.set(application_count, lm, mu, sg)
        self.run()
        self.collected_data["data_for_plotting"]["probability_distribution_processed"] = \
            get_probability_of_processing_data(
                self.collected_data["data_for_plotting"]["handler_status_graphic"]["time"].copy(),
                self.collected_data["data_for_plotting"]["handler_status_graphic"]["value"].copy()
            )
        self.collected_data["algorithm_working_time"] = time() - start_algorithm_working_time
        self.collected_data["status"] = -1
        return self.collected_data


def main(application_count, lm, mu, sg):
    return AlgorithmS1().get_results(application_count, lm, mu, sg)


if __name__ == '__main__':
    result = main(application_count=4, lm=3, mu=1, sg=1)
    for name, data in result["data_for_plotting"].items():
        print("\t", name)
        for key, values in data.items():
            print(key, values)
    print(result["algorithm_working_time"])
