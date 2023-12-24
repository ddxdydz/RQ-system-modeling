from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QSpacerItem, QSizePolicy, QHBoxLayout

from interface.ParameterLine import ParameterLine


class Parameter:
    def __init__(self, parameter_edit_settings, parameter_label_settings, installation_layout):
        self.parameter_edit_settings = parameter_edit_settings
        self.parameter_label_settings = parameter_label_settings
        self.parameter_edit_widget = ParameterLine(parameter_edit_settings)
        self.parameter_label_widget = QLabel()
        self.init_widget_ui(installation_layout)

    def init_widget_ui(self, installation_layout):
        self.parameter_label_widget.setText(self.parameter_label_settings["text"])
        if self.parameter_edit_widget.is_one_line():
            self.parameter_label_widget.setFont(QFont('MS Shell Dlg 2', 10))
            parameter_layout = QHBoxLayout()
            parameter_layout.addWidget(self.parameter_label_widget)
            parameter_layout.addWidget(self.parameter_edit_widget)
            installation_layout.addLayout(parameter_layout)
        else:
            installation_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Fixed, QSizePolicy.Fixed))
            installation_layout.addWidget(self.parameter_label_widget)
            installation_layout.addWidget(self.parameter_edit_widget)

    def get_value(self):
        return self.parameter_edit_widget.get_value()
