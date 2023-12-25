from PyQt5.QtWidgets import QSizePolicy
from pyqtgraph import mkBrush, mkPen, PlotWidget

from basic.constants.plotting import GRAPHIC_VIEW_INDENT_MULTIPLIER


class Graphic(PlotWidget):
    def __init__(self, graphic_widget_settings, layout_settings, installation_layout):
        super(Graphic, self).__init__()
        self.settings = graphic_widget_settings
        self.layout_settings = layout_settings
        self.init_widget_ui(installation_layout)
        self.init_graphic_ui()

    def init_widget_ui(self, installation_layout):
        sp = self.sizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Preferred)
        sp.setVerticalPolicy(QSizePolicy.Preferred)
        installation_layout.addWidget(self, self.layout_settings["stretch"])

    def init_graphic_ui(self):
        self.addLegend()
        self.setBackground(self.settings["background_style"])
        self.setTitle(self.settings["title"], **self.settings["styles_title"])
        self.setLabel("left", self.settings["left_label"], **self.settings["styles_labels"])
        self.setLabel("bottom", self.settings["bottom_label"], **self.settings["styles_labels"])
        ay = self.getAxis('left')
        ay.setWidth(w=self.settings["indent_left_axis_px"])
        self.showGrid(**self.settings["show_grid"])
        self.setMouseEnabled(**self.settings["set_mouse_enabled"])
        self.getPlotItem().setMenuEnabled(False)
        self.hideButtons()

    def get_max_value(self, data_for_plotting):
        if self.settings["maximum_value"] is None:
            return max(data_for_plotting["value"])
        return self.settings["maximum_value"]

    def update_ticks_text(self, data_for_plotting):
        max_value = self.get_max_value(data_for_plotting)
        ay = self.getAxis('left')
        ticks_count = self.settings["max_count_of_left_ticks"]
        step = max_value // ticks_count if max_value > ticks_count else 1
        ticks = [i for i in range(0, max_value + 1, step)]
        ay.setTicks([[(v, str(v)) for v in ticks]])

    def update_range(self, data_for_plotting, graphic_plot_settings):
        total_range = data_for_plotting["time"][-1] - data_for_plotting["time"][0]
        min_x_in_range = data_for_plotting["time"][0] - total_range * GRAPHIC_VIEW_INDENT_MULTIPLIER
        max_x_in_range = data_for_plotting["time"][-1] + total_range * GRAPHIC_VIEW_INDENT_MULTIPLIER
        self.setXRange(min_x_in_range, max_x_in_range)
        # self.plotItem.vb.setLimits(xMin=min_x_in_range, xMax=max_x_in_range)
        if graphic_plot_settings["range_oy"] is not None:
            self.setYRange(
                graphic_plot_settings["range_oy"]["min"],
                graphic_plot_settings["range_oy"]["max"]
            )

    def add_graphic(self, data_for_plotting, graphic_plot_settings):
        graphic_type = graphic_plot_settings["type"]

        # Удаляем последнее значение из данных для графиков для возможности отображения гистограм
        # Это последнее значение равняется изначальному значению и не влияет на общий результат
        if graphic_type == "histogram":
            data_for_plotting["value"].pop(-1)

        self.plot(
            data_for_plotting["time"],
            data_for_plotting["value"],
            stepMode="center" if graphic_type == "histogram" else None,
            fillLevel=graphic_plot_settings["fillLevel"],
            fillOutline=True,
            brush=mkBrush(**graphic_plot_settings["brush_parameters"]),
            pen=mkPen(**graphic_plot_settings["pen_parameters"]),
        )
        self.update_ticks_text(data_for_plotting)
        self.update_range(data_for_plotting, graphic_plot_settings)
