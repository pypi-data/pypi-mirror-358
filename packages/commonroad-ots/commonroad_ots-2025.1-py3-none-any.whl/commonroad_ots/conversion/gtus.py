import json
import math
import random

import jpype
import numpy as np
from commonroad.scenario.lanelet import LaneletNetwork
from commonroad.scenario.obstacle import ObstacleType
from commonroad.scenario.scenario import ScenarioID, Scenario
from java.util import ArrayList, HashSet
from jpype._jstring import JString
from nl.tudelft.simulation.jstats.streams import MersenneTwister
from org.djunits.unit import LengthUnit, SpeedUnit
from org.djunits.value.vdouble.scalar import Duration, Length, Speed
from org.opentrafficsim.core.definitions import DefaultsNl
from org.opentrafficsim.core.distributions import ConstantGenerator, Distribution
from org.djunits.unit import DurationUnit, FrequencyUnit
from org.opentrafficsim.road.network import RoadNetwork
from org.opentrafficsim.core.dsol import OtsSimulatorInterface
from org.opentrafficsim.core.network.route import FixedRouteGenerator, Route
from org.opentrafficsim.core.parameters import ParameterFactoryByType
from org.opentrafficsim.road.gtu.generator.characteristics import LaneBasedGtuTemplate, LaneBasedGtuTemplateDistribution
from org.opentrafficsim.road.gtu.generator import GtuSpawner
from org.opentrafficsim.road.gtu.lane.tactical.following import IdmPlusFactory
from org.opentrafficsim.road.gtu.lane.tactical.lmrs import DefaultLmrsPerceptionFactory, LmrsFactory
from org.opentrafficsim.road.gtu.strategical import LaneBasedStrategicalRoutePlannerFactory
from org.opentrafficsim.road.network.lane import LanePosition
from org.opentrafficsim.core.distributions.Distribution import FrequencyAndObject
from org.opentrafficsim.core.network.route import ProbabilisticRouteGenerator
from org.opentrafficsim.core.idgenerator import IdGenerator
from org.opentrafficsim.road.gtu.generator import GeneratorPositions, LaneBasedGtuGenerator, TtcRoomChecker
from org.opentrafficsim.road.gtu.generator.headway import HeadwayGenerator
from org.djunits.value.vdouble.scalar import Frequency
from org.opentrafficsim.core.gtu import GtuType
from org.opentrafficsim.core.definitions import Defaults
from org.opentrafficsim.road.gtu.generator import Injections
from org.djutils.data import Column, ListTable
from org.djutils.immutablecollections import ImmutableLinkedHashMap
from java.util import HashMap
from java.lang import String

from commonroad_ots.conversion.default_speed_limit import get_default_speed_limit_for_lanelet_type
from commonroad_ots.conversion.utility import (
    calc_dist_on_lane,
    find_terminal_lanelet_seq,
    find_all_end_nodes,
    postprocess_generator_positions,
    get_scenario_length,
)
from commonroad_ots.map_matching.map_matching import MapMatcher


def check_driven_distance(state_list: list) -> float:
    """
    Calculates the distance a gtu drives throughout the whole scenario duration
    Parameters
    ----------
    state_list: list
        Trajectory state list with position information.

    Returns
    ---------
    float: Overall driven distance.
    """
    dist = 0.0
    for i in range(len(state_list) - 1):
        dist += math.dist(state_list[i].position, state_list[i + 1].position)
    return dist


