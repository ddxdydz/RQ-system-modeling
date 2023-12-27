from time import time

from algorithms.Algorithm import Algorithm
from algorithms.support.get_time import get_time
from algorithms.support.extra_plotting_data.get_probability_of_processing_data import *
from algorithms.support.extra_plotting_data.get_probability_of_orbit_data import *
from basic.constants.algorithm_working import *


class AlgorithmS2(Algorithm):
    def __init__(self, signal_to_change_progress_value=None):
        super().__init__(signal_to_change_progress_value)

        self.mu2, self.dt1, self.dt2 = None, None, None

    def set_parameters(self, application_count, lm, mu1, mu2, sg, dt1, dt2):
        self.set(application_count, lm, mu1, sg)
        self.mu2, self.dt1, self.dt2, = mu2, dt1, dt2
        self.event_manager.add_event(
            self.get_broken_delta_time(),
            HANDLER_BROKEN_EVENT,
            0
        )

    def get_recover_delta_time(self):
        return get_time(self.mu2)

    def get_broken_delta_time(self):
        if self.handler_status == FREE:
            return get_time(self.dt1)
        else:  # Если был занят
            return get_time(self.dt2)

    def to_recover_handler(self, event_time):
        self.handler_status = FREE
        self.add_data_to_handler_status_graphic(event_time, self.handler_status)
        self.event_manager.add_event(
            event_time + self.get_broken_delta_time(),
            HANDLER_BROKEN_EVENT,
            0
        )

    def to_broken_handler(self, event_time):
        if self.handler_status == PROCESSING:
            self.to_orbit(event_time, self.handler_app_id)
            self.event_manager.delete_event(HANDLER_COMPLETED_EVENT, 0)
            self.handler_app_id = None
        self.event_manager.add_event(
            event_time + self.get_recover_delta_time(),
            HANDLER_RECOVER_EVENT,
            0
        )
        self.handler_status = BROKEN
        self.add_data_to_handler_status_graphic(event_time, self.handler_status)

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
            # Если обработчик сломался:
            elif event_type == HANDLER_BROKEN_EVENT:
                self.to_broken_handler(event_time)
            # Если обработчик восстановился
            elif event_type == HANDLER_RECOVER_EVENT:
                self.to_recover_handler(event_time)

    def get_results(self, application_count, lm, mu1, mu2, sg, dt1, dt2):
        """
        :param application_count:
        :param lm: интенсивность прихода заявок
        :param mu1: интенсивность обслуживания
        :param mu2: время восстановления
        :param sg: время на орбите
        :param dt1: время выхода из строя если свободен
        :param dt2: время выхода из строя если занят
        :return:
        """
        start_algorithm_working_time = time()
        self.set_parameters(application_count, lm, mu1, mu2, sg, dt1, dt2)
        self.run()
        self.collected_data["data_for_plotting"]["probability_distribution_processed"] = \
            get_probability_of_processing_data(
                self.collected_data["data_for_plotting"]["handler_status_graphic"]["time"].copy(),
                self.collected_data["data_for_plotting"]["handler_status_graphic"]["value"].copy()
            )
        self.collected_data["data_for_plotting"]["probability_distribution_orbit"] = \
            get_probability_of_orbit_data(
                self.collected_data["data_for_plotting"]["application_count_graphic"]["time"].copy(),
                self.collected_data["data_for_plotting"]["application_count_graphic"]["value"].copy(),
                self.collected_data["data_for_plotting"]["handler_status_graphic"]["time"].copy(),
                self.collected_data["data_for_plotting"]["handler_status_graphic"]["value"].copy()
            )
        self.collected_data["algorithm_working_time"] = time() - start_algorithm_working_time
        self.collected_data["status"] = -1

        return self.collected_data


def main(application_count, lm, mu, mu2, sg, dt1, dt2):
    return AlgorithmS2().get_results(application_count, lm, mu, mu2, sg, dt1, dt2)


if __name__ == '__main__':
    result = main(application_count=4, lm=3, mu=1, mu2=1, sg=1, dt1=0.5, dt2=0.5)
    for name, data in result["data_for_plotting"].items():
        print("\t", name)
        for time, value in zip(*data.values()):
            print(time, value)
    print(result["algorithm_working_time"])
