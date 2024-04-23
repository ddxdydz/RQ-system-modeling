from interface.support.widgets.Graphic import Graphic


class ProbabilityOrbitGraphic(Graphic):
    def __init__(self, installation_layout):
        self.graphic_widget_settings = {
            "title": "Распределение вероятностей нахождения на орбите",
            "styles_title": {"color": "b", "font-size": "8pt"},
            "left_label": "Вероятность (%)",
            "bottom_label":  "Число заявок на орбите",
            "styles_labels": {"color": "#f00", "font-size": "8pt"},
            "max_count_of_left_ticks": 2,
            "indent_left_axis_px": 35,
            "maximum_value": None,
            "background_style": "w",
            "show_grid": {"x": True, "y": True},
            "set_mouse_enabled": {"x": False, "y": False},
            "range_oy": None
        }
        self.graphic_plot_settings = {
            "brush_parameters": {"color": (0, 0, 255, 80)},
            "pen_parameters": {"color": (0, 0, 0)},
            "fillLevel": 0
        }
        self.layout_settings = {"stretch": 4}
        super().__init__(self.graphic_widget_settings, self.layout_settings, installation_layout)

    def plot_graphic(self, data_for_plotting):
        self.add_columnar_diagram(data_for_plotting, self.graphic_plot_settings)
