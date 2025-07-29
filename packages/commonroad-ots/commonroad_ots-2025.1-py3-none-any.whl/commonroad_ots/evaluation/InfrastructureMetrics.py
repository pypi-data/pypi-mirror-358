import statistics
from typing import Tuple

from commonroad_ots.visualization.plots import draw_multi_plot


def calculate_vehicles_in_simulation(
    warm_up: float,
    orig_states: dict,
    sim_states: dict,
    lane_length: float,
    timestep: float,
    only_draw_mean: bool,
    frame_factor_orig: float,
    frame_factor_sim: float,
) -> Tuple[float, float, float, float]:
    """
    Calculates the number of vehicles in the simulation at each timestep, as well as the density of vehicles per meter

    Parameters
    ----------
    warm_up: float
    orig_states: dict
    sim_states: dict
    lane_length: float
    timestep: float
    only_draw_mean: bool
    frame_factor_orig: float
    frame_factor_sim: float
    """
    vehicles_per_timestep_orig = dict()
    vehicles_per_timestep_sim = dict()
    for gtu in orig_states.keys():
        states = orig_states.get(gtu)
        for i in range(len(states)):
            t = warm_up + states[i].timestep
            t = t * timestep
            if t not in vehicles_per_timestep_orig.keys():
                vehicles_per_timestep_orig.update({t: []})
            vehicles_per_timestep_orig.get(t).append(gtu)

    for gtu in sim_states.keys():
        states = sim_states.get(gtu)
        for i in range(len(states)):
            t = states[i].timestep
            t = t * timestep
            if t not in vehicles_per_timestep_sim.keys():
                vehicles_per_timestep_sim.update({t: []})
            vehicles_per_timestep_sim.get(t).append(gtu)

    data_orig_x = []
    data_orig_y = []
    for k, v in vehicles_per_timestep_orig.items():
        data_orig_x.append(k)
        data_orig_y.append(len(v))
    data_orig_sorted = sorted(zip(data_orig_x, data_orig_y))
    for (i, elem) in enumerate(data_orig_sorted):
        data_orig_x[i] = elem[0]
        data_orig_y[i] = elem[1]

    data_sim_x = []
    data_sim_y = []
    for k, v in vehicles_per_timestep_sim.items():
        data_sim_x.append(k)
        data_sim_y.append(len(v))
    data_sim_sorted = sorted(zip(data_sim_x, data_sim_y))
    for (i, elem) in enumerate(data_sim_sorted):
        data_sim_x[i] = elem[0]
        data_sim_y[i] = elem[1]

    mean_vehicles_orig = statistics.mean(data_orig_y)
    stdev_vehicles_orig = statistics.stdev(data_orig_y)
    mean_traffic_density_orig = mean_vehicles_orig / (lane_length * frame_factor_orig)
    stdev_traffic_density_orig = stdev_vehicles_orig / (lane_length * frame_factor_orig)
    print("Original mean traffic density:", mean_traffic_density_orig)
    print("Original stdev traffic density:", stdev_traffic_density_orig)

    if len(data_sim_y) > 1:
        mean_vehicles_sim = statistics.mean(data_sim_y)
        stdev_vehicles_sim = statistics.stdev(data_sim_y)
        mean_traffic_density_sim = mean_vehicles_sim / (lane_length * frame_factor_sim)
        stdev_traffic_density_sim = stdev_vehicles_sim / (lane_length * frame_factor_sim)
        print("Simulated mean traffic density:", mean_traffic_density_sim)
        print("Simulated stdev traffic density:", stdev_traffic_density_sim)
    else:
        print("No simulated data found for 'vehicles in simulation'")
        mean_traffic_density_sim = -1
        stdev_traffic_density_sim = -1

    mean_plot = 0
    std_plot = 0

    if only_draw_mean:
        data_orig_y = [statistics.mean(data_orig_y)] * len(data_orig_y)
        mean_plot = mean_vehicles_orig
        std_plot = stdev_vehicles_orig

    # vehicles in simulation
    draw_multi_plot(
        [
            [data_orig_x, data_orig_y],
            [data_sim_x, data_sim_y],
        ],
        warm_up * timestep,
        ["Recording", "Simulation"],
        "Vehicles in Simulation",
        "",
        "Time [s]",
        "Number of Vehicles [-]",
        max(max(data_orig_y), max(data_sim_y)) * 1.1,
        0,
        mean_plot,
        std_plot,
    )

    mean_plot_td = 0
    std_plot_td = 0

    data_orig_y = [x / (lane_length * frame_factor_orig) for x in data_orig_y]

    if only_draw_mean:
        data_orig_y = [mean_traffic_density_orig] * len(data_orig_y)
        mean_plot_td = mean_traffic_density_orig
        std_plot_td = stdev_traffic_density_orig

    # traffic density
    draw_multi_plot(
        [
            [data_orig_x, [x * 1000 for x in data_orig_y]],
            [data_sim_x, [x / (lane_length * frame_factor_sim) * 1000 for x in data_sim_y]],
        ],
        warm_up * timestep,
        ["Recording", "Simulation"],
        "Traffic Density",
        "",
        "Time [s]",
        "Traffic Density [1/km]",
        max(max(data_orig_y) / frame_factor_orig, max(data_sim_y) / frame_factor_sim) * 1.1 / lane_length * 1000,
        0,
        mean_plot_td * 1000,
        std_plot_td * 1000,
    )

    return mean_traffic_density_orig, stdev_traffic_density_orig, mean_traffic_density_sim, stdev_traffic_density_sim


def calculate_mean_velocity_over_time(
    warm_up: float, orig_states: dict, sim_states: dict, timestep: float, only_draw_mean: bool
) -> Tuple[float, float, float, float]:
    """
    Calculates the mean velocity over time

    Parameters
    ----------
    warm_up: float
    orig_states: dict
    sim_states: dict
    timestep: float
    only_draw_mean: bool
    """
    vehicles_per_timestep_orig = dict()
    vehicles_per_timestep_sim = dict()
    for gtu in orig_states.keys():
        states = orig_states.get(gtu)
        for i in range(len(states)):
            t = warm_up + states[i].timestep
            t = t * timestep
            if t not in vehicles_per_timestep_orig.keys():
                vehicles_per_timestep_orig.update({t: []})
            vehicles_per_timestep_orig.get(t).append(states[i].vel)

    for gtu in sim_states.keys():
        states = sim_states.get(gtu)
        for i in range(len(states)):
            t = states[i].timestep
            t = t * timestep
            if t not in vehicles_per_timestep_sim.keys():
                vehicles_per_timestep_sim.update({t: []})
            vehicles_per_timestep_sim.get(t).append(states[i].vel)

    data_orig_x = []
    data_orig_y = []
    for k, v in vehicles_per_timestep_orig.items():
        data_orig_x.append(k)
        data_orig_y.append(statistics.mean(v))
    data_orig_sorted = sorted(zip(data_orig_x, data_orig_y))
    for (i, elem) in enumerate(data_orig_sorted):
        data_orig_x[i] = elem[0]
        data_orig_y[i] = elem[1]

    data_sim_x = []
    data_sim_y = []
    for k, v in vehicles_per_timestep_sim.items():
        data_sim_x.append(k)
        data_sim_y.append(statistics.mean(v))
    data_sim_sorted = sorted(zip(data_sim_x, data_sim_y))
    for (i, elem) in enumerate(data_sim_sorted):
        data_sim_x[i] = elem[0]
        data_sim_y[i] = elem[1]

    mean_velocity_orig = statistics.mean(data_orig_y)
    stdev_velocity_orig = statistics.stdev(data_orig_y)
    print("Original mean velocity:", mean_velocity_orig)
    print("Original stdev velocity:", stdev_velocity_orig)

    if len(data_sim_y) > 1:
        mean_velocity_sim = statistics.mean(data_sim_y)
        stdev_velocity_sim = statistics.stdev(data_sim_y)
        print("Simulated mean velocity:", mean_velocity_sim)
        print("Simulated stdev velocity:", stdev_velocity_sim)
    else:
        print("No simulated velocity data found")
        mean_velocity_sim = -1
        stdev_velocity_sim = -1

    mean_plot = 0
    std_plot = 0

    if only_draw_mean:
        data_orig_y = [statistics.mean(data_orig_y)] * len(data_orig_y)
        mean_plot = mean_velocity_orig
        std_plot = stdev_velocity_orig

    draw_multi_plot(
        [
            [data_orig_x, data_orig_y],
            [data_sim_x, data_sim_y],
        ],
        warm_up * timestep,
        ["Recording", "Simulation"],
        "Mean Velocity",
        "",
        "Time [s]",
        "Velocity [m/s]",
        max(max(data_orig_y), max(data_sim_y)) * 1.1,
        0,
        mean_plot,
        std_plot,
    )

    return mean_velocity_orig, stdev_velocity_orig, mean_velocity_sim, stdev_velocity_sim


def calculate_spawn_frequency(orig_states: dict, sim_states: dict, timestep: float) -> Tuple[float, float]:
    """
    Calculates the spawn frequency

    Parameters
    ----------
    orig_states: dict
    sim_states: dict
    timestep: float
    """
    max_orig_time = 0
    max_sim_time = 0
    orig_vehicles = 0
    sim_vehicles = 0

    for gtu in orig_states.values():
        if gtu[0].timestep > 0:
            orig_vehicles += 1
        if gtu[-1].timestep > max_orig_time:
            max_orig_time = gtu[-1].timestep

    for gtu in sim_states.values():
        if gtu[0].timestep > 0:
            sim_vehicles += 1
        if gtu[-1].timestep > max_sim_time:
            max_sim_time = gtu[-1].timestep

    spawn_freq_rec = orig_vehicles / (max_orig_time * timestep)
    spawn_freq_sim = sim_vehicles / (max_sim_time * timestep)
    print(f"Orig: {orig_vehicles} vehicles in {max_orig_time * timestep} seconds")
    print(f"The original spawn frequency is {spawn_freq_rec} vehicles/s")
    print(f"Sim: {sim_vehicles} vehicles in {max_sim_time * timestep} seconds")
    print(f"The simulated spawn frequency is {spawn_freq_sim} vehicles/s")

    return spawn_freq_rec, spawn_freq_sim
