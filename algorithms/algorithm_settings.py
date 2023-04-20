from constants import HISTOGRAM


SETTINGS_ALGORITHM_1 = {

    "PARAMETERS_KEYS": ("application_count", "lm", "mu", "sg"),

    "PARAMETERS_LABELS": {
        "application_count": "Количество заявок:",
        "lm": "λ:",
        "mu": "μ:",
        "sg": "σ:"
    },

    "PARAMETERS_RANGE": {
        "application_count": {"min": 0, "max": 100000},
        "lm": {"min": 0, "max": 999},
        "mu": {"min": 0, "max": 999},
        "sg": {"min": 0, "max": 999}
    },

    "GRAPHICS_KEYS": ("application_count_graphic", "handler_status_graphic"),

    "GRAPHICS_TYPES": {
        "application_count_graphic": HISTOGRAM,
        "handler_status_graphic": HISTOGRAM
    },

    "GRAPHICS_INIT_SETTINGS": {

        "application_count_graphic": {
            "title": "Изменение количества заявок",
            "styles_title": {"color": "b", "font-size": "15pt"},
            "left_label": "Количество заявок в системе",
            "bottom_label": "Время (секунды)",
            "styles_labels": {"color": "#f00", "font-size": "8pt"},
            "max_count_of_left_ticks": 15,
            "width_left_axis_px": 35,
            "background_style": "w",
            "show_grid": {"x": True, "y": True},
            "set_mouse_enabled": {"x": True, "y": False}
        },

        "handler_status_graphic": {
            "title": "Изменение количества заявок",
            "styles_title": {"color": "b", "font-size": "15pt"},
            "left_label": "Количество заявок в системе",
            "bottom_label": "Время (секунды)",
            "styles_labels": {"color": "#f00", "font-size": "8pt"},
            "max_count_of_left_ticks": 15,
            "width_left_axis_px": 35,
            "background_style": "w",
            "show_grid": {"x": True, "y": True},
            "set_mouse_enabled": {"x": True, "y": False}
        },
    },

    "GRAPHICS_PLOT_SETTINGS": {

        "application_count_graphic": {
            "brush_parameters": [0, 0, 255, 80],
            "pen_parameters": [0, 0, 0]
        },

        "handler_status_graphic": {
            "brush_parameters": [255, 0, 0, 80],
            "pen_parameters": [0, 0, 0]
        }
    }
}