def create_gtus(
    net: RoadNetwork,
    sim: OtsSimulatorInterface,
    lanelet_network: LaneletNetwork,
    group_id_by_lane_id: dict,
    obstacles: dict,
    time_step: float,
    scenario_id: ScenarioID,
    parameters: dict,
    seed: int,
    orig_scenario: Scenario,
) -> None:
    """
    Creates GTUs at their exact locations based on the CR dynamic obstacles

    Parameters
    ----------
    net : RoadNetwork
        The OTS network
    sim: OtsSimulatorInterface
        The OTS simulator
    lanelet_network: LaneletNetwork
        The CR lanelet network
    group_id_by_lane_id: dict
        Mapping from groupId/linkId to all the lanes of that group/link
    obstacles: dict
        Mapping from obstacle id to obstacle
    time_step: float
        The time step size of the scenario
    scenario_id: ScenarioID
        The scenario id used for caching
    parameters: dict
        Custom key-value parameter pairs for the driver models
    seed: int
        seed to use for all random drawn values
    orig_scenario: Scenario
        The real-world scenario
    """

    stream = MersenneTwister(seed)
    mm = MapMatcher(lanelet_network)

    # iterate over all dynamic obstacles in cr
    for obstacle_id in obstacles.keys():
        try:
            obstacle = obstacles.get(obstacle_id)
            distance = check_driven_distance(obstacle.prediction.trajectory.state_list)
            if distance < 0.1:
                orig_scenario.remove_obstacle(obstacles.get(obstacle_id))
                continue
            if obstacle.obstacle_type == ObstacleType.PEDESTRIAN:
                orig_scenario.remove_obstacle(obstacles.get(obstacle_id))
                continue

            lane_seq = mm.map_matching(
                obstacle.prediction.trajectory.state_list, obstacle.initial_state, shape=obstacle.obstacle_shape
            )
            lane_id = lane_seq[0]
            final_lanelet = lane_seq[-1]

            # extend the route of the vehicle to a terminal lanelet -> necessary in ots
            path_extension = find_terminal_lanelet_seq(lanelet_network, set(), final_lanelet)
            lane_seq.extend(path_extension)

            link_start = group_id_by_lane_id.get(lane_id)
            lane_start = net.getLink(str(link_start)).getCrossSectionElement(str(lane_id))
            node_start = net.getLink(str(link_start)).getStartNode()

            pos_on_lane = calc_dist_on_lane(
                lane_start.getCenterLine(),
                [obstacle.initial_state.position[0], obstacle.initial_state.position[1]],
            )
            pos = Length.instantiateSI(pos_on_lane)
            position = LanePosition(lane_start, pos)

            match obstacle.obstacle_type:
                case ObstacleType.TRUCK:
                    gtu_type = DefaultsNl.TRUCK
                case ObstacleType.BUS:
                    gtu_type = DefaultsNl.BUS
                case ObstacleType.BICYCLE:
                    gtu_type = DefaultsNl.BICYCLE
                case ObstacleType.PEDESTRIAN:
                    gtu_type = DefaultsNl.PEDESTRIAN
                case ObstacleType.TRAIN:
                    gtu_type = DefaultsNl.TRAIN
                case ObstacleType.MOTORCYCLE:
                    gtu_type = DefaultsNl.MOTORCYCLE
                case _:
                    gtu_type = DefaultsNl.CAR

            node_list = ArrayList()
            node_list.add(node_start)
            for lane_id in lane_seq:
                link_id = group_id_by_lane_id.get(lane_id)
                end_node = net.getLink(str(link_id)).getEndNode()
                if end_node.getId() == node_list[-1].getId():
                    # no need to add the same node twice e.g. for a lateral lane change on the same link
                    continue
                node_list.add(end_node)

            # route to drive
            route = Route(str(obstacle_id), gtu_type, node_list)
            route_generator = FixedRouteGenerator(route)

            idm_plus_factory = IdmPlusFactory(stream)
            tactical_factory = LmrsFactory(idm_plus_factory, DefaultLmrsPerceptionFactory())
            parameter_factory = ParameterFactoryByType()
            for key, value in parameters.items():
                parameter_factory.addParameter(key, value)
            strategical_factory = LaneBasedStrategicalRoutePlannerFactory(tactical_factory, parameter_factory)

            # specify properties of the GTU
            length_generator = ConstantGenerator(Length(obstacle.obstacle_shape.length, LengthUnit.METER))
            width_generator = ConstantGenerator(Length(obstacle.obstacle_shape.width, LengthUnit.METER))
            # we have to specify a speed here, but later on the default max_speed for the gtu_type is used
            maximum_speed_generator = ConstantGenerator(Speed(180, SpeedUnit.KM_PER_HOUR))

            template_gtu_type = LaneBasedGtuTemplate(
                gtu_type,
                length_generator,
                width_generator,
                maximum_speed_generator,
                strategical_factory,
                route_generator,
            )
            template_gtu_type = template_gtu_type.draw()

            # Spawning of GTU
            gtu_creator = GtuSpawner().setNoLaneChangeDistance(Length.instantiateSI(5.0))

            arr = jpype.JArray(jpype.JObject)
            ev = arr(5)
            ev[0] = JString(str(obstacle_id))
            ev[1] = template_gtu_type
            ev[2] = net
            ev[3] = Speed(obstacle.initial_state.velocity, SpeedUnit.METER_PER_SECOND)
            ev[4] = position

            d = Duration.instantiateSI(obstacle.initial_state.time_step * time_step)

            sim.scheduleEventRel(d, gtu_creator, "spawnGtu", ev)

        except Exception as e:
            print(str(scenario_id) + ": Error during creation of gtu", obstacle_id, "with type", obstacle.obstacle_type)
            orig_scenario.remove_obstacle(obstacles.get(obstacle_id))
            print(e.with_traceback())


