import sys
from math import log
from random import random

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic


# Статусы заявок
NOT_RECEIVED = 1352  # Не принято в обработку
ACTIVE = 2536  # Находится в системе / активно
COMPLETED = 7435  # Завершено / обработано
# Статусы обработчика
PROCESSING = 6366  # В обработке / занято
FREE = 9643  # Свободно


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.init_ui()
        self.application_count = None
        self.lm = None
        self.mu = None
        self.sg = None
        self.applications_count_y = [0]
        self.handler_statuses_y = [0]
        self.events_times = [0.0]
        self.launch()

    def init_ui(self):
        uic.loadUi('MainWindow.ui', self)
        self.setWindowTitle("Имитационное моделирование систем массового обслуживания")
        self.pushButton.clicked.connect(self.launch)
        self.init_application_count_graphic_ui()
        self.init_handler_statuses_graphic_ui()

    def init_application_count_graphic_ui(self):
        # Add Background colour to white
        self.application_count_graphic.setBackground('w')
        # Add Title
        self.application_count_graphic.setTitle("Количество заявок в системе", color="b", size="20pt")
        # Add Axis Labels
        styles = {"color": "#f00", "font-size": "15px"}
        self.application_count_graphic.setLabel("left", "Заявки", **styles)
        # self.application_count_graphic.setLabel("bottom", "Время (секунды)", **styles)

    def init_handler_statuses_graphic_ui(self):
        # Add Background colour to white
        self.handler_status_graphic.setBackground('w')
        # Add Title
        self.handler_status_graphic.setTitle("Изменение статуса обработчика", color="b", size="20pt")
        # Add Axis Labels
        styles = {"color": "#f00", "font-size": "15px"}
        self.handler_status_graphic.setLabel("left", "Статус", **styles)
        self.handler_status_graphic.setLabel("bottom", "Время (секунды)", **styles)

    def launch(self):
        try:
            self.clear_last_graphic_data()
            self.update_parameters()
            self.check_parameters_range()
            self.launch_imitation()
            self.update_graphics()
            self.clear_message()
        except ValueError:
            self.show_message("Ошибка: \nНекорректные данные")
        except RangeError:
            self.show_message("Ошибка: диапазон")

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter - 1:
            self.launch()

    def update_parameters(self):
        self.application_count = int(self.lineEdit_count_value.text().replace(',', '.'))
        self.lm = float(self.lineEdit_lm_value.text().replace(',', '.'))
        self.mu = float(self.lineEdit_mu_value.text().replace(',', '.'))
        self.sg = float(self.lineEdit_sg_value.text().replace(',', '.'))

    def check_parameters_range(self):
        if not (0 < self.application_count < 350 and
                0 < self.lm and 0 < self.mu and 0 < self.sg):
            raise RangeError

    def show_message(self, text):
        self.label_message.setText(text)

    def clear_message(self):
        self.label_message.setText("")

    def launch_imitation(self):
        # события, относящиеся к заявке по номерам
        applications_events_times = [
            self.get_arrival_time()
            for _ in range(self.application_count)]
        applications_indicators = [NOT_RECEIVED] * self.application_count
        handler_status = FREE
        handler_elem_id = None
        completed_applications_count = 0
        active_applications_count = 0

        while self.application_count != completed_applications_count:
            # Находим индекс заявки, учавтсующей в ближайшем событии
            nearest_event_applications_index = None
            min_time = None
            for i in range(self.application_count):
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
                applications_events_times[nearest_event_applications_index] += \
                    self.get_handler_time()
            # если прибор был занят текущей заявкой, то освобождаем его
            elif handler_status == PROCESSING and handler_elem_id == nearest_event_applications_index:
                handler_status = FREE
                handler_elem_id = None
                applications_indicators[nearest_event_applications_index] = COMPLETED
                completed_applications_count += 1
                active_applications_count -= 1
            else:  # на орбиту
                applications_events_times[nearest_event_applications_index] += \
                    self.get_orbit_time()
            self.collect_data(min_time, handler_status, active_applications_count)

    def collect_data(self, time, handler_status, active_applications_count):
        self.applications_count_y.append(active_applications_count)
        self.handler_statuses_y.append(1 if handler_status == PROCESSING else 0)
        self.events_times.append(time)

    def clear_last_graphic_data(self):
        self.applications_count_y.clear()
        self.handler_statuses_y.clear()
        self.events_times.clear()
        self.application_count_graphic.clear()
        self.handler_status_graphic.clear()

    def update_graphics(self):
        self.events_times.append(self.events_times[-1] + 5)
        self.application_count_graphic.plot(
            self.events_times,
            self.applications_count_y,
            stepMode="center",
            fillLevel=0,
            fillOutline=True,
            brush=(0, 0, 255, 150)
        )
        self.handler_status_graphic.plot(
            self.events_times,
            self.handler_statuses_y,
            stepMode="center",
            fillLevel=0,
            fillOutline=True,
            brush=(0, 0, 255, 150)
        )

    def get_arrival_time(self) -> float:
        return -log(random()) / self.lm

    def get_handler_time(self) -> float:
        return -log(random()) / self.mu

    def get_orbit_time(self) -> float:
        return -log(random()) / self.sg


class RangeError(Exception):
    pass


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
