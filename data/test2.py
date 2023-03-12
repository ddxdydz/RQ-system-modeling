self.application_count_graphic.plot(
            self.events_times,
            self.applications_count_y,
            name="Количество заявок",
            stepMode="center",
            fillLevel=0,
            fillOutline=True,
            brush=(0, 0, 255, 100),
            symbol='+'
        )

#Set Range
self.graphWidget.setXRange(0, 10, padding=0)
self.graphWidget.setYRange(20, 55, padding=40)

'''
        self.application_count_graphic.plot(
            self.events_times,
            self.applications_count_y,
            name="Количество заявок",
            stepMode="center",
            fillLevel=0,
            fillOutline=True,
            brush=(0, 0, 255, 100),
            symbol='+'
        )
        if self.checkBox.isChecked():
            self.application_count_graphic.plot(
                self.events_times,
                [i / 2 for i in self.handler_statuses_y],
                stepMode="center",
                fillLevel=0,
                fillOutline=True,
                pen=(0, 0, 0),
                brush=(255, 0, 0, 100),
                name="Состояния обработчика",
                symbol='+'
            )
            self.handler_status_graphic.hide()
            styles = {"color": "#f00", "font-size": "15px"}
            self.application_count_graphic.setLabel("bottom", "Время (секунды)", **styles)
        else:
            self.handler_status_graphic.plot(
                self.events_times,
                self.handler_statuses_y,
                stepMode="center",
                fillLevel=0,
                fillOutline=True,
                brush=(255, 0, 0, 100),
                name="Состояния обработчика",
                symbol='+'
            )
            self.handler_status_graphic.show()
            styles = {"color": "#f00", "font-size": "15px"}
            self.application_count_graphic.setLabel("bottom", "", **styles)
            '''

self.checkBox.clicked.connect(self.check_box_event)

if event.key() == QtCore.Qt.Key_Up:
    self.p += 0.1
    print(self.p)
    self.application_count_graphic.setYRange(
        0.6, self.data_for_graphics["handler_statuses_graphic_data"]["values"][-1], padding=self.p)
if event.key() == QtCore.Qt.Key_Down:
    self.p -= 0.1
    print(self.p)
    self.application_count_graphic.setYRange(
        0.6, self.data_for_graphics["handler_statuses_graphic_data"]["values"][-1], padding=self.p)

name_list = ['o', 's', 't', 't1', 't2', 't3', 'd', '+', 'x', 'p', 'h', 'star',
             'arrow_up', 'arrow_right', 'arrow_down', 'arrow_left']