from basic.constants.plotting import PLOTTING_COUNT_DATA_LIMIT
from interface.support.widgets.Graphic import Graphic


class ProbabilityProcessingGraphic(Graphic):
    def __init__(self, installation_layout):
        self.graphic_widget_settings = {
            "title": "Распределение вероятностей занятости обработчика",
            "styles_title": {"color": "b", "font-size": "8pt"},
            "left_label": "Вероятность",
            "bottom_label": "Время (секунды)",
            "styles_labels": {"color": "#f00", "font-size": "8pt"},
            "max_count_of_left_ticks": 2,
            "ndigits_round_left_ticks": 1,  # если 0, то округляется до целого вверх
            "indent_left_axis_px": 35,
            "maximum_value": 1,
            "background_style": "w",
            "show_grid": {"x": True, "y": True},
            "set_mouse_enabled": {"x": False, "y": False},
            "range_oy": (0, 1)
        }
        self.graphic_plot_free_settings = {
            "brush_parameters": {"color": (255, 0, 0, 0)},
            "pen_parameters": {"color": (0, 0, 255, 200), "width": 1},
            "fillLevel": None
        },

        self.graphic_plot_processed_settings = {
            "brush_parameters": {"color": (0, 0, 255, 0)},
            "pen_parameters": {"color": (255, 0, 0, 200), "width": 1},
            "fillLevel": None
        }
        self.layout_settings = {"stretch": 4}
        super().__init__(self.graphic_widget_settings, self.layout_settings, installation_layout)

    def plot_probability_distribution_free_graphic(self, data_for_plotting, compress_data=True):
        data_x, data_y = data_for_plotting["time"], data_for_plotting["value"]
        if compress_data:
            data_x, data_y = Graphic.compress_data(data_x, data_y, PLOTTING_COUNT_DATA_LIMIT)
        self.add_line_graph(data_x, data_y, self.graphic_plot_free_settings)

    def plot_probability_distribution_processed_graphic(self, data_for_plotting, compress_data=True):
        data_x, data_y = data_for_plotting["time"], data_for_plotting["value"]
        if compress_data:
            data_x, data_y = Graphic.compress_data(data_x, data_y, PLOTTING_COUNT_DATA_LIMIT)
        self.add_line_graph(data_x, data_y, self.graphic_plot_processed_settings)
