import math
from pathlib import Path
import time
from typing import Tuple
import tempfile

import numpy as np
import pandas as pd
from commonroad.common.file_writer import CommonRoadFileWriter
from commonroad.common.writer.file_writer_interface import OverwriteExistingFile
from commonroad.geometry.shape import Rectangle
from commonroad.planning.planning_problem import PlanningProblemSet
from commonroad.prediction.prediction import TrajectoryPrediction
from commonroad.scenario.obstacle import DynamicObstacle, ObstacleType
from commonroad.scenario.scenario import Scenario, ScenarioID
from commonroad.scenario.state import CustomState, InitialState
from commonroad.scenario.trajectory import Trajectory
from nl.tudelft.simulation.dsol.simulators import RunState
from numpy import ndarray
from org.opentrafficsim.kpi.sampling import SamplerData
from org.opentrafficsim.road.network.sampling import RoadSampler
from org.opentrafficsim.core.dsol import OtsAnimator

from commonroad_ots.abstractions.abstraction_level import AbstractionLevel


def collect_trajectories(
    simulator: OtsAnimator, sampler: RoadSampler, max_time: float, warmup: float, gui_enabled: bool, keep_warmup: bool
) -> Tuple[ndarray, float]:
    """
    Returns the exported OTS trajectories as a numpy array

    Parameters
    ----------
    simulator: Simulator
        The OTS simulator.
    sampler: RoadSampler
        The CR road sampler.
    max_time: float
        Time in sec to export trajectories.
    warmup: float
        The warm up time for the simulation
    gui_enabled: bool
        Whether the gui is enabled or not
    keep_warmup: bool
        Whether to keep to warm up data in the export
     Returns
    -------
    data: ndarray containing the trajectory exports
    """
    time_start_sim = time.time()
    restart_count = 0
    while simulator.getSimulatorTime().getSI() <= max_time + warmup:
        if simulator.getRunState() == RunState.ENDED:
            break
        if not gui_enabled and simulator.getRunState() != RunState.STARTED:
            if restart_count < 5:
                restart_count += 1
                print("Restarted Simulation due to an error.")
                simulator.start()
            else:
                raise RuntimeError(f"Giving up on simulation after {restart_count} unsuccessfull restart attempts.")

        time.sleep(0.01)

    if not simulator.isStoppingOrStopped():
        simulator.stop()
    time_end_sim = time.time()

    trajectory_data_file_name = str(hash(str(hash(simulator) + hash(sampler) + hash(max_time)))) + ".csv"
    with tempfile.TemporaryDirectory() as tempdir:
        trajectory_data_file_path = Path(tempdir) / trajectory_data_file_name
        sampler.getSamplerData().writeToFile(str(trajectory_data_file_path), SamplerData.Compression.NONE)
        data = pd.read_csv(trajectory_data_file_path)

    if not keep_warmup:
        data = data[data["t"] >= warmup]
        data.reset_index(inplace=True, drop=True)
    simulation_time = time_end_sim - time_start_sim
    return data.to_numpy(), simulation_time


def check_interpolation(data: ndarray, timestep: float) -> bool:
    """
    Checks if there are missing values in the exported trajectories and interpolates them if necessary

    Parameters
    ----------
    data: ndarray
        The trajectory data for one gtu
    timestep: float
        the time step size

     Returns
    -------
    success
        True if there were no missing values or the missing values could be interpolated, False otherwise
    """

    first_missing = -1
    last_missing = -1
    for i in range(len(data) - 1):
        if data[i + 1][4] - data[i][4] > (timestep + 0.001):
            first_missing = int(round(data[i][4] / timestep) + 1)
            last_missing = int(round(data[i + 1][4] / timestep) - 1)
            break

    if (first_missing == -1 and last_missing == -1) or first_missing == last_missing:
        return True

    print("Interpolating values for gtu", data[0][3], "between time steps", first_missing, last_missing)

    entry_first = data[(first_missing - 1) * timestep]
    entry_last = data[(last_missing + 1) * timestep]

    t_step = last_missing - first_missing + 2
    v_step = (entry_last[6] - entry_first[6]) / t_step
    a_step = (entry_last[7] - entry_first[7]) / t_step
    x_step = (entry_last[8] - entry_first[8]) / t_step
    y_step = (entry_last[9] - entry_first[9]) / t_step
    dir_step = (entry_last[10] - entry_first[10]) / t_step

    gtu_id = entry_first[3]

    # add missing values to dataframe
    for i in range(1, int(t_step)):

        new_row = [
            -1,
            -1,
            -1,
            gtu_id,
            round((first_missing + i - 1) * timestep, 3),
            -1,
            entry_first[6] + i * v_step,
            entry_first[7] + i * a_step,
            entry_first[8] + i * x_step,
            entry_first[9] + i * y_step,
            entry_first[10] + i * dir_step,
            entry_first[11],
            entry_first[12],
            entry_first[3],
        ]
        np.append(data, [new_row], axis=0)

    sorted(data, key=lambda d: d[4])  # sort again after adding new interpolated entries

    return True


