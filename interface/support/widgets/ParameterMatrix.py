from basic.errors.MatrixNestingError import MatrixNestingError
from basic.errors.MatrixSizeError import MatrixSizeError
from interface.support.widgets.Parameter import Parameter


class ParameterMatrix(Parameter):
    def __init__(self, label_text, installation_layout, default="",
                 range_min=0, range_max=100000, is_square=False, is_oneline=True):
        super(ParameterMatrix, self).__init__(label_text, installation_layout, is_oneline)

        self.is_square = is_square
        self.range_min, self.range_max = range_min, range_max
        self.default = default

        self.setText(str(self.default))

    @staticmethod
    def string_to_matrix(matrix_string):
        # matrix_string: "{{float, float, ..., float}, ..., {float, float, ..., float}}"

        matrix_string = matrix_string.replace(" ", "")  # Удаление пробелов
        rows = matrix_string[2:-2].split("},{")  # Разделение на строки
        matrix = []

        for row in rows:
            row_elements = row.split(",")
            row_elements = [float(x.strip()) for x in row_elements]  # Преобразование в числа
            matrix.append(row_elements)

        return matrix

    def get_value(self):
        self.check_parameters_fullness()

        matrix_string = self.text().replace(" ", "")  # Удаление пробелов

        # Проверка вложенности скобок:
        if not matrix_string.startswith("{{") or not matrix_string.endswith("}}"):
            raise MatrixNestingError
        matrix_string_without = matrix_string[2:-2].replace("},{", "")  # Удаление "ожидаемых" скобок
        if "}" in matrix_string_without or "{" in matrix_string_without:  # Если есть лишние скобки
            raise MatrixNestingError

        matrix = self.string_to_matrix(matrix_string)

        # Проверка значений матрицы на соответствие диапазону:
        for row in matrix:
            for value in row:
                self.check_parameters_range(value, self.range_min, self.range_max)

        # Проверка размеров строк матрицы:
        expected_row_size = len(matrix) if self.is_square else len(matrix[0])
        for row in matrix:
            if len(row) != expected_row_size:
                raise MatrixSizeError("Несоответвите размеров строк в квадратной матрице Q.")

        return matrix
