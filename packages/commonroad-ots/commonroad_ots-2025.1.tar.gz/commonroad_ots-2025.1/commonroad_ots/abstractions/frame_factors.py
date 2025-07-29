from typing import Tuple

orig_factors = {
    "MONAEast-2": 0.75,
    "MONAMerge-2": 0.6,
    "MONAWest-2": 0.9,
    "AachenBendplatz-1": 0.7,
    "AachenHeckstrasse-1": 0.78,
    "LocationCLower4-1": 0.87,
}

sim_factors = {
    "MONAEast-2_RESIMULATION": 0.86,
    "MONAEast-2_DELAY": 0.86,
    "MONAMerge-2_RESIMULATION": 0.8,
    "MONAMerge-2_DELAY": 0.80,
    "MONAWest-2_RESIMULATION": 0.96,
    "MONAWest-2_DELAY": 0.96,
    "AachenBendplatz-1_RESIMULATION": 0.85,
    "AachenBendplatz-1_DELAY": 0.85,
    "AachenBendplatz-1_OD_ABSTRACTION": 0.85,
    "AachenBendplatz-1_INFRASTRUCTURE_ABSTRACTION": 0.85,
    "AachenHeckstrasse-1_RESIMULATION": 0.90,
    "AachenHeckstrasse-1_DELAY": 0.90,
    "LocationCLower4-1_RESIMULATION": 0.94,
    "LocationCLower4-1_DELAY": 0.94,
}


def get_frame_factor(scenario_name: str, abstraction_name: str) -> Tuple[float, float]:
    """
    Returns an (estimated) factor on how large the detection frame of the recording is compared
    to the actual road network
    """
    orig_factor = 1
    sim_factor = 1
    if scenario_name in orig_factors.keys():
        orig_factor = orig_factors.get(scenario_name)
    else:
        print(f"Could not find recording's frame factor for {scenario_name}.")
    if scenario_name + "_" + abstraction_name in sim_factors.keys():
        sim_factor = sim_factors.get(scenario_name + "_" + abstraction_name)
    else:
        print(f"Could not find frame factor for {scenario_name} and {abstraction_name} abstraction.")
    return orig_factor, sim_factor
