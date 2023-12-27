from PyQt5.QtWidgets import QLineEdit

from basic.errors.FullnessError import FullnessError
from basic.errors.RangeError import RangeError


class Parameter(QLineEdit):
    def __init__(self, range_min=0, range_max=100000, default=0, is_int=False):
        super(Parameter, self).__init__()

        self.range_min, self.range_max = range_min, range_max
        self.default = default
        self.is_int = is_int

        self.setText(str(self.default))

    def check_parameters_fullness(self):
        if self.text().strip() == "":
            raise FullnessError

    def check_parameters_range(self, checking_value):
        if not ((checking_value > self.range_min) and (checking_value <= self.range_max)):
            raise RangeError

    def get_value(self):
        self.check_parameters_fullness()
        value = float(self.text().replace(',', '.'))
        if self.is_int:
            value = int(value)
        self.check_parameters_range(value)
        return value
