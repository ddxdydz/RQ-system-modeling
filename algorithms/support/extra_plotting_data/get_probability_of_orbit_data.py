from basic.constants.algorithm_working import *


def get_probability_of_orbit_data(app_time_list: list, app_value_list: list,
                                  hs_time_list: list, hs_value_list: list) -> dict:
    # Объединяем данные:
    events = list(zip(app_time_list, [APP_EVENT] * len(app_time_list), app_value_list)) +\
             list(zip(hs_time_list, [HANDLER_EVENT] * len(app_time_list), hs_value_list))
    events.sort(key=lambda e: e[0])

    times = {0: 0}  # количество заявок на орбите: время нахождения
    last_time = 0
    active_apps_count = 0
    orbit_apps_count = 0
    is_app_in_handler = False

    for time, event_type, value in events:

        if event_type == HANDLER_EVENT:
            is_app_in_handler = True if value == PROCESSING else False
        elif event_type == APPLICATION_EVENT:
            active_apps_count = value

        current_orbit_apps_count = active_apps_count - int(is_app_in_handler)
        if current_orbit_apps_count != orbit_apps_count:

            times[orbit_apps_count] += time - last_time

            if current_orbit_apps_count not in times.keys():
                times[current_orbit_apps_count] = 0
            last_time, orbit_apps_count = time, current_orbit_apps_count

    total_time = app_time_list[-1] - app_time_list[0]
    return {
        "time": list(times.keys()),
        "value": [(time / total_time) * 100 for time in times.values()]
    }
