import sys

from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication
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
        self.max_count_of_left_ticks = 15
        self.width_left_axis_px = 35

        # Выносим процесс вычисления результатов симуляции в отдельный поток для разгрузки основного цикла:
        self.thread_alg1 = Thread(alg1, self.parameters)
        # В этом случае управление вернёться к основному циклу обработки событий после запуска потока.
        # Это делается для возможности обновления графического интерфейса без ожидания окончания симуляции.

        self.init_ui()
        self.launch()

    def init_ui(self):
        uic.loadUi(r'data\MainWindow.ui', self)
        self.setWindowIcon(QIcon(r'data\app_icon.ico'))
        self.setWindowTitle("Имитационное моделирование систем массового обслуживания")

        # Добавление параметров по умолчанию в строки ввода:
        self.lineEdit_lm_value.setText(str(self.parameters["lm"]))
        self.lineEdit_mu_value.setText(str(self.parameters["mu"]))
        self.lineEdit_sg_value.setText(str(self.parameters["sg"]))
        self.lineEdit_count_value.setText(str(self.parameters["application_count"]))

        # При нажатии на кнопку "запуск" будет вызвана функция self.launch:
        self.pushButton.clicked.connect(self.launch)

        # После завершения алгоритма будут вызваны переданные функции:
        self.thread_alg1.finished.connect(lambda: self.process_the_collected_data())
        self.thread_alg1.finished.connect(lambda: self.to_based_widgets_state())

        # Подключение функции для возможности её вызова из потока по сигналу:
        self.thread_alg1.change_value.connect(self.progressBar.setValue)

        # Инициализация интерфейса графических виджетов:
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

    def init_graphic_ui(self, graphic_obj, title=None, left_label=None, bottom_label=None):
        graphic_obj.addLegend()
        graphic_obj.setBackground('w')
        graphic_obj.showGrid(x=True, y=True)
        graphic_obj.setTitle(title, color="b", size="15pt")
        styles = {"color": "#f00", "font-size": "8pt"}
        graphic_obj.setLabel("left", left_label, **styles)
        graphic_obj.setLabel("bottom", bottom_label, **styles)
        ay = graphic_obj.getAxis('left')
        ay.setWidth(w=self.width_left_axis_px)
        graphic_obj.setMouseEnabled(x=True, y=False)
        graphic_obj.getPlotItem().setMenuEnabled(False)

    def launch(self):
        if not self.thread_alg1.isRunning():
            try:
                self.clear_message()
                self.update_parameters()
                self.check_parameters_range()
                self.pushButton.setEnabled(False)
                if self.parameters["application_count"] > 101:
                    self.pushButton.hide()
                    self.progressBar.show()
                # Запуск алгоритма в отдельном процессе:
                self.thread_alg1.set_parameters(self.parameters)
                self.thread_alg1.start()
            except ValueError:
                self.show_message("Ошибка: \nНекорректные значения")
                self.to_based_widgets_state()
            except RangeError:
                self.show_message("Ошибка: \nНекорректный диапазон")
                self.to_based_widgets_state()

    def process_the_collected_data(self):
        # Обрабатываем собранные значения и строим на их основе графики:
        collected_data_alg1 = self.thread_alg1.results
        self.update_data_for_graphics(collected_data_alg1)
        self.update_graphic_widgets()

    def to_based_widgets_state(self):
        self.pushButton.show()
        self.pushButton.setEnabled(True)
        self.progressBar.setValue(0)
        self.progressBar.hide()

    def update_parameters(self):
        self.parameters["lm"] = float(self.lineEdit_lm_value.text().replace(',', '.'))
        self.parameters["mu"] = float(self.lineEdit_mu_value.text().replace(',', '.'))
        self.parameters["sg"] = float(self.lineEdit_sg_value.text().replace(',', '.'))
        self.parameters["application_count"] = int(self.lineEdit_count_value.text())

    def check_parameters_range(self):
        if not (0 < self.parameters["application_count"] <= 400 and
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
            pen=mkPen(0, 0, 0)
        )
        self.add_histogram(
            self.handler_status_graphic,
            data_name="handler_statuses_graphic_data",
            brush=mkBrush(255, 0, 0, 80),
            pen=mkPen(0, 0, 0)
        )

    def add_histogram(self, graphic_obj, data_name, brush, pen):
        graphic_obj.plot(
            self.data_for_graphics[data_name]["time"],
            self.data_for_graphics[data_name]["values"],
            stepMode="center",
            fillLevel=0,
            fillOutline=True,
            brush=brush,
            pen=pen,
            symbol=None
        )
        self.set_left_view_values(graphic_obj, data_name)
        graphic_obj.autoRange()

    def set_left_view_values(self, graphic_obj, data_name):
        ay = graphic_obj.getAxis('left')
        graphic_values = self.data_for_graphics[data_name]["values"]
        max_elem = max(graphic_values)
        step = 1
        if max_elem > self.max_count_of_left_ticks:
            step = max_elem // self.max_count_of_left_ticks
        ticks = [i for i in range(0, max_elem + 1, step)]
        ay.setTicks([[(v, str(v)) for v in ticks]])

    def clear_graphic_widgets(self):
        self.application_count_graphic.clear()
        self.handler_status_graphic.clear()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter - 1:
            self.launch()
        if event.key() == QtCore.Qt.Key_F5:
            self.application_count_graphic.autoRange()
            self.handler_status_graphic.autoRange()


class Thread(QtCore.QThread):
    change_value = QtCore.pyqtSignal(int)  # Для счёта процентов выполнения

    def __init__(self, algorithm, parameters=None):
        super(Thread, self).__init__()
        self.algorithm = algorithm
        self.parameters = parameters
        self.results = None

    def set_parameters(self, parameters):
        self.parameters = parameters

    def run(self):
        self.results = self.algorithm(
            **self.parameters,
            signal_to_change_progress_value=self.change_value
        )


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
