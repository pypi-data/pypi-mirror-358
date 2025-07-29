from commonroad.scenario.lanelet import LaneletNetwork
from commonroad.scenario.traffic_light import TrafficLightState
from java.util import HashSet
from jpype import JString
from org.djunits.value.vdouble.scalar import Duration
from org.opentrafficsim.road.network.lane.object.trafficlight import TrafficLight, TrafficLightColor
from org.opentrafficsim.trafficcontrol import FixedTimeController
from org.opentrafficsim.trafficcontrol.FixedTimeController import SignalGroup
from org.opentrafficsim.road.network import RoadNetwork
from org.opentrafficsim.core.dsol import OtsAnimator
from org.opentrafficsim.road.network.lane import Lane

from commonroad_ots.conversion import lane_groups


def choose_correct_traffic_light(lights: list, direc: list) -> TrafficLight:
    """
    Chooses the correct traffic light (direction) for a lane.
    If lane has only one successor choose between 'left', 'right' and 'straight'
    If the lane has two successors choose between 'straightLeft', 'straightRight' and 'leftRight'
    Otherwise choose always choose 'all' as a default

    Parameters
    ----------
    lights : list
        all the CR traffic lights for this lane
    direc : list
        all the directions of the successor lanes

    Returns
    -------
    trafficLight
        The chosen trafficlight
    """

    light_values = [l.direction.value for l in lights]

    if len(direc) == 1:
        if direc[0] in light_values:
            return lights[light_values.index(direc[0])]
        else:
            print("INFO: Single turn lane with traffic-light, but no matching traffic-light direction")
            return lights[light_values.index("all")]
    else:
        if "left" in direc and "straight" in direc and "leftStraight" in light_values:
            return lights[light_values.index("leftStraight")]
        elif "right" in direc and "straight" in direc and "straightRight" in light_values:
            return lights[light_values.index("straightRight")]
        elif "right" in direc and "left" in direc and "leftRight" in light_values:
            return lights[light_values.index("leftRight")]
        return lights[light_values.index("all")]


def create_traffic_lights(
    lane: Lane, lights: list, lanelet_network: LaneletNetwork, sim: OtsAnimator, net: RoadNetwork
) -> FixedTimeController:
    """
    Creates new traffic lights.

    Parameters
    ----------
    lane : Lane
        The ots lane to create the traffic lights on
    lights : list
        The CR traffic lights
    lanelet_network : LaneletNetwork
        The CR laneletNetwork
    sim : OtsAnimator
        The ots simulator used for the traffic lights
    net : RoadNetwork
        The ots Network

    Returns
    -------
    res
        The created traffic light controller
    """

    direction_by_lane_id = lane_groups.assign_turning_direction_to_lanes(lanelet_network)

    if len(lights) == 0:
        return
    elif len(lights) == 1:
        t = lights[0]
    else:
        succ = lanelet_network.find_lanelet_by_id(int(str(lane.getId()))).successor

        direc = []
        for lane_id in succ:
            if lane_id in direction_by_lane_id:
                direc.append(direction_by_lane_id.get(lane_id))
            else:
                direc.append("straight")

        # important: each lane in OTS currently only gets one traffic light assigned
        t = choose_correct_traffic_light(lights, direc)

    res = None

    dist = lane.getLength()
    tl = TrafficLight(str(lane.getId()) + "_" + str(t.traffic_light_id), lane, dist, sim)
    cycle = []  # trafficlight colors + cycle times in correct order
    cycle_dict = dict()  # set of trafficlight colors
    cycle_time = 0  # overall cycle time
    for c in t.traffic_light_cycle.cycle_elements:
        cycle_time += c.duration
        match c.state:
            case TrafficLightState.GREEN:
                cycle.append((TrafficLightColor.GREEN, c.duration))
                cycle_dict.update({TrafficLightColor.GREEN: c.duration})
            case TrafficLightState.YELLOW:
                cycle.append((TrafficLightColor.YELLOW, c.duration))
                cycle_dict.update({TrafficLightColor.YELLOW: c.duration})
            case TrafficLightState.RED:
                cycle.append((TrafficLightColor.RED, c.duration))
                cycle_dict.update({TrafficLightColor.RED: c.duration})
            case TrafficLightState.RED_YELLOW:
                cycle.append((TrafficLightColor.PREGREEN, c.duration))
                cycle_dict.update({TrafficLightColor.PREGREEN: c.duration})
            case TrafficLightState.INACTIVE:
                cycle.append((TrafficLightColor.BLACK, c.duration))
                cycle_dict.update({TrafficLightColor.BLACK: c.duration})

    light = HashSet()
    light.add(tl.getFullId())
    tl.setTrafficLightColor(cycle[0][0])
    group = None
    if TrafficLightColor.PREGREEN in cycle_dict:
        # trafficlight with pre green phase
        group = SignalGroup(
            JString(str(lane.getId()) + "_" + str(t.traffic_light_id)),
            light,
            Duration.ZERO,
            Duration.instantiateSI(cycle_dict.get(TrafficLightColor.PREGREEN)),
            Duration.instantiateSI(cycle_dict.get(TrafficLightColor.GREEN)),
            Duration.instantiateSI(cycle_dict.get(TrafficLightColor.YELLOW)),
        )
    else:
        # trafficlight without pre green phase
        group = SignalGroup(
            JString(str(lane.getId()) + "_" + str(t.traffic_light_id)),
            light,
            Duration.ZERO,
            Duration.instantiateSI(cycle_dict.get(TrafficLightColor.GREEN)),
            Duration.instantiateSI(cycle_dict.get(TrafficLightColor.YELLOW)),
        )

    groups = HashSet()
    groups.add(group)
    res = FixedTimeController(
        JString(str(lane.getId()) + "_" + str(t.traffic_light_id) + "_controller"),
        sim,
        net,
        Duration.instantiateSI(cycle_time),
        Duration.instantiateSI(t.traffic_light_cycle.time_offset),
        groups,
    )
    return res
