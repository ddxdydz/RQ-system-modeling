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
from algorithms.algorithm1_v3 import main as alg1
from algorithms.algorithm1_settings import *


WINDOW_MINIMUM_SIZE = 480, 300
WINDOW_SIZE = 680, 400


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Словарь виджетов для ввода параметров:
        self.parameter_widgets = dict()
        
        # Словать виджетов, отображающих графики:
        self.graphic_widgets = dict()

        # Выносим процесс вычисления результатов симуляции в отдельный поток для разгрузки основного цикла:
        self.thread_alg1 = Thread(alg1)
        # В этом случае управление вернёться к основному циклу обработки событий после запуска потока.
        # Это делается для возможности обновления графического интерфейса без ожидания окончания симуляции.

        # Инициализация панели состояния:
        self.status_bar = StatusBar(self.statusBar())

        # Инициализация интерфейса главного окна:
        self.init_main_ui()
        self.init_parameter_widgets()
        self.init_graphic_widgets()
        self.to_based_widgets_state()

    def init_main_ui(self):
        uic.loadUi(r'data\MainWindow.ui', self)
        self.setWindowIcon(QIcon(r'data\icons\app_icon.ico'))
        self.setWindowTitle("Имитационное моделирование систем массового обслуживания")
        self.setMinimumSize(*WINDOW_MINIMUM_SIZE)
        self.resize(*WINDOW_SIZE)

        # Подключение кнопок к вызываемым функциям:
        self.lunch_button.clicked.connect(self.launch)
        self.status_bar.connect_stop_button(self.stop)

        # После завершения алгоритма будут вызваны переданные функции:
        self.thread_alg1.finished.connect(lambda: self.process_results())
        self.thread_alg1.finished.connect(lambda: self.to_based_widgets_state())

        # Подключение функции для возможности её вызова из потока по сигналу:
        self.thread_alg1.change_value.connect(self.status_bar.set_progress_value)

    def init_graphic_widgets(self):
        # Инициализация виджетов для вывода графиков:
        for key in ALGORITHM_1_SETTINGS["GRAPHICS_KEYS"]:
            self.graphic_widgets[key] = Graphic(ALGORITHM_1_SETTINGS["GRAPHICS_SETTINGS"][key])
            self.verticalLayout_graphic_widgets.addWidget(
                self.graphic_widgets[key],
                ALGORITHM_1_SETTINGS["GRAPHICS_LAYOUT_STRETCH"][key]
            )
    
    def init_parameter_widgets(self):
        # Инициализация виджетов для ввода параметров:
        for parameter_key in ALGORITHM_1_SETTINGS["PARAMETERS_KEYS"]:
            parameter_label_widget = QLabel()
            parameter_label_widget.setText(
                ALGORITHM_1_SETTINGS["PARAMETERS_LABELS"][parameter_key])
            self.parameter_widgets[parameter_key] = Parameter(
                ALGORITHM_1_SETTINGS["PARAMETERS_SETTINGS"][parameter_key])
            if self.parameter_widgets[parameter_key].is_one_line():
                parameter_label_widget.setFont(QFont('MS Shell Dlg 2', 10))
                parameter_layout = QHBoxLayout()
                parameter_layout.addWidget(parameter_label_widget)
                parameter_layout.addWidget(self.parameter_widgets[parameter_key])
                self.verticalLayout_parameters.addLayout(parameter_layout)
            else:
                self.verticalLayout_parameters.addItem(
                    QSpacerItem(20, 10, QSizePolicy.Fixed, QSizePolicy.Fixed))
                self.verticalLayout_parameters.addWidget(parameter_label_widget)
                self.verticalLayout_parameters.addWidget(
                    self.parameter_widgets[parameter_key])

    def launch(self):
        if not self.thread_alg1.isRunning():
            try:
                self.lunch_button.setEnabled(False)
                self.status_bar.update_message("Обработка...")
                self.status_bar.show_progress()
                # Запуск алгоритма в отдельном процессе:
                self.thread_alg1.set_parameters(self.get_parameters())
                self.thread_alg1.start()
            except ValueError:
                self.status_bar.update_message("Ошибка: Некорректные значения")
                self.to_based_widgets_state()
            except FullnessError:
                self.status_bar.update_message("Ошибка: Некоторые параметры без значения")
                self.to_based_widgets_state()
            except RangeError:
                self.status_bar.update_message("Ошибка: Некорректный диапазон")
                self.to_based_widgets_state()

    def stop(self):
        self.thread_alg1.terminate()

    def get_parameters(self):
        parameters = dict()
        for key, widget in self.parameter_widgets.items():
            parameters[key] = widget.get_value()
        return parameters

    def to_based_widgets_state(self):
        self.lunch_button.setEnabled(True)
        self.status_bar.hide_progress()

    def update_graphic_widgets(self, collected_data):
        data_for_graphics = dict()
        for key in self.graphic_widgets.keys():
            data_for_graphics[key] = {"time": [0], "values": [0]}

        # Формируем данные для построения гистограмм из собранных значений:
        for i in range(1, len(collected_data)):
            for key in self.graphic_widgets.keys():
                # Если рассматриваемое значение не изменилось, то не записываем его в данные для гистограммы:
                if self.graphic_widgets[key].type() == "histogram":
                    if collected_data[i - 1]["values"][key] == collected_data[i]["values"][key]:
                        continue
                data_for_graphics[key]["time"].append(collected_data[i]["time"])
                data_for_graphics[key]["values"].append(collected_data[i]["values"][key])

        # Удаляем последнее значение из данных для графиков для возможности отображения гистограм
        # Это последнее значение равняется изначальному значению и не влияет на общий результат
        for key in self.graphic_widgets.keys():
            if self.graphic_widgets[key].get_type() == "histogram":
                data_for_graphics[key]["values"].pop(-1)

        # Строим график по полученным значениям:
        for key in self.graphic_widgets.keys():
            self.graphic_widgets[key].update_graphic_view(data_for_graphics[key])

    def process_results(self):
        results = self.thread_alg1.results
        if results["status"] == ITERATION_LIMIT:
            self.status_bar.update_message("Превышено количество итераций. Проверьте введённые значения")
            self.to_based_widgets_state()
        elif results["status"] == TERMITE:
            self.status_bar.update_message("Обработка отменена")
            self.to_based_widgets_state()
        else:
            work_time = results['algorithm_working_time']
            work_time_for_status = round(work_time, 3) if work_time >= 0.01 else 0.01
            self.status_bar.update_message(f"Обработка завершена за {work_time_for_status} сек. ")
            self.update_graphic_widgets(results["events_data"])

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Enter - 1:
            self.launch()
        if event.key() == QtCore.Qt.Key.Key_F5:
            for widget in self.graphic_widgets.values():
                widget.autoRange()


