from time import time

from algorithms.Algorithm import Algorithm
from algorithms.support.get_time import get_time
from algorithms.support.extra_plotting_data.probability_distribution_data import *
from basic.constants.algorithm_working import *


class Algorithm1(Algorithm):
    def __init__(self, signal_to_change_progress_value=None):
        super().__init__(signal_to_change_progress_value)

        self.mu2, self.dt1, self.dt2 = None, None, None
        self.handler_time = 0

    def update_handler_time(self):
        if self.handler_status == BROKEN:
            # добавление времени восстановления
            self.handler_time += get_time(self.mu2)
        else:
            if self.handler_status == FREE:
                self.handler_time += get_time(self.dt1)
            else:  # Если был занят
                self.handler_time += get_time(self.dt2)

    def collect_handler_status_graphic_data(self):
        self.collected_data["data_for_plotting"]["handler_status_graphic"]["time"].append(
            self.handler_time
        )
        self.collected_data["data_for_plotting"]["handler_status_graphic"]["value"].append(
            self.handler_status
        )

    def run(self):
        while not self.app_manager.is_all_completed():
            nearest_app_id = self.app_manager.get_nearest_app_id()

            # Если событие с учатием обработчика наступает быстрее
            if self.handler_time < self.app_manager.get_time(nearest_app_id):
                if self.handler_status == BROKEN:
                    self.handler_status = FREE
                else:
                    if self.handler_status == PROCESSING:
                        self.to_orbit(self.handler_app_id)
                    self.handler_status = BROKEN
                self.update_handler_time()
                self.collect_handler_status_graphic_data()
            else:
                # Поступление заявки в систему:
                if self.app_manager.get_status(nearest_app_id) == NOT_RECEIVED:
                    self.to_active_app(nearest_app_id)
                # Если прибор свободен, то занимаем его ближайшей заявкой:
                if self.handler_status == FREE:
                    self.to_process_handler(nearest_app_id)
                # Если прибор был занят текущей заявкой, то освобождаем его:
                elif self.handler_app_id == nearest_app_id:
                    self.to_finish_handler(nearest_app_id)
                else:  # на орбиту
                    self.to_orbit(nearest_app_id)

                # Обновление списка заявок:
                self.app_manager.update_sorted_app_ids_list(nearest_app_id)

                # Обновление индикатора выполнения:
                self.progress_indicator.update(self.app_manager.get_progress())

    def get_results(self, application_count, lm, mu, mu2, sg, dt1, dt2):
        """
        :param application_count:
        :param lm: интенсивность прихода заявок
        :param mu: итенсивность обслуживания
        :param mu2: время восстановления
        :param sg: время на орбите
        :param dt1: время выхода из строя если свободен
        :param dt2: время выхода из строя если занят
        :return:
        """
        start_algorithm_working_time = time()
        self.set_parameters(application_count, lm, mu, sg)
        self.mu2, self.dt1, self.dt2 = mu2, dt1, dt2
        self.run()
        self.collected_data["data_for_plotting"]["probability_distribution_processed"] = \
            add_probability_distribution_data(
                self.collected_data["data_for_plotting"]["handler_status_graphic"]["time"],
                self.collected_data["data_for_plotting"]["handler_status_graphic"]["value"]
            )
        self.collected_data["algorithm_working_time"] = time() - start_algorithm_working_time
        self.collected_data["status"] = -1
        return self.collected_data


def main(application_count, lm, mu, mu2, sg, dt1, dt2):
    return Algorithm1().get_results(application_count, lm, mu, mu2, sg, dt1, dt2)


if __name__ == '__main__':
    result = main(application_count=4, lm=3, mu=1, mu2=1, sg=1, dt1=0.5, dt2=0.5)
    for name, data in result["data_for_plotting"].items():
        print("\t", name)
        for key, values in data.items():
            print(key, values)
    print(result["algorithm_working_time"])
