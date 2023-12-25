from PyQt5.QtWidgets import QLabel, QSpacerItem, QSizePolicy

from interface.support.widgets.Parameter import Parameter


class ParameterType2:
    def __init__(self, label_text, installation_layout, range_min=0, range_max=100000, default=0, is_int=False):
        self.parameter_edit_widget = Parameter(range_min, range_max, default, is_int)
        self.parameter_label_widget = QLabel(label_text)
        self.init_widget_ui(installation_layout)

    def init_widget_ui(self, installation_layout):
        # in two lines
        installation_layout.addItem(QSpacerItem(20, 10, QSizePolicy.Fixed, QSizePolicy.Fixed))
        installation_layout.addWidget(self.parameter_label_widget)
        installation_layout.addWidget(self.parameter_edit_widget)

    def get_value(self):
        return self.parameter_edit_widget.get_value()
