import sys

from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QHBoxLayout, QSpacerItem,
    QProgressBar, QLabel, QPushButton, QLineEdit)
from PyQt5.QtWidgets import QSizePolicy
from pyqtgraph import (
    mkBrush, mkPen, PlotWidget)

from constants import *
from algorithms.algorithm1 import main as alg1
from algorithms.algorithm1_settings import *


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Создание списка параметров для выполнения алгоритма:
        self.parameters = ALGORITHM_1_SETTINGS["PARAMETERS_DEFAULT_VALUES"]

        # Словарь виджетов для ввода параметров:
        self.parameter_input_widgets = dict()

        # Выносим процесс вычисления результатов симуляции в отдельный поток для разгрузки основного цикла:
        self.thread_alg1 = Thread(alg1, self.parameters)
        # В этом случае управление вернёться к основному циклу обработки событий после запуска потока.
        # Это делается для возможности обновления графического интерфейса без ожидания окончания симуляции.

        # Словарь виджетов для отображения графиков::
        self.graphic_widgets = dict()
        for key in ALGORITHM_1_SETTINGS["GRAPHICS_KEYS"]:
            self.graphic_widgets[key] = Graphic(ALGORITHM_1_SETTINGS["GRAPHICS_SETTINGS"][key])

        # Инициализация виджетов для панели состояния:
        self.progressBar = QProgressBar()
        self.label_message = QLabel()
        self.stop_button = QPushButton()

        # Инициализация интерфейса главного окна:
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

        # Подключение кнопок к вызываемым функциям:
        self.lunch_button.clicked.connect(self.launch)
        self.stop_button.clicked.connect(self.stop)

        # После завершения алгоритма будут вызваны переданные функции:
        self.thread_alg1.finished.connect(lambda: self.process_results())
        self.thread_alg1.finished.connect(lambda: self.to_based_widgets_state())

        # Подключение функции для возможности её вызова из потока по сигналу:
        self.thread_alg1.change_value.connect(self.progressBar.setValue)

        # Добавление графических виджетов на главный экран:
        for key in ALGORITHM_1_SETTINGS["GRAPHICS_KEYS"]:
            self.verticalLayout_graphic_widgets.addWidget(
                self.graphic_widgets[key],
                ALGORITHM_1_SETTINGS["GRAPHICS_LAYOUT_STRETCH"][key]
            )

        # Инициализация виджетов для ввода параметров:
        for parameter_key in ALGORITHM_1_SETTINGS["PARAMETERS_KEYS"]:
            parameter_label_text = ALGORITHM_1_SETTINGS["PARAMETERS_LABELS"][parameter_key]
            parameter_value = ALGORITHM_1_SETTINGS["PARAMETERS_DEFAULT_VALUES"][parameter_key]
            parameter_label_widget = QLabel()
            parameter_label_widget.setText(parameter_label_text)
            parameter_line_edit_widget = QLineEdit()
            self.parameter_input_widgets[parameter_key] = parameter_line_edit_widget
            parameter_line_edit_widget.setText(str(parameter_value))
            if len(parameter_label_text) == 2:  # Если описание параметра имеет вид: "<символ>:"
                parameter_label_widget.setFont(QFont('MS Shell Dlg 2', 10))
                parameter_line_edit_widget.setFixedWidth(100)
                parameter_line_edit_widget.setFixedHeight(20)
                parameter_layout = QHBoxLayout()
                parameter_layout.addWidget(parameter_label_widget)
                parameter_layout.addWidget(parameter_line_edit_widget)
                self.verticalLayout_parameters.addLayout(parameter_layout)
            else:
                parameter_line_edit_widget.setFixedWidth(133)
                parameter_line_edit_widget.setFixedHeight(20)
                self.verticalLayout_parameters.addItem(
                    QSpacerItem(20, 10, QSizePolicy.Fixed, QSizePolicy.Fixed))
                self.verticalLayout_parameters.addWidget(parameter_label_widget)
                self.verticalLayout_parameters.addWidget(parameter_line_edit_widget)

        self.to_based_widgets_state()

    def launch(self):
        if not self.thread_alg1.isRunning():
            try:
                self.check_parameters_fullness()
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
            except FullnessError:
                self.update_message("Ошибка: Некоторые параметры без значения")
                self.to_based_widgets_state()
            except RangeError:
                self.update_message("Ошибка: Некорректный диапазон")
                self.to_based_widgets_state()

    def stop(self):
        self.thread_alg1.terminate()
        self.to_based_widgets_state()

    def update_parameters(self):
        for parameter_key in ALGORITHM_1_SETTINGS["PARAMETERS_KEYS"]:
            value_type = ALGORITHM_1_SETTINGS["PARAMETERS_TYPES"][parameter_key]
            input_widget = self.parameter_input_widgets[parameter_key]
            self.parameters[parameter_key] = value_type(input_widget.text().replace(',', '.'))

    def update_message(self, text):
        self.label_message.setText(f"  {text}   ")

    def check_parameters_fullness(self):
        for parameter_key in ALGORITHM_1_SETTINGS["PARAMETERS_KEYS"]:
            input_widget = self.parameter_input_widgets[parameter_key]
            if input_widget.text().strip() == "":
                raise FullnessError

    def check_parameters_range(self):
        for parameter_key in ALGORITHM_1_SETTINGS["PARAMETERS_KEYS"]:
            min_value = ALGORITHM_1_SETTINGS["PARAMETERS_RANGE"][parameter_key]["min"]
            max_value = ALGORITHM_1_SETTINGS["PARAMETERS_RANGE"][parameter_key]["max"]
            if not (min_value < self.parameters[parameter_key] <= max_value):
                raise RangeError

    def process_results(self):
        # Обрабатываем собранные значения и строим на их основе графики:
        results = self.thread_alg1.results
        if results["status"] == ITERATION_LIMIT:
            self.update_message("Превышено количество итераций. Проверьте введённые значения")
            self.to_based_widgets_state()
        elif results["status"] == TERMITE:
            self.update_message("Обработка отменена")
            self.to_based_widgets_state()
        else:
            work_time = round(results['algorithm_working_time'], 3)
            self.update_message(f"Обработка завершена за {work_time if work_time >= 0.01 else 0.01} сек. ")
            self.update_graphic_widgets(results["events_data"])

    def to_based_widgets_state(self):
        self.lunch_button.setEnabled(True)
        self.progressBar.hide()
        self.progressBar.setValue(0)
        self.stop_button.hide()

    def update_graphic_widgets(self, collected_data):
        data_for_graphics = dict()
        for key in ALGORITHM_1_SETTINGS["GRAPHICS_KEYS"]:
            data_for_graphics[key] = {"time": [0], "values": [0]}

        # Формируем данные для построения гистограмм из собранных значений:
        for i in range(1, len(collected_data)):
            for key in ALGORITHM_1_SETTINGS["GRAPHICS_KEYS"]:
                # Если рассматриваемое значение изменилось, то фиксируем его:
                if collected_data[i - 1]["values"][key] != collected_data[i]["values"][key]:
                    data_for_graphics[key]["time"].append(collected_data[i]["time"])
                    data_for_graphics[key]["values"].append(collected_data[i]["values"][key])

        # Удаляем последнее значение из данных для графиков для возможности отображения гистограм
        # Это последнее значение равняется изначальному значению и не влияет на общий результат
        for key in ALGORITHM_1_SETTINGS["GRAPHICS_KEYS"]:
            if ALGORITHM_1_SETTINGS["GRAPHICS_SETTINGS"][key]["type"] == "histogram":
                data_for_graphics[key]["values"].pop(-1)

        # Строим график по полученным значениям:
        for key in ALGORITHM_1_SETTINGS["GRAPHICS_KEYS"]:
            self.graphic_widgets[key].update_graphic_view(data_for_graphics[key])

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Enter - 1:
            self.launch()
        if event.key() == QtCore.Qt.Key.Key_F5:
            for key in ALGORITHM_1_SETTINGS["GRAPHICS_KEYS"]:
                self.graphic_widgets[key].autoRange()


