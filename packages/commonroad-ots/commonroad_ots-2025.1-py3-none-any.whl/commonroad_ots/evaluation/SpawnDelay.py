import statistics

import numpy as np
from matplotlib import pyplot as plt

from typing import Tuple

from commonroad_ots.visualization.plots import draw_bar_plot


def calculate_spawn_delay(orig_states: dict, sim_states: dict, timestep: float) -> Tuple[float, float]:
    """
    Calculates the delay between the initial timestep in the original and simulated scenario for each vehicle.

    Parameters
    ----------
    orig_states: dict
    sim_states: dict
    timestep: float
    """
    delays = []

    sorted_ids = list(orig_states.keys())
    sorted_ids.sort(key=lambda gtu_id: orig_states.get(gtu_id)[0].timestep)

    ids = []

    for gtu in sorted_ids:
        if orig_states.get(gtu)[0].timestep > 0:
            delays.append((sim_states.get(gtu)[0].timestep - orig_states.get(gtu)[0].timestep) * timestep)
            ids.append(gtu)

    if len(delays) > 1:
        mean_delay = statistics.mean(delays)
        stdev_delay = statistics.stdev(delays)
        print("Mean spawning delay in seconds:", mean_delay)
        print("Stdev spawning delay in seconds:", stdev_delay)
    else:
        print("No data for spawn delay faound")
        mean_delay = -1
        stdev_delay = -1
    draw_bar_plot(delays, ids, mean_delay, "Spawn Delay", "GTU ID", "Delay [s]")
    return mean_delay, stdev_delay
