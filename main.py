import sys

from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtWidgets import QGraphicsRectItem
from pyqtgraph import mkBrush, mkPen

from algorithms.alg1 import main as alg1


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Создание списка параметров для выполнения алгоритма:
        self.parameters = {
            "application_count": 4,
            "lm": 3.0,
            "mu": 1.0,
            "sg": 1.0
        }

        # Данные для построения графиков (гистограмм):
        self.data_for_graphics = {
            "handler_statuses_graphic_data": {"time": [], "values": []},
            "applications_count_graphic_data": {"time": [], "values": []}
        }

        # Параметры отображения графиков:
        self.enabled_dividing_lines = False
        self.enabled_graphic_symbol = False
        self.y_range_padding = 0

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

        # При нажатии на кнопку "запуск" будет вызвана функция self.launch
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
            left_label="Статус",
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
            self.pushButton.hide()
            self.update_parameters()
            self.check_parameters_range()
            if self.parameters["application_count"] > 101:
                self.progressBar.show()
            collected_data_alg1 = alg1(**self.parameters, progress_bar_widget=self.progressBar)
            self.update_data_for_graphics(collected_data_alg1)
            self.enabled_dividing_lines = False
            self.update_graphic_widgets()
            self.progressBar.hide()
        except ValueError:
            self.show_message("Ошибка: \nНекорректные значения")
        except RangeError:
            self.show_message("Ошибка: \nНекорректный диапазон")
        finally:
            self.pushButton.show()

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

    def update_data_for_graphics(self, collected_data):
        self.clear_graphic_data()
        collected_events_data = collected_data["events_data"]

        # Формируем данные для построения гистограмм из собранных значений:
        for i in range(1, len(collected_events_data)):

            # Формирование данных для гистограммы, показывающей изменение количества заявок по времени:
            if collected_events_data[i - 1]["values"]["app_count"] != \
                    collected_events_data[i]["values"]["app_count"]:  # Если есть изменение, то записываем его
                # Добавляем время, когда произошло изменение:
                self.data_for_graphics["applications_count_graphic_data"]["time"].append(
                    collected_events_data[i]["time"])
                # Добавляем изменённое количество заявок в системе:
                self.data_for_graphics["applications_count_graphic_data"]["values"].append(
                    collected_events_data[i]["values"]["app_count"])

            # Формирование данных для гистограммы, показывающей изменение статуса обработчика по времени:
            if collected_events_data[i - 1]["values"]["h_status"] != \
                    collected_events_data[i]["values"]["h_status"]:  # Если есть изменение, то записываем его
                # Добавляем время, когда произошло изменение:
                self.data_for_graphics["handler_statuses_graphic_data"]["time"].append(
                    collected_events_data[i]["time"])
                # Добавляем изменённый статус обработчика:
                self.data_for_graphics["handler_statuses_graphic_data"]["values"].append(
                    collected_events_data[i]["values"]["h_status"])

        # Удаляем последнее значение из данных для графиков для возможности отображения гистограм
        # Это последнее значение равняется изначальному значению и не влияет на общий результат
        self.data_for_graphics["handler_statuses_graphic_data"]["values"].pop(-1)
        self.data_for_graphics["applications_count_graphic_data"]["values"].pop(-1)

    def clear_graphic_data(self):
        self.data_for_graphics["handler_statuses_graphic_data"]["time"].clear()
        self.data_for_graphics["handler_statuses_graphic_data"]["values"].clear()
        self.data_for_graphics["applications_count_graphic_data"]["time"].clear()
        self.data_for_graphics["applications_count_graphic_data"]["values"].clear()

    def update_graphic_widgets(self):
        self.clear_graphic_widgets()
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
        # Добавление столбцов гистограммы в виде прямоугольников
        for i in range(len(self.data_for_graphics[data_name]["time"]) - 1):
            next_time = self.data_for_graphics[data_name]["time"][i + 1]
            current_time = self.data_for_graphics[data_name]["time"][i]
            value = self.data_for_graphics[data_name]["values"][i]
            rect = QGraphicsRectItem(QtCore.QRectF(
                current_time, 0, next_time - current_time, value))
            rect.setPen(pen)
            rect.setBrush(brush)
            graphic_obj.addItem(rect)

    def clear_graphic_widgets(self):
        self.application_count_graphic.clear()
        self.handler_status_graphic.clear()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter - 1:
            self.launch()

        # Сжатие/растяжение отображения графика по оси Y
        if event.key() == QtCore.Qt.Key_Up:
            self.y_range_padding += 1
            self.application_count_graphic.setYRange(
                0, max(self.data_for_graphics["applications_count_graphic_data"]["values"]),
                padding=self.y_range_padding * 0.1)
        if event.key() == QtCore.Qt.Key_Down and self.y_range_padding > 1:
            self.y_range_padding -= 1
            self.application_count_graphic.setYRange(
                0, max(self.data_for_graphics["applications_count_graphic_data"]["values"]),
                padding=self.y_range_padding * 0.1)

        # Показать/скрыть линии, разделяющие столбцы гистограммы
        if event.key() == QtCore.Qt.Key_F1:
            self.enabled_dividing_lines = not self.enabled_dividing_lines
            self.update_graphic_widgets()

        # Показать/скрыть символы над столбцами гистограммы
        if event.key() == QtCore.Qt.Key_F2:
            self.enabled_graphic_symbol = not self.enabled_graphic_symbol
            self.update_graphic_widgets()


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
