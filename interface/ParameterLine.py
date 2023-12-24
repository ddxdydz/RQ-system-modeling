from PyQt5.QtWidgets import QLineEdit

from basic.errors.FullnessError import FullnessError
from basic.errors.RangeError import RangeError


class ParameterLine(QLineEdit):
    def __init__(self, parameter_widget_settings):
        super(ParameterLine, self).__init__()
        self.settings = parameter_widget_settings
        self.init_widget_ui()

    def init_widget_ui(self):
        self.setText(str(self.settings["default_value"]))
        # if self.is_one_line():
        #     self.setFixedWidth(100)
        #     self.setFixedHeight(20)
        # else:
        #     self.setFixedWidth(133)
        #     self.setFixedHeight(20)

    def is_one_line(self):
        return self.settings["one_line_label"]

    def check_parameters_fullness(self):
        if self.text().strip() == "":
            raise FullnessError

    def check_parameters_range(self, checking_value):
        if not ((checking_value > self.settings["range"]["min"]) and
                (checking_value <= self.settings["range"]["max"])):
            raise RangeError

    def get_value(self):
        self.check_parameters_fullness()
        value_type = self.settings["type"]
        value = value_type(self.text().replace(',', '.'))
        self.check_parameters_range(value)
        return value
