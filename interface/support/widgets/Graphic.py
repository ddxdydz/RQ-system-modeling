from math import ceil
from PyQt5.QtWidgets import QSizePolicy
from pyqtgraph import mkBrush, mkPen, PlotWidget

from basic.constants.plotting import GRAPHIC_VIEW_INDENT_MULTIPLIER, COLUMNAR_GRAPHIC_WIDTH_INDENT


class Graphic(PlotWidget):
    def __init__(self, graphic_widget_settings, layout_settings, installation_layout):
        super(Graphic, self).__init__()

        # Настройки по умолчанию:
        self.settings = {
            "title": "Название",
            "styles_title": {"color": "b", "font-size": "30px"},
            "left_label": "Подпись слева",
            "bottom_label": None,
            "styles_labels": {"color": "#f00", "font-size": "11px"},
            "max_count_of_left_ticks": 8,
            "ndigits_round_left_ticks": 0,  # если 0, то округляется до целого вверх
            "indent_left_axis_px": 35,
            "maximum_value": None,
            "background_style": "w",
            "show_grid": {"x": True, "y": True},
            "set_mouse_enabled": {"x": False, "y": False},
            "range_oy": (0, None)
        }

        # Изменение настроик по умолчанию:
        self.settings.update(graphic_widget_settings)
        self.layout_settings.update(layout_settings)

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

    @staticmethod
    def compress_data(x_data, y_data, new_count_ticks):
        if len(x_data) > new_count_ticks:
            new_x_data, new_y_data = [0], [0]

            step = (x_data[-1] - x_data[0]) / new_count_ticks

            last_x, last_y = 0, 0
            current_new_x = step
            current_square_sum = 0

            for x, y in zip(x_data, y_data):
                if x > current_new_x:

                    while x > current_new_x:

                        current_square_sum += last_y * (current_new_x - last_x)

                        new_x_data.append(current_new_x)
                        new_y_data.append(current_square_sum / step)

                        current_square_sum = 0

                        last_x = current_new_x
                        current_new_x += step

                    current_square_sum = y * (x - last_x)

                else:
                    current_square_sum += last_y * (x - last_x)

                last_x, last_y = x, y
            return new_x_data, new_y_data

        return x_data, y_data

    def get_max_value_y(self, y_data):
        if self.settings["maximum_value"] is None:
            return max(y_data)
        return self.settings["maximum_value"]

    def update_left_ticks_text(self, y_data):
        min_value, max_value = 0, self.get_max_value_y(y_data)

        ay = self.getAxis('left')
        ticks_count = self.settings["max_count_of_left_ticks"]
        ndigits = self.settings["ndigits_round_left_ticks"]

        step = max_value / ticks_count
        if step == 0:
            step = 1
        elif ndigits == 0:
            step = ceil(step)
        else:
            step = round(step, ndigits)

        ticks = [min_value]
        while ticks[-1] < max_value:
            next_tick = ticks[-1] + step
            if ndigits == 0:
                next_tick = ceil(next_tick)
            else:
                next_tick = round(next_tick, ndigits)
            ticks.append(next_tick)
        ay.setTicks([[(v, str(v)) for v in ticks]])

    def set_visual_range_x(self, x_data):
        min_x, max_x = x_data[0], x_data[-1]

        total_range = max_x - min_x
        normalized_min_x = min_x - total_range * GRAPHIC_VIEW_INDENT_MULTIPLIER
        normalized_max_x = max_x + total_range * GRAPHIC_VIEW_INDENT_MULTIPLIER

        self.setXRange(normalized_min_x, normalized_max_x)
        # self.plotItem.vb.setLimits(xMin=min_x_in_range, xMax=max_x_in_range)

    def set_visual_range_y(self, y_data):
        min_y, max_y = self.settings["range_oy"]
        if min_y is None:
            min_y = min(y_data)
        if max_y is None:
            max_y = self.get_max_value_y(y_data)

        total_range = max_y - min_y
        normalized_min_y = min_y - total_range * GRAPHIC_VIEW_INDENT_MULTIPLIER
        normalized_max_y = max_y + total_range * GRAPHIC_VIEW_INDENT_MULTIPLIER

        self.setYRange(normalized_min_y, normalized_max_y)

    def add_graphic(self, x_data, y_data, graphic_plot_settings, step_mode=None):
        self.plot(
            x_data, y_data,
            stepMode=step_mode,
            fillLevel=graphic_plot_settings["fillLevel"],
            fillOutline=True,
            brush=mkBrush(**graphic_plot_settings["brush_parameters"]),
            pen=mkPen(**graphic_plot_settings["pen_parameters"]),
        )

    def add_histogram(self, x_data, y_data, graphic_plot_settings):
        # Удаляем последнее значение из данных для графиков для возможности отображения гистограм
        # Это последнее значение равняется изначальному значению и не влияет на общий результат
        y_data = y_data.copy()
        y_data.pop(-1)

        self.add_graphic(
            x_data, y_data,
            graphic_plot_settings, step_mode="center"
        )
        self.update_left_ticks_text(y_data=y_data)
        self.set_visual_range_x(x_data=x_data)
        self.set_visual_range_y(y_data=y_data)

    def add_line_graph(self, x_data, y_data, graphic_plot_settings):
        self.add_graphic(
            x_data, y_data,
            graphic_plot_settings
        )
        self.update_left_ticks_text(y_data=y_data)
        self.set_visual_range_x(x_data=x_data)
        self.set_visual_range_y(y_data=y_data)

    def add_columnar_diagram(self, x_data, y_data, graphic_plot_settings):
        x_modified_data, y_modified_data = [], []
        for count in x_data:
            x_modified_data.append(count - COLUMNAR_GRAPHIC_WIDTH_INDENT)
            x_modified_data.append(count + COLUMNAR_GRAPHIC_WIDTH_INDENT)
        for value in y_data:
            y_modified_data.append(value)
            y_modified_data.append(0)

        if not y_modified_data:  # если данных для вывода нет
            return

        y_modified_data.pop(-1)

        self.add_graphic(
            x_modified_data, y_modified_data,
            graphic_plot_settings, step_mode="center"
        )
        self.update_left_ticks_text(y_data=y_modified_data)
        self.set_visual_range_x(x_data=x_modified_data)
        ax = self.getAxis('bottom')
        ax.setTicks([[(v, str(v)) for v in x_data]])
        self.set_visual_range_y(y_data=y_modified_data)
