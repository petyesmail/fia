"""
PEGASIS: Power-Efficient Gathering in Sensor Information Systems.

Chain-based routing protocol where nodes form a chain and take turns
being the leader that transmits to the sink.

Reference:
Lindsey, S., & Raghavendra, C. S. (2002).
PEGASIS: Power-efficient gathering in sensor information systems.
In IEEE Aerospace Conference.

Expected Performance:
- FND: ~1.5× LEACH
- Energy efficiency: +30% vs LEACH
"""

import numpy as np
from typing import Dict, List
from ..base import RoutingAlgorithm


class PEGASIS(RoutingAlgorithm):
    """
    PEGASIS routing algorithm.

    Forms a chain of nodes using greedy algorithm.
    Nodes take turns as leader to transmit to sink.
    """

    def __init__(self):
        """Initialize PEGASIS."""
        self.chain = []
        self.leader_index = 0
        self.chain_formed = False

    @property
    def algorithm_name(self) -> str:
        return "PEGASIS"

    def get_description(self) -> str:
        return ("PEGASIS: Power-Efficient Gathering in Sensor Information Systems. "
                "Chain-based routing with rotating leadership.")

    def _form_chain(self, controller) -> List[str]:
        """
        Form chain using greedy nearest-neighbor algorithm.

        Args:
            controller: SDN controller

        Returns:
            List of node IDs in chain order
        """
        alive_nodes = [nid for nid, n in controller.nodes.items()
                       if nid != 'SINK' and n.is_alive]

        if len(alive_nodes) == 0:
            return []

        chain = []
        remaining = set(alive_nodes)

        # Start from node farthest from sink
        sink_x = controller.nodes['SINK'].x
        sink_y = controller.nodes['SINK'].y

        max_dist = 0
        start_node = None

        for node_id in remaining:
            node = controller.nodes[node_id]
            dist = np.sqrt((node.x - sink_x) ** 2 + (node.y - sink_y) ** 2)
            if dist > max_dist:
                max_dist = dist
                start_node = node_id

        # Build chain greedily
        current = start_node
        chain.append(current)
        remaining.remove(current)

        while remaining:
            # Find nearest unvisited node
            min_dist = float('inf')
            nearest = None
            current_node = controller.nodes[current]

            for node_id in remaining:
                node = controller.nodes[node_id]
                dist = np.sqrt((current_node.x - node.x) ** 2 +
                               (current_node.y - node.y) ** 2)
                if dist < min_dist:
                    min_dist = dist
                    nearest = node_id

            if nearest:
                chain.append(nearest)
                remaining.remove(nearest)
                current = nearest
            else:
                break

        return chain

    def compute_routing_table(self, controller) -> Dict[str, str]:
        """
        Compute PEGASIS routing table.

        Data flows along the chain to the leader,
        then leader transmits to sink.

        Args:
            controller: SDN controller

        Returns:
            Routing table
        """
        # Form chain once or reform if needed
        if not self.chain_formed or len(self.chain) == 0:
            self.chain = self._form_chain(controller)
            self.chain_formed = True

        # Remove dead nodes from chain
        self.chain = [nid for nid in self.chain
                      if controller.nodes[nid].is_alive]

        if len(self.chain) == 0:
            return {}

        # Select leader (rotate)
        self.leader_index = self.leader_index % len(self.chain)
        leader = self.chain[self.leader_index]

        routing_table = {}

        # Leader routes to SINK
        routing_table[leader] = 'SINK'

        # Nodes before leader route forward
        for i in range(self.leader_index):
            routing_table[self.chain[i]] = self.chain[i + 1]

        # Nodes after leader route backward
        for i in range(self.leader_index + 1, len(self.chain)):
            if i > 0:
                routing_table[self.chain[i]] = self.chain[i - 1]

        # Rotate leader for next round
        self.leader_index = (self.leader_index + 1) % len(self.chain) if self.chain else 0

        return routing_table