def prepare_model(parameters: dict, stream: MersenneTwister) -> LaneBasedStrategicalRoutePlannerFactory:
    """
    Registers the default template supplier for the gtu types and creates the tactical/strategical factory
    """
    GtuType.registerTemplateSupplier(DefaultsNl.CAR, Defaults.NL)
    GtuType.registerTemplateSupplier(DefaultsNl.BUS, Defaults.NL)
    GtuType.registerTemplateSupplier(DefaultsNl.TRUCK, Defaults.NL)
    GtuType.registerTemplateSupplier(DefaultsNl.MOTORCYCLE, Defaults.NL)
    GtuType.registerTemplateSupplier(DefaultsNl.BICYCLE, Defaults.NL)

    # strategical factory with parameters
    idm_plus_factory = IdmPlusFactory(stream)
    tactical_factory = LmrsFactory(idm_plus_factory, DefaultLmrsPerceptionFactory())
    parameter_factory = ParameterFactoryByType()
    for key, value in parameters.items():
        parameter_factory.addParameter(key, value)
    strategical_factory = LaneBasedStrategicalRoutePlannerFactory(tactical_factory, parameter_factory)

    return strategical_factory


def create_injections(
    net: RoadNetwork,
    sim: OtsSimulatorInterface,
    lanelet_network: LaneletNetwork,
    group_id_by_lane_id: dict,
    time_step: float,
    obstacles: dict,
    parameters: dict,
    seed: int,
    orig_scenario: Scenario,
) -> None:
    """
    Creates GtuGenerators using Injections based on the CR dynamic obstacles

    Parameters
    ----------
    net : RoadNetwork
        The OTS network
    sim: OtsSimulatorInterface
        The OTS simulator
    lanelet_network: LaneletNetwork
        The CR lanelet network
    group_id_by_lane_id: dict
        Mapping from groupId/linkId to all the lanes of that group/link
    time_step: float
        The time step size of the scenario
    obstacles: dict
        Mapping from obstacle id to obstacle
    parameters: dict
        Custom key-value parameter pairs for the driver models
    seed: int
        seed to use for all random drawn values
    orig_scenario: Scenario
        The real-world scenario
    """

    stream = MersenneTwister(seed)
    strategical_factory = prepare_model(parameters, stream)

    columns = ArrayList()
    columns.add(Column(Injections.TIME_COLUMN, Injections.TIME_COLUMN, Duration, "s"))
    columns.add(Column(Injections.ID_COLUMN, Injections.ID_COLUMN, String))
    columns.add(Column(Injections.POSITION_COLUMN, Injections.POSITION_COLUMN, Length, "m"))
    columns.add(Column(Injections.LANE_COLUMN, Injections.LANE_COLUMN, String))
    columns.add(Column(Injections.LINK_COLUMN, Injections.LINK_COLUMN, String))
    columns.add(Column(Injections.ROUTE_COLUMN, Injections.ROUTE_COLUMN, String))
    columns.add(Column(Injections.SPEED_COLUMN, Injections.SPEED_COLUMN, Speed, "m/s"))
    columns.add(Column(Injections.GTU_TYPE_COLUMN, Injections.GTU_TYPE_COLUMN, String))
    columns.add(Column(Injections.LENGTH_COLUMN, Injections.LENGTH_COLUMN, Length, "m"))
    columns.add(Column(Injections.WIDTH_COLUMN, Injections.WIDTH_COLUMN, Length, "m"))
    columns.add(Column(Injections.FRONT_COLUMN, Injections.FRONT_COLUMN, Length, "m"))

    table = ListTable("injections", "injections", columns)
    gtu_types = HashMap()
    gtu_types.put("ObstacleType.CAR", DefaultsNl.CAR)
    gtu_types.put("ObstacleType.BUS", DefaultsNl.BUS)
    gtu_types.put("ObstacleType.TRUCK", DefaultsNl.TRUCK)
    gtu_types.put("ObstacleType.MOTORCYCLE", DefaultsNl.MOTORCYCLE)
    gtu_types.put("ObstacleType.BICYCLE", DefaultsNl.BICYCLE)
    gtu_types = ImmutableLinkedHashMap(gtu_types)

    mm = MapMatcher(lanelet_network)

    for obstacle_id in obstacles.keys():
        try:
            obstacle = obstacles.get(obstacle_id)
            distance = check_driven_distance(obstacle.prediction.trajectory.state_list)
            if distance < 0.1:
                orig_scenario.remove_obstacle(obstacles.get(obstacle_id))
                continue
            if obstacle.obstacle_type == ObstacleType.PEDESTRIAN:
                orig_scenario.remove_obstacle(obstacles.get(obstacle_id))
                continue

            lane_seq = mm.map_matching(
                obstacle.prediction.trajectory.state_list, obstacle.initial_state, shape=obstacle.obstacle_shape
            )
            lane_id = lane_seq[0]
            final_lanelet = lane_seq[-1]

            # extend the route of the vehicle to a terminal lanelet -> necessary in ots
            path_extension = find_terminal_lanelet_seq(lanelet_network, set(), final_lanelet)
            lane_seq.extend(path_extension)

            link_start = group_id_by_lane_id.get(lane_id)
            lane_start = net.getLink(str(link_start)).getCrossSectionElement(str(lane_id))
            node_start = net.getLink(str(link_start)).getStartNode()

            pos_on_lane = calc_dist_on_lane(
                lane_start.getCenterLine(),
                [obstacle.initial_state.position[0], obstacle.initial_state.position[1]],
            )

            node_list = ArrayList()
            node_list.add(node_start)
            for lane_id in lane_seq:
                link_id = group_id_by_lane_id.get(lane_id)
                end_node = net.getLink(str(link_id)).getEndNode()
                if end_node.getId() == node_list[-1].getId():
                    # no need to add the same node twice e.g. for a lateral lane change on the same link
                    continue
                node_list.add(end_node)

            # route to drive
            route = Route("Route_" + str(obstacle_id), gtu_types.get(str(obstacle.obstacle_type)), node_list)
            net.addRoute(gtu_types.get(str(obstacle.obstacle_type)), route)
            arr = jpype.JArray(jpype.JObject)
            properties = arr(11)
            properties[0] = Duration.instantiateSI(obstacle.initial_state.time_step * time_step)
            properties[1] = JString(str(obstacle_id))
            properties[2] = Length.instantiateSI(pos_on_lane)
            properties[3] = JString(str(lane_seq[0]))
            properties[4] = JString(str(group_id_by_lane_id.get(lane_seq[0])))
            properties[5] = JString("Route_" + str(obstacle_id))
            properties[6] = Speed(obstacle.initial_state.velocity, SpeedUnit.METER_PER_SECOND)
            properties[7] = JString(str(obstacle.obstacle_type))
            properties[8] = Length(obstacle.obstacle_shape.length, LengthUnit.METER)
            properties[9] = Length(obstacle.obstacle_shape.width, LengthUnit.METER)
            properties[10] = Length(obstacle.obstacle_shape.length, LengthUnit.METER).divide(2)

            table.addRow(properties)
        except Exception as e:
            print("Error during creation of gtu", obstacle_id, "with type", str(obstacle.obstacle_type))
            orig_scenario.remove_obstacle(obstacles.get(obstacle_id))
            print(e)

    injections = Injections(table, net, gtu_types, strategical_factory, stream, Duration.instantiateSI(5.0))

    LaneBasedGtuGenerator(
        "Injections",
        injections,
        injections.asLaneBasedGtuCharacteristicsGenerator(),
        injections,
        net,
        sim,
        injections,
        injections,
    )


