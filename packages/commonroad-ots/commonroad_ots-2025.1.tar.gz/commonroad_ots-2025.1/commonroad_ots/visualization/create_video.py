from pathlib import Path

from commonroad.scenario.scenario import Scenario
from commonroad.visualization.mp_renderer import MPRenderer


def create_video_wrapper(
    scenario: Scenario, name: str, directory: Path = Path(__file__).parents[2].joinpath("videos")
) -> None:
    """
    Wrapper function to create a video from a scenario.

    Parameters
    ----------
    scenario: Scenario
        The scenario to create a video from.
    name: str
        The name of the video file.
    directory: Path
        The directory to save the video in.
    """
    # time range
    time_start = min([obstacle.prediction.initial_time_step for obstacle in scenario.dynamic_obstacles])
    time_end = max([obstacle.prediction.final_time_step for obstacle in scenario.dynamic_obstacles])

    # figure size
    x_min, x_max, y_min, y_max = float("inf"), -float("inf"), float("inf"), -float("inf")
    for lanelet in scenario.lanelet_network.lanelets:
        for point in lanelet.polygon.vertices:
            x_min = min(x_min, point[0])
            x_max = max(x_max, point[0])
            y_min = min(y_min, point[1])
            y_max = max(y_max, point[1])
    figure_size = [(x_max - x_min) / 10, (y_max - y_min) / 10]

    # folder structure
    directory.mkdir(parents=True, exist_ok=True)
    video_file = directory.joinpath(name)

    # rendering
    rnd = MPRenderer()
    scenario.draw(rnd)
    rnd.draw_params.time_begin = time_start
    rnd.draw_params.time_end = time_end
    rnd.create_video(scenario.obstacles, str(video_file), fig_size=figure_size)
