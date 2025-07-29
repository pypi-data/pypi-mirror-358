import random
import time
from copy import deepcopy
from typing import Optional, Tuple

from commonroad.common.common_lanelet import LaneletType
from commonroad.geometry.shape import Circle
from commonroad.scenario.lanelet import LaneletNetwork

from commonroad_ots.abstractions.abstraction_level import AbstractionLevel
from commonroad_ots.abstractions.warm_up_estimator import warm_up_estimator
from commonroad.scenario.scenario import Scenario, Tag

from commonroad_ots.conversion.default_speed_limit import get_default_speed_limit_for_lanelet_type
from commonroad_ots.conversion.gtus import (
    create_gtus,
    create_gtu_generators,
    generate_random_generators,
    create_injections,
)
from commonroad_ots.conversion.main import Conversion
from commonroad_ots.conversion.retransfer import export_as_cr_scenario, collect_trajectories
from commonroad_ots.conversion.utility import get_scenario_length


def group_obs_by_initial_lanelet(lanelet_network: LaneletNetwork, obstacles: dict) -> dict:
    """
    Groups all the obstacles by their initial lanelet id

    Parameters
    ----------
    lanelet_network: LaneletNetwork
    obstacles: dict
    """
    res = dict()

    for obs in obstacles.values():
        try:
            initial_lanelet = lanelet_network.find_lanelet_by_id(
                lanelet_network.find_most_likely_lanelet_by_state([obs.initial_state])[0]
            )
        except Exception:
            continue
        if initial_lanelet not in res.keys():
            res.update({initial_lanelet: list()})
        entry = res.get(initial_lanelet)
        entry.append(obs)
        res.update({initial_lanelet: entry})

    return res


