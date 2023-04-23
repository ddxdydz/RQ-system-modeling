ALGORITHM_1_SETTINGS = {

    "PARAMETERS_KEYS": ("lm", "mu", "sg", "application_count"),

    "PARAMETERS_LABELS": {

        "application_count": "Количество заявок:",
        "lm": "λ:",
        "mu": "μ:",
        "sg": "σ:"

    },

    "PARAMETERS_SETTINGS": {

        "application_count": {
            "type": int,
            "default_value": 4,
            "range": {"min": 0, "max": 100000},
            "one_line_label": False
        },

        "lm": {
            "type": float,
            "default_value": 3.0,
            "range": {"min": 0.001, "max": 999},
            "one_line_label": True
        },

        "mu": {
            "type": float,
            "default_value": 1.0,
            "range": {"min": 0.001, "max": 999},
            "one_line_label": True
        },

        "sg": {
            "type": float,
            "default_value": 1.0,
            "range": {"min": 0.001, "max": 999},
            "one_line_label": True
        }

    },

    "GRAPHICS_KEYS": ("application_count_graphic", "handler_status_graphic", "handler_percent_graphic"),

    "GRAPHICS_LAYOUT_STRETCH": {

        "application_count_graphic": 6,

        "handler_status_graphic": 3,

        "handler_percent_graphic": 4

    },

    "GRAPHICS_SETTINGS": {

        "application_count_graphic": {
            "title": "Изменение количества заявок",
            "styles_title": {"color": "b", "font-size": "15pt"},
            "left_label": "Количество заявок в системе",
            "bottom_label": None,
            "styles_labels": {"color": "#f00", "font-size": "8pt"},
            "max_count_of_left_ticks": 8,
            "width_left_axis_px": 35,
            "maximum_value": None,
            "background_style": "w",
            "show_grid": {"x": True, "y": True},
            "set_mouse_enabled": {"x": True, "y": False},
            "brush_parameters": {"color": (0, 0, 255, 80)},
            "pen_parameters": {"color": (0, 0, 0)},
            "fillLevel": 0,
            "type": "histogram"
        },

        "handler_status_graphic": {
            "title": "Изменение статуса обработчика",
            "styles_title": {"color": "b", "font-size": "15pt"},
            "left_label": "Статус",
            "bottom_label": None,
            "styles_labels": {"color": "#f00", "font-size": "8pt"},
            "max_count_of_left_ticks": 15,
            "width_left_axis_px": 35,
            "maximum_value": 1,
            "background_style": "w",
            "show_grid": {"x": True, "y": True},
            "set_mouse_enabled": {"x": True, "y": False},
            "brush_parameters": {"color": (255, 0, 0, 80)},
            "pen_parameters": {"color": (0, 0, 0)},
            "fillLevel": 0,
            "type": "histogram"
        },

        "handler_percent_graphic": {
            "title": "Вероятность занятости обработчка",
            "styles_title": {"color": "b", "font-size": "15pt"},
            "left_label": "Вероятность (%)",
            "bottom_label": "Время (секунды)",
            "styles_labels": {"color": "#f00", "font-size": "8pt"},
            "max_count_of_left_ticks": 4,
            "width_left_axis_px": 35,
            "maximum_value": 100,
            "background_style": "w",
            "show_grid": {"x": True, "y": True},
            "set_mouse_enabled": {"x": True, "y": False},
            "brush_parameters": {"color": (0, 255, 0, 80)},
            "pen_parameters": {"color": (0, 0, 0), "width": 1},
            "fillLevel": 0,
            "type": "not_histogram"
        }

    }

}
