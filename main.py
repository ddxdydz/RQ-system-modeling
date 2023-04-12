import sys
from math import log
from random import random

from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtWidgets import QGraphicsRectItem

from pyqtgraph import mkBrush, mkPen


# Статусы заявок
NOT_RECEIVED = 1352  # Не поступило в систему
ACTIVE = 2536  # Находится в системе / активно
COMPLETED = 7435  # Завершено / обработано
# Статусы обработчика
PROCESSING = 6366  # В обработке / занято
FREE = 9643  # Свободно


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.enabled_dividing_lines = False
        self.enabled_graphic_symbol = False
        self.y_range_padding = 0
        self.parameters = {
            "application_count": 4,
            "lm": 3.0,
            "mu": 1.0,
            "sg": 1.0
        }
        self.collected_data = []
        self.data_for_graphics = {
            "handler_statuses_graphic_data": {"time": [], "values": []},
            "applications_count_graphic_data": {"time": [], "values": []}
        }
        self.init_ui()
        self.launch()

    def init_ui(self):
        uic.loadUi(r'data\MainWindow.ui', self)
        self.setWindowIcon(QIcon(r'data\app_icon.ico'))
        self.setWindowTitle("Имитационное моделирование систем массового обслуживания")

        # Добавление параметров по умолчанию в строки ввода
        self.lineEdit_lm_value.setText(str(self.parameters["lm"]))
        self.lineEdit_mu_value.setText(str(self.parameters["mu"]))
        self.lineEdit_sg_value.setText(str(self.parameters["sg"]))
        self.lineEdit_count_value.setText(str(self.parameters["application_count"]))

        self.pushButton.clicked.connect(self.launch)

        self.init_graphic_ui(
            self.application_count_graphic,
            title="Изменение количества заявок",
            left_label="Количество заявок в системе",
            bottom_label="Время (секунды)"
        )
        self.init_graphic_ui(
            self.handler_status_graphic,
            title="Изменение статуса обработчика",
            left_label="Статус обработчика",
            bottom_label="Время (секунды)"
        )

    @staticmethod
    def init_graphic_ui(graphic_obj, title=None, left_label=None, bottom_label=None):
        graphic_obj.addLegend()
        graphic_obj.setBackground('w')
        graphic_obj.showGrid(x=True, y=True)
        graphic_obj.setTitle(title, color="b", size="15pt")
        styles = {"color": "#f00", "font-size": "8pt"}
        graphic_obj.setLabel("left", left_label, **styles)
        graphic_obj.setLabel("bottom", bottom_label, **styles)

    def launch(self):
        try:
            self.clear_message()
            self.update_parameters()
            self.check_parameters_range()
            if self.parameters["application_count"] > 101:
                self.progressBar.show()
            self.collected_data = self.launch_imitation(**self.parameters)
            self.enabled_dividing_lines = False
            self.update_data_for_graphics()
            self.update_graphics()
            self.progressBar.hide()
        except ValueError:
            self.show_message("Ошибка: \nНекорректные данные")
        except RangeError:
            self.show_message("Ошибка: диапазон")

    def update_parameters(self):
        self.parameters["lm"] = float(self.lineEdit_lm_value.text().replace(',', '.'))
        self.parameters["mu"] = float(self.lineEdit_mu_value.text().replace(',', '.'))
        self.parameters["sg"] = float(self.lineEdit_sg_value.text().replace(',', '.'))
        self.parameters["application_count"] = int(self.lineEdit_count_value.text())

    def check_parameters_range(self):
        if not (0 < self.parameters["application_count"] < 351 and
                0 < self.parameters["lm"] and
                0 < self.parameters["mu"] and
                0 < self.parameters["sg"]):
            raise RangeError

    def show_message(self, text):
        self.label_message.show()
        self.label_message.setText(text)

    def clear_message(self):
        self.label_message.hide()
        self.label_message.setText("")

    def launch_imitation(self, lm, mu, sg, application_count) -> list:
        collected_data = [{"time": 0, "values": {"h_status": 0, "app_count": 0}}]

        def get_arrival_time() -> float:
            return -log(random()) / lm

        def get_handler_time() -> float:
            return -log(random()) / mu

        def get_orbit_time() -> float:
            return -log(random()) / sg

        # времена необработанных событий по номерам заявок (номер заявки=индекс)
        applications_events_times = [
            get_arrival_time() for _ in range(application_count)]

        # статусы заявок по их номерам
        applications_statuses = [NOT_RECEIVED] * application_count
        handler_status = FREE
        handler_elem_id = None
        completed_applications_count = 0
        active_applications_count = 0

        while application_count != completed_applications_count:

            # Находим индекс заявки, участвующей в ближайшем необработанном событии
            nearest_event_applications_index = None
            nearest_event_time = None
            for i in range(application_count):
                if applications_statuses[i] != COMPLETED:
                    if nearest_event_time is None or \
                            applications_events_times[i] < nearest_event_time:
                        nearest_event_time = applications_events_times[i]
                        nearest_event_applications_index = i

            # поступление в систему
            if applications_statuses[nearest_event_applications_index] == NOT_RECEIVED:
                applications_statuses[nearest_event_applications_index] = ACTIVE
                active_applications_count += 1

            # если прибор свободен, то занимаем его ближайшей заявкой
            if handler_status == FREE:
                handler_status = PROCESSING
                handler_elem_id = nearest_event_applications_index
                applications_events_times[nearest_event_applications_index] += get_handler_time()
            # если прибор был занят текущей заявкой, то освобождаем его
            elif handler_status == PROCESSING and \
                    handler_elem_id == nearest_event_applications_index:
                handler_status = FREE
                handler_elem_id = None
                applications_statuses[nearest_event_applications_index] = COMPLETED
                completed_applications_count += 1
                active_applications_count -= 1
            else:  # на орбиту
                applications_events_times[nearest_event_applications_index] += get_orbit_time()

            collected_data.append(
                {
                    "time": nearest_event_time,
                    "values":
                        {
                            "h_status": int(handler_status == PROCESSING),
                            "app_count": active_applications_count
                        }
                }
            )
            progress = int(completed_applications_count * 100 / application_count)
            self.progressBar.setValue(progress)

        return collected_data

    def update_data_for_graphics(self):
        self.clear_last_graphic_data()
        for i in range(1, len(self.collected_data)):
            if self.collected_data[i - 1]["values"]["app_count"] != \
                    self.collected_data[i]["values"]["app_count"]:  # Если есть изменение, то записываем
                self.data_for_graphics["applications_count_graphic_data"]["time"].append(
                    self.collected_data[i]["time"]),
                self.data_for_graphics["applications_count_graphic_data"]["values"].append(
                    self.collected_data[i]["values"]["app_count"])
            if self.collected_data[i - 1]["values"]["h_status"] != \
                    self.collected_data[i]["values"]["h_status"]:  # Если есть изменение, то записываем
                self.data_for_graphics["handler_statuses_graphic_data"]["time"].append(
                    self.collected_data[i]["time"]),
                self.data_for_graphics["handler_statuses_graphic_data"]["values"].append(
                    self.collected_data[i]["values"]["h_status"])
        # Удаляем последнее значение из данных для графиков для возможности отображения гистограм
        self.data_for_graphics["handler_statuses_graphic_data"]["values"].pop(-1)
        self.data_for_graphics["applications_count_graphic_data"]["values"].pop(-1)

    def clear_last_graphic_data(self):
        self.data_for_graphics["handler_statuses_graphic_data"]["time"].clear()
        self.data_for_graphics["handler_statuses_graphic_data"]["values"].clear()
        self.data_for_graphics["applications_count_graphic_data"]["time"].clear()
        self.data_for_graphics["applications_count_graphic_data"]["values"].clear()

    def update_graphics(self):
        self.clear_graphics()
        self.add_histogram(
            self.application_count_graphic,
            data_name="applications_count_graphic_data",
            brush=mkBrush(0, 0, 255, 80),
            pen=mkPen(0, 0, 0),
            sym_brush=mkBrush(0, 0, 255, 255)
        )
        self.add_histogram(
            self.handler_status_graphic,
            data_name="handler_statuses_graphic_data",
            brush=mkBrush(255, 0, 0, 80),
            pen=mkPen(0, 0, 0),
            sym_brush=mkBrush(255, 0, 0, 255)
        )

    def add_histogram(self, graphic_obj, data_name, brush, pen, sym_brush=None):
        if not self.enabled_dividing_lines:
            self.add_solid_histogram(graphic_obj, data_name, brush, pen, sym_brush)
        else:
            self.add_divided_histogram(graphic_obj, data_name, brush, pen)

    def add_solid_histogram(self, graphic_obj, data_name, brush, pen, sym_brush=None):
        graphic_obj.plot(
            self.data_for_graphics[data_name]["time"],
            self.data_for_graphics[data_name]["values"],
            stepMode="center",
            fillLevel=0,
            fillOutline=True,
            brush=brush,
            pen=pen,
            symbol="s" if self.enabled_graphic_symbol else None,
            symbolBrush=sym_brush
        )

    def add_divided_histogram(self, graphic_obj, data_name, brush, pen):
        for i in range(len(self.data_for_graphics[data_name]["time"]) - 1):
            next_time = self.data_for_graphics[data_name]["time"][i + 1]
            current_time = self.data_for_graphics[data_name]["time"][i]
            value = self.data_for_graphics[data_name]["values"][i]
            rect = QGraphicsRectItem(QtCore.QRectF(
                current_time, 0, next_time - current_time, value))
            rect.setPen(pen)
            rect.setBrush(brush)
            graphic_obj.addItem(rect)

    def clear_graphics(self):
        self.application_count_graphic.clear()
        self.handler_status_graphic.clear()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter - 1:
            self.launch()
        if event.key() == QtCore.Qt.Key_Up:
            self.y_range_padding += 0.1
            self.application_count_graphic.setYRange(
                0.6, self.data_for_graphics["handler_statuses_graphic_data"]["values"][-1],
                padding=self.y_range_padding)
        if event.key() == QtCore.Qt.Key_Down and self.y_range_padding - 1 >= 0:
            self.y_range_padding -= 0.1
            self.application_count_graphic.setYRange(
                0.6, self.data_for_graphics["handler_statuses_graphic_data"]["values"][-1],
                padding=self.y_range_padding)
        if event.key() == QtCore.Qt.Key_F1:
            self.enabled_dividing_lines = not self.enabled_dividing_lines
            self.update_graphics()
        if event.key() == QtCore.Qt.Key_F2:
            self.enabled_graphic_symbol = not self.enabled_graphic_symbol
            self.update_graphics()


class RangeError(Exception):
    pass


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
