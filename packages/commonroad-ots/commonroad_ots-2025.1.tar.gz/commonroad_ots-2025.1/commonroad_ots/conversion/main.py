import math

from commonroad.scenario.lanelet import LaneletNetwork, LineMarking, Lanelet
import jpype
from jpype import JString

from commonroad_ots.conversion.setup import setup_ots

setup_ots()

from java.io import Serializable
from java.util import Locale
from org.djunits.unit import DirectionUnit
from org.djunits.value.vdouble.scalar import Direction, Duration, Frequency, Length, Time
from org.djutils.draw.point import Point2d
from org.opentrafficsim.animation import GraphLaneUtil
from org.opentrafficsim.core.definitions import DefaultsNl
from org.opentrafficsim.core.dsol import OtsAnimator
from org.opentrafficsim.core.geometry import OtsLine2d
from org.opentrafficsim.core.network import Node
from org.opentrafficsim.swing.gui import CustomSimulation
from org.opentrafficsim.swing.gui.CustomSimulation import CustomModel
from org.opentrafficsim.draw.graphs import GraphPath
from org.opentrafficsim.road.network import RoadNetwork
from org.opentrafficsim.road.network.lane import CrossSectionLink
from org.opentrafficsim.road.network.lane.changing import LaneKeepingPolicy
from org.opentrafficsim.road.network.lane.conflict import ConflictBuilder
from org.opentrafficsim.road.network.sampling import RoadSampler
from org.opentrafficsim.road.network.sampling.data import (
    WorldXData,
    WorldYData,
    WorldDirData,
    FilterDataLength,
    FilterDataWidth,
)
from org.opentrafficsim.kpi.sampling.meta import FilterDataGtuType
import commonroad_ots.conversion.lane_groups as lane_groups
import commonroad_ots.conversion.utility as utility
from commonroad_ots.conversion.lanes import add_lane, add_line, connect_lanes
from commonroad_ots.conversion.trafficlights import create_traffic_lights
from commonroad_ots.conversion.trafficsigns import handle_traffic_signs, preprocess_traffic_signs


