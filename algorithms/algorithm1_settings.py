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

    "GRAPHICS_KEYS": (
        "application_count_graphic",
        "handler_status_graphic",
        "probability_distribution_processed"
    ),

    "GRAPHICS_PLOT_SETTINGS": {

        "application_count_graphic": {
            "plot_widget_key": "application_count_graphic_widget",
            "brush_parameters": {"color": (0, 0, 255, 80)},
            "pen_parameters": {"color": (0, 0, 0)},
            "fillLevel": 0,
            "type": "histogram"
        },

        "handler_status_graphic": {
            "plot_widget_key": "handler_status_graphic_widget",
            "brush_parameters": {"color": (255, 0, 0, 80)},
            "pen_parameters": {"color": (0, 0, 0)},
            "fillLevel": 0,
            "type": "histogram"
        },

        "probability_distribution_free": {
            "plot_widget_key": "probability_distribution_graphic_widget",
            "brush_parameters": {"color": (255, 0, 0, 0)},
            "pen_parameters": {"color": (0, 0, 255, 200), "width": 1},
            "fillLevel": None,
            "type": "not_histogram"
        },

        "probability_distribution_processed": {
            "plot_widget_key": "probability_distribution_graphic_widget",
            "brush_parameters": {"color": (0, 0, 255, 0)},
            "pen_parameters": {"color": (255, 0, 0, 200), "width": 1},
            "fillLevel": None,
            "type": "not_histogram"
        }

    },

    "GRAPHICS_WIDGETS_KEYS": (
        "application_count_graphic_widget",
        "handler_status_graphic_widget",
        "probability_distribution_graphic_widget"
    ),

    "GRAPHICS_LAYOUT_STRETCH": {

        "application_count_graphic_widget": 6,

        "handler_status_graphic_widget": 3,

        "probability_distribution_graphic_widget": 4

    },

    "GRAPHICS_WIDGETS_SETTINGS": {

        "application_count_graphic_widget": {
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
            "set_mouse_enabled": {"x": True, "y": False}
        },

        "handler_status_graphic_widget": {
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
            "set_mouse_enabled": {"x": True, "y": False}
        },

        "probability_distribution_graphic_widget": {
            "title": "Распределение вероятностей занятости обработчика",
            "styles_title": {"color": "b", "font-size": "15pt"},
            "left_label": "Вероятность (%)",
            "bottom_label": "Время (секунды)",
            "styles_labels": {"color": "#f00", "font-size": "8pt"},
            "max_count_of_left_ticks": 4,
            "width_left_axis_px": 35,
            "maximum_value": 100,
            "background_style": "w",
            "show_grid": {"x": True, "y": True},
            "set_mouse_enabled": {"x": True, "y": False}
        }

    }

}
