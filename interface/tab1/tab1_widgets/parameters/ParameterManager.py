from interface.support.widgets.ParameterType1 import ParameterType1
from interface.support.widgets.ParameterType2 import ParameterType2


class ParameterManager:
    def __init__(self, installation_layout):
        self.lm = ParameterType1(
            label_text="λ: ",
            installation_layout=installation_layout,
            range_min=0.001,
            range_max=999,
            default=3
        )
        self.mu = ParameterType1(
            label_text="μ: ",
            installation_layout=installation_layout,
            range_min=0.001,
            range_max=999,
            default=1
        )
        self.sg = ParameterType1(
            label_text="σ: ",
            installation_layout=installation_layout,
            range_min=0.001,
            range_max=999,
            default=1
        )
        self.application_count = ParameterType2(
            label_text="Количество заявок:",
            installation_layout=installation_layout,
            range_min=0,
            range_max=100000,
            default=4,
            is_int=True
        )

    def get_parameters(self) -> dict:
        return {
            "application_count": self.application_count.get_value(),
            "lm": self.lm.get_value(),
            "mu": self.mu.get_value(),
            "sg": self.sg.get_value()
        }
