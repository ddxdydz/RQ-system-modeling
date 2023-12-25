from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QHBoxLayout

from interface.support.widgets.Parameter import Parameter


class ParameterType1:
    def __init__(self, label_text, installation_layout, range_min=0, range_max=100000, default=0, is_int=False):
        self.parameter_edit_widget = Parameter(range_min, range_max, default, is_int)
        self.parameter_label_widget = QLabel(label_text)
        self.init_widget_ui(installation_layout)

    def init_widget_ui(self, installation_layout):
        # in one lines
        self.parameter_label_widget.setFont(QFont('MS Shell Dlg 2', 10))
        parameter_layout = QHBoxLayout()
        parameter_layout.addWidget(self.parameter_label_widget)
        parameter_layout.addWidget(self.parameter_edit_widget)
        installation_layout.addLayout(parameter_layout)

    def get_value(self):
        return self.parameter_edit_widget.get_value()
