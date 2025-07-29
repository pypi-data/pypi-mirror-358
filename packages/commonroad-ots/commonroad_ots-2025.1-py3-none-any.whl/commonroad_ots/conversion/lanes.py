from commonroad.scenario.lanelet import Lanelet, LaneletType, LineMarking, RoadUser, LaneletNetwork
from java.util import ArrayList, HashMap, HashSet
from jpype import JString
from numpy import ndarray
from org.djunits.value.vdouble.scalar import Length, Speed
from org.djutils.draw.line import Polygon2d
from org.opentrafficsim.core.definitions import DefaultsNl
from org.opentrafficsim.core.geometry import ContinuousPolyLine, FractionalLengthData
from org.opentrafficsim.core.gtu import GtuType
from org.opentrafficsim.road.definitions import DefaultsRoadNl
from org.opentrafficsim.road.network.lane import CrossSectionSlice, Lane, LaneType, Stripe
from org.opentrafficsim.road.network.lane.object import BusStop
from org.opentrafficsim.road.network.lane.object.detector import SinkDetector
from org.opentrafficsim.road.network.lane import CrossSectionLink
from org.opentrafficsim.road.network.lane.Stripe import Type
from org.opentrafficsim.core.dsol import OtsAnimator
from org.opentrafficsim.road.network import RoadNetwork

from commonroad_ots.conversion.default_speed_limit import get_default_speed_limit_for_lanelet_type
from commonroad_ots.conversion.utility import calc_lane_offsets_from_link, to_ots_line, to_ots_point


def add_line(line_marking: LineMarking, link: CrossSectionLink, center_line: ndarray) -> Stripe:
    """
    Creates a new stripe/line marking for a given type and centerLine

    Parameters
    ----------
    line_marking : LineMarking
        The CR line marking type
    link : Link
        The ots link on which the stripe should be created
    center_line : ndarray
        The center line of the stripe

    Returns
    -------
    stripe
        The created ots stripe
    """

    center_line = to_ots_line(center_line)
    start_offset, end_offset = calc_lane_offsets_from_link(center_line, link)

    slices = ArrayList()
    slices.add(CrossSectionSlice(Length.ZERO, start_offset, Length.instantiateSI(0.2)))
    slices.add(CrossSectionSlice(link.getLength(), end_offset, Length.instantiateSI(0.2)))

    line = ContinuousPolyLine(center_line.getLine2d())
    left = line.flattenOffset(FractionalLengthData.of(0.0, 0.5 * 0.2), None)
    right = line.flattenOffset(FractionalLengthData.of(0.0, -0.5 * 0.2), None)

    points = ArrayList()
    left.getPoints().forEachRemaining(lambda e: points.add(e))
    right.reverse().getPoints().forEachRemaining(lambda e: points.add(e))
    contour = Polygon2d(points)

    match line_marking:
        case LineMarking.DASHED:
            line_type = Type.DASHED
        case LineMarking.BROAD_DASHED:
            line_type = Type.BLOCK
        case LineMarking.SOLID:
            line_type = Type.SOLID
        case LineMarking.BROAD_SOLID:
            line_type = Type.SOLID
        case _:
            print(
                "INFO: Line marking not converted. The following line marking type is currently not supported: ",
                line_marking,
            )
            return

    stripe = Stripe(line_type, link, center_line, contour, slices)
    return stripe


