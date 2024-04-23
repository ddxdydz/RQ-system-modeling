def get_probability_of_orbit_data_from_orbit(orbit_time_list: list, orbit_value_list: list) -> dict:

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

    total_time = orbit_time_list[-1]

    counts = list(times.keys())
    values = list([value * 100 / total_time for value in times.values()])

    return {
        "counts": counts,
        "values": values
    }
