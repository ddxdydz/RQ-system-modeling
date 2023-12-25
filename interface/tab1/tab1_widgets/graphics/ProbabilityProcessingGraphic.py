from interface.support.widgets.Graphic import Graphic


class ProbabilityProcessingGraphic(Graphic):
    def __init__(self, installation_layout):
        self.graphic_widget_settings = {
            "title": "Распределение вероятностей занятости обработчика",
            "styles_title": {"color": "b", "font-size": "8pt"},
            "left_label": "Вероятность (%)",
            "bottom_label": "Время (секунды)",
            "styles_labels": {"color": "#f00", "font-size": "8pt"},
            "max_count_of_left_ticks": 2,
            "indent_left_axis_px": 35,
            "maximum_value": 100,
            "background_style": "w",
            "show_grid": {"x": True, "y": True},
            "set_mouse_enabled": {"x": False, "y": False}
        }
        self.graphic_plot_free_settings = {
            "brush_parameters": {"color": (255, 0, 0, 0)},
            "pen_parameters": {"color": (0, 0, 255, 200), "width": 1},
            "fillLevel": None,
            "type": "not_histogram",
            "range_oy": {"min": 0, "max": 100}
        },

        self.graphic_plot_processed_settings = {
            "plot_widget_key": "probability_distribution_graphic_widget",
            "brush_parameters": {"color": (0, 0, 255, 0)},
            "pen_parameters": {"color": (255, 0, 0, 200), "width": 1},
            "fillLevel": None,
            "type": "not_histogram",
            "range_oy": {"min": 0, "max": 100}
        }
        self.layout_settings = {"stretch": 4}
        super().__init__(self.graphic_widget_settings, self.layout_settings, installation_layout)

    def plot_probability_distribution_free_graphic(self, data_for_plotting):
        super().add_graphic(data_for_plotting, self.graphic_plot_free_settings)

    def plot_probability_distribution_processed_graphic(self, data_for_plotting):
        super().add_graphic(data_for_plotting, self.graphic_plot_processed_settings)