def get_routes(obstacles: dict, lanelet_network: LaneletNetwork, orig_scenario: Scenario) -> dict:
    """
    Groups all (moving) obstacle routes by start-lanelet id and gtu type.
    The number of identical routes for the same gtu type are counted

    Parameters
    ----------
    obstacles : dict
        The commonRoad dynamic obstacles
    lanelet_network: LaneletNetwork
        The commonRoad lanelet network
    orig_scenario
        The real-world scenario

    Returns
    -------
    routes
        obstacles routes grouped by start_id and gtu type
    """

    routes = dict()

    for obstacle_id in obstacles.keys():
        obstacle = obstacles.get(obstacle_id)
        distance = check_driven_distance(obstacle.prediction.trajectory.state_list)
        if distance < 0.1:
            orig_scenario.remove_obstacle(obstacles.get(obstacle_id))
            continue

        try:
            start_id = lanelet_network.find_most_likely_lanelet_by_state([obstacle.initial_state])[0]
            end_id = lanelet_network.find_most_likely_lanelet_by_state([obstacle.prediction.trajectory.final_state])[0]
        except Exception:
            orig_scenario.remove_obstacle(obstacles.get(obstacle_id))
            print("Skipping vehicle", obstacle_id)
            continue

        match obstacle.obstacle_type:
            case ObstacleType.TRUCK:
                gtu_type = DefaultsNl.TRUCK
            case ObstacleType.BUS:
                gtu_type = DefaultsNl.BUS
            case ObstacleType.BICYCLE:
                gtu_type = DefaultsNl.BICYCLE
            case ObstacleType.PEDESTRIAN:
                gtu_type = DefaultsNl.PEDESTRIAN
            case ObstacleType.TRAIN:
                gtu_type = DefaultsNl.TRAIN
            case ObstacleType.MOTORCYCLE:
                gtu_type = DefaultsNl.MOTORCYCLE
            case _:
                gtu_type = DefaultsNl.CAR

        if (start_id, gtu_type) in routes.keys():
            ends = routes.get((start_id, gtu_type))
            if end_id in ends.keys():
                ends.update({end_id: ends.get(end_id) + 1})
            else:
                ends.update({end_id: 1})
        else:
            ends = dict()
            ends.update({end_id: 1})
            routes.update({(start_id, gtu_type): ends})

    return routes


