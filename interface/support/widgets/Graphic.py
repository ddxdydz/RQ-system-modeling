from PyQt5.QtWidgets import QSizePolicy
from pyqtgraph import mkBrush, mkPen, PlotWidget

from basic.constants.plotting import GRAPHIC_VIEW_INDENT_MULTIPLIER, COLUMNAR_GRAPHIC_WIDTH_INDENT


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

    def update_left_ticks_text(self, y_data):
        max_value = self.settings["maximum_value"]
        if max_value is None:
            max_value = int(max(y_data)) + 1
        ay = self.getAxis('left')
        ticks_count = self.settings["max_count_of_left_ticks"]
        step = max_value // ticks_count if max_value > ticks_count else 1
        ticks = [i for i in range(0, max_value + 1, step)]
        ay.setTicks([[(v, str(v)) for v in ticks]])

    def update_range(self, x_data):
        total_range = x_data[-1] - x_data[0]
        min_x_in_range = x_data[0] - total_range * GRAPHIC_VIEW_INDENT_MULTIPLIER
        max_x_in_range = x_data[-1] + total_range * GRAPHIC_VIEW_INDENT_MULTIPLIER
        self.setXRange(min_x_in_range, max_x_in_range)
        # self.plotItem.vb.setLimits(xMin=min_x_in_range, xMax=max_x_in_range)
        if self.settings["range_oy"] is not None:
            self.setYRange(*self.settings["range_oy"])

    def add_graphic(self, x_data, y_data, graphic_plot_settings, step_mode=None):
        self.plot(
            x_data, y_data,
            stepMode=step_mode,
            fillLevel=graphic_plot_settings["fillLevel"],
            fillOutline=True,
            brush=mkBrush(**graphic_plot_settings["brush_parameters"]),
            pen=mkPen(**graphic_plot_settings["pen_parameters"]),
        )

    def add_histogram(self, data_for_plotting, graphic_plot_settings):
        # Удаляем последнее значение из данных для графиков для возможности отображения гистограм
        # Это последнее значение равняется изначальному значению и не влияет на общий результат
        value = data_for_plotting["value"].copy()
        value.pop(-1)

        self.add_graphic(
            data_for_plotting["time"], value,
            graphic_plot_settings, step_mode="center"
        )
        self.update_left_ticks_text(y_data=value)
        self.update_range(x_data=data_for_plotting["time"])

    def add_line_graph(self, data_for_plotting, graphic_plot_settings):
        self.add_graphic(
            data_for_plotting["time"], data_for_plotting["value"],
            graphic_plot_settings
        )
        self.update_left_ticks_text(y_data=data_for_plotting["value"])
        self.update_range(x_data=data_for_plotting["time"])

    def add_columnar_diagram(self, data_for_plotting, graphic_plot_settings):
        x_data, y_data = [], []
        for count in data_for_plotting["counts"]:
            x_data.append(count - COLUMNAR_GRAPHIC_WIDTH_INDENT)
            x_data.append(count + COLUMNAR_GRAPHIC_WIDTH_INDENT)
        for value in data_for_plotting["values"]:
            y_data.append(value)
            y_data.append(0)
        y_data.pop(-1)

        self.add_graphic(
            x_data, y_data,
            graphic_plot_settings, step_mode="center"
        )
        self.update_left_ticks_text(y_data=y_data)
        self.update_range(x_data=x_data)
        ax = self.getAxis('bottom')
        ax.setTicks([[(v, str(v)) for v in data_for_plotting["counts"]]])
