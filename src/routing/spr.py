"""
Shortest Path Routing (SPR) - Baseline Algorithm.

This module implements traditional Dijkstra-based shortest path routing
using distance as the only metric.
"""

import networkx as nx
from typing import Dict
from .base import RoutingAlgorithm
from ..models.network import SDNController


class ShortestPathRouting(RoutingAlgorithm):
    """
    Shortest Path Routing using Dijkstra's algorithm.

    This baseline algorithm finds the shortest path from each sensor
    to the sink based solely on hop distance, without considering
    energy levels or load balancing.

    Characteristics:
    - Simple and computationally efficient
    - Minimizes hop count and transmission distance
    - Does not consider energy consumption
    - Can lead to unbalanced load and hotspot formation
    - Serves as performance baseline
    """

    @property
    def algorithm_name(self) -> str:
        return "SPR"

    def get_description(self) -> str:
        return ("Shortest Path Routing: Dijkstra-based routing using distance "
                "as the sole metric. Baseline algorithm.")

    def compute_routing_table(self, controller: SDNController) -> Dict[str, str]:
        """
        Compute shortest path routes using Dijkstra's algorithm.

        Args:
            controller: SDN controller with network state

        Returns:
            Routing table mapping nodes to next hops
        """
        routes = {}

        # Get active nodes
        active_nodes = [
            node_id for node_id in controller.network_graph.nodes()
            if controller.nodes[node_id].is_alive
        ]

        if "SINK" not in active_nodes:
            return routes

        # Create subgraph with only active nodes
        active_subgraph = controller.network_graph.subgraph(active_nodes).copy()

        # Compute shortest path from each sensor to sink
        for source in active_nodes:
            if source == "SINK":
                continue

            try:
                # Find shortest path using distance weights
                path = nx.shortest_path(
                    active_subgraph,
                    source=source,
                    target="SINK",
                    weight='weight'
                )

                # Set next hop (second node in path)
                if len(path) > 1:
                    routes[source] = path[1]

            except nx.NetworkXNoPath:
                # No path exists to sink
                pass

        return routes
