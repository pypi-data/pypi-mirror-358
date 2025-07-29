import math
import sqlite3
from typing import Tuple

from scipy.spatial import KDTree

import commonroad_ots
from commonroad_ots.conversion.main import Conversion
from commonroad.scenario.obstacle import ObstacleType
from commonroad.scenario.scenario import Scenario

from commonroad_ots.conversion.gtus import check_driven_distance
from commonroad_ots.evaluation.vehicle_state import VehicleState


def get_states_by_gtu(scenario: Scenario, timespan: int, timestep: float, warm_up) -> dict:
    """
    Extracts the vehicle states from the scenario to a dict by gtu_id
    """
    res = dict()
    for obs in scenario.dynamic_obstacles:
        if obs.obstacle_type == ObstacleType.PEDESTRIAN:
            continue
        distance = check_driven_distance(obs.prediction.trajectory.state_list)
        if distance < 0.1:
            continue
        states = [obs.initial_state]
        states.extend(obs.prediction.trajectory.state_list)
        pos = [[s.position[0], s.position[1]] for s in states]
        v = [s.velocity for s in states]
        t = [s.time_step for s in states]
        o = [s.orientation for s in states]

        vehicle_states = []
        for i in range(len(t)):
            # filter all data after timespan
            if t[i] > (timespan + warm_up) / timestep:
                break
            vehicle_states.append(
                VehicleState(t[i], pos[i], v[i], o[i], obs.obstacle_shape.length, obs.obstacle_shape.width)
            )
        if len(vehicle_states) > 0:
            res.update({str(obs.obstacle_id): vehicle_states})
    return res


def limit_data_by_distance(orig_states: dict, sim_states: dict) -> Tuple[dict, dict]:
    """
    Limits the data for each vehicle by the minimum of orig and sim based on the driven distance
    """
    to_remove = []

    for gtu in orig_states.keys():
        if gtu not in sim_states.keys():
            # print("No simulated trajectory data for obstacle ", gtu)
            to_remove.append(gtu)
            continue

        driven_distance_orig = 0
        for i in range(len(orig_states[gtu]) - 1):
            driven_distance_orig += math.dist(orig_states[gtu][i].pos, orig_states[gtu][i + 1].pos)
        driven_distance_sim = 0
        for i in range(len(sim_states[gtu]) - 1):
            driven_distance_sim += math.dist(sim_states[gtu][i].pos, sim_states[gtu][i + 1].pos)

        step = 0
        if driven_distance_orig > driven_distance_sim:
            while driven_distance_sim - math.dist(orig_states[gtu][step].pos, orig_states[gtu][step + 1].pos) > 0:
                driven_distance_sim -= math.dist(orig_states[gtu][step].pos, orig_states[gtu][step + 1].pos)
                step += 1
            cut_states = orig_states.get(gtu)[:step]
            orig_states.update({gtu: cut_states})
            if len(orig_states.get(gtu)) == 0:
                to_remove.append(gtu)
        elif driven_distance_sim > driven_distance_orig:
            while driven_distance_orig - math.dist(sim_states[gtu][step].pos, sim_states[gtu][step + 1].pos) > 0:
                driven_distance_orig -= math.dist(sim_states[gtu][step].pos, sim_states[gtu][step + 1].pos)
                step += 1
            cut_states = sim_states.get(gtu)[:step]
            sim_states.update({gtu: cut_states})

    for gtu in to_remove:
        del orig_states[gtu]

    return orig_states, sim_states


def limit_data_by_time(orig_states: dict, sim_states: dict) -> Tuple[dict, dict]:
    """
    Limits the data in order to have the same trajectory length for two gtus with the same id.
    """
    to_remove = []
    for gtu in orig_states.keys():
        if gtu not in sim_states.keys():
            to_remove.append(gtu)
            continue

        min_orig = min([s.timestep for s in orig_states.get(gtu)])
        max_orig = max([s.timestep for s in orig_states.get(gtu)])
        min_sim = min([s.timestep for s in sim_states.get(gtu)])
        max_sim = max([s.timestep for s in sim_states.get(gtu)])

        first_t = max(min_orig, min_sim)
        last_t = min(max_orig, max_sim)

        orig_states.update({gtu: [s for s in orig_states.get(gtu) if last_t >= s.timestep >= first_t]})
        sim_states.update({gtu: [s for s in sim_states.get(gtu) if last_t >= s.timestep >= first_t]})

        if len(orig_states.get(gtu)) == 0 or len(sim_states.get(gtu)) == 0:
            to_remove.append(gtu)

    for gtu in to_remove:
        del orig_states[gtu]
        if gtu in sim_states.keys():
            del sim_states[gtu]

    return orig_states, sim_states


def match_vehicle_ids(orig_data: dict, sim_data: dict) -> dict:
    """
    Matches the simulated data to the right vehicle IDs
    """
    new_sim_data = {}

    to_match_data = []
    point_to_id_lookup = {}
    for gtu_id in orig_data.keys():
        if gtu_id in sim_data.keys():
            orig = orig_data.get(gtu_id)[0]
            sim = sim_data.get(gtu_id)[0]
            if math.dist(orig.pos, sim.pos) > 3 or math.fabs((orig.length + orig.width) - (sim.length + sim.width)) > 0:
                to_match_data.append(sim_data.get(gtu_id))
                point_to_id_lookup.update({(orig.pos[0], orig.pos[1], orig.length * 10000, orig.width * 10000): gtu_id})
            else:
                new_sim_data.update({gtu_id: sim_data.get(gtu_id)})
        else:
            orig = orig_data.get(gtu_id)[0]
            point_to_id_lookup.update({(orig.pos[0], orig.pos[1], orig.length * 10000, orig.width * 10000): gtu_id})

    if len(to_match_data) == 0:
        return new_sim_data

    tree = KDTree([[p1, p2, l, w] for (p1, p2, l, w) in point_to_id_lookup.keys()])

    matched = set()

    for data in to_match_data:
        dist, ind = tree.query([data[0].pos[0], data[0].pos[1], data[0].length * 10000, data[0].width * 10000])
        best_match = tree.data[ind]
        matched_id = point_to_id_lookup.get((best_match[0], best_match[1], best_match[2], best_match[3]))
        if matched_id in matched:
            raise Exception(f"ID {matched_id} has been matched twice")
        matched.add(matched_id)

        new_sim_data.update({matched_id: data})

    return new_sim_data


class DataCollector:
    def __init__(self, timestep: float, original: Scenario, simulation: Scenario):
        self.timestep = timestep
        self.original_scenario = original
        self.simulated_scenario = simulation

    def get_vehicle_states(
        self, timespan: int, warm_up: float, filter_time: bool, filter_distance: bool, match_ids=False
    ) -> Tuple[dict, dict]:
        """
        Extracts the vehicle states from each gtu for the original and simulated scenarios and performs some
        preprocessing before the actual evaluation
        """

        orig_states = get_states_by_gtu(self.original_scenario, timespan, self.timestep, 0)
        sim_states = get_states_by_gtu(self.simulated_scenario, timespan, self.timestep, warm_up)

        if match_ids:
            sim_states = match_vehicle_ids(orig_states, sim_states)

        if filter_time:
            return limit_data_by_time(orig_states, sim_states)
        if filter_distance:
            return limit_data_by_distance(orig_states, sim_states)

        return orig_states, sim_states
