from interface.support.widgets.ParameterNumerical import ParameterNumerical


class ParameterManager:
    def __init__(self, installation_layout):
        self.lm = ParameterNumerical(
            label_text="λ: ",
            installation_layout=installation_layout,
            range_min=0.001,
            range_max=999,
            default=2
        )
        self.mu1 = ParameterNumerical(
            label_text="μ₁:",
            installation_layout=installation_layout,
            range_min=0.001,
            range_max=999,
            default=3
        )
        self.mu2 = ParameterNumerical(
            label_text="μ₂:",
            installation_layout=installation_layout,
            range_min=0.001,
            range_max=999,
            default=2
        )
        self.sg = ParameterNumerical(
            label_text="σ: ",
            installation_layout=installation_layout,
            range_min=0.001,
            range_max=999,
            default=1
        )
        self.dt1 = ParameterNumerical(
            label_text="δ₁:",
            installation_layout=installation_layout,
            range_min=0.001,
            range_max=999,
            default=0.4
        )
        self.dt2 = ParameterNumerical(
            label_text="δ₂:",
            installation_layout=installation_layout,
            range_min=0.001,
            range_max=999,
            default=0.2
        )
        self.application_count = ParameterNumerical(
            label_text="Количество заявок:",
            installation_layout=installation_layout,
            range_min=0,
            range_max=500000,
            default=4,
            is_oneline=False,
            is_int=True
        )

    def get_parameters(self) -> dict:
        return {
            "application_count": self.application_count.get_value(),
            "lm": self.lm.get_value(),
            "mu1": self.mu1.get_value(),
            "mu2": self.mu2.get_value(),
            "sg": self.sg.get_value(),
            "dt1": self.dt1.get_value(),
            "dt2": self.dt2.get_value()
        }

    def get_description(self):
        return """
        Описание параметров RQ-системы с ненадёжным прибором:
        
        λ - Параметр времени поступления заявки из входного потока
        μ₁ - Параметр времени обслуживания заявок
        μ₂ - Параметр времени восстановления
        σ - Параметр времени ожидания заявки на орбите
        δ₁ - Параметр времени бесперебойной работы прибора в свободном состоянии
        δ₂ - Параметр времени бесперебойной работы прибора в занятом состоянии
        """
