from copy import deepcopy
from pathlib import Path
from typing import List
from os import getpid

import numpy as np
from commonroad.common.file_reader import CommonRoadFileReader
from commonroad.geometry.shape import Circle
from commonroad.scenario.scenario import Scenario

from commonroad_ots.conversion.gtus import create_gtus

# OpenTrafficSim imports
from commonroad_ots.conversion.main import Conversion
from commonroad_ots.conversion.retransfer import collect_trajectories, export_as_cr_scenario
from commonroad_ots.conversion.utility import get_scenario_length
from commonroad_ots.evaluation.data_collector import DataCollector
from commonroad_ots.evaluation.NDTW import calculate_scores_ndtw
from nl.tudelft.simulation.jstats.distributions import DistNormal
from nl.tudelft.simulation.jstats.streams import MersenneTwister
from org.djunits.unit import AccelerationUnit
from org.djunits.value.vdouble.scalar import Acceleration
from org.opentrafficsim.base.parameters import ParameterTypes
from scipy.optimize import differential_evolution, OptimizeResult
from tqdm import tqdm

import multiprocessing as mp

mp.set_start_method("spawn", force=True)


class Calibration:
    """
    Class to handle the calibration process.
    """

    def __init__(self) -> None:
        """
        Constructor of the class.
        """
        self.number_of_selected_scenarios: int = None
        self.scenarios: List[Scenario] = None
        self.selected_scenarios: List[Scenario] = None

    def load_scenarios(
        self, scenarios_path: Path, number_of_selected_scenarios: int, max_number_of_loaded_scenarios: int = 999999
    ) -> None:
        """
        Load the scenarios from the given path and initialize _selected_ scenarios.

        Parameters
        ----------
        scenarios_path: Path
            The path to the scenarios.
        number_of_selected_scenarios: int
            The number of scenarios to select for the calibration process.
        max_number_of_loaded_scenarios: int
            The maximum number of scenarios to select for the calibration process.
        """
        if self.scenarios is not None:
            raise ValueError("Scenarios already loaded.")

        self.scenarios = [
            CommonRoadFileReader(file).open()[0]
            for file in tqdm(sorted(scenarios_path.glob("*.xml"))[:max_number_of_loaded_scenarios])
        ]
        assert len(self.scenarios) > number_of_selected_scenarios
        self.number_of_selected_scenarios = number_of_selected_scenarios
        self.update_selected_scenarios()
        print(f"Loaded {len(self.scenarios)} scenarios. Selected {len(self.selected_scenarios)} scenarios.")

    def update_selected_scenarios(self, *args) -> None:
        """
        Randomly select n scenarios. This function is used as a callback for the differential evolution algorithm.
        """
        if self.scenarios is None:
            raise ValueError("Scenarios not loaded.")

        self.selected_scenarios = list(
            np.random.choice(self.scenarios, self.number_of_selected_scenarios, replace=False)
        )

    def objective_function(self, x: np.ndarray) -> float:
        """
        Objective function for the calibration process.

        Parameters
        ----------
        x: np.ndarray
            The parameter set of the human driver model.

        Returns
        -------
        objective: float
            The objective value.
        """
        # print scenario IDs of the selected scenarios
        # print([str(scenario.scenario_id) for scenario in self.selected_scenarios])
        # initialize result vector
        print(
            f"################################################################################### \n"
            f"# Starting calibration with parameter set: {x}\n"
            f"# Process ID: {getpid()}\n"
            f"################################################################################### \n"
        )
        metric_results = np.zeros(self.number_of_selected_scenarios)
        stream = MersenneTwister(123)
        parameters = {
            ParameterTypes.FSPEED: DistNormal(stream, x[0] / 120, x[1] / 120),  # 123.7 km/h, 12.0 km/h
            ParameterTypes.A: Acceleration(x[2], AccelerationUnit.SI),  # 0.8 m/s^2
        }

        # for each scenario in selected scenarios
        for ind, scenario in enumerate(self.selected_scenarios):
            # run simulation -- using the parameter set x
            print(f"Running simulation for scenario {scenario.scenario_id} with parameter set {x}.")
            conv = Conversion()
            sim_scenario = deepcopy(scenario)
            simulator, model = conv.setup_simulator()
            shift_priority_signs = "Bendplatz" not in str(sim_scenario.scenario_id)
            network = conv.create_network(simulator, sim_scenario.lanelet_network, shift_priority_signs)

            obstacles = {}
            for o in sim_scenario.dynamic_obstacles:
                if isinstance(o.obstacle_shape, Circle):
                    # skip pedestrians
                    continue
                else:
                    obstacles.update({o.obstacle_id: o})

            create_gtus(
                network,
                simulator,
                sim_scenario.lanelet_network,
                conv.group_id_by_lane_id,
                obstacles,
                sim_scenario.dt,
                sim_scenario.scenario_id,
                parameters,
                1234,
                sim_scenario,
            )
            model.setNetwork(network)
            sampler = conv.setup_analytics(network, 1 / sim_scenario.dt)

            conv.start_resimulation(False, simulator, model)

            trajectories, simulation_time = collect_trajectories(
                simulator, sampler, get_scenario_length(scenario), 0, False, True
            )

            simulated, _ = export_as_cr_scenario(
                trajectories,
                sim_scenario,
                "Calibration",
                0,
                False,
                True,
            )

            # compute metric
            collector = DataCollector(scenario.dt, scenario, simulated)
            distance_limited_states = collector.get_vehicle_states(40, 0, False, True)
            metric = calculate_scores_ndtw(distance_limited_states[0], distance_limited_states[1], False)

            # add metric to result vector
            print(f"Metric value: {metric}")
            metric_results[ind] = metric

        # return the sum of the metrics
        objective = np.sum(metric_results)
        print(f"Objective value: {objective}")
        return objective

    def execute_calibration(self, number_of_workers: int) -> OptimizeResult:
        """
        Execute the calibration process.
        """
        pool = mp.Pool(number_of_workers)

        calibration_result = differential_evolution(
            self.objective_function,
            bounds=[(100, 140), (8, 16), (0, 2)],
            callback=self.update_selected_scenarios,
            updating="deferred",
            maxiter=4,
            popsize=12,
            init="latinhypercube",
            disp=True,
            polish=False,
            tol=0.1,
            workers=pool.map,
        )
        return calibration_result