def create_gtu_generators(
    net: RoadNetwork,
    sim: OtsSimulatorInterface,
    lanelet_network: LaneletNetwork,
    group_id_by_lane_id: dict,
    obstacles: dict,
    parameters: dict,
    seed: int,
    orig_scenario: Scenario,
    demands={},
) -> None:
    """
    Creates GTU generators based on the traffic demands of the original scenario

    Parameters
    ----------
    net : RoadNetwork
        The OTS network
    sim: OtsSimulatorInterface
        The OTS simulator
    lanelet_network: LaneletNetwork
        The CR lanelet network
    group_id_by_lane_id: dict
        Mapping from groupId/linkId to all the lanes of that group/link
    obstacles: dict
        Mapping from obstacle id to obstacle
    parameters: dict
        Custom key-value parameter pairs for the driver models
    seed: int
        seed to use for all random drawn values
    orig_scenario: Scenario
        The real-world scenario
    demands: dict
        Mapping from lanelet id to demand per Minute
    """

    templates_by_start_node = dict()
    stream = MersenneTwister(seed)

    strategical_factory = prepare_model(parameters, stream)
    routes_by_start_id_and_gtu_type = get_routes(obstacles, lanelet_network, orig_scenario)

    postprocess_generator_positions(routes_by_start_id_and_gtu_type, lanelet_network)

    # gtu templates
    for (start_id, gtu_type) in routes_by_start_id_and_gtu_type.keys():
        routes = ArrayList()
        n = sum(routes_by_start_id_and_gtu_type.get((start_id, gtu_type)).values())
        for end_id in routes_by_start_id_and_gtu_type.get((start_id, gtu_type)).keys():
            frac = routes_by_start_id_and_gtu_type.get((start_id, gtu_type)).get(end_id) / n
            link_start = group_id_by_lane_id.get(start_id)
            start_node = net.getLink(str(link_start)).getStartNode()
            orig_link_end = group_id_by_lane_id.get(end_id)
            orig_end_node = net.getLink(str(orig_link_end)).getEndNode()

            extension = find_terminal_lanelet_seq(lanelet_network, set(), end_id)
            prev_end = ""
            if len(extension) > 0:
                prev_end = end_id
                end_id = extension[-1]

            link_end = group_id_by_lane_id.get(end_id)
            end_node = net.getLink(str(link_end)).getEndNode()

            via = ArrayList()
            via.add(orig_end_node)

            route = net.getShortestRouteBetween(gtu_type, start_node, end_node, via)
            if route is None:
                print(f"Couldn't create route with start {start_id} and end {end_id} with intermediate: {prev_end}")
                continue
            routes.add(FrequencyAndObject(frac, route))

        route_generator = ProbabilisticRouteGenerator(routes, stream)
        defaultCharacteristics = GtuType.defaultCharacteristics(gtu_type, net, stream)
        gtu_template = LaneBasedGtuTemplate(
            gtu_type,
            ConstantGenerator(defaultCharacteristics.getLength()),
            ConstantGenerator(defaultCharacteristics.getWidth()),
            ConstantGenerator(defaultCharacteristics.getMaximumSpeed()),
            strategical_factory,
            route_generator,
        )

        if start_id not in templates_by_start_node:
            templates_by_start_node.update({start_id: list()})
        templates_by_start_node.get(start_id).append((gtu_template, n))

    # GTU generators
    id_generator = IdGenerator("")
    room_checker = TtcRoomChecker(Duration(5.0, DurationUnit.SI))
    for start_id in templates_by_start_node.keys():
        n = sum(i for (temp, i) in templates_by_start_node.get(start_id))
        distribution = Distribution(stream)
        for (templ, num) in templates_by_start_node.get(start_id):
            distribution.add(FrequencyAndObject(num / n, templ))

        link_start = group_id_by_lane_id.get(start_id)
        lane_start = net.getLink(str(link_start)).getCrossSectionElement(str(start_id))

        positions = HashSet()
        pos = Length.instantiateSI(2)
        positions.add(LanePosition(lane_start, pos))
        characteristicsGenerator = LaneBasedGtuTemplateDistribution(distribution)
        if start_id in demands.keys():
            demand = demands.get(start_id) / 60
        else:
            demand = n / get_scenario_length(orig_scenario)
        headway = HeadwayGenerator(Frequency(demand, FrequencyUnit.PER_SECOND), stream)

        LaneBasedGtuGenerator(
            "Gen_" + str(start_id),
            headway,
            characteristicsGenerator,
            GeneratorPositions.create(positions, stream),
            net,
            sim,
            room_checker,
            id_generator,
        )