def add_lane(
    sim: OtsAnimator, lane: Lanelet, link: CrossSectionLink, lane_width_start: Length, lane_width_end: Length
) -> Lane:
    """
    Creates a new lane for a link and specify the allowed GTU types.

    Parameters
    ----------
    sim: Simulator
        The OTS Simulator needed to create BusStops
    lane : Lanelet
        The CR lanelent
    link : Link
        The ots link on which the stripe should be created
    lane_width_start : Length
        The lane width at the start of the lane
    lane_width_end : Length
        The lane width at the end of the lane

    Returns
    -------
    lane
        The created ots lane
    """

    lane_type = None
    center_line = to_ots_line(lane.center_vertices)
    start_offset, end_offset = calc_lane_offsets_from_link(center_line, link)

    slices = ArrayList()
    slices.add(CrossSectionSlice(Length.ZERO, start_offset, lane_width_start))
    slices.add(CrossSectionSlice(link.getLength(), end_offset, lane_width_end))

    points = []
    for p in lane.left_vertices:
        points.append(to_ots_point(p))

    for p in reversed(lane.right_vertices):
        points.append(to_ots_point(p))

    contour = Polygon2d(True, points)

    speed = get_default_speed_limit_for_lanelet_type(lane.lanelet_type)

    # convert laneletType
    match lane.lanelet_type.pop():
        case LaneletType.URBAN:
            URBAN = LaneType("URBAN")
            lane_type = URBAN
        case LaneletType.INTERSECTION:
            INTERSECTION = LaneType("INTERSECTION")
            lane_type = INTERSECTION
        case LaneletType.COUNTRY:
            COUNTRY = LaneType("COUNTRY")
            lane_type = COUNTRY
        case LaneletType.HIGHWAY:
            HIGHWAY = LaneType("HIGHWAY")
            lane_type = HIGHWAY
        case LaneletType.DRIVE_WAY:
            DRIVE_WAY = LaneType("DRIVE_WAY")
            lane_type = DRIVE_WAY
        case LaneletType.MAIN_CARRIAGE_WAY:
            MAIN_CARRIAGE_WAY = LaneType("MAIN_CARRIAGE_WAY")
            lane_type = MAIN_CARRIAGE_WAY
        case LaneletType.ACCESS_RAMP:
            ACCESS_RAMP = LaneType("ACCESS_RAMP")
            lane_type = ACCESS_RAMP
        case LaneletType.EXIT_RAMP:
            EXIT_RAMP = LaneType("EXIT_RAMP")
            lane_type = EXIT_RAMP
        case LaneletType.SHOULDER:
            return Lane.shoulder(link, JString(str(lane.lanelet_id)), center_line, contour, slices)
        case LaneletType.BUS_LANE:
            BUS_LANE = LaneType("BUS_LANE")
            lane_type = BUS_LANE
        case LaneletType.BUS_STOP:
            BUS_STOP = LaneType("BUS_STOP")
            lane_type = BUS_STOP
            lane_type.addCompatibleGtuType(DefaultsNl.BUS)
            lane = Lane(link, JString(str(lane.lanelet_id)), center_line, contour, slices, lane_type, HashMap())
            lane.setSpeedLimit(DefaultsNl.ROAD_USER, Speed.instantiateSI(8.33))
            BusStop(JString(str(lane.lanelet_id) + "_BusStop"), lane, Length.instantiateSI(0), sim, DefaultsNl.BUS)
            return lane
        case LaneletType.BICYCLE_LANE:
            BICYCLE_LANE = LaneType("BICYCLE_LANE")
            lane_type = BICYCLE_LANE
        case LaneletType.SIDEWALK:
            SIDEWALK = LaneType("SIDEWALK")
            lane_type = SIDEWALK
        case LaneletType.CROSSWALK:
            CROSSWALK = LaneType("CROSSWALK")
            lane_type = CROSSWALK
        case LaneletType.INTERSTATE:
            INTERSTATE = LaneType("INTERSTATE")
            lane_type = INTERSTATE
        case LaneletType.PARKING:
            PARKING = LaneType("PARKING")
            lane_type = PARKING
        case _:
            UNKNOWN = LaneType("UNKNOWN")
            lane_type = UNKNOWN

    user = lane.user_one_way
    if len(user) == 0:
        # no concrete road user specified -> allow all types of GTUs
        lane_type.addCompatibleGtuType(DefaultsNl.ROAD_USER)
        lane_type.addCompatibleGtuType(DefaultsNl.WATERWAY_USER)
        lane_type.addCompatibleGtuType(DefaultsNl.RAILWAY_USER)

    # convert road user
    for u in user:
        match u:
            case RoadUser.VEHICLE:
                lane_type.addCompatibleGtuType(DefaultsNl.VEHICLE)
            case RoadUser.CAR:
                lane_type.addCompatibleGtuType(DefaultsNl.CAR)
            case RoadUser.BUS:
                lane_type.addCompatibleGtuType(DefaultsNl.BUS)
            case RoadUser.PRIORITY_VEHICLE:
                lane_type.addCompatibleGtuType(GtuType("PRIORITY_VEHICLE", DefaultsNl.CAR))
            case RoadUser.MOTORCYCLE:
                lane_type.addCompatibleGtuType(DefaultsNl.MOTORCYCLE)
            case RoadUser.BICYCLE:
                lane_type.addCompatibleGtuType(DefaultsNl.BICYCLE)
            case RoadUser.PEDESTRIAN:
                lane_type.addCompatibleGtuType(DefaultsNl.PEDESTRIAN)
            case RoadUser.TRAIN:
                lane_type.addCompatibleGtuType(DefaultsNl.TRAIN)
            case RoadUser.TRAIN:
                lane_type.addCompatibleGtuType(GtuType("TAXI", DefaultsNl.CAR))

    lane_ots = Lane(link, JString(str(lane.lanelet_id)), center_line, contour, slices, lane_type, HashMap())
    lane_ots.setSpeedLimit(DefaultsNl.ROAD_USER, Speed.instantiateSI(speed))

    # if this lane is a terminal one, create a sink 50cm before the end of the lane
    if len(lane.successor) == 0:
        pos = Length.instantiateSI(lane_ots.getLength().getSI() - 0.5)
        SinkDetector(lane_ots, pos, sim, DefaultsRoadNl.ROAD_USERS)
    return lane_ots


def connect_lanes(lanelet_network: LaneletNetwork, network: RoadNetwork, group_id_by_lane_id: dict) -> None:
    """
    Manually set the successors for each lane to ensure a correct road network

    Parameters
    ----------
    lanelet_network : LaneletNetwork
        The CR lanelet_network
    network : RoadNetwork
        The OTS road network
    group_id_by_lane_id: dict
        contains the group id for each lane id
    """

    for lane_id in group_id_by_lane_id.keys():
        succ_list = lanelet_network.find_lanelet_by_id(lane_id).successor
        lane = network.getLink(str(group_id_by_lane_id.get(lane_id))).getCrossSectionElement(str(lane_id))
        succ = HashSet()
        for successor in succ_list:
            succ.add(network.getLink(str(group_id_by_lane_id.get(successor))).getCrossSectionElement(str(successor)))

        lane.forceNextLanes(succ)
