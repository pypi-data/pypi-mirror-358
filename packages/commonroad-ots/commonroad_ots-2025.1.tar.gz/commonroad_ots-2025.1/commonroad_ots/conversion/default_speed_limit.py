from typing import Set

from commonroad.common.common_lanelet import LaneletType


def get_default_speed_limit_for_lanelet_type(lanelet_types: Set[LaneletType]) -> float:

    """
    Determine the velocity limit based on the lanelet type.

    Parameters
    ----------
    lanelet_types: Set[LaneletType]
        Set of lanelet types.

    Returns
    -------
    velocity_limit: float
        Velocity limit in m/s.
    """
    velocity_limit = float("inf")
    for lt_type in lanelet_types:
        if lt_type in (
            LaneletType.BICYCLE_LANE,
            LaneletType.SIDEWALK,
            LaneletType.CROSSWALK,
            LaneletType.PARKING,
            LaneletType.BUS_STOP,
            LaneletType.DRIVE_WAY,
        ):
            velocity_limit = min(velocity_limit, 30 / 3.6)  # 8.33
        elif lt_type in (LaneletType.INTERSECTION, LaneletType.URBAN):
            velocity_limit = min(velocity_limit, 50 / 3.6)  # 13.89
        elif lt_type in (LaneletType.COUNTRY, LaneletType.BUS_LANE):
            velocity_limit = min(velocity_limit, 100 / 3.6)  # 27.78
        elif lt_type in (LaneletType.ACCESS_RAMP, LaneletType.EXIT_RAMP):
            velocity_limit = min(velocity_limit, 140 / 3.6)  # 38.89
        elif lt_type in (LaneletType.HIGHWAY, LaneletType.INTERSTATE, LaneletType.MAIN_CARRIAGE_WAY):
            velocity_limit = min(velocity_limit, 160 / 3.6)  # 44.44
        else:
            # we assume a default of 50km/h if the lanelet type is unknown
            velocity_limit = min(velocity_limit, 50 / 3.6)  # 13.89

    return velocity_limit
