from basic.constants.algorithm_working import PROCESSING

AC = 'a'
HS = 'h'


def get_probability_of_orbit_data(app_time_list: list, app_value_list: list,
                                  hs_time_list: list, hs_value_list: list) -> dict:

    # Объединяем данные:
    events = list(zip(app_time_list, [AC] * len(app_time_list), app_value_list)) +\
             list(zip(hs_time_list, [HS] * len(hs_time_list), hs_value_list))
    events.sort(key=lambda e: e[0])

    # Вычисляем изменение заявок на орбите:
    orbit_time_list, orbit_value_list = [0], [0]
    active_apps_count = 0
    last_orbit_apps_count = 0
    is_app_in_handler = False
    for time, event_type, value in events:
        if event_type == HS:
            is_app_in_handler = True if value == PROCESSING else False
        elif event_type == AC:
            active_apps_count = value
        current_orbit_apps_count = active_apps_count - int(is_app_in_handler)
        if current_orbit_apps_count != last_orbit_apps_count:
            orbit_time_list.append(time)
            orbit_value_list.append(current_orbit_apps_count)
            last_orbit_apps_count = current_orbit_apps_count

    # Вычисляем вероятность для каждого количества заявок:
    times = {}
    last_time, last_count = 0, 0
    for time, count in zip(orbit_time_list, orbit_value_list):
        if count != last_count:
            if last_count not in times.keys():
                times[last_count] = time - last_time
            else:
                times[last_count] += time - last_time
            last_time, last_count = time, count
    total_time = orbit_time_list[-1] - orbit_time_list[0]
    counts = list(times.keys())
    values = list([value * 100 / total_time for value in times.values()])

    if -1 in counts:
        index = counts.index(-1)
        counts.pop(index)
        values.pop(index)

    return {
        "counts": counts,
        "values": values
    }
