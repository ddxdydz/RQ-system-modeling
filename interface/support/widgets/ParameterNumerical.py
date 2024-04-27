from interface.support.widgets.Parameter import Parameter


class ParameterNumerical(Parameter):
    def __init__(self, label_text, installation_layout, default=0, range_min=0, range_max=100000,
                 is_int=False, is_oneline=True):
        super(ParameterNumerical, self).__init__(label_text, installation_layout, is_oneline)

        self.range_min, self.range_max = range_min, range_max
        self.default = default
        self.is_int = is_int

        self.setText(str(self.default))

    def get_value(self):
        self.check_parameters_fullness()
        value = self.text().replace(',', '.')
        if self.is_int:
            if '.' in value:
                raise ValueError
            value = int(value)
        else:
            value = float(value)
        self.check_parameters_range(value, self.range_min, self.range_max)
        return value
