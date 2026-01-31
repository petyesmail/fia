"""
OSPF: Open Shortest Path First (Adapted for WSN-SDN).

Link-state routing protocol using Dijkstra's algorithm.
Used as baseline for SDN comparison.

Characteristics:
- Fast convergence
- High PDR
- No energy consideration
- Can create hotspots
"""

import numpy as np
import networkx as nx
from typing import Dict
from ..base import RoutingAlgorithm


class OSPF(RoutingAlgorithm):
    """
    OSPF-like routing for WSN-SDN.

    Uses shortest path based on hop count.
    Does not consider energy levels.
    """

    @property
    def algorithm_name(self) -> str:
        return "OSPF"

    def get_description(self) -> str:
        return ("OSPF: Open Shortest Path First. "
                "Link-state routing with shortest path calculation.")

    def compute_routing_table(self, controller) -> Dict[str, str]:
        """
        Compute routing table using Dijkstra's shortest path.

        Args:
            controller: SDN controller

        Returns:
            Routing table
        """
        routing_table = {}

        # Build graph
        G = nx.Graph()

        # Add nodes
        for node_id, node in controller.network.nodes.items():
            if node.is_alive() or node_id == 'SINK':
                G.add_node(node_id)

        # Add edges (within communication range)
        comm_range = controller.network.config.communication_range

        for node1_id, node1 in controller.network.nodes.items():
            if not node1.is_alive() and node1_id != 'SINK':
                continue

            for node2_id, node2 in controller.network.nodes.items():
                if node1_id >= node2_id:  # Avoid duplicates
                    continue

                if not node2.is_alive() and node2_id != 'SINK':
                    continue

                # Calculate distance
                dist = np.sqrt((node1.x - node2.x) ** 2 +
                               (node1.y - node2.y) ** 2)

                if dist <= comm_range:
                    G.add_edge(node1_id, node2_id, weight=1.0)  # Hop count

        # Compute shortest paths to SINK
        if 'SINK' in G:
            try:
                paths = nx.single_source_shortest_path(G, 'SINK')

                for target, path in paths.items():
                    if target == 'SINK' or len(path) < 2:
                        continue

                    # Next hop is second-to-last in path (from SINK perspective)
                    # Reverse to get path from target to SINK
                    next_hop = path[-2]
                    routing_table[target] = next_hop

            except nx.NetworkXError:
                pass  # No path exists

        return routing_table
