import math

import numpy as np
import statistics
from dtaidistance import dtw, dtw_ndim


def calculate_scores_ndtw(orig_states: dict, sim_states: dict, single_dim: bool) -> float:
    """
    Calculates the mean NDTW value across all GTUs.

    Parameters
    ----------
    orig_states: dict
    sim_states: dict
    single_dim: bool
    """
    if single_dim:
        return two_d_ndtw(orig_states, sim_states)
    else:
        return n_d_ndtw(orig_states, sim_states)


def n_d_ndtw(orig_states: dict, sim_states: dict) -> float:
    ndtw_values_by_gtu = dict()

    for gtu in orig_states.keys():
        orig_data = [[s.pos[0], s.pos[1], s.vel, s.ori] for s in orig_states.get(gtu)]
        sim_data = [[s.pos[0], s.pos[1], s.vel, s.ori] for s in sim_states.get(gtu)]
        ndtw = math.sqrt(
            dtw_ndim.distance(np.array(orig_data), np.array(sim_data)) / max(len(orig_states), len(sim_data))
        )
        ndtw_values_by_gtu.update({gtu: ndtw})

    print("Mean N-Dim NDTW:", statistics.mean(ndtw_values_by_gtu.values()))
    return statistics.mean(ndtw_values_by_gtu.values())


def two_d_ndtw(orig_states: dict, sim_states: dict) -> float:
    ndtw_values_by_gtu = dict()

    for gtu in orig_states.keys():
        orig_data = [s.pos[0] + s.pos[1] + s.vel + s.ori for s in orig_states.get(gtu)]
        sim_data = [s.pos[0] + s.pos[1] + s.vel + s.ori for s in sim_states.get(gtu)]
        ndtw = math.sqrt(dtw.distance(np.array(orig_data), np.array(sim_data)) / max(len(orig_states), len(sim_data)))
        ndtw_values_by_gtu.update({gtu: ndtw})

    print("Mean 2-Dim NDTW:", str(statistics.mean(ndtw_values_by_gtu.values())))
    return statistics.mean(ndtw_values_by_gtu.values())
