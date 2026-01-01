"""
Adaptive Load Balancing (ALB) Routing Algorithm.

This module implements adaptive load balancing with multi-metric optimization
considering energy, distance, and traffic load.
"""

import networkx as nx
from typing import Dict
from .base import RoutingAlgorithm
from ..models.network import SDNController


class AdaptiveLoadBalancing(RoutingAlgorithm):
    """
    Adaptive Load Balancing with multi-metric optimization.

    This algorithm considers three metrics when making routing decisions:
    1. Energy: Residual energy of nodes
    2. Distance: Physical distance between nodes
    3. Load: Traffic load (transmitted packets)

    The composite cost function is:
    Cost = w_e * energy_cost + w_d * distance_cost + w_l * load_cost

    Characteristics:
    - Balances energy, distance, and load
    - Prevents hotspot formation
    - Improves network lifetime and fairness
    - Adaptive to network state
    """

    def __init__(
        self,
        weight_energy: float = 0.4,
        weight_distance: float = 0.3,
        weight_load: float = 0.3
    ):
        """
        Initialize Adaptive Load Balancing routing.

        Args:
            weight_energy: Weight for energy metric (0-1)
            weight_distance: Weight for distance metric (0-1)
            weight_load: Weight for load metric (0-1)

        Raises:
            ValueError: If weights don't sum to approximately 1.0
        """
        total = weight_energy + weight_distance + weight_load
        if not 0.99 <= total <= 1.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")

        self.weight_energy = weight_energy
        self.weight_distance = weight_distance
        self.weight_load = weight_load

    @property
    def algorithm_name(self) -> str:
        return "ALB"

    def get_description(self) -> str:
        return (f"Adaptive Load Balancing: Multi-metric optimization "
                f"(E={self.weight_energy}, D={self.weight_distance}, "
                f"L={self.weight_load})")

    def compute_routing_table(self, controller: SDNController) -> Dict[str, str]:
        """
        Compute adaptive load-balanced routes.

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

        # Build weighted graph
        weighted_graph = nx.Graph()
        for node in active_nodes:
            weighted_graph.add_node(node)

        # Calculate maximum load for normalization
        max_transmitted = max(
            (controller.nodes[n].transmitted_packets for n in active_nodes),
            default=1
        )
        if max_transmitted == 0:
            max_transmitted = 1

        # Add weighted edges
        for u, v in controller.network_graph.edges():
            if u not in active_nodes or v not in active_nodes:
                continue

            # Get edge properties
            distance = controller.network_graph[u][v]['weight']

            # Energy metric: use minimum of the two nodes
            energy_u = controller.nodes[u].get_residual_energy_ratio()
            energy_v = controller.nodes[v].get_residual_energy_ratio()
            min_energy = min(energy_u, energy_v)

            # Energy cost: lower energy = higher cost
            energy_cost = 1.0 - min_energy

            # Distance cost: normalized
            distance_cost = distance / controller.config.comm_range

            # Load metric: average load of both nodes
            load_u = controller.nodes[u].transmitted_packets / max_transmitted
            load_v = controller.nodes[v].transmitted_packets / max_transmitted
            load_factor = (load_u + load_v) / 2

            # Composite cost
            total_cost = (
                self.weight_energy * energy_cost +
                self.weight_distance * distance_cost +
                self.weight_load * load_factor
            )

            weighted_graph.add_edge(u, v, weight=max(0.01, total_cost))

        # Compute shortest paths
        for source in active_nodes:
            if source == "SINK":
                continue

            try:
                path = nx.shortest_path(
                    weighted_graph,
                    source=source,
                    target="SINK",
                    weight='weight'
                )

                if len(path) > 1:
                    routes[source] = path[1]

            except nx.NetworkXNoPath:
                pass

        return routes
