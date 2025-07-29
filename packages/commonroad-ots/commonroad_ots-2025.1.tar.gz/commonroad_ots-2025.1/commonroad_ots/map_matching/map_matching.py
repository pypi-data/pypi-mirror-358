import math
from typing import List, Set, Tuple

import networkx as nx
import numpy as np
from commonroad.geometry.shape import Rectangle
from commonroad.scenario.lanelet import LaneletNetwork
from commonroad.scenario.state import State


class MapMatcher:
    """
    Map matching class for CommonRoad scenarios. The lanelet network is converted into a graph structure. Candidate
    routes are generated using the all_simple_paths algorithm with a cutoff value. The best route is selected based on
    the intersection rate of the trajectory (or vehicle, if considering its shape) with the lanelets.
    """

    def __init__(self, lanelet_network: LaneletNetwork) -> None:
        """
        Constructor of the MapMatcher class.

        Parameters
        ----------
        lanelet_network: LaneletNetwork
            The lanelet network that will be used for map matching.
        """
        self._lanelet_network: LaneletNetwork = lanelet_network
        self._graph: nx.DiGraph = None
        self._mapping: dict = {lanelet.lanelet_id: i for i, lanelet in enumerate(self._lanelet_network.lanelets)}
        self._mapping_reverse: dict = {
            i: lanelet.lanelet_id for i, lanelet in enumerate(self._lanelet_network.lanelets)
        }
        self.create_graph()

    def create_graph(self) -> None:
        """
        Create a nx.DiGraph from the lanelet network.
        """
        num_lanelets = len(self._lanelet_network.lanelets)
        adjacency_matrix = np.zeros((num_lanelets, num_lanelets), dtype=bool)

        for lanelet in self._lanelet_network.lanelets:
            # right adjacency?
            if lanelet.adj_right is not None:
                if lanelet.adj_right_same_direction:
                    adjacency_matrix[self._mapping[lanelet.lanelet_id], self._mapping[lanelet.adj_right]] = True

            # left adjacency?
            if lanelet.adj_left is not None:
                if lanelet.adj_left_same_direction:
                    adjacency_matrix[self._mapping[lanelet.lanelet_id], self._mapping[lanelet.adj_left]] = True

            # set the corresponding entries in the adjacency matrix to True
            for successor in lanelet.successor:
                adjacency_matrix[self._mapping[lanelet.lanelet_id], self._mapping[successor]] = True

        self._graph = nx.from_numpy_array(adjacency_matrix, create_using=nx.DiGraph)

    def get_lanelet_candidates(self, state: State, shape: Rectangle = None) -> Set[int]:
        """
        Get lanelet candidates based on the state.

        Parameters
        ----------
        state: State
            The state to get the lanelet candidates for.
        shape: Rectangle
            The shape of the vehicle. If not a rectangle, the vehicle is treated as a point.

        Returns
        -------
        lanelet_candidates: Set[int]
            A set of lanelet candidates.
        """
        lanelet_candidates = set()
        if isinstance(shape, Rectangle):
            transformed_shape = shape.rotate_translate_local(state.position, state.orientation)
            lanelet_ids = self._lanelet_network.find_lanelet_by_position(
                [vertex for vertex in transformed_shape.vertices]
            )
        else:
            lanelet_ids = self._lanelet_network.find_lanelet_by_position([state.position])
        for x in lanelet_ids:
            for y in x:
                lanelet_candidates.add(y)
        return lanelet_candidates

    def get_route_candidates(
        self, state_start: State, state_end: State, exploration_value: int, shape: Rectangle = None
    ) -> List[List[int]]:
        """
        Get route candidates based on the start and end states.

        Parameters
        ----------
        state_start: State
            The possible start states of the trajectory.
        state_end: State
            The possible end states of the trajectory.
        exploration_value: float
            To add to the shortest path's length to get the cutoff value for the all_simple_paths algorithm.
        shape: Rectangle
            The shape of the vehicle. If not a rectangle, the vehicle is treated as a point.

        Returns
        -------
        route_candidates: List[List[int]]
            A list of route candidates. Each route candidate is a list of lanelet ids.
        """
        assert exploration_value >= 0
        # Exploration value should be at least 2. This enables one back-and-forth lane change.

        # Start and end lanelets:
        # Only use shape if the vehicle center does not lie in any lanelet.
        # This ensures that these lanelets are not cut off if the vehicle shape touches other lanelets at the very
        # beginning or end.
        lanelets_start = self.get_lanelet_candidates(state_start)
        if len(lanelets_start) < 1:
            lanelets_start = self.get_lanelet_candidates(state_start, shape=shape)
        lanelets_end = self.get_lanelet_candidates(state_end)
        if len(lanelets_end) < 1:
            lanelets_end = self.get_lanelet_candidates(state_end, shape=shape)

        assert len(lanelets_start) > 0, "No lanelet found for start position"
        assert len(lanelets_end) > 0, "No lanelet found for end position"

        # Use the global shortest path.
        shortest_path_length = 9999
        for lt_start in lanelets_start:
            for lt_end in lanelets_end:
                if lt_start == lt_end:
                    return [[lt_start]]
                else:
                    try:
                        candidate_length = nx.shortest_path_length(
                            self._graph, source=self._mapping[lt_start], target=self._mapping[lt_end]
                        )
                        shortest_path_length = min(shortest_path_length, candidate_length)
                    except nx.NetworkXNoPath:
                        pass
                if shortest_path_length == 0:
                    raise ValueError("This should never occur. Debug!")

        if not shortest_path_length < 9999:  # No path found between start and end position
            # relax: use shape for start and end
            lanelets_start = self.get_lanelet_candidates(state_start, shape=shape)
            lanelets_end = self.get_lanelet_candidates(state_end, shape=shape)

            for lt_start in lanelets_start:
                for lt_end in lanelets_end:
                    if lt_start == lt_end:
                        return [[lt_start]]
                    else:
                        try:
                            candidate_length = nx.shortest_path_length(
                                self._graph, source=self._mapping[lt_start], target=self._mapping[lt_end]
                            )
                            shortest_path_length = min(shortest_path_length, candidate_length)
                        except nx.NetworkXNoPath:
                            pass
                    if shortest_path_length == 0:
                        raise ValueError("This should never occur. Debug!")
            if not shortest_path_length < 9999:
                return []

        route_candidates = []
        for lt_start in lanelets_start:
            for lt_end in lanelets_end:
                # lt_start == lt_end already handled above.
                try:
                    for route in nx.all_simple_paths(
                        self._graph,
                        source=self._mapping[lt_start],
                        target=self._mapping[lt_end],
                        cutoff=math.ceil(shortest_path_length + exploration_value),
                    ):
                        route_candidates.append([self._mapping_reverse[i] for i in route])
                except nx.NetworkXNoPath:
                    continue

        if len(route_candidates) >= 100:
            print(f"Many route candidates: {len(route_candidates)}. Reduce exploration value: {exploration_value}.")

        return route_candidates

    def map_matching(
        self,
        trajectory: List[State],
        initial_state: State = None,
        shape: Rectangle = None,
        return_lanelet_trace: bool = False,
        accuracy_threshold: float = 0.3,
        exploration_value: int = 2,
    ) -> [List[int], List[int]]:
        """
        Map matching algorithm to find the best route for a given trajectory. The best route is selected based on the
        intersection rate of the trajectory (or vehicle, if considering its shape) with the lanelets.

        Parameters
        ----------
        trajectory: List[State]
            The trajectory to map match.
        initial_state: State
            Extends the trajectory by adding the initial state to the beginning of the trajectory.
        shape: Rectangle
            The shape of the vehicle. If None, the trajectory is treated as a point.
        return_lanelet_trace: bool
            If True, the lanelet trace is returned.
        accuracy_threshold: float
            The accuracy threshold to consider a route as valid.
        exploration_value: int
            Add to the shortest path's length to get the cutoff value for the all_simple_paths algorithm.

        Returns
        -------
        best_route: List[int]
            The best route found by the map matching algorithm.
        lanelet_trace: List[int]
            The lanelet trace. Only returned if return_lanelet_trace is True.

        Raises
        ------
        ValueError
            If no route is found.
        """
        # print("Started MapMatching")

        if initial_state is not None:
            trajectory = [initial_state] + trajectory

        # get route candidates
        route_candidates = self.get_route_candidates(
            trajectory[0], trajectory[-1], shape=shape, exploration_value=exploration_value
        )
        min_route_length = len(min(route_candidates, key=len))

        # calculate the score for each route candidate
        best_score = -1
        best_route_index = -1
        for route_index, route in enumerate(route_candidates):
            accuracy, score = self.evaluate_route_score(route, trajectory, min_route_length)
            if accuracy > accuracy_threshold and score > best_score:
                best_score = score
                best_route_index = route_index

        if best_route_index == -1:
            raise ValueError("No route found.")
        best_route = route_candidates[best_route_index]
        # print("Finished MapMatching")
        if return_lanelet_trace:
            lanelet_trace = self.construct_lanelet_trace(best_route, trajectory)
            return best_route, lanelet_trace
        else:
            return best_route

    def evaluate_route_score(self, route: List[int], trajectory: List[State], min_steps: int) -> Tuple[float, float]:
        """
        Evaluate the score of a route based on the intersection rate of the trajectory (or vehicle, if considering its
        shape) with the lanelets.

        Parameters
        ----------
        route: List[int]
            The route to evaluate. List of lanelet ids.
        trajectory: List[State]
            The trajectory to evaluate. List of states.
        min_steps: int
            The minimum number of steps of any route. Required for the score calculation.

        Returns
        -------
        accuracy, score: Tuple[float, float]
            The score of the route.
        """
        # TODO ideas:
        #  - Consider distance to centerline instead of binary inside/outside.
        #  - Consider shape of vehicle.

        counter_inside = 0
        counter_outside = 0
        for state in trajectory:
            if self.is_inside(route, state):
                counter_inside += 1
            else:
                counter_outside += 1
        accuracy = counter_inside / (counter_inside + counter_outside)
        score = 2 * accuracy + min_steps / len(route)  # fewer lanelets incentive
        return accuracy, score

    def is_inside(self, lt_ids: List[int], state: State, shape: Rectangle = None) -> bool:
        """
        Check if a state is inside the lanelets.

        Parameters
        ----------
        lt_ids: List[int]
            The lanelet ids to check.
        state: State
            The state to check.
        shape:
            The shape of the vehicle. If None, the state is treated as a point.

        Returns
        -------
        is_inside: bool
            True if the state is inside the lanelets, False otherwise.
        """
        if isinstance(shape, Rectangle):
            transformed_shape = shape.rotate_translate_local(state.position, state.orientation)
            for lt_id in lt_ids:
                for vertex in transformed_shape.vertices:  # TODO using the vertices is not accurate
                    if self._lanelet_network.find_lanelet_by_id(lt_id).polygon.contains_point(vertex):
                        return True
            return False

        else:  # no Rectangle given, treat as point
            for lt_id in lt_ids:
                if self._lanelet_network.find_lanelet_by_id(lt_id).polygon.contains_point(state.position):
                    return True
            return False

    def construct_lanelet_trace(self, route: List[int], trajectory: List[State]) -> List[int]:
        """
        Construct the lanelet trace based on the route and the trajectory.

        Parameters
        ----------
        route: List[int]
            The route to use. List of lanelet ids.
        trajectory:
            The trajectory to use. List of states.

        Returns
        -------
        lanelet_trace: List[int]
            The lanelet trace.
        """
        # TODO consider shape of vehicle?
        lanelet_trace = []
        counter_route = -1
        for state in trajectory:
            if counter_route < len(route) - 1 and self._lanelet_network.find_lanelet_by_id(
                route[counter_route + 1]
            ).polygon.contains_point(state.position):
                counter_route += 1

            lanelet_trace.append(route[counter_route])

        return lanelet_trace
