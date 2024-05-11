import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox

# Прямое подключение скрытых зависимостей для избежания неполной сборки exe-файла через pyinstaller:
# import pyqtgraph.graphicsItems.ViewBox.axisCtrlTemplate_pyqt5
# import pyqtgraph.graphicsItems.PlotItem.plotConfigTemplate_pyqt5
# import pyqtgraph.imageview.ImageViewTemplate_pyqt5

from basic.constants.error_indexes import *
from basic.constants.window_settings import *
from basic.errors.FullnessError import FullnessError
from basic.errors.MatrixNestingError import MatrixNestingError
from basic.errors.MatrixSizeError import MatrixSizeError
from basic.errors.RangeError import RangeError
from interface.ui.MainWindow import Ui_MainWindow
from interface.support.widgets.StatusBar import StatusBar
from interface.support.controllers.Thread import Thread
from interface.support.get_window_size import get_window_size
from interface.support.get_ico_from_code import get_ico
from interface.tab1.Tab1 import Tab1
from interface.tab2.Tab2 import Tab2
from interface.tab3.Tab3 import Tab3
from algorithms.AlgorithmTab1 import AlgorithmTab1
from algorithms.AlgorithmTab2 import AlgorithmTab2
from algorithms.AlgorithmTab3 import AlgorithmTab3


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Выносим процесс вычисления результатов алгоритма в отдельный поток для разгрузки основного цикла:
        self.thread_alg1 = Thread(AlgorithmTab1)
        self.thread_alg2 = Thread(AlgorithmTab2)
        self.thread_alg3 = Thread(AlgorithmTab3)
        # В этом случае управление вернёться к основному циклу обработки событий после запуска потока.
        # Это делается для возможности обновления графического интерфейса без ожидания окончания симуляции.

        self.setupUi(self)

        self.tab1 = Tab1(self.layout_parameters_tab1, self.layout_graphics_tab1)
        self.tab2 = Tab2(self.layout_parameters_tab2, self.layout_graphics_tab2)
        self.tab3 = Tab3(self.layout_parameters_tab3, self.layout_graphics_tab3)
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
        self.launch_button_tab3.clicked.connect(self.launch)
        self.tab2.file_button.clicked.connect(lambda: self.print_to_file(2))
        self.tab3.file_button.clicked.connect(lambda: self.print_to_file(3))
        self.tab1.description_button.clicked.connect(lambda: self.show_message_box(
            self.tab1.parameter_manager.get_description()))
        self.tab2.description_button.clicked.connect(lambda: self.show_message_box(
            self.tab2.parameter_manager.get_description()))
        self.tab3.description_button.clicked.connect(lambda: self.show_message_box(
            self.tab3.parameter_manager.get_description()))
        self.status_bar.connect_stop_button(self.stop)

        # После завершения алгоритма будут вызваны переданные функции:
        self.thread_alg1.finished.connect(lambda: self.to_based_state())
        self.thread_alg1.finished.connect(lambda: self.process_results(1))
        self.thread_alg2.finished.connect(lambda: self.to_based_state())
        self.thread_alg2.finished.connect(lambda: self.process_results(2))
        self.thread_alg3.finished.connect(lambda: self.to_based_state())
        self.thread_alg3.finished.connect(lambda: self.process_results(3))

        # Подключение функции для возможности её вызова из потока по сигналу:
        self.thread_alg1.change_value.connect(self.status_bar.set_progress_value)
        self.thread_alg2.change_value.connect(self.status_bar.set_progress_value)
        self.thread_alg3.change_value.connect(self.status_bar.set_progress_value)

    def launch(self):
        try:
            self.stop()
            self.status_bar.update_message("Обработка...")
            self.status_bar.show_progress()
            if self.tabWidget.currentIndex() == 0:
                self.launch_button_tab1.setEnabled(False)
                self.thread_alg1.set_parameters(self.tab1.get_parameters())
                self.thread_alg1.start()
            elif self.tabWidget.currentIndex() == 1:
                self.launch_button_tab2.setEnabled(False)
                self.thread_alg2.set_parameters(self.tab2.get_parameters())
                self.thread_alg2.start()
            else:
                self.launch_button_tab3.setEnabled(False)
                self.thread_alg3.set_parameters(self.tab3.get_parameters())
                self.thread_alg3.start()
        except ValueError:
            self.status_bar.update_message("Ошибка: Некорректные значения")
            self.to_based_state()
        except FullnessError:
            self.status_bar.update_message("Ошибка: Некоторые параметры без значения")
            self.to_based_state()
        except RangeError:
            self.status_bar.update_message("Ошибка: Некорректный диапазон")
            self.to_based_state()
        except MatrixSizeError as m_er:
            self.status_bar.update_message(f"Ошибка: {m_er}")
            self.to_based_state()
        except MatrixNestingError:
            self.status_bar.update_message("Ошибка: Неверная вложенность скобок")
            self.to_based_state()

    def stop(self):
        self.thread_alg1.terminate()
        self.thread_alg2.terminate()
        self.thread_alg3.terminate()
        self.to_based_state()

    def process_results(self, alg_num):
        if alg_num == 1:
            results = self.thread_alg1.results
        elif alg_num == 2:
            results = self.thread_alg2.results
        else:
            results = self.thread_alg3.results

        if results["status"] == TERMITE:
            self.status_bar.update_message("Обработка отменена")
            self.to_based_state()
        else:
            work_time = results['algorithm_working_time']
            work_time_for_status = round(work_time, 3) if work_time >= 0.01 else 0.01
            self.status_bar.update_message(f"Обработка завершена за {work_time_for_status} сек. ")
            if alg_num == 1 and self.tab1.plot_data_checkbox.isChecked():
                self.tab1.plot_graphics(results["data_for_plotting"])
            elif alg_num == 2 and self.tab2.plot_data_checkbox.isChecked():
                self.tab2.plot_graphics(results["data_for_plotting"])
            elif alg_num == 3 and self.tab3.plot_data_checkbox.isChecked():
                self.tab3.plot_graphics(results["data_for_plotting"])

    def to_based_state(self):
        self.launch_button_tab1.setEnabled(True)
        self.launch_button_tab2.setEnabled(True)
        self.launch_button_tab3.setEnabled(True)
        self.status_bar.hide_progress()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Enter - 1:
            self.launch()

    def print_to_file(self, alg_num):
        file = QtWidgets.QFileDialog.getSaveFileName(
            parent=None, caption="Выберите место для сохранения файла",
            directory="c:\\",
            filter="All (*);;txt (*.txt *.txt)",
            initialFilter="txt (*.txt *.txt)"
        )
        file_name = file[0]

        if file_name != "":

            if alg_num == 2:
                results = self.thread_alg2.results
            else:
                results = self.thread_alg3.results

            with open(file_name, mode="wt", encoding="UTF-8") as file:
                if 'data_for_plotting' in results:
                    for v in results["data_for_plotting"]["probability_distribution_orbit"]["values"]:
                        file.write(f"{v}\n")

    def show_message_box(self, message: str):
        msg = QMessageBox()
        msg.setWindowTitle("Описание")
        msg.setText(message)
        msg.show()
        msg.exec_()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
