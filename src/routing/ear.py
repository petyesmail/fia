"""
Energy-Aware Routing (EAR) Algorithm.

This module implements energy-aware routing that considers both
distance and residual energy when making routing decisions.
"""

import networkx as nx
from typing import Dict
from .base import RoutingAlgorithm
from ..models.network import SDNController


class EnergyAwareRouting(RoutingAlgorithm):
    """
    Energy-Aware Routing with residual energy consideration.

    This algorithm balances distance and energy consumption by
    preferring routes through nodes with higher residual energy.

    The composite cost function is:
    Cost = α * energy_cost + (1-α) * distance_cost

    Where:
    - energy_cost = 2 - (energy_u + energy_v)
    - distance_cost = distance / comm_range
    - α = energy_weight (default: 0.6)

    Characteristics:
    - Considers node residual energy
    - Balances energy and distance
    - Extends network lifetime compared to SPR
    - Higher computational complexity than SPR
    """

    def __init__(self, energy_weight: float = 0.6):
        """
        Initialize Energy-Aware Routing.

        Args:
            energy_weight: Weight for energy term (0-1). Higher values
                          prioritize energy conservation.
        """
        if not 0 <= energy_weight <= 1:
            raise ValueError("energy_weight must be between 0 and 1")

        self.energy_weight = energy_weight

    @property
    def algorithm_name(self) -> str:
        return "EAR"

    def get_description(self) -> str:
        return (f"Energy-Aware Routing: Balances distance and energy "
                f"(weight={self.energy_weight})")

    def compute_routing_table(self, controller: SDNController) -> Dict[str, str]:
        """
        Compute energy-aware routes.

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

        # Add weighted edges
        for u, v in controller.network_graph.edges():
            if u not in active_nodes or v not in active_nodes:
                continue

            # Get edge properties
            distance = controller.network_graph[u][v]['weight']
            energy_u = controller.nodes[u].get_residual_energy_ratio()
            energy_v = controller.nodes[v].get_residual_energy_ratio()

            # Calculate composite cost
            # Energy cost: lower residual energy = higher cost
            energy_cost = 2.0 - (energy_u + energy_v)

            # Distance cost: normalized by communication range
            distance_cost = distance / controller.config.comm_range

            # Weighted combination
            total_cost = (
                self.energy_weight * energy_cost +
                (1 - self.energy_weight) * distance_cost
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