def generate_random_generators(
    net: RoadNetwork,
    sim: OtsSimulatorInterface,
    lanelet_network: LaneletNetwork,
    group_id_by_lane_id: dict,
    speed_limits: dict,
    parameters: dict,
    seed: int,
) -> None:
    """
    Creates random GTU generators at all incoming lanelets

    Parameters
    ----------
    net : RoadNetwork
        The OTS network
    sim: OtsSimulatorInterface
        The OTS simulator
    lanelet_network: LaneletNetwork
        The CR lanelet network
    group_id_by_lane_id: dict
        Mapping from groupId/linkId to all the lanes of that group/link
    parameters: dict
        Custom key-value parameter pairs for the driver models
    seed: int
        seed to use for all random drawn values
    """

    stream = MersenneTwister(seed)
    id_generator = IdGenerator("")
    room_checker = TtcRoomChecker(Duration(5.0, DurationUnit.SI))
    strategical_factory = prepare_model(parameters, stream)

    for lanelet in lanelet_network.lanelets:
        if len(lanelet.predecessor) == 0:
            load_factor = random.normalvariate(mu=0.3, sigma=0.2)
            link_start = group_id_by_lane_id.get(lanelet.lanelet_id)
            start_node = net.getLink(str(link_start)).getStartNode()
            lane_start = net.getLink(str(link_start)).getCrossSectionElement(str(lanelet.lanelet_id))
            end_nodes = find_all_end_nodes(net, lanelet_network, lanelet, group_id_by_lane_id)

            # incoming lanelet
            freq_car = max(0.0, np.random.normal(0.86478, 0.03313))
            freq_bus = max(0.0, np.random.normal(0.00511, 0.00297))
            freq_truck = max(0.0, np.random.normal(0.11999, 0.02962))
            freq_motorcycle = max(0.0, np.random.normal(0.00912, 0.00630))

            sum_freq = freq_car + freq_bus + freq_truck + freq_motorcycle
            frequencies = [freq_car / sum_freq, freq_bus / sum_freq, freq_truck / sum_freq, freq_motorcycle / sum_freq]
            # print(lanelet.lanelet_id, frequencies)
            gtu_types = [DefaultsNl.CAR, DefaultsNl.BUS, DefaultsNl.TRUCK, DefaultsNl.MOTORCYCLE]

            distribution = Distribution(stream)

            for i, gtu_type in enumerate(gtu_types):
                routes = ArrayList()
                dist = np.random.uniform(0, 1, len(end_nodes))
                for n, end_node in enumerate(end_nodes):
                    route = net.getShortestRouteBetween(gtu_type, start_node, end_node)
                    # print(lanelet.lanelet_id, gtu_type, end_node, dist[n] / sum(dist))
                    routes.add(FrequencyAndObject(dist[n] / sum(dist), route))

                route_generator = ProbabilisticRouteGenerator(routes, stream)
                defaultCharacteristics = GtuType.defaultCharacteristics(gtu_type, net, stream)
                gtu_template = LaneBasedGtuTemplate(
                    gtu_type,
                    ConstantGenerator(defaultCharacteristics.getLength()),
                    ConstantGenerator(defaultCharacteristics.getWidth()),
                    ConstantGenerator(defaultCharacteristics.getMaximumSpeed()),
                    strategical_factory,
                    route_generator,
                )

                distribution.add(FrequencyAndObject(frequencies[i], gtu_template))

            positions = HashSet()
            pos = Length.instantiateSI(2)
            positions.add(LanePosition(lane_start, pos))
            characteristicsGenerator = LaneBasedGtuTemplateDistribution(distribution)

            # calculate lanelet capacity
            speed_limit = get_default_speed_limit_for_lanelet_type(lanelet.lanelet_type)
            for sign_id in lanelet.traffic_signs:
                if sign_id in speed_limits.keys():
                    speed_limit = speed_limits.get(sign_id)
            l = (
                frequencies[0] * 4.19 + frequencies[1] * 12 + frequencies[2] * 12 + frequencies[3] * 2.1
            )  # we use the default OTS length values
            s_0 = 2.0  # m -- minimum distance between vehicles
            T = 1.45  # s -- desired time headway
            demand = 60.0 * speed_limit / (l + (s_0 + speed_limit * T))

            headway = HeadwayGenerator(Frequency(demand * load_factor, FrequencyUnit.PER_MINUTE), stream)

            LaneBasedGtuGenerator(
                "Gen_" + str(lanelet.lanelet_id),
                headway,
                characteristicsGenerator,
                GeneratorPositions.create(positions, stream),
                net,
                sim,
                room_checker,
                id_generator,
            )