class SimulationExecutor:
    def __init__(
        self,
        original_scenario: Scenario,
        configuration: AbstractionLevel,
        gui_enabled: bool,
        parameters: dict,
        seed: int,
        write_to_file: bool,
        keep_warmup=False,
        max_time: Optional[float] = None,
    ) -> None:
        """
        Constructor of the SimulationExecutor class.

        Parameters
        ----------
        original_scenario: Scenario
        configuration: AbstractionLevel
        gui_enabled: bool
        parameters: dict
        keep_warmup: bool
        max_time: Optional[float]
            Number of seconds the simulation should be run (excludes the warmup time).
            If not set, the length will be determined automatically from the input scenario.
        """
        self.original_scenario = original_scenario
        self.simulated_scenario = deepcopy(original_scenario)
        self.configuration = configuration
        self.gui_enabled = gui_enabled
        self.parameters = parameters
        self.lanelet_flow = dict()
        self.keep_warmup = keep_warmup
        self.seed = seed if seed is not None else random.randint(0, 100000)
        self.write_to_file = write_to_file
        if max_time is None:
            self.max_time = get_scenario_length(original_scenario)
        else:
            self.max_time = max_time

    def execute(self) -> Tuple[Scenario, float, float, float, float]:
        """
        Executes the simulation according to the given configuration.

        Returns
        -------
        Scenario
        """
        time_start = time.time()
        conv = Conversion()
        simulator, model = conv.setup_simulator()
        shift_priority_signs = "Bendplatz" not in str(self.original_scenario.scenario_id)
        network = conv.create_network(simulator, self.original_scenario.lanelet_network, shift_priority_signs)
        obstacles = dict()
        initial_obstacles = dict()
        warmup = 0
        keep_ids = True

        speed_limits = dict()
        for sign in self.original_scenario.lanelet_network.traffic_signs:
            if sign.traffic_sign_elements[0].traffic_sign_element_id.value in ["274", "274.1", "R2-1"]:
                speed_limits.update({sign.traffic_sign_id: float(sign.traffic_sign_elements[0].additional_values[0])})

        for o in self.simulated_scenario.dynamic_obstacles:
            if isinstance(o.obstacle_shape, Circle):
                # skip pedestrians
                continue
            if o.initial_state.time_step <= 0:
                initial_obstacles.update({o.obstacle_id: o})
            else:
                obstacles.update({o.obstacle_id: o})

        match self.configuration:
            case AbstractionLevel.RESIMULATION:
                create_gtus(
                    network,
                    simulator,
                    self.simulated_scenario.lanelet_network,
                    conv.group_id_by_lane_id,
                    initial_obstacles | obstacles,
                    self.simulated_scenario.dt,
                    self.simulated_scenario.scenario_id,
                    self.parameters,
                    self.seed,
                    self.original_scenario,
                )

            case AbstractionLevel.DELAY:
                # spawn initial GTUs at exact positions
                create_gtus(
                    network,
                    simulator,
                    self.simulated_scenario.lanelet_network,
                    conv.group_id_by_lane_id,
                    initial_obstacles,
                    self.simulated_scenario.dt,
                    self.simulated_scenario.scenario_id,
                    self.parameters,
                    self.seed,
                    self.original_scenario,
                )

                # use list generators for all later gtus
                create_injections(
                    network,
                    simulator,
                    self.simulated_scenario.lanelet_network,
                    conv.group_id_by_lane_id,
                    self.simulated_scenario.dt,
                    obstacles,
                    self.parameters,
                    self.seed,
                    self.original_scenario,
                )

            case AbstractionLevel.DEMAND:
                warmup = warm_up_estimator(self.simulated_scenario.lanelet_network)
                keep_ids = False

                create_gtu_generators(
                    network,
                    simulator,
                    self.simulated_scenario.lanelet_network,
                    conv.group_id_by_lane_id,
                    obstacles,
                    self.parameters,
                    self.seed,
                    self.original_scenario,
                )

            case AbstractionLevel.INFRASTRUCTURE:
                warmup = warm_up_estimator(self.simulated_scenario.lanelet_network)
                keep_ids = False

                grouped_obs = group_obs_by_initial_lanelet(self.simulated_scenario.lanelet_network, obstacles)

                self.lanelet_usage_infrastructure(
                    grouped_obs, len(self.simulated_scenario.dynamic_obstacles), speed_limits
                )

                create_gtu_generators(
                    network,
                    simulator,
                    self.simulated_scenario.lanelet_network,
                    conv.group_id_by_lane_id,
                    obstacles,
                    self.parameters,
                    self.seed,
                    self.original_scenario,
                    self.lanelet_flow,
                )

            case AbstractionLevel.RANDOM:
                warmup = warm_up_estimator(self.simulated_scenario.lanelet_network)
                keep_ids = False

                generate_random_generators(
                    network,
                    simulator,
                    self.simulated_scenario.lanelet_network,
                    conv.group_id_by_lane_id,
                    speed_limits,
                    self.parameters,
                    self.seed,
                )

        model.setNetwork(network)
        sampler = conv.setup_analytics(network, 1 / self.simulated_scenario.dt)

        time_end = time.time()
        conversion_time = time_end - time_start

        conv.start_resimulation(self.gui_enabled, simulator, model)

        trajectories, simulation_time = collect_trajectories(
            simulator, sampler, self.max_time, warmup, self.gui_enabled, self.keep_warmup
        )

        resimulated_scenario, retransfer_time = export_as_cr_scenario(
            trajectories,
            self.simulated_scenario,
            self.configuration,
            0 if self.keep_warmup else warmup,
            self.write_to_file,
            keep_ids,
        )

        simulator.cleanUp()

        return (
            resimulated_scenario,
            conversion_time,
            simulation_time,
            retransfer_time,
            warmup if self.keep_warmup else 0,
        )

    def lanelet_usage_infrastructure(
        self, grouped_obstacles: dict, dyn_obs_count: int, speed_limit_signs: dict
    ) -> None:
        """
        Computes the lanelet flow for each lanelet based on a load factor
        """
        lane_capacity = dict()
        for lanelet in grouped_obstacles.keys():
            speed_limit = get_default_speed_limit_for_lanelet_type(lanelet.lanelet_type)
            for sign_id in lanelet.traffic_signs:
                if sign_id in speed_limit_signs.keys():
                    speed_limit = speed_limit_signs.get(sign_id)

            l = sum([obs.obstacle_shape.length for obs in grouped_obstacles.get(lanelet)]) / len(
                grouped_obstacles.get(lanelet)
            )
            s_0 = 2.0  # m -- minimum distance between vehicles
            T = 1.45  # s -- desired time headway
            lane_capacity[lanelet.lanelet_id] = 60 * speed_limit / (l + (s_0 + speed_limit * T))

        load_factor = dyn_obs_count / sum(lane_capacity.values())

        for lanelet_id in lane_capacity.keys():
            self.lanelet_flow[lanelet_id] = lane_capacity[lanelet_id] * load_factor
