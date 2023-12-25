from interface.tab1.tab1_widgets.graphics.AppCountGraphic import AppCountGraphic
from interface.tab2.tab2_widgets.graphics.HandlerStatusGraphic import HandlerStatusGraphic
from interface.tab1.tab1_widgets.graphics.ProbabilityProcessingGraphic import ProbabilityProcessingGraphic
from interface.tab2.tab2_widgets.graphics.ProbabilityOrbitGraphic import ProbabilityOrbitGraphic
from interface.tab2.tab2_widgets.parameters.ParameterManager import ParameterManager


class Tab2:
    def __init__(self, parameters_installation_layout, graphics_installation_layout):
        self.app_count_graphic = AppCountGraphic(graphics_installation_layout)
        self.handler_status_graphic = HandlerStatusGraphic(graphics_installation_layout)
        self.probability_processing_graphic = ProbabilityProcessingGraphic(graphics_installation_layout)
        self.probability_orbit_graphic = ProbabilityOrbitGraphic(graphics_installation_layout)
        self.parameter_manager = ParameterManager(parameters_installation_layout)

    def plot_graphics(self, data_for_plotting):
        for time, value in zip(data_for_plotting["handler_status_graphic"]["time"],
                               data_for_plotting["handler_status_graphic"]["value"]):
            print(time, value)

        self.clear_graphics()  # Очищаем пространство от прошлых графиков
        self.app_count_graphic.plot_graphic(data_for_plotting["application_count_graphic"])
        self.handler_status_graphic.plot_graphic(data_for_plotting["handler_status_graphic"])
        self.probability_processing_graphic.plot_probability_distribution_processed_graphic(
            data_for_plotting["probability_distribution_processed"]
        )
        self.probability_orbit_graphic.plot_graphic(
            data_for_plotting["probability_distribution_orbit"]
        )

    def clear_graphics(self):
        self.app_count_graphic.clear()
        self.handler_status_graphic.clear()
        self.probability_processing_graphic.clear()
        self.probability_orbit_graphic.clear()

    def get_parameters(self) -> dict:
        return self.parameter_manager.get_parameters()
