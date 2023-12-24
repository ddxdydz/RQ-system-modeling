import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication

# Прямое подключение скрытых зависимостей для избежания неполной сборки exe-файла через pyinstaller:

from basic.constants.error_indexes import *
from basic.constants.window_settings import *
from basic.errors.FullnessError import FullnessError
from basic.errors.RangeError import RangeError
from interface.ui.MainWindow import Ui_MainWindow
from interface.ui.get_window_size import get_window_size
from interface.ui.get_ico_from_code import get_ico
from algorithms.AlgorithmS1 import Algorithm1
from interface.plot_settings.algorithm1_display_settings import *
from interface.Graphic import Graphic
from interface.Parameter import Parameter
from interface.StatusBar import StatusBar
from interface.Thread import Thread


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.parameter_widgets = dict()
        self.graphic_widgets = dict()

        self.status_bar = StatusBar(self.statusBar())

        # Выносим процесс вычисления результатов симуляции в отдельный поток для разгрузки основного цикла:
        self.thread_alg1 = Thread(Algorithm1)
        # В этом случае управление вернёться к основному циклу обработки событий после запуска потока.
        # Это делается для возможности обновления графического интерфейса без ожидания окончания симуляции.

        self.setupUi(self)
        self.init_main_ui()
        self.init_parameter_widgets()
        self.init_graphic_widgets()
        self.to_based_widgets_state()

    def init_main_ui(self):
        self.setWindowIcon(get_ico())
        self.setWindowTitle("Имитационное моделирование систем массового обслуживания")
        self.setMinimumSize(*WINDOW_MINIMUM_SIZE)
        self.setMaximumSize(*WINDOW_MAXIMUM_SIZE)
        self.resize(*get_window_size())

        # Подключение кнопок к вызываемым функциям:
        self.lunch_button.clicked.connect(self.launch)
        self.status_bar.connect_stop_button(self.stop)

        # После завершения алгоритма будут вызваны переданные функции:
        self.thread_alg1.finished.connect(lambda: self.process_results())
        self.thread_alg1.finished.connect(lambda: self.to_based_widgets_state())

        # Подключение функции для возможности её вызова из потока по сигналу:
        self.thread_alg1.change_value.connect(self.status_bar.set_progress_value)

    def init_parameter_widgets(self):
        # Инициализация виджетов для ввода параметров:
        for parameter_key in ALGORITHM_1_SETTINGS["PARAMETERS_KEYS"]:
            self.parameter_widgets[parameter_key] = Parameter(
                ALGORITHM_1_SETTINGS["PARAMETERS_EDIT_SETTINGS"][parameter_key],
                ALGORITHM_1_SETTINGS["PARAMETERS_LABELS_SETTINGS"][parameter_key],
                self.verticalLayout_parameters
            )

    def init_graphic_widgets(self):
        # Инициализация виджетов для вывода графиков:
        for key in ALGORITHM_1_SETTINGS["GRAPHICS_WIDGETS_KEYS"]:
            self.graphic_widgets[key] = Graphic(
                ALGORITHM_1_SETTINGS["GRAPHICS_WIDGETS_SETTINGS"][key],
                ALGORITHM_1_SETTINGS["GRAPHICS_WIDGETS_LAYOUT_SETTINGS"][key],
                self.verticalLayout_graphic_widgets
            )

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

    def process_results(self):
        results = self.thread_alg1.results
        if results["status"] == TERMITE:
            self.status_bar.update_message("Обработка отменена")
            self.to_based_widgets_state()
        else:
            work_time = results['algorithm_working_time']
            work_time_for_status = round(work_time, 3) if work_time >= 0.01 else 0.01
            self.status_bar.update_message(f"Обработка завершена за {work_time_for_status} сек. ")
            self.update_graphic_widgets(results["data_for_plotting"])

    def clear_graphic_widgets(self):
        for graphic_widget in self.graphic_widgets.values():
            graphic_widget.clear()

    def update_graphic_widgets(self, collected_data):
        self.clear_graphic_widgets()
        for graphic_key in collected_data.keys():
            plot_settings = ALGORITHM_1_SETTINGS["GRAPHICS_PLOT_SETTINGS"][graphic_key]
            widget_key = plot_settings["plot_widget_key"]
            self.graphic_widgets[widget_key].add_graphic(
                collected_data[graphic_key], plot_settings)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Enter - 1:
            self.launch()
        # if event.key() == QtCore.Qt.Key.Key_F5:
        #     for widget in self.graphic_widgets.values():
        #         widget.autoRange()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
