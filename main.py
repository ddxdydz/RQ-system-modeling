import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication

# Прямое подключение скрытых зависимостей для избежания неполной сборки exe-файла через pyinstaller:
import pyqtgraph.graphicsItems.ViewBox.axisCtrlTemplate_pyqt5
import pyqtgraph.graphicsItems.PlotItem.plotConfigTemplate_pyqt5
import pyqtgraph.imageview.ImageViewTemplate_pyqt5

from basic.constants.error_indexes import *
from basic.constants.window_settings import *
from basic.errors.FullnessError import FullnessError
from basic.errors.RangeError import RangeError
from interface.ui.MainWindow import Ui_MainWindow
from interface.support.widgets.StatusBar import StatusBar
from interface.support.widgets.Thread import Thread
from interface.support.get_window_size import get_window_size
from interface.support.get_ico_from_code import get_ico
from interface.tab1.Tab1 import Tab1
from interface.tab2.Tab2 import Tab2
from algorithms.AlgorithmS1 import AlgorithmS1
from algorithms.AlgorithmS2 import AlgorithmS2


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Выносим процесс вычисления результатов алгоритма в отдельный поток для разгрузки основного цикла:
        self.thread_alg1 = Thread(AlgorithmS1)
        self.thread_alg2 = Thread(AlgorithmS2)
        # В этом случае управление вернёться к основному циклу обработки событий после запуска потока.
        # Это делается для возможности обновления графического интерфейса без ожидания окончания симуляции.

        self.setupUi(self)

        self.tab1 = Tab1(self.layout_parameters_tab1, self.layout_graphics_tab1)
        self.tab2 = Tab2(self.layout_parameters_tab2, self.layout_graphics_tab2)
        self.status_bar = StatusBar(self.statusBar())

        self.init_main_ui()
        self.to_based_state()

    def init_main_ui(self):
        self.setWindowIcon(get_ico())
        self.setWindowTitle("Имитационное моделирование систем массового обслуживания")
        self.setMinimumSize(*WINDOW_MINIMUM_SIZE)
        self.setMaximumSize(*WINDOW_MAXIMUM_SIZE)
        self.resize(*get_window_size())

        # Подключение кнопок к вызываемым функциям:
        self.launch_button_tab1.clicked.connect(self.launch)
        self.launch_button_tab2.clicked.connect(self.launch)
        self.status_bar.connect_stop_button(self.stop)

        # После завершения алгоритма будут вызваны переданные функции:
        self.thread_alg1.finished.connect(lambda: self.to_based_state())
        self.thread_alg1.finished.connect(lambda: self.process_results(1))
        self.thread_alg2.finished.connect(lambda: self.to_based_state())
        self.thread_alg2.finished.connect(lambda: self.process_results(2))

        # Подключение функции для возможности её вызова из потока по сигналу:
        self.thread_alg1.change_value.connect(self.status_bar.set_progress_value)
        self.thread_alg2.change_value.connect(self.status_bar.set_progress_value)

    def launch(self):
        try:
            self.stop()
            self.status_bar.update_message("Обработка...")
            self.status_bar.show_progress()
            if self.tabWidget.currentIndex() == 0:
                self.launch_button_tab1.setEnabled(False)
                self.thread_alg1.set_parameters(self.tab1.get_parameters())
                self.thread_alg1.start()
            else:
                self.launch_button_tab2.setEnabled(False)
                self.thread_alg2.set_parameters(self.tab2.get_parameters())
                self.thread_alg2.start()
        except ValueError:
            self.status_bar.update_message("Ошибка: Некорректные значения")
            self.to_based_state()
        except FullnessError:
            self.status_bar.update_message("Ошибка: Некоторые параметры без значения")
            self.to_based_state()
        except RangeError:
            self.status_bar.update_message("Ошибка: Некорректный диапазон")
            self.to_based_state()

    def stop(self):
        self.thread_alg1.terminate()
        self.thread_alg2.terminate()
        self.to_based_state()

    def process_results(self, alg_num):
        results = self.thread_alg1.results if alg_num == 1 else self.thread_alg2.results
        if results["status"] == TERMITE:
            self.status_bar.update_message("Обработка отменена")
            self.to_based_state()
        else:
            work_time = results['algorithm_working_time']
            work_time_for_status = round(work_time, 3) if work_time >= 0.01 else 0.01
            self.status_bar.update_message(f"Обработка завершена за {work_time_for_status} сек. ")
            if alg_num == 1:
                self.tab1.plot_graphics(results["data_for_plotting"])
            elif alg_num == 2:
                self.tab2.plot_graphics(results["data_for_plotting"])

    def to_based_state(self):
        self.launch_button_tab1.setEnabled(True)
        self.launch_button_tab2.setEnabled(True)
        self.status_bar.hide_progress()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Enter - 1:
            self.launch()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
