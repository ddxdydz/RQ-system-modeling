import sys

from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QMainWindow, QApplication,
    QProgressBar, QLabel, QPushButton)
from pyqtgraph import (mkBrush, mkPen)

from data.constants import *
from algorithms.alg1_1 import main as alg1


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

        self.progressBar = QProgressBar()
        self.label_message = QLabel()
        self.stop_button = QPushButton()
        self.init_ui()

    def init_ui(self):
        uic.loadUi(r'data\MainWindow.ui', self)
        self.setWindowIcon(QIcon(r'data\icons\app_icon.ico'))
        self.setWindowTitle("Имитационное моделирование систем массового обслуживания")

        # Настройка панели состояния:
        self.update_message("Готов...")
        self.progressBar.setFixedHeight(13)
        self.progressBar.setFixedWidth(150)
        self.stop_button.setText("×")
        self.stop_button.setFixedHeight(15)
        self.stop_button.setFixedWidth(15)
        self.statusBar.addWidget(self.label_message)
        self.statusBar.addWidget(self.stop_button)
        self.statusBar.addWidget(self.progressBar)

        # Добавление параметров по умолчанию в строки ввода:
        self.lineEdit_lm_value.setText(str(self.parameters["lm"]))
        self.lineEdit_mu_value.setText(str(self.parameters["mu"]))
        self.lineEdit_sg_value.setText(str(self.parameters["sg"]))
        self.lineEdit_count_value.setText(str(self.parameters["application_count"]))

        # Подключение кнопок к вызываемым функциям:
        self.lunch_button.clicked.connect(self.launch)
        self.stop_button.clicked.connect(self.stop)

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

        self.to_based_widgets_state()

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
                self.update_parameters()
                self.check_parameters_range()
                self.lunch_button.setEnabled(False)
                self.progressBar.show()
                self.stop_button.show()
                self.update_message("Обработка...")
                # Запуск алгоритма в отдельном процессе:
                self.thread_alg1.set_parameters(self.parameters)
                self.thread_alg1.start()
            except ValueError:
                self.update_message("Ошибка: Некорректные значения")
                self.to_based_widgets_state()
            except RangeError:
                self.update_message("Ошибка: Некорректный диапазон")
                self.to_based_widgets_state()

    def stop(self):
        self.thread_alg1.terminate()
        self.to_based_widgets_state()

    def process_the_collected_data(self):
        # Обрабатываем собранные значения и строим на их основе графики:
        results = self.thread_alg1.results

        if results["status"] == ITERATION_LIMIT:
            self.update_message("Превышено количество итераций. Проверьте введённые значения")
            self.to_based_widgets_state()
        elif results["status"] == TERMITE:
            self.update_message("Обработка отменена")
            self.to_based_widgets_state()
        else:
            self.update_data_for_graphics(results["events_data"])
            self.update_graphic_widgets()
            working_time = round(results['algorithm_working_time'], 3)
            if working_time < 0.01:
                working_time = 0.01
            self.update_message(f"Обработка завершена за {working_time} сек. ")

    def to_based_widgets_state(self):
        self.lunch_button.setEnabled(True)
        self.progressBar.hide()
        self.progressBar.setValue(0)
        self.stop_button.hide()

    def update_parameters(self):
        self.parameters["lm"] = float(self.lineEdit_lm_value.text().replace(',', '.'))
        self.parameters["mu"] = float(self.lineEdit_mu_value.text().replace(',', '.'))
        self.parameters["sg"] = float(self.lineEdit_sg_value.text().replace(',', '.'))
        self.parameters["application_count"] = int(self.lineEdit_count_value.text())

    def check_parameters_range(self):
        if not (0 < self.parameters["application_count"] <= 100000 and
                0 < self.parameters["lm"] and
                0 < self.parameters["mu"] and
                0 < self.parameters["sg"]):
            raise RangeError

    def update_message(self, text):
        self.label_message.setText(f"  {text}   ")

    def update_data_for_graphics(self, collected_data):
        self.clear_graphic_data()

        # Формируем данные для построения гистограмм из собранных значений:
        for i in range(1, len(collected_data)):

            # Формирование данных для гистограммы, показывающей изменение количества заявок по времени:
            if collected_data[i - 1]["values"]["app_count"] != \
                    collected_data[i]["values"]["app_count"]:  # Если есть изменение, то записываем его
                # Добавляем время, когда произошло изменение:
                self.data_for_graphics["applications_count_graphic_data"]["time"].append(
                    collected_data[i]["time"])
                # Добавляем изменённое количество заявок в системе:
                self.data_for_graphics["applications_count_graphic_data"]["values"].append(
                    collected_data[i]["values"]["app_count"])

            # Формирование данных для гистограммы, показывающей изменение статуса обработчика по времени:
            if collected_data[i - 1]["values"]["h_status"] != \
                    collected_data[i]["values"]["h_status"]:  # Если есть изменение, то записываем его
                # Добавляем время, когда произошло изменение:
                self.data_for_graphics["handler_statuses_graphic_data"]["time"].append(
                    collected_data[i]["time"])
                # Добавляем изменённый статус обработчика:
                self.data_for_graphics["handler_statuses_graphic_data"]["values"].append(
                    collected_data[i]["values"]["h_status"])

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
        if event.key() == QtCore.Qt.Key.Key_Enter - 1:
            self.launch()
        if event.key() == QtCore.Qt.Key.Key_F5:
            self.application_count_graphic.autoRange()
            self.handler_status_graphic.autoRange()


class Thread(QtCore.QThread):
    change_value = QtCore.pyqtSignal(int)  # Для счёта процентов выполнения

    def __init__(self, algorithm, parameters=None):
        super(Thread, self).__init__()
        self.algorithm = algorithm
        self.parameters = parameters
        self.results = dict()

    def set_parameters(self, parameters):
        self.parameters = parameters

    def run(self):
        # В случае если процесс будет принудительно остановлен:
        self.results["status"] = TERMITE
        # Запус процесса:
        self.results = self.algorithm(
            **self.parameters,
            signal_to_change_progress_value=self.change_value
        )


class RangeError(Exception):
    pass


class IterationError(Exception):
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
