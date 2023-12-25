from basic.constants.plotting import PD_GRAPHIC_FREQUENCY


def get_probability_of_processing_data(hs_time_list: list, hs_value_list: list) -> dict:

    # Добавление дополнительных значений для плавности графика:
    step = (hs_time_list[-1] - hs_time_list[0]) / PD_GRAPHIC_FREQUENCY
    time_for_adding = step * PD_GRAPHIC_FREQUENCY - step
    for id_time in range(len(hs_time_list) - 2, -1, -1):
        start_time_range = hs_time_list[id_time]
        end_time_range = hs_time_list[id_time + 1]
        hs_status_in_range = hs_value_list[id_time]
        while start_time_range < time_for_adding < end_time_range:
            hs_time_list.insert(id_time + 1, time_for_adding)
            hs_value_list.insert(id_time + 1, hs_status_in_range)
            time_for_adding -= step

    # Добавление данных для построения графика:
    probability_distribution_data = [0]
    working_time_sum = 0
    total_time_sum = 0
    for id_time in range(1, len(hs_time_list)):
        hs_status_in_range = hs_value_list[id_time - 1]
        start_time_range = hs_time_list[id_time - 1]
        end_time_range = hs_time_list[id_time]
        delta_time = end_time_range - start_time_range
        if hs_status_in_range == 1:
            working_time_sum += delta_time
        total_time_sum += delta_time
        probability_distribution_data.append(working_time_sum * 100 / total_time_sum)

    return {"time": hs_time_list, "value": probability_distribution_data}
