import math
import statistics

import numpy as np

from typing import List, Tuple

from commonroad_ots.visualization.plots import draw_bar_plot


def calculate_scores_rmse(orig_states: dict, sim_states: dict) -> Tuple[List[float], List[float], List[float]]:
    """
    Calculates the mean RMSE for [position, velocity, orientation].

    Parameters
    ----------
    orig_states: dict
    sim_states: dict
    """
    pos_values = []
    vel_values = []
    ori_values = []

    sorted_ids = list(orig_states.keys())
    sorted_ids.sort(key=lambda gtu_id: orig_states.get(gtu_id)[0].timestep)

    for gtu in sorted_ids:
        x_data_orig = [s.pos[0] for s in orig_states.get(gtu)]
        x_data_sim = [s.pos[0] for s in sim_states.get(gtu)]
        y_data_orig = [s.pos[1] for s in orig_states.get(gtu)]
        y_data_sim = [s.pos[1] for s in sim_states.get(gtu)]
        distances = []
        for i in range(len(x_data_orig)):
            distances.append(math.dist([x_data_orig[i], y_data_orig[i]], [x_data_sim[i], y_data_sim[i]]))
        rmse_pos = math.sqrt(np.square(distances).mean())
        pos_values.append(rmse_pos)

        vel_data_orig = [s.vel for s in orig_states.get(gtu)]
        vel_data_sim = [s.vel for s in sim_states.get(gtu)]
        rmse_vel = math.sqrt(np.square(np.subtract(vel_data_orig, vel_data_sim)).mean())
        vel_values.append(rmse_vel)

        ori_data_orig = [s.ori for s in orig_states.get(gtu)]
        ori_data_sim = [s.ori for s in sim_states.get(gtu)]
        rmse_ori = math.sqrt(np.square(np.subtract(ori_data_orig, ori_data_sim)).mean())
        ori_values.append(rmse_ori)

    rmse_mean = [
        statistics.mean(pos_values),
        statistics.mean(vel_values),
        statistics.mean(ori_values),
    ]
    print("Mean RMSE values for [pos, vel, ori]:", rmse_mean)

    rmse_stdev = [
        statistics.stdev(pos_values),
        statistics.stdev(vel_values),
        statistics.stdev(ori_values),
    ]
    print("Stdev RMSE values for [pos, vel, ori]:", rmse_stdev)

    rmse_median = [
        statistics.median(pos_values),
        statistics.median(vel_values),
        statistics.median(ori_values),
    ]
    print("Median RMSE values for [pos, vel, ori]:", rmse_median)

    draw_bar_plot(pos_values, list(orig_states.keys()), rmse_mean[0], "RMSE Position", "GTU ID [-]", "RMSE [m]")

    return rmse_mean, rmse_stdev, rmse_median
