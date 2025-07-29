import matplotlib.pyplot as plt
import matplot2tikz
from commonroad.common.file_reader import CommonRoadFileReader
from commonroad.visualization.mp_renderer import MPRenderer
from IPython.display import clear_output

file_path = "../../resources/abstraction/C-DEU_MONAWest-2_1_T-299.xml"

# The following code is taken from https://commonroad.in.tum.de/getting-started and just used to visualize the original
# CR scenario

# read in the scenario and planning problem set
scenario, planning_problem_set = CommonRoadFileReader(file_path).open()

timestep = 10
for i in range(timestep, timestep + 1):
    # plot the planning problem and the scenario for the fifth time step
    plt.figure(figsize=(40, 30))
    rnd = MPRenderer()
    clear_output(wait=True)
    rnd.draw_params.time_begin = i
    rnd.draw_params.time_end = i
    scenario.draw(rnd)
    # planning_problem_set.draw(rnd)
    rnd.render()
    plt.axis("off")
    # plt.show()
    plt.savefig("CR_network.png", bbox_inches="tight")
    matplot2tikz.save("CR_network.tikz")
