class StatusBarUpdater:
    def __init__(self, signal_to_change_progress_value=None):
        self.signal_to_change_progress_value = signal_to_change_progress_value
        self.last_progress_value_for_indicator = 0

    def update(self, progress):
        if self.signal_to_change_progress_value is not None:

            if progress < self.last_progress_value_for_indicator:
                self.last_progress_value_for_indicator = 0

            if progress != self.last_progress_value_for_indicator and progress % 5 == 0:
                self.signal_to_change_progress_value.emit(progress)
                self.last_progress_value_for_indicator = progress
