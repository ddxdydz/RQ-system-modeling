from interface.support.widgets.ParameterNumerical import ParameterNumerical


class ParameterManager:
    def __init__(self, installation_layout):
        self.lm = ParameterNumerical(
            label_text="λ: ",
            installation_layout=installation_layout,
            range_min=0.001,
            range_max=999,
            default=3
        )
        self.mu = ParameterNumerical(
            label_text="μ: ",
            installation_layout=installation_layout,
            range_min=0.001,
            range_max=999,
            default=1
        )
        self.sg = ParameterNumerical(
            label_text="σ: ",
            installation_layout=installation_layout,
            range_min=0.001,
            range_max=999,
            default=1
        )
        self.application_count = ParameterNumerical(
            label_text="Количество заявок:",
            installation_layout=installation_layout,
            range_min=0,
            range_max=100000,
            default=4,
            is_oneline=False,
            is_int=True
        )

    def get_parameters(self) -> dict:
        return {
            "application_count": self.application_count.get_value(),
            "lm": self.lm.get_value(),
            "mu": self.mu.get_value(),
            "sg": self.sg.get_value()
        }

    def get_description(self):
        return """
        Описание параметров RQ-системы с надёжным прибором:
        
        λ - Параметр времени поступления заявки из входного потока
        μ - Параметр времени обслуживания заявок
        σ - Параметр времени ожидания заявки на орбите
        """
