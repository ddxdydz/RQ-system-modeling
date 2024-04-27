from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLineEdit, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy

from basic.errors.FullnessError import FullnessError
from basic.errors.RangeError import RangeError


class Parameter(QLineEdit):
    def __init__(self, label_text, installation_layout, is_oneline=True):
        super(Parameter, self).__init__()
        self.parameter_label_widget = QLabel(label_text)
        if is_oneline:
            self.init_widget_ui_oneline(installation_layout)
        else:
            self.init_widget_ui_twoline(installation_layout)

    def init_widget_ui_oneline(self, installation_layout):
        # in one lines
        self.parameter_label_widget.setFont(QFont('MS Shell Dlg 2', 10))
        parameter_layout = QHBoxLayout()
        parameter_layout.addWidget(self.parameter_label_widget)
        parameter_layout.addWidget(self)
        installation_layout.addLayout(parameter_layout)

    def init_widget_ui_twoline(self, installation_layout):
        # in two lines
        installation_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Fixed, QSizePolicy.Fixed))
        installation_layout.addWidget(self.parameter_label_widget)
        installation_layout.addWidget(self)

    def check_parameters_fullness(self):
        if self.text().strip() == "":
            raise FullnessError

    @staticmethod
    def check_parameters_range(checking_value, min_value, max_value):
        if not ((checking_value > min_value) and (checking_value <= max_value)):
            raise RangeError
