from basic.errors.MatrixSizeError import MatrixSizeError
from interface.support.widgets.ParameterNumerical import ParameterNumerical
from interface.support.widgets.ParameterMatrix import ParameterMatrix


class ParameterManager:
    def __init__(self, installation_layout):
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
        self.sigma = ParameterNumerical(
            label_text="σ:",
            installation_layout=installation_layout,
            range_min=0.001,
            range_max=999,
            default=1
        )
        self.gamma1 = ParameterNumerical(
            label_text="γ₁:",
            installation_layout=installation_layout,
            range_min=0.001,
            range_max=999,
            default=0.4
        )
        self.gamma2 = ParameterNumerical(
            label_text="γ₂:",
            installation_layout=installation_layout,
            range_min=0.001,
            range_max=999,
            default=0.2
        )

        self.lambdas = ParameterMatrix(
            label_text="Λ:",
            installation_layout=installation_layout,
            range_min=0.001,
            range_max=999,
            default="{{2.0, 2.0, 2.0}}"
        )
        self.q = ParameterMatrix(
            label_text="Q:",
            installation_layout=installation_layout,
            range_min=-999,
            range_max=999,
            default="{{-0.4, 0.1, 0.3}, {0.3, -0.5, 0.2}, {0.1, 0.1, -0.2}}",
            is_square=True
        )
        # self.modeling_time = ParameterNumerical(
        #     label_text="V:",
        #     installation_layout=installation_layout,
        #     range_min=0.001,
        #     range_max=99999999,
        #     default=10000000
        # )
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
        if len(self.lambdas.get_value()[0]) != len(self.q.get_value()):
            raise MatrixSizeError("Конфликт в размерах матриц Q и Λ")
        return {
            "mu1": self.mu1.get_value(),
            "mu2": self.mu2.get_value(),
            "sigma": self.sigma.get_value(),
            "gamma1": self.gamma1.get_value(),
            "gamma2": self.gamma2.get_value(),
            "lambdas": self.lambdas.get_value(),
            "q": self.q.get_value(),
            "v": self.application_count.get_value()
        }

    def get_description(self):
        return """
        Описание параметров MMPP RQ-системы с ненадёжным прибором:
        
        μ₁ - Параметр времени обслуживания заявок
        μ₂ - Параметр времени восстановления
        σ - Параметр времени ожидания заявки на орбите
        γ₁ - Параметр времени бесперебойной работы прибора в свободном состоянии
        γ₂ - Параметр времени бесперебойной работы прибора в занятом состоянии
        Λ - Вектор условных интенсивностей
        Q - Матрица инфинитезимальных характеристик
        """
