from commonroad.scenario.lanelet import LaneletNetwork, Lanelet
from commonroad.scenario.traffic_sign import TrafficSignIDGermany
from jpype import JDouble
from org.djunits.value.vdouble.scalar import Duration, Length, Speed
from org.opentrafficsim.core.definitions import DefaultsNl
from org.opentrafficsim.road.network.lane.CrossSectionLink import Priority
from org.opentrafficsim.road.network.lane.object import SpeedSign
from org.opentrafficsim.road.network.lane import Lane
from org.opentrafficsim.core.dsol import OtsAnimator


def handle_traffic_signs(signs: list, lane: Lane, sim: OtsAnimator) -> Priority:
    """
    Converters traffic signs by setting the respective speedLimit or returning the respective link priority.

    Parameters
    ----------
    signs : list
        The CR traffic signs
    lane : Lane
        The ots Lane which contains the sign
    sim : OtsAnimator
        The ots simulator used for the traffic signs

    Returns
    -------
    priority
        The extracted priority for the link
    """

    priority = Priority.NONE
    speed = None
    dist = Length.instantiateSI(0)

    # for speedLimit: create a speedLimit and set speed
    # for priority signs, return priority of link

    for s in signs:
        match s.traffic_sign_elements[0].traffic_sign_element_id.value:
            case "205":
                priority = Priority.YIELD
            case "206":
                priority = Priority.STOP
            case "274" | "274.1" | "R2-1":
                speed_temp = JDouble(s.traffic_sign_elements[0].additional_values[0])
                if speed is None or speed_temp < speed:
                    speed = speed_temp
            case "301" | "306" | "308":
                priority = Priority.PRIORITY
            case "310":
                # Town sign : set speedLimit to 50km/h ~ 13.888m/s
                if speed is None or speed > 13.888:
                    speed = 13.888
            case "720":
                priority = Priority.TURN_ON_RED
            case (
                "1002-10"
                | "1002-11"
                | "1002-12"
                | "1002-13"
                | "1002-14"
                | "1002-20"
                | "1002-21"
                | "1002-22"
                | "1002-23"
                | "1002-24"
            ):
                priority = Priority.PRIORITY
            case _:
                print(
                    "INFO: No matching traffic sign found in ots for: ",
                    s.traffic_sign_elements[0].traffic_sign_element_id.value,
                )
    if speed is not None:
        SpeedSign(
            str(lane.getId()) + "_" + str(speed),
            lane,
            dist,
            sim,
            Speed.instantiateSI(speed),
            DefaultsNl.ROAD_USER,
            Duration.ZERO,
            Duration.POS_MAXVALUE,
        )
        lane.setSpeedLimit(DefaultsNl.ROAD_USER, Speed.instantiateSI(speed))

    return priority


def preprocess_traffic_signs(lanelet_network: LaneletNetwork, traffic_signs: dict, shift_prio_signs: bool):
    """
    Preprocess signs:
    - shift priority signs to the next lane
    - add additional signs (e.g. each lane between town_sign and town_sign back gets a town_sign attached)

    Parameters
    ----------
    lanelet_network : LaneletNetwork
        The CR lanelet network
    traffic_signs : dict
        lookup from traffic light id to traffic light
    shift_prio_signs: bool
        whether to shift all priority signs to the next lanelet or not
    """

    if shift_prio_signs:
        shift_priority_signs(lanelet_network, traffic_signs)

    incoming_lanelets = [l for l in lanelet_network.lanelets if len(l.predecessor) == 0]

    for lanelet in incoming_lanelets:
        assign_correct_signs(lanelet_network, lanelet, None, None, traffic_signs, set())


def assign_correct_signs(
    lanelet_network: LaneletNetwork,
    lanelet: Lanelet,
    town_sign_id: int,
    speed_zone_id: int,
    traffic_signs: dict,
    visited: set,
) -> None:
    """
    Recursively traverse through the network and assign supported signs if necessary
    supported signs: town_sign, max_speed_zone

    Parameters
    ----------
    lanelet_network : LaneletNetwork
        The CR lanelet network
    lanelet: Lanelet
        The current lanelet
    town_sign_id: int
        town_sign id to assign or None if inactive
    speed_zone_id: int
        max_speed_zone id to assign or None if inactive
    traffic_signs : dict
        lookup from traffic light id to traffic light
    visited: set
        already visited lanelets
    """

    if lanelet.lanelet_id in visited:
        return
    visited.add(lanelet.lanelet_id)

    if town_sign_id is not None:
        lanelet.traffic_signs.add(town_sign_id)
    if speed_zone_id is not None:
        lanelet.traffic_signs.add(speed_zone_id)

    current_signs = [traffic_signs.get(t) for t in lanelet.traffic_signs]
    for s in current_signs:
        sign_value = s.traffic_sign_elements[0].traffic_sign_element_id.value
        if "310" == sign_value:
            town_sign_id = s.traffic_sign_id
        if "311" == sign_value:
            town_sign_id = None
        if "274.1" == sign_value:
            speed_zone_id = s.traffic_sign_id
        if "274.2" == sign_value:
            speed_zone_id = None

    for succ in lanelet.successor:
        assign_correct_signs(
            lanelet_network,
            lanelet_network.find_lanelet_by_id(succ),
            town_sign_id,
            speed_zone_id,
            traffic_signs,
            visited,
        )


def shift_priority_signs(lanelet_network: LaneletNetwork, traffic_signs: dict) -> None:
    """
    Assigns all traffic signs valid from the end of the lanelet to the successor lanelets

    Parameters
    ----------
    lanelet_network : LaneletNetwork
        The CR lanelet network
    traffic_signs : dict
        lookup from traffic light id to traffic light
    """

    end_ids = [
        "205",
        "206",
        "720",
        "301",
        "306",
        "308",
        "1002-10",
        "1002-11",
        "1002-12",
        "1002-13",
        "1002-14",
        "1002-20",
        "1002-21",
        "1002-22",
        "1002-23",
        "1002-24",
    ]

    to_add = dict()

    for lane in lanelet_network.lanelets:
        signs = lane.traffic_signs
        succ = lane.successor
        to_remove = []
        for s_id in signs:
            if traffic_signs.get(s_id).traffic_sign_elements[0].traffic_sign_element_id.value in end_ids:
                to_remove.append(s_id)
                for s in succ:
                    if s not in to_add:
                        to_add.update({s: []})
                    to_add.get(s).append(s_id)
        for s_id in to_remove:
            signs.remove(s_id)

    for lane in to_add:
        for s_id in to_add.get(lane):
            lanelet_network.find_lanelet_by_id(lane).traffic_signs.add(s_id)
