from PyQt5.QtWidgets import QProgressBar, QLabel, QPushButton


class StatusBar:
    def __init__(self, parent):
        self.parent = parent
        self.progressBar = QProgressBar()
        self.label_message = QLabel()
        self.stop_button = QPushButton()
        self.init_status_bar_init()

    def init_status_bar_init(self):
        # Настройка панели состояния:
        self.update_message("Готов...")
        self.progressBar.setFixedHeight(13)
        self.progressBar.setFixedWidth(150)
        self.stop_button.setText("×")
        self.stop_button.setFixedHeight(15)
        self.stop_button.setFixedWidth(15)
        self.parent.addWidget(self.label_message)
        self.parent.addWidget(self.stop_button)
        self.parent.addWidget(self.progressBar)
        styles = "QStatusBar {\n  border: 1px solid#D7D7D7;\n  background-color: #F0F0F0;\n}"
        self.parent.setStyleSheet(styles)

    def update_message(self, text):
        self.label_message.setText(f"  {text}   ")

    def connect_stop_button(self, func):
        self.stop_button.clicked.connect(func)

    def set_progress_value(self, value):
        self.progressBar.setValue(value)

    def hide_progress(self):
        self.progressBar.hide()
        self.progressBar.setValue(0)
        self.stop_button.hide()

    def show_progress(self):
        self.progressBar.show()
        self.stop_button.show()
