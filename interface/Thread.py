from PyQt5 import QtCore


class Thread(QtCore.QThread):
    change_value = QtCore.pyqtSignal(int)  # Для подсчёта процентов выполнения

    def __init__(self, algorithm, parameters=None):
        super(Thread, self).__init__()
        self.algorithm = algorithm(self.change_value)
        self.parameters = parameters
        self.results = dict()

    def set_parameters(self, parameters):
        self.parameters = parameters

    def run(self):
        self.results = self.algorithm.get_results(**self.parameters)
