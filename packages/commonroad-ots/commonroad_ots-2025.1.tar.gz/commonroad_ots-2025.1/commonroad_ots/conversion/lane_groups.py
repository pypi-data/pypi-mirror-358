from commonroad.scenario.lanelet import LaneletNetwork

import commonroad_ots.conversion.utility as utility


def build_lane_groups(
    lanelet_network: LaneletNetwork,
    group_id_by_lane_id: dict,
    lanes_by_group_id: dict,
    group_nodes_by_id: dict,
    defining_lane_by_group_id: dict,
) -> None:
    """
    Groups adjacent lanelets with the same driving direction into a lane group. Each lane group will then result in a
    link with one or more lanes.

    Parameters
    ----------
    lanelet_network
        The CR laneletNetwork
    group_id_by_lane_id : dict
        contains assigned group id for each lanelet id
    lanes_by_group_id : dict
        contains assigned lanelets for each group id
    group_nodes_by_id : dict
        contains assigned center nodes for each group id
    defining_lane_by_group_id : dict
        contains the lane with offset 0 for each group id
    """

    group_id = 0
    for lanelet in lanelet_network.lanelets:
        if lanelet.lanelet_id not in group_id_by_lane_id.keys():
            current_group = set()
            group_id_by_lane_id.update({lanelet.lanelet_id: group_id})
            current_group.add(lanelet)

            current = lanelet
            left = lanelet.adj_left
            right = lanelet.adj_right

            # add all lanes on the left with same driving direction
            while left is not None and current.adj_left_same_direction:
                group_id_by_lane_id.update({left: group_id})
                current = lanelet_network.find_lanelet_by_id(left)
                current_group.add(current)
                left = current.adj_left

            # add all lanes on the right with same driving direction
            while right is not None and current.adj_right_same_direction:
                group_id_by_lane_id.update({right: group_id})
                current = lanelet_network.find_lanelet_by_id(right)
                current_group.add(current)
                right = current.adj_right

            lanes_by_group_id.update({group_id: list(current_group)})
            group_nodes_by_id.update({group_id: lanelet.center_vertices})

            # take one lanelet to define the shape of the link
            defining_lane_by_group_id.update({group_id: lanelet.lanelet_id})
            group_id += 1


def connect_lane_groups(
    lanelet_network: LaneletNetwork, group_nodes_by_id: dict, lanes_by_group_id: dict, group_id_by_lane_id: dict
) -> None:
    """
    Connection each lane group with its successors and predecessors.
    Algorithm:
    if group has multiple predecessors -> keep own startNode, else take endNode of previous group (and shift all other
    nodes accordingly)
    if group has multiple successors -> keep one endNode, else take startNode of next group (and shift all other nodes
    accordingly)

    Parameters
    ----------
    lanelet_network
        The CR laneletNetwork
    lanes_by_group_id : dict
        contains assigned lanelets for each group id
    group_nodes_by_id : dict
        contains assigned center nodes for each group id
    group_id_by_lane_id : dict
        contains assigned group id for each lanelet id
    """

    for next_group in lanes_by_group_id.keys():
        pre = utility.get_predecessors(lanelet_network, next_group, lanes_by_group_id, group_id_by_lane_id)
        succ = utility.get_successors(lanelet_network, next_group, lanes_by_group_id, group_id_by_lane_id)

        goal_end = None
        if len(succ) == 1:
            # only one successor -> use its startNode as new own endNode
            orig = group_nodes_by_id.get(next_group)[-1]
            pre_org = group_nodes_by_id.get(next_group)[-2]
            driving_angle = utility.calc_angle(pre_org[0], pre_org[1], orig[0], orig[1])
            goal = group_nodes_by_id.get(succ[0])[0]
            offset = utility.get_offset(orig, goal, driving_angle)
            # shift all center nodes of the link
            new_nodes = utility.apply_offset_end(group_nodes_by_id.get(next_group), offset)
            group_nodes_by_id.update({next_group: new_nodes})
            goal_end = goal

        goal_start = None
        if len(pre) == 1:
            # only one predecessor -> use its endNode as new own startNode
            orig = group_nodes_by_id.get(next_group)[0]
            post_orig = group_nodes_by_id.get(next_group)[1]
            goal = group_nodes_by_id.get(pre[0])[-1]
            driving_angle = utility.calc_angle(orig[0], orig[1], post_orig[0], post_orig[1])
            offset = utility.get_offset(orig, goal, driving_angle)
            # shift all center nodes of the link
            new_nodes = utility.apply_offset_start(group_nodes_by_id.get(next_group), offset)
            group_nodes_by_id.update({next_group: new_nodes})
            goal_start = goal

        # make sure that the start/endNode of succ/pred are exactly the same
        nodes = group_nodes_by_id.get(next_group)
        if goal_end is not None:
            nodes[-1] = goal_end
        if goal_start is not None:
            nodes[0] = goal_start


def assign_turning_direction_to_lanes(lanelet_network: LaneletNetwork) -> dict:
    """
    Explicitly extracts all lanes which are turning lanes. The resulting dict contains information whether the lane
    turns right or left.

    Parameters
    ----------
    lanelet_network
        The CR laneletNetwork
    """

    direction_by_lane_id = dict()

    for intersection in lanelet_network.intersections:
        incoming = intersection.incomings
        for i in incoming:
            left = i.successors_left
            right = i.successors_right

            for le in left:
                direction_by_lane_id.update({le: "left"})
            for ri in right:
                direction_by_lane_id.update({ri: "right"})

    return direction_by_lane_id