class Graphic(PlotWidget):
    def __init__(self, view_settings):
        super(Graphic, self).__init__()
        self.view_settings = view_settings
        self.init_widget_ui()
        self.init_graphic_ui()

    def init_widget_ui(self):
        sp = self.sizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Preferred)
        sp.setVerticalPolicy(QSizePolicy.Preferred)

    def init_graphic_ui(self):
        self.addLegend()
        self.setBackground(self.view_settings["background_style"])
        self.setTitle(
            self.view_settings["title"],
            **self.view_settings["styles_title"]
        )
        self.setLabel(
            "left",
            self.view_settings["left_label"],
            **self.view_settings["styles_labels"]
        )
        self.setLabel(
            "bottom",
            self.view_settings["bottom_label"],
            **self.view_settings["styles_labels"]
        )
        ay = self.getAxis('left')
        ay.setWidth(w=self.view_settings["width_left_axis_px"])
        self.showGrid(**self.view_settings["show_grid"])
        self.setMouseEnabled(**self.view_settings["set_mouse_enabled"])
        self.getPlotItem().setMenuEnabled(False)

    def set_left_ticks_view(self, data_for_graphic):
        ay = self.getAxis('left')
        max_elem = max(data_for_graphic["values"])
        step = 1
        max_count_of_left_ticks = self.view_settings["max_count_of_left_ticks"]
        if max_elem > max_count_of_left_ticks:
            step = max_elem // max_count_of_left_ticks
        ticks = [i for i in range(0, max_elem + 1, step)]
        ay.setTicks([[(v, str(v)) for v in ticks]])

    def update_graphic_view(self, data_for_graphic):
        self.clear()
        count_x_values = len(data_for_graphic["time"])
        count_y_values = len(data_for_graphic["values"])
        self.plot(
            data_for_graphic["time"],
            data_for_graphic["values"],
            stepMode="center" if count_x_values > count_y_values else None,
            fillLevel=self.view_settings["fillLevel"],
            fillOutline=True,
            brush=mkBrush(**self.view_settings["brush_parameters"]),
            pen=mkPen(**self.view_settings["pen_parameters"]),
        )
        self.set_left_ticks_view(data_for_graphic)
        self.autoRange()


class Thread(QtCore.QThread):
    change_value = QtCore.pyqtSignal(int)  # Для подсчёта процентов выполнения

    def __init__(self, algorithm, parameters=None):
        super(Thread, self).__init__()
        self.algorithm = algorithm
        self.parameters = parameters
        self.results = dict()

    def set_parameters(self, parameters):
        self.parameters = parameters

    def run(self):
        # В случае, если процесс будет принудительно остановлен:
        self.results["status"] = TERMITE
        # Запуск процесса:
        self.results = self.algorithm(
            **self.parameters,
            signal_to_change_progress_value=self.change_value
        )


class FullnessError(Exception):
    pass


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