class StatusBar:
    def __init__(self, parent):
        self.parent = parent
        self.progressBar = QProgressBar()
        self.label_message = QLabel()
        self.stop_button = QPushButton()
        self.init_status_bar_init()

    def init_status_bar_init(self):
        # Настройка панели состояния:
        self.update_message("Готов...")
        self.progressBar.setFixedHeight(13)
        self.progressBar.setFixedWidth(150)
        self.stop_button.setText("×")
        self.stop_button.setFixedHeight(15)
        self.stop_button.setFixedWidth(15)
        self.parent.addWidget(self.label_message)
        self.parent.addWidget(self.stop_button)
        self.parent.addWidget(self.progressBar)
        styles = "QStatusBar {\n  border: 1px solid#D7D7D7;\n  background-color: #F0F0F0;\n}"
        self.parent.setStyleSheet(styles)

    def update_message(self, text):
        self.label_message.setText(f"  {text}   ")

    def connect_stop_button(self, func):
        self.stop_button.clicked.connect(func)

    def set_progress_value(self, value):
        self.progressBar.setValue(value)

    def hide_progress(self):
        self.progressBar.hide()
        self.progressBar.setValue(0)
        self.stop_button.hide()

    def show_progress(self):
        self.progressBar.show()
        self.stop_button.show()


class Parameter(QLineEdit):
    def __init__(self, parameter_settings):
        super(Parameter, self).__init__()
        self.settings = parameter_settings
        self.init_widget_ui()
    
    def init_widget_ui(self):
        self.setText(str(self.settings["default_value"]))
        if self.is_one_line:
            self.setFixedWidth(100)
            self.setFixedHeight(20)
        else:
            self.setFixedWidth(133)
            self.setFixedHeight(20)

    def is_one_line(self):
        return self.settings["one_line_label"]

    def check_parameters_fullness(self):
        if self.text().strip() == "":
            raise FullnessError

    def check_parameters_range(self, checking_value):
        if not ((checking_value > self.settings["range"]["min"]) and
                (checking_value <= self.settings["range"]["max"])):
            raise RangeError

    def get_value(self):
        self.check_parameters_fullness()
        value_type = self.settings["type"]
        value = value_type(self.text().replace(',', '.'))
        self.check_parameters_range(value)
        return value


class Graphic(PlotWidget):
    def __init__(self, graphic_settings):
        super(Graphic, self).__init__()
        self.settings = graphic_settings
        self.init_widget_ui()
        self.init_graphic_ui()

    def init_widget_ui(self):
        sp = self.sizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Preferred)
        sp.setVerticalPolicy(QSizePolicy.Preferred)

    def init_graphic_ui(self):
        self.addLegend()
        self.setBackground(self.settings["background_style"])
        self.setTitle(self.settings["title"], **self.settings["styles_title"])
        self.setLabel("left", self.settings["left_label"], **self.settings["styles_labels"])
        self.setLabel("bottom", self.settings["bottom_label"], **self.settings["styles_labels"])
        ay = self.getAxis('left')
        ay.setWidth(w=self.settings["width_left_axis_px"])
        self.showGrid(**self.settings["show_grid"])
        self.setMouseEnabled(**self.settings["set_mouse_enabled"])
        self.getPlotItem().setMenuEnabled(False)

    def get_type(self):
        return self.settings["type"]

    def get_max_value(self, data_for_graphic):
        if self.settings["maximum_value"] is None:
            return max(data_for_graphic["values"])
        return self.settings["maximum_value"]

    def set_left_ticks_view(self, max_value):
        ay = self.getAxis('left')
        ticks_count = self.settings["max_count_of_left_ticks"]
        step = max_value // ticks_count if max_value > ticks_count else 1
        ticks = [i for i in range(0, max_value + 1, step)]
        ay.setTicks([[(v, str(v)) for v in ticks]])

    def update_graphic_view(self, data_for_graphic):
        self.clear()
        self.plot(
            data_for_graphic["time"],
            data_for_graphic["values"],
            stepMode="center" if self.get_type() == "histogram" else None,
            fillLevel=self.settings["fillLevel"],
            fillOutline=True,
            brush=mkBrush(**self.settings["brush_parameters"]),
            pen=mkPen(**self.settings["pen_parameters"]),
        )
        self.set_left_ticks_view(self.get_max_value(data_for_graphic))
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
