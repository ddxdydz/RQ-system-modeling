from PyQt5.QtWidgets import QDesktopWidget

from basic.constants.window_settings import *


def get_window_size():
    q = QDesktopWidget().availableGeometry()
    screen_width, screen_height = q.width(), q.height()
    base_window_size = 680, 440  # window size for 1366x680
    k = screen_width / 1366
    widget_width, widget_height = int(k * base_window_size[0]), int(k * base_window_size[1])
    if widget_width > WINDOW_MAXIMUM_SIZE[0] or widget_height > WINDOW_MAXIMUM_SIZE[1]:
        return WINDOW_MAXIMUM_SIZE
    if widget_width < WINDOW_MINIMUM_SIZE[0] or widget_height < WINDOW_MINIMUM_SIZE[1]:
        return WINDOW_MINIMUM_SIZE
    return widget_width, widget_height