def filter_data(data: ndarray, timestep: float) -> ndarray:
    """
    Removes all entries with timestamps that are not a multiple of the step size (may exist due to internal OTS events)

    Parameters
    ----------
    data: ndarray
        The OTS trajectory data to be filtered
    timestep: float
        the time step size
    """
    to_remove = []
    for d in data:
        if not math.isclose(
            int(round(d[4] * 100, 5) / (timestep * 100)) - (round(d[4] * 100, 5) / (timestep * 100)), 0, abs_tol=0.001
        ):
            to_remove.append(False)
        else:
            to_remove.append(True)

    return data[to_remove]


def filter_on_gtu(data: ndarray, gtu_id: int) -> ndarray:
    """
    Filters the trajectory data for one specific gtu id

    Parameters
    ----------
    data: ndarray
        The OTS trajectory data to be filtered
    gtu_id: int
        the gtu id to filter for
    """
    filter_arr = []
    for d in data:
        if d[3] == gtu_id:
            filter_arr.append(True)
        else:
            filter_arr.append(False)

    return data[filter_arr]


def export_as_cr_scenario(
    trajectory_data: ndarray,
    scenario: Scenario,
    abstraction_type: AbstractionLevel,
    warmup=0,
    write_to_file=False,
    keep_ids=True,
) -> Tuple[Scenario, float]:
    """
    Transfers a set of GTU trajectories back to CommonRoad.

    Parameters
    ----------
    trajectory_data: ndarray
        The OTS trajectory data
    scenario: Scenario
        The original CR scenario
    abstraction_type: str
        The abstraction type used for the simulation
    write_to_file: bool
        If True, the scenario is written to a file.
    warmup: int
        The warm up time of the resimulation (everything before this time will not be exported)
    keep_ids: bool
        Whether to keep the OTS GTU IDs for the export or not
    """

    # In the following only indices are used to retrieve data from the exported trajectory_data columns
    # Indices mapping: 0: TrajectoryId, 1: LinkId, 2: LaneId, 3:GtuId, 4: timestep, 5: position, 6: velocity
    #                   7: acceleration, 8: x, 9: y, 10: dir, 11: Length, 12: Width, 13: GtuType

    time_start_retransfer = time.time()
    # remove old dynamic obstacles
    for dyn_ob in scenario.dynamic_obstacles:
        scenario.remove_obstacle(dyn_ob)

    trajectory_data = filter_data(trajectory_data, scenario.dt)

    factor = 1 / scenario.dt
    generated_gtus = set([d[3] for d in trajectory_data])

    for gtu in generated_gtus:
        data = filter_on_gtu(trajectory_data, gtu)  # filter trajectory for current gtu id
        data = sorted(data, key=lambda d: d[4])
        if len(data) <= 1:
            print("No trajectory data found for gtu ", gtu)
            continue
        if not check_interpolation(data, scenario.dt):
            print("Error during the interpolation for gtu", gtu)

        initial_time = int(float(data[0][4]) * factor)

        dynamic_obstacle_initial_state = InitialState(
            position=np.array([data[0][8], data[0][9]]),
            velocity=data[0][6],
            orientation=data[0][10],
            acceleration=data[0][7],
            time_step=int(initial_time - warmup * factor),
        )

        # transfer data into a dict with the time steps as a key to deal with duplicate time steps
        pos_by_time = dict()
        for entry in data:
            pos = [entry[8], entry[9], entry[10]]
            if entry[4] * factor in pos_by_time:
                pos_by_time.get(int(round(entry[4] * factor))).append(pos)
            else:
                pos_by_time.update({int(round(entry[4] * factor)): [pos]})

        size = len(pos_by_time.keys())

        if size <= 1:
            # we need to filter again at this point, incase there were multiple entries in the dataset,
            # but all with the same timestep
            continue

        state_list = []
        for i in range(initial_time + 1, initial_time + size):
            # compute new position
            index = i
            entry = pos_by_time.get(index)
            if entry is None:
                print(f"Scenario {scenario.scenario_id}: Missing entry for gtu {gtu} at timestamp", i / factor)
                if pos_by_time.get(index - 1) is not None:
                    index -= 1
                    entry = pos_by_time.get(index)
                    print("Replaced value with previous entry")
            pos = entry[
                0
            ]  # always take the first entry of the trajectory export, incase time steps occur more than one

            # create new state
            try:
                vel = data[index - initial_time][6]
                acc = data[index - initial_time][7]
            except Exception as e:
                print(f"Error in scenario {scenario.scenario_id} for GTU {gtu} at timestamp {i}")
                raise e
            new_state = CustomState(
                position=np.array([pos[0], pos[1]]),
                velocity=vel,
                orientation=pos[2],
                acceleration=acc,
                time_step=int(i - warmup * factor),
            )
            # add new state to state_list
            state_list.append(new_state)

        # create the trajectory of the obstacle, starting at time step 1
        dynamic_obstacle_trajectory = Trajectory(int(initial_time - warmup * factor) + 1, state_list)

        # create the prediction using the trajectory and the shape of the obstacle
        dynamic_obstacle_shape = Rectangle(width=float(data[0][12]), length=float(data[0][11]))
        dynamic_obstacle_prediction = TrajectoryPrediction(dynamic_obstacle_trajectory, dynamic_obstacle_shape)

        if keep_ids:
            dynamic_obstacle_id = int(gtu)
        else:
            dynamic_obstacle_id = int(gtu) + 20000

        gtu_type = str(data[0][13])
        if "BUS" in gtu_type:
            dynamic_obstacle_type = ObstacleType.BUS
        elif "TRUCK" in gtu_type:
            dynamic_obstacle_type = ObstacleType.TRUCK
        elif "MOTORCYCLE" in gtu_type:
            dynamic_obstacle_type = ObstacleType.MOTORCYCLE
        else:
            dynamic_obstacle_type = ObstacleType.CAR

        # generate the dynamic obstacle according to the specification
        dynamic_obstacle = DynamicObstacle(
            dynamic_obstacle_id,
            dynamic_obstacle_type,
            dynamic_obstacle_shape,
            dynamic_obstacle_initial_state,
            dynamic_obstacle_prediction,
        )

        # add dynamic obstacle to the scenario
        scenario.add_objects(dynamic_obstacle)

    time_end_retransfer = time.time()
    retransfer_time = time_end_retransfer - time_start_retransfer

    if write_to_file:
        planning_set = PlanningProblemSet()

        new_scenario_id = ScenarioID(
            False,
            scenario.scenario_id.country_id,
            scenario.scenario_id.map_name,
            scenario.scenario_id.map_id,
            abstraction_type.value + 1,
            scenario.scenario_id.obstacle_behavior,
            scenario.scenario_id.prediction_id,
            scenario.scenario_id.scenario_version,
        )
        scenario.scenario_id = new_scenario_id

        print(str(new_scenario_id))

        filename = str(new_scenario_id) + ".xml"
        fw = CommonRoadFileWriter(
            scenario, planning_set, "Florian Finkeldei, Christoph Thees", "TUM", "OpenTrafficSim", scenario.tags
        )
        path = Path(__file__).parents[1].joinpath("../resources/simulations")
        path.mkdir(parents=True, exist_ok=True)

        fw.write_to_file(str(path.joinpath(filename)), OverwriteExistingFile.ALWAYS)

    return scenario, retransfer_time
