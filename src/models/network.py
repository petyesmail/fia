"""
Network controller for SDN-based WSN management.

This module implements the Software-Defined Networking controller
that manages the wireless sensor network.
"""

import networkx as nx
from typing import Dict, List, Optional, Set, TYPE_CHECKING
from .node import SensorNode

if TYPE_CHECKING:
    from ..config import SimulationConfig


class SDNController:
    """
    Software-Defined Networking Controller for centralized WSN management.

    The SDN controller maintains a global view of the network and provides:
    - Node registration and management
    - Link establishment and topology maintenance
    - Network state monitoring
    - Routing table computation support

    Attributes:
        config: Simulation configuration
        nodes: Dictionary mapping node IDs to SensorNode objects
        network_graph: NetworkX graph representing network topology
    """

    def __init__(self, config: 'SimulationConfig'):
        """
        Initialize SDN controller.

        Args:
            config: Simulation configuration
        """
        self.config = config
        self.nodes: Dict[str, SensorNode] = {}
        self.network_graph = nx.Graph()

        # Statistics
        self.total_nodes_registered = 0
        self.total_links_established = 0

    def register_node(self, node: SensorNode):
        """
        Register a sensor node with the controller.

        Args:
            node: SensorNode to register
        """
        self.nodes[node.id] = node
        self.network_graph.add_node(node.id)
        self.total_nodes_registered += 1

    def establish_link(self, node1_id: str, node2_id: str, weight: float):
        """
        Establish a bidirectional link between two nodes.

        Args:
            node1_id: First node ID
            node2_id: Second node ID
            weight: Link weight (typically distance)
        """
        if node1_id not in self.nodes or node2_id not in self.nodes:
            raise ValueError(f"Cannot establish link: node(s) not registered")

        # Add edge to graph
        self.network_graph.add_edge(node1_id, node2_id, weight=weight)

        # Update neighbor lists
        if node2_id not in self.nodes[node1_id].neighbors:
            self.nodes[node1_id].neighbors.append(node2_id)
        if node1_id not in self.nodes[node2_id].neighbors:
            self.nodes[node2_id].neighbors.append(node1_id)

        self.total_links_established += 1

    def get_active_sensors(self) -> List[str]:
        """
        Get list of active (alive, non-sink) sensor nodes.

        Returns:
            List of active sensor node IDs
        """
        return [
            node_id for node_id, node in self.nodes.items()
            if node.is_alive and not node.is_sink
        ]

    def get_all_active_nodes(self) -> List[str]:
        """
        Get list of all active nodes (including sink).

        Returns:
            List of active node IDs
        """
        return [
            node_id for node_id, node in self.nodes.items()
            if node.is_alive
        ]

    def get_active_node_count(self) -> int:
        """
        Get count of active sensor nodes.

        Returns:
            Number of active sensors
        """
        return len(self.get_active_sensors())

    def get_total_node_count(self) -> int:
        """
        Get total count of sensor nodes (excluding sink).

        Returns:
            Total number of sensor nodes
        """
        return sum(1 for node in self.nodes.values() if not node.is_sink)

    def get_network_energy_statistics(self) -> dict:
        """
        Calculate comprehensive network energy statistics.

        Returns:
            Dictionary with energy statistics
        """
        active_sensors = [
            self.nodes[nid] for nid in self.get_active_sensors()
        ]

        if not active_sensors:
            return {
                'total_initial_energy': 0.0,
                'total_current_energy': 0.0,
                'total_consumed_energy': 0.0,
                'average_residual_energy': 0.0,
                'min_residual_energy': 0.0,
                'max_residual_energy': 0.0,
                'std_residual_energy': 0.0,
                'network_lifetime_ratio': 0.0
            }

        energy_ratios = [node.get_residual_energy_ratio() for node in active_sensors]
        energies = [node.current_energy for node in active_sensors]

        return {
            'total_initial_energy': sum(n.initial_energy for n in active_sensors),
            'total_current_energy': sum(energies),
            'total_consumed_energy': sum(n.total_energy_consumed for n in active_sensors),
            'average_residual_energy': sum(energies) / len(energies),
            'average_residual_ratio': sum(energy_ratios) / len(energy_ratios),
            'min_residual_energy': min(energies),
            'max_residual_energy': max(energies),
            'std_residual_energy': self._std(energies),
            'network_lifetime_ratio': sum(energy_ratios) / len(energy_ratios)
        }

    def get_network_traffic_statistics(self) -> dict:
        """
        Calculate network traffic statistics.

        Returns:
            Dictionary with traffic statistics
        """
        active_sensors = [
            self.nodes[nid] for nid in self.get_active_sensors()
        ]

        if not active_sensors:
            return {
                'total_transmitted': 0,
                'total_received': 0,
                'total_forwarded': 0,
                'total_dropped': 0,
                'average_load': 0.0,
                'max_load': 0,
                'load_std': 0.0
            }

        loads = [node.transmitted_packets for node in active_sensors]

        return {
            'total_transmitted': sum(loads),
            'total_received': sum(n.received_packets for n in active_sensors),
            'total_forwarded': sum(n.forwarded_packets for n in active_sensors),
            'total_dropped': sum(n.dropped_packets for n in active_sensors),
            'average_load': sum(loads) / len(loads) if loads else 0,
            'max_load': max(loads) if loads else 0,
            'load_std': self._std(loads)
        }

    def get_topology_statistics(self) -> dict:
        """
        Calculate network topology statistics.

        Returns:
            Dictionary with topology statistics
        """
        active_nodes = self.get_all_active_nodes()
        active_graph = self.network_graph.subgraph(active_nodes)

        # Calculate connectivity
        is_connected = nx.is_connected(active_graph) if len(active_nodes) > 0 else False

        # Calculate average degree
        degrees = [deg for _, deg in active_graph.degree()]
        avg_degree = sum(degrees) / len(degrees) if degrees else 0

        return {
            'total_nodes': len(self.nodes),
            'active_nodes': len(active_nodes),
            'active_sensors': len(self.get_active_sensors()),
            'total_edges': self.network_graph.number_of_edges(),
            'active_edges': active_graph.number_of_edges(),
            'is_connected': is_connected,
            'average_degree': avg_degree,
            'network_density': nx.density(active_graph) if len(active_nodes) > 1 else 0
        }

    def calculate_fairness_index(self) -> float:
        """
        Calculate Jain's Fairness Index for load distribution.

        The fairness index ranges from 0 to 1, where:
        - 1.0 indicates perfect fairness (all nodes have equal load)
        - Lower values indicate unfair load distribution

        Returns:
            Jain's Fairness Index [0, 1]
        """
        active_sensors = [
            self.nodes[nid] for nid in self.get_active_sensors()
        ]

        if not active_sensors:
            return 1.0

        loads = [node.transmitted_packets for node in active_sensors]
        n = len(loads)

        sum_loads = sum(loads)
        sum_loads_squared = sum(load**2 for load in loads)

        if sum_loads_squared == 0:
            return 1.0

        fairness = (sum_loads ** 2) / (n * sum_loads_squared)
        return min(1.0, fairness)

    def get_sink_node(self) -> Optional[SensorNode]:
        """
        Get the sink node.

        Returns:
            Sink node or None if not found
        """
        for node in self.nodes.values():
            if node.is_sink:
                return node
        return None

    def get_node(self, node_id: str) -> Optional[SensorNode]:
        """
        Get node by ID.

        Args:
            node_id: Node identifier

        Returns:
            SensorNode or None if not found
        """
        return self.nodes.get(node_id)

    def reset_network(self):
        """Reset all nodes to initial state."""
        for node in self.nodes.values():
            node.reset()

    def update_all_lifetimes(self, current_round: int):
        """
        Update lifetime statistics for all nodes.

        Args:
            current_round: Current simulation round
        """
        for node in self.nodes.values():
            if not node.is_sink:
                node.update_lifetime(current_round)

    @staticmethod
    def _std(values: List[float]) -> float:
        """
        Calculate standard deviation.

        Args:
            values: List of values

        Returns:
            Standard deviation
        """
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5

    def get_comprehensive_statistics(self) -> dict:
        """
        Get comprehensive network statistics.

        Returns:
            Dictionary with all statistics
        """
        return {
            'energy': self.get_network_energy_statistics(),
            'traffic': self.get_network_traffic_statistics(),
            'topology': self.get_topology_statistics(),
            'fairness_index': self.calculate_fairness_index()
        }

    def __str__(self) -> str:
        stats = self.get_topology_statistics()
        return (f"SDNController: "
                f"{stats['active_sensors']}/{stats['total_nodes']-1} sensors alive, "
                f"{stats['active_edges']} active links, "
                f"Connected: {stats['is_connected']}")

    def __repr__(self) -> str:
        return f"SDNController(nodes={len(self.nodes)}, edges={self.network_graph.number_of_edges()})"
