from interface.support.widgets.Graphic import Graphic


class HandlerStatusGraphic(Graphic):
    def __init__(self, installation_layout):
        self.graphic_widget_settings = {
            "title": "Изменение статуса обработчика",
            "styles_title": {"color": "b", "font-size": "8pt"},
            "left_label": "Статус",
            "bottom_label": None,
            "styles_labels": {"color": "#f00", "font-size": "8pt"},
            "max_count_of_left_ticks": 15,
            "indent_left_axis_px": 35,
            "maximum_value": 2,
            "background_style": "w",
            "show_grid": {"x": True, "y": True},
            "set_mouse_enabled": {"x": False, "y": False}
        }
        self.graphic_plot_settings = {
            "brush_parameters": {"color": (255, 0, 0, 80)},
            "pen_parameters": {"color": (0, 0, 0)},
            "fillLevel": 0,
            "type": "histogram",
            "range_oy": {"min": -0.05, "max": 2.05}
        }
        self.layout_settings = {"stretch": 3}
        super().__init__(self.graphic_widget_settings, self.layout_settings, installation_layout)

    def plot_graphic(self, data_for_plotting):
        super().add_graphic(data_for_plotting, self.graphic_plot_settings)
