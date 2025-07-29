from commonroad.scenario.lanelet import LaneletNetwork
from commonroad.scenario.scenario import Scenario
from shapely import LineString
import pyperclip

from commonroad_ots.abstractions.abstraction_level import AbstractionLevel
from commonroad_ots.abstractions.frame_factors import get_frame_factor
from commonroad_ots.evaluation.InfrastructureMetrics import (
    calculate_vehicles_in_simulation,
    calculate_mean_velocity_over_time,
    calculate_spawn_frequency,
)
from commonroad_ots.evaluation.NDTW import calculate_scores_ndtw
from commonroad_ots.evaluation.RMSE import calculate_scores_rmse
from commonroad_ots.evaluation.SpawnDelay import calculate_spawn_delay
from commonroad_ots.evaluation.data_collector import DataCollector


class EvaluationExecutor:
    def __init__(
        self,
        original_scenario: Scenario,
        simulated_scenario: Scenario,
        configuration: AbstractionLevel,
        warm_up: float,
    ) -> None:
        """
        Constructor of the EvaluationExecutor class.

        Parameters
        ----------
        original_scenario: Scenario
        simulated_scenario: Scenario
        configuration: AbstractionLevel
        warm_up: float
        """
        self.original_scenario = original_scenario
        self.simulated_scenario = simulated_scenario
        self.configuration = configuration
        self.warm_up = warm_up

    def evaluate(
        self,
        time_to_consider: int,
        conversion_time: float = -1,
        simulation_time: float = -1,
        retransfer_time: float = -1,
    ) -> None:
        """
        Calculates different metrics based on the abstraction level.

        Parameters
        ----------
        time_to_consider: int
        conversion_time
        simulation_time
        retransfer_time
        """
        # evaluate similarity
        collector = DataCollector(self.original_scenario.dt, self.original_scenario, self.simulated_scenario)
        only_draw_mean = False

        ndtw_ndim_mu = -1
        rmse_mu = -1
        rmse_sigma = -1
        rmse_median = -1
        spawn_delay_mu = -1
        spawn_delay_sigma = -1
        rho_recorded_mu = -1
        rho_recorded_sigma = -1
        rho_mu = -1
        rho_sigma = -1
        v_recorded_mu = -1
        v_recorded_sigma = -1
        v_mu = -1
        v_sigma = -1
        spawn_frequency_recorded_mu = -1
        spawn_frequency_mu = -1

        match self.configuration:
            case AbstractionLevel.RESIMULATION:
                time_limited_states = collector.get_vehicle_states(time_to_consider, 0, True, False)
                distance_limited_states = collector.get_vehicle_states(time_to_consider, 0, False, True)
                ndtw_ndim_mu = calculate_scores_ndtw(distance_limited_states[0], distance_limited_states[1], False)
                rmse_values = calculate_scores_rmse(time_limited_states[0], time_limited_states[1])
                rmse_mu = rmse_values[0][0]
                rmse_sigma = rmse_values[1][0]
                rmse_median = rmse_values[2][0]

            case AbstractionLevel.DELAY:
                time_limited_states = collector.get_vehicle_states(time_to_consider, 0, True, False, True)
                distance_limited_states = collector.get_vehicle_states(time_to_consider, 0, False, True, True)
                ndtw_ndim_mu = calculate_scores_ndtw(distance_limited_states[0], distance_limited_states[1], False)
                rmse_values = calculate_scores_rmse(time_limited_states[0], time_limited_states[1])
                rmse_mu = rmse_values[0][0]
                rmse_sigma = rmse_values[1][0]
                rmse_median = rmse_values[2][0]
                spawn_delay_mu, spawn_delay_sigma = calculate_spawn_delay(
                    distance_limited_states[0], distance_limited_states[1], self.original_scenario.dt
                )
            case (AbstractionLevel.DEMAND | AbstractionLevel.INFRASTRUCTURE | AbstractionLevel.RANDOM):
                only_draw_mean = True

        vehicle_data = collector.get_vehicle_states(time_to_consider, self.warm_up, False, False)
        orig_frame_factor, sim_frame_factor = get_frame_factor(
            str(self.original_scenario.scenario_id).split("_")[1], str(self.configuration).split(".")[1]
        )
        rho_recorded_mu, rho_recorded_sigma, rho_mu, rho_sigma = calculate_vehicles_in_simulation(
            self.warm_up / self.original_scenario.dt,
            vehicle_data[0],
            vehicle_data[1],
            get_total_road_length(self.original_scenario.lanelet_network),
            self.original_scenario.dt,
            only_draw_mean,
            orig_frame_factor,
            sim_frame_factor,
        )

        v_recorded_mu, v_recorded_sigma, v_mu, v_sigma = calculate_mean_velocity_over_time(
            self.warm_up / self.original_scenario.dt,
            vehicle_data[0],
            vehicle_data[1],
            self.original_scenario.dt,
            only_draw_mean,
        )

        spawn_frequency_recorded_mu, spawn_frequency_mu = calculate_spawn_frequency(
            vehicle_data[0], vehicle_data[1], self.original_scenario.dt
        )

        output_string = (
            f"{ndtw_ndim_mu}, {rmse_mu}, {rmse_sigma}, {rmse_median}, {spawn_delay_mu}, "
            f"{spawn_delay_sigma}, {rho_recorded_mu}, {rho_recorded_sigma}, {rho_mu}, {rho_sigma}, "
            f"{v_recorded_mu}, {v_recorded_sigma}, {v_mu}, {v_sigma}, {spawn_frequency_recorded_mu}, "
            f"{spawn_frequency_mu}, {conversion_time}, {simulation_time}, {retransfer_time}"
        )

        pyperclip.copy(output_string)

        print(f"Parsable: {output_string}")


def get_total_road_length(lanelet_network: LaneletNetwork) -> float:
    """
    Calculates to total length of all lanelets in the lanelet network

    Parameters
    ----------
    lanelet_network: LaneletNetwork
    """
    length = 0
    for lane in lanelet_network.lanelets:
        length += LineString(lane.center_vertices).length
    print("Lanelet network length: ", length)
    return length
