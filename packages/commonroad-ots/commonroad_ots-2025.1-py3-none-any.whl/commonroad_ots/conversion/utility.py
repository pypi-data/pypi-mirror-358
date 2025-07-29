import math
import random

from commonroad.scenario.lanelet import LaneletNetwork, Lanelet
from commonroad.scenario.scenario import Scenario
from numpy import ndarray
from org.djunits.value.vdouble.scalar import Length
from org.djutils.draw.point import Point2d
from org.opentrafficsim.core.geometry import OtsLine2d
from org.opentrafficsim.road.network.lane import CrossSectionLink
from org.opentrafficsim.road.network import RoadNetwork
from shapely import LineString, Point


def calc_angle(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calculates the angle in ots between two lines given through x1,y1 and x2,y2.

    Parameters
    ----------
    x1 : float
        x-coordinate of the first point
    y1 : float
        y-coordinate of the first point
    x2 : float
        x-coordinate of the second point
    y2 : float
        y-coordinate of the second point

    Returns
    -------
    angle
        the calculated angle
    """

    if x1 == x2:
        if y1 > y2:
            return 270
        else:
            return 90
    elif x1 < x2:
        deg = math.degrees(math.atan((y2 - y1) / (x2 - x1)))
        if deg >= 0:
            return deg
        return deg + 360
    else:
        deg = math.degrees(math.atan((y2 - y1) / (x2 - x1)))
        return deg + 180


def calc_diff(last_point: list, next_point: list, offset: float) -> (float, float):
    """
    Calculate the difference in x and y direction between a point and the point with applied offset.
    Two succeeding points are needed to calculate the angle of the driving direction.

    Parameters
    ----------
    last_point : list
        Coordinates of the first point
    next_point : list
        Coordinates of the succeeding point
    offset: float
        Offset that will be applied

    Returns
    -------
    x,y
        distances in x and y direction to the point with applied offset
    """

    angle = calc_angle(last_point[0], last_point[1], next_point[0], next_point[1])
    if angle == 0:
        return 0, offset
    if angle == 90:
        return -offset, 0
    if angle == 180:
        return 0, -offset
    if angle == 270:
        return offset, 0

    if 0 < angle < 90:
        y = math.sin(math.radians(90 - angle)) * offset
        x = -math.cos(math.radians(90 - angle)) * offset
    elif 90 < angle < 180:
        y = -math.sin(math.radians(angle - 90)) * offset
        x = -math.cos(math.radians(angle - 90)) * offset
    elif 180 < angle < 270:
        y = -math.sin(math.radians(270 - angle)) * offset
        x = math.cos(math.radians(270 - angle)) * offset
    else:
        y = math.sin(math.radians(angle - 270)) * offset
        x = math.cos(math.radians(angle - 270)) * offset
    return x, y


def calc_dist_on_lane(center_line: OtsLine2d, coordinate: list) -> float:
    """
    Calculated the distance of a point from the startNode on a given lane.

    Parameters
    ----------
    center_line : OtsLine2d
        A OtsLine2d
    coordinate : list
        coordinate of the object [x, y]

    Returns
    -------
    distance
        the distance of the point from the start of the line
    """

    line = LineString([p.getX(), p.getY()] for p in center_line.getPoints())
    point = Point(coordinate[0], coordinate[1])

    return line.project(point)


def to_ots_line(center_line: [list | ndarray]) -> OtsLine2d:
    """
    Converts a list of coordinates to an OtsLine2d

    Parameters
    ----------
    center_line : ndarray
        List of coordinates

    Returns
    -------
    new_line
        converted OtsLine2d
    """

    created = set()
    points = []
    for p in center_line:
        if p[0] not in created or p[1] not in created:
            points.append(to_ots_point(p))
            created.update((p[0], p[1]))
    new_line = OtsLine2d(points)
    return new_line


def to_ots_point(coord: list) -> Point2d:
    """
    Converts a coordinates to a Point2d

    Parameters
    ----------
    coord : list
        [x, y]

    Returns
    -------
    point
        converted Point2d
    """
    return Point2d(coord[0], coord[1])


def calc_lane_offsets_from_link(center_line: OtsLine2d, link: CrossSectionLink) -> (Length, Length):
    """
    Calculates the offsets of the center_line of a lane to its parentLink

    Parameters
    ----------
    center_line : OtsLine2d
        The center_line of a lane
    link : CrossSectionLink
        A OTS Link

    Returns
    -------
    start_offset, end_offset
        start and end offset of the lane from the link
    """

    sx1 = link.getDesignLine().get(0).x
    sy1 = link.getDesignLine().get(0).y
    snextx = link.getDesignLine().get(1).x
    snexty = link.getDesignLine().get(1).y
    sx2 = center_line.get(0).x
    sy2 = center_line.get(0).y

    start_offset = get_offset([sx1, sy1], [sx2, sy2], calc_angle(sx1, sy1, snextx, snexty))

    len_design = link.getDesignLine().size()
    len_center = center_line.size()
    ex1 = link.getDesignLine().get(len_design - 1).x
    ey1 = link.getDesignLine().get(len_design - 1).y
    eprevx = link.getDesignLine().get(len_design - 2).x
    eprevy = link.getDesignLine().get(len_design - 2).y
    ex2 = center_line.get(len_center - 1).x
    ey2 = center_line.get(len_center - 1).y

    end_offset = get_offset([ex1, ey1], [ex2, ey2], calc_angle(eprevx, eprevy, ex1, ey1))

    return Length.instantiateSI(start_offset), Length.instantiateSI(end_offset)


def get_predecessors(
    lanelet_network: LaneletNetwork, group_id: int, lanes_by_group_id: dict, group_id_by_lane_id: dict
) -> list:
    """
    Calculates all the predecessors group of a given group

    Parameters
    ----------
    lanelet_network : LaneletNetwork
        The CR lanelet network
    group_id : int
        The group id, the predecessors should be calculated for
    lanes_by_group_id : dict
        contains assigned lanes for each group id
    group_id_by_lane_id: dict
        contains assigned group id for each lane

    Returns
    -------
    predecessors
        List of predecessors group ids
    """

    la = lanes_by_group_id.get(group_id)
    predecessors = set()
    for lane in la:
        pre = lanelet_network.find_lanelet_by_id(lane.lanelet_id).predecessor
        if len(pre) > 0:
            for p in pre:
                predecessors.add(group_id_by_lane_id.get(p))
    return list(predecessors)


def get_successors(
    lanelet_network: LaneletNetwork, group_id: int, lanes_by_group_id: dict, group_id_by_lane_id: dict
) -> list:
    """
    Calculates all the successor group of a given group

    Parameters
    ----------
    lanelet_network : LaneletNetwork
        The CR lanelet network
    group_id : float
        The group id, the successors should be calculated for
    lanes_by_group_id : dict
        contains assigned lanes for each group id
    group_id_by_lane_id: dict
        contains assigned group id for each lane

    Returns
    -------
    successors
        List of successor group ids
    """

    la = lanes_by_group_id.get(group_id)
    successors = set()
    for lane in la:
        succ = lanelet_network.find_lanelet_by_id(lane.lanelet_id).successor
        if len(succ) > 0:
            for s in succ:
                successors.add(group_id_by_lane_id.get(s))
    return list(successors)


def get_offset(point_from: list, point_to: list, angle: float) -> float:
    """
    Calculates the offset to be applied with respect do the driving direction/angle (left: positive, right: negative)

    Parameters
    ----------
    point_from : list
        Coordinates of the original point
    point_to : list
        Coordinates of the goal, where point_from should be moved to
    angle : float
        Driving angle

    Returns
    -------
    offset
        The offset to move point_from to point_to
    """
    dist = math.dist(point_from, point_to)
    if angle == 0:
        if point_to[1] > point_from[1]:
            return dist
        else:
            return -dist
    if angle == 180:
        if point_to[1] > point_from[1]:
            return -dist
        else:
            return dist
    if angle == 90:
        if point_to[0] > point_from[0]:
            return -dist
        else:
            return dist
    if angle == 270:
        if point_to[0] > point_from[0]:
            return dist
        else:
            return -dist

    if 0 < angle < 45 or 315 < angle < 360:
        if point_to[1] > point_from[1]:
            return dist
        else:
            return -dist
    elif 135 < angle < 225:
        if point_to[1] > point_from[1]:
            return -dist
        else:
            return dist
    elif 45 < angle < 135:
        if point_to[0] > point_from[0]:
            return -dist
        else:
            return dist
    else:
        if point_to[0] > point_from[0]:
            return dist
        else:
            return -dist


def apply_offset_end(points: list, offset: float) -> list:
    """
    Applies an offset perpendicular to the last node and moves all other nodes by an offset linearly decreasing.

    Parameters
    ----------
    points : list
        The original coordinates
    offset : float
        The offset to be applied

    Returns
    -------
    res
        The offset line of coordinates
    """

    length = 0
    res = []
    last_point = points[0]
    for p in points:
        length += math.dist(last_point, p)
        last_point = p
    current_length = 0
    last_point = points[0]
    for i in range(len(points)):
        current_length += math.dist(last_point, points[i])
        off = (current_length / length) * offset
        dff = calc_diff(last_point, points[i], off)
        res.append([points[i][0] + dff[0], points[i][1] + dff[1]])
        last_point = points[i]

    return res


def apply_offset_start(points: list, offset: float) -> list:
    """
    Applies an offset perpendicular to the first node and moves all other nodes by an offset linearly decreasing.

    Parameters
    ----------
    points : list
        The original coordinates
    offset : float
        The offset to be applied

    Returns
    -------
    line
        The offset line
    """

    length = 0
    res = []
    last_point = points[0]
    for p in points:
        length += math.dist(last_point, p)
        last_point = p

    current_length = 0
    last_point = points[len(points) - 1]
    for i in range(len(points) - 1, -1, -1):
        current_length += math.dist(last_point, points[i])
        off = (current_length / length) * offset
        dff = calc_diff(points[i], last_point, off)
        res.insert(0, [points[i][0] + dff[0], points[i][1] + dff[1]])
        last_point = points[i]

    return res


def find_terminal_lanelet_seq(lanelet_network: LaneletNetwork, visited: set, lane_id: int) -> list:
    """
    Tries to find the next terminal link (link without successors) using DFS.

    Parameters
    ----------
    lanelet_network : LaneletNetwork
        The CR lanelet network
    visited: set
        The set of already visited links
    lane_id: int
        lane id to search a terminal lane for

    Returns
    -------
    seq
        The sequence of lanelets leading to a terminal lanelet
    """
    if lane_id in visited:
        return None
    visited.add(lane_id)
    succ = lanelet_network.find_lanelet_by_id(lane_id).successor

    # make the search for the successor random
    random.shuffle(succ)
    if len(succ) == 0:
        return []
    else:
        for s in succ:
            seq = find_terminal_lanelet_seq(lanelet_network, visited, s)
            if seq is not None:
                res = [s]
                res.extend(seq)
                return res


def find_all_end_nodes(
    net: RoadNetwork, lanelet_network: LaneletNetwork, lanelet: Lanelet, group_id_by_lane_id: dict
) -> set:
    """
    Returns all the reachable OTS end nodes from a certain start lanelet

    Parameters
    ----------
    net: RoadNetwork
        The OTS road network
    lanelet_network: LaneletNetwork
        The CR lanelet network
    lanelet: Lanelet
        The start lanelet
    group_id_by_lane_id: dict
        mapping from lanelet id to link/group id

    Returns
    -------
    res
        The list of end nodes
    """
    frontier = [lanelet.lanelet_id]
    res = set()
    visited = set()

    while len(frontier) > 0:
        current = frontier.pop(0)
        while current in visited:
            if len(frontier) == 0:
                if len(res) == 0:
                    print(f"Found no end Node for lanelet {lanelet.lanelet_id}")
                return res
            current = frontier.pop(0)
        visited.add(current)
        if len(lanelet_network.find_lanelet_by_id(current).successor) == 0:
            link_end = group_id_by_lane_id.get(current)
            end_node = net.getLink(str(link_end)).getEndNode()
            res.add(end_node)
        curr_l = lanelet_network.find_lanelet_by_id(current)
        frontier.extend(curr_l.successor)
        if curr_l.adj_left_same_direction:
            frontier.append(curr_l.adj_left)
        if curr_l.adj_right_same_direction:
            frontier.append(curr_l.adj_right)

    if len(lanelet_network.find_lanelet_by_id(current).successor) == 0:
        link_end = group_id_by_lane_id.get(current)
        end_node = net.getLink(str(link_end)).getEndNode()
        res.add(end_node)

    if len(res) == 0:
        print(f"Found no end Node for lanelet {lanelet.lanelet_id}")
    return res


def postprocess_generator_positions(generator_positions: dict, lanelet_network: LaneletNetwork) -> None:
    """
    Removes all generators that are inside the road network / downstream an existing generator

    Parameters
    ----------
    generator_positions: RoadNetwork
        The calculated start lanelets for the generators
    lanelet_network: LaneletNetwork
        The CR lanelet network
    """

    start_ids = [i for (i, t) in generator_positions.keys()]
    to_remove = set()

    for (start_id, g_type) in generator_positions.keys():
        frontier = list()
        frontier.extend(lanelet_network.find_lanelet_by_id(start_id).successor)
        while len(frontier) > 0:
            current = frontier.pop(0)
            if current in start_ids:
                to_remove.add(current)
            curr_l = lanelet_network.find_lanelet_by_id(current)
            frontier.extend(curr_l.successor)

    removals = [(i, t) for (i, t) in generator_positions.keys() if i in to_remove]

    for r in removals:
        del generator_positions[r]


def get_scenario_length(scenario: Scenario) -> int:
    """
    Returns the maximum timestep/length of the scenario in seconds

    Parameters
    ----------
    scenario: Scenario
        The CR scenario
    """
    max_time = 0

    for obs in scenario.dynamic_obstacles:
        if obs.prediction.final_time_step > max_time:
            max_time = obs.prediction.final_time_step

    return math.ceil(max_time * scenario.dt)
