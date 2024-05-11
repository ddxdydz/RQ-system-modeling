from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton, QLabel, QCheckBox

from interface.tab1.tab1_widgets.graphics.AppCountGraphic import AppCountGraphic
from interface.tab1.tab1_widgets.graphics.HandlerStatusGraphic import HandlerStatusGraphic
from interface.tab1.tab1_widgets.graphics.ProbabilityProcessingGraphic import ProbabilityProcessingGraphic
from interface.tab1.tab1_widgets.parameters.ParameterManager import ParameterManager


class Tab1:
    def __init__(self, parameters_installation_layout, graphics_installation_layout):
        self.app_count_graphic = AppCountGraphic(graphics_installation_layout)
        self.handler_status_graphic = HandlerStatusGraphic(graphics_installation_layout)
        self.probability_processing_graphic = ProbabilityProcessingGraphic(graphics_installation_layout)
        self.parameter_manager = ParameterManager(parameters_installation_layout)

        parameters_installation_layout.addWidget(QLabel("Дополнительно: "))

        # Добавляем кнопку для вывода описания:
        self.description_button = QPushButton()
        self.description_button.setText("ОПИСАНИЕ ПАРАМЕТРОВ")
        self.description_button.setMinimumSize(QSize(0, 30))
        parameters_installation_layout.addWidget(self.description_button)

        # CheckBox для возможности не выводить данные на графики
        self.plot_data_checkbox = QCheckBox()
        self.plot_data_checkbox.setText("Строить графики")
        self.plot_data_checkbox.setChecked(True)
        parameters_installation_layout.addWidget(self.plot_data_checkbox)

    def plot_graphics(self, data_for_plotting):
        self.clear_graphics()  # Очищаем пространство от прошлых графиков
        self.app_count_graphic.plot_graphic(data_for_plotting["application_count_graphic"])
        self.handler_status_graphic.plot_graphic(data_for_plotting["handler_status_graphic"])
        self.probability_processing_graphic.plot_probability_distribution_processed_graphic(
            data_for_plotting["probability_distribution_processed"]
        )

    def clear_graphics(self):
        self.app_count_graphic.clear()
        self.handler_status_graphic.clear()
        self.probability_processing_graphic.clear()

    def get_parameters(self) -> dict:
        return self.parameter_manager.get_parameters()