class Conversion:
    """This class converts CommonRoad XML files to OTS Scenarios and displays them"""

    def __init__(self):
        # group-id -> List[(X,Y)]
        self.group_nodes_by_id = dict()
        # lane-id -> group-id
        self.group_id_by_lane_id = dict()
        # group-id -> List[lane-id]
        self.lanes_by_group_id = dict()
        # group-id -> lanelet_id which defines the shape of the link
        self.defining_lane_by_group_id = dict()

    def create_static_objects(
        self,
        lane: Lanelet,
        lanelet_network: LaneletNetwork,
        sim: OtsAnimator,
        net: RoadNetwork,
        traffic_signs: dict,
        traffic_lights: dict,
        link: CrossSectionLink,
        created_lanes: set,
    ) -> None:
        """
        Create all the static objects such as lanes, stripes, signs and traffic lights

        Parameters
        ----------
        lane : Lanelet
            The CR lanelet
        lanelet_network : LaneletNetwork
            The CR laneletNetwork
        sim: Simulator
            The OTS simulator
        net: Network
            The OTS road network
        traffic_signs: dict
            CR traffic signs
        traffic_lights: dict
            CR traffic lights
        link: Link
            OTS Link for which the objects should be created
        created_lanes: set
            already created lanes
        """

        left = (lane.left_vertices[0][0], lane.left_vertices[0][1])
        right = (lane.right_vertices[0][0], lane.right_vertices[0][1])
        lane_width_start = Length.instantiateSI(abs(math.dist(left, right)))
        left = (lane.left_vertices[-1][0], lane.left_vertices[-1][1])
        right = (lane.right_vertices[-1][0], lane.right_vertices[-1][1])
        lane_width_end = Length.instantiateSI(abs(math.dist(left, right)))

        lights = [traffic_lights.get(l) for l in lane.traffic_lights]
        signs = [traffic_signs.get(s) for s in lane.traffic_signs]

        created_lane = add_lane(sim, lane, link, lane_width_start, lane_width_end)
        created_lanes.add(lane.lanelet_id)

        priority = handle_traffic_signs(signs, created_lane, sim)
        link.setPriority(priority)

        create_traffic_lights(created_lane, lights, lanelet_network, sim, net)

        if (
            lane.line_marking_left_vertices != LineMarking.UNKNOWN
            and lane.line_marking_left_vertices != LineMarking.NO_MARKING
        ):
            add_line(lane.line_marking_left_vertices, link, lane.left_vertices)

        if lane.adj_right is not None and lane.adj_right not in created_lanes and lane.adj_right_same_direction:
            self.create_static_objects(
                lanelet_network.find_lanelet_by_id(lane.adj_right),
                lanelet_network,
                sim,
                net,
                traffic_signs,
                traffic_lights,
                link,
                created_lanes,
            )
        if (
            lane.line_marking_right_vertices != LineMarking.UNKNOWN
            and lane.line_marking_right_vertices != LineMarking.NO_MARKING
        ):
            add_line(lane.line_marking_right_vertices, link, lane.right_vertices)

        if lane.adj_left is not None and lane.adj_left not in created_lanes and lane.adj_left_same_direction:
            self.create_static_objects(
                lanelet_network.find_lanelet_by_id(lane.adj_left),
                lanelet_network,
                sim,
                net,
                traffic_signs,
                traffic_lights,
                link,
                created_lanes,
            )

    def create_network(
        self, sim: OtsAnimator, lanelet_network: LaneletNetwork, shift_priority_signs: bool
    ) -> RoadNetwork:
        """
        Create the OTS network

        Parameters
        ----------
        sim: Simulator
            The OTS simulator.
        lanelet_network: LaneletNetwork
            Original CommonRoad lanelet network to be converted.
        shift_priority_signs: bool
            Whether to preprocess signs or not
        """

        net = RoadNetwork("CR-Scenario Network", sim)

        traffic_signs_list = lanelet_network.traffic_signs
        traffic_lights_list = lanelet_network.traffic_lights

        traffic_lights = dict()
        traffic_signs = dict()

        for t in traffic_lights_list:
            traffic_lights.update({t.traffic_light_id: t})
        for t in traffic_signs_list:
            traffic_signs.update({t.traffic_sign_id: t})

        # preprocessing for traffic lights and traffic signs
        preprocess_traffic_signs(lanelet_network, traffic_signs, shift_priority_signs)

        created_nodes = dict()
        created_lanes = set()

        lane_groups.build_lane_groups(
            lanelet_network,
            self.group_id_by_lane_id,
            self.lanes_by_group_id,
            self.group_nodes_by_id,
            self.defining_lane_by_group_id,
        )
        lane_groups.connect_lane_groups(
            lanelet_network, self.group_nodes_by_id, self.lanes_by_group_id, self.group_id_by_lane_id
        )

        # iterate over all lane groups and create static objects
        for group in self.lanes_by_group_id.keys():
            group_id = str(group)

            center = self.group_nodes_by_id.get(group)
            initial_lane = lanelet_network.find_lanelet_by_id(self.defining_lane_by_group_id.get(group))
            initial_lane_center = initial_lane.center_vertices

            # create startNode of link
            node_start = None
            if (center[0][0], center[0][1]) in created_nodes:
                node_start = created_nodes.get((center[0][0], center[0][1]))

            if node_start is None:
                deg_start = utility.calc_angle(
                    initial_lane_center[0][0],
                    initial_lane_center[0][1],
                    initial_lane_center[1][0],
                    initial_lane_center[1][1],
                )
                node_start = Node(
                    net,
                    JString(group_id + "-Start"),
                    Point2d(center[0][0], center[0][1]),
                    Direction(deg_start, DirectionUnit.EAST_DEGREE),
                )
                created_nodes.update({(center[0][0], center[0][1]): node_start})

            # create EndNode of link
            node_end = None
            if (center[-1][0], center[-1][1]) in created_nodes:
                node_end = created_nodes.get((center[-1][0], center[-1][1]))

            if node_end is None:
                deg_end = utility.calc_angle(
                    initial_lane_center[-2][0],
                    initial_lane_center[-2][1],
                    initial_lane_center[-1][0],
                    initial_lane_center[-1][1],
                )
                node_end = Node(
                    net,
                    JString(group_id + "-End"),
                    Point2d(center[-1][0], center[-1][1]),
                    Direction(deg_end, DirectionUnit.EAST_DEGREE),
                )
                created_nodes.update({(center[-1][0], center[-1][1]): node_end})

            points = [Point2d(p[0], p[1]) for p in center]
            line = OtsLine2d(points)

            link_type = DefaultsNl.ROAD
            policy = LaneKeepingPolicy.KEEPLANE

            link = CrossSectionLink(net, JString(group_id), node_start, node_end, link_type, line, None, policy)

            self.create_static_objects(
                initial_lane, lanelet_network, sim, net, traffic_signs, traffic_lights, link, created_lanes
            )

        connect_lanes(lanelet_network, net, self.group_id_by_lane_id)

        ConflictBuilder.buildConflicts(net, sim, ConflictBuilder.RelativeWidthGenerator(0.4))

        return net

    def setup_simulator(self) -> (OtsAnimator, CustomModel):
        """Set up the necessary simulator for OTS and create a model"""

        Locale.setDefault(Locale.US)
        sim = OtsAnimator(jpype.JProxy(Serializable, inst="CustomSimulation"))
        mod = CustomModel(sim)
        sim.initialize(Time.ZERO, Duration.ZERO, Duration.instantiateSI(10000000.0), mod)

        return sim, mod

    def setup_analytics(self, net: RoadNetwork, freq: float) -> RoadSampler:
        """
        Sets up the road sampler for the trajectory export

        Parameters
        ----------
        net : RoadNetwork
            The OTS road network
        freq: double
            The frequency for the trajectory logging
        """
        sampler = (
            RoadSampler.build(net)
            .setFrequency(Frequency.instantiateSI(freq))
            .registerExtendedDataType(WorldXData())
            .registerExtendedDataType(WorldYData())
            .registerExtendedDataType(WorldDirData())
            .registerFilterDataType(FilterDataLength())
            .registerFilterDataType(FilterDataWidth())
            .registerFilterDataType(FilterDataGtuType())
            .create()
        )
        for link in self.lanes_by_group_id.keys():
            for lane in self.lanes_by_group_id.get(link):
                path = GraphLaneUtil.createPath(
                    "Lane" + str(lane.lanelet_id), net.getLink(str(link)).getCrossSectionElement(str(lane.lanelet_id))
                )
                GraphPath.initRecording(sampler, path)
        return sampler

    def start_resimulation(self, gui_enabled: bool, simulator: OtsAnimator, model: CustomModel) -> None:
        """
        Starts the actual simulation

        Parameters
        ----------
        gui_enabled : bool
            Whether there should be a GUI or not
        simulator: OtsAnimator
            The OTS simulator
        model: CustomModel
            The model containing the network and all the GTUs
        """
        if gui_enabled:
            CustomSimulation.demo(True, simulator, model)
        else:
            simulator.start()
            simulator.setSpeedFactor(120)
