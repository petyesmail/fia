"""
LEACH: Low-Energy Adaptive Clustering Hierarchy.

This is the classic baseline clustering algorithm for WSNs.

Reference:
Heinzelman, W. R., Chandrakasan, A., & Balakrishnan, H. (2000).
Energy-efficient communication protocol for wireless microsensor networks.
In IEEE HICSS.

Expected Performance (100 nodes, 0.5J initial energy):
- FND: ~500-700 rounds
- PDR: 95-98%
- Energy: baseline reference
"""

import numpy as np
from typing import Dict, List, Tuple
from ..base import RoutingAlgorithm


class LEACH(RoutingAlgorithm):
    """
    LEACH routing algorithm implementation.

    Characteristics:
    - Random probabilistic cluster head (CH) selection
    - Clusters reform every round
    - TDMA scheduling within clusters
    - Direct CH-to-sink transmission
    """

    def __init__(self, optimal_ch_percentage: float = 0.05):
        """
        Initialize LEACH.

        Args:
            optimal_ch_percentage: Optimal percentage of cluster heads (typically 5%)
        """
        self.optimal_ch_percentage = optimal_ch_percentage
        self.cluster_heads = []
        self.clusters = {}
        self.round_num = 0
        self.ch_history = {}  # Track how many times each node was CH

    @property
    def algorithm_name(self) -> str:
        return "LEACH"

    def get_description(self) -> str:
        return ("LEACH: Low-Energy Adaptive Clustering Hierarchy. "
                "Classic probabilistic clustering algorithm for WSNs.")

    def _select_cluster_heads(self, controller) -> List[str]:
        """
        Select cluster heads using LEACH threshold.

        Threshold T(n) = p / (1 - p * (r mod (1/p)))
        where p = optimal CH percentage, r = round number

        Args:
            controller: SDN controller

        Returns:
            List of CH node IDs
        """
        cluster_heads = []
        p = self.optimal_ch_percentage
        period = int(1.0 / p) if p > 0 else 100
        r_mod = self.round_num % period

        for node_id, node in controller.network.nodes.items():
            if node_id == 'SINK':
                continue

            if not node.is_alive():
                continue

            # Check if node has been CH in this period
            times_ch = self.ch_history.get(node_id, 0)

            # Reset CH history at start of new period
            if r_mod == 0:
                self.ch_history[node_id] = 0
                times_ch = 0

            # Skip if already served as CH in this period
            if times_ch > 0 and r_mod > 0:
                continue

            # Calculate threshold
            if r_mod < period:
                threshold = p / (1 - p * r_mod)
            else:
                threshold = 0.0

            # Random selection
            if np.random.random() < threshold:
                cluster_heads.append(node_id)
                self.ch_history[node_id] = self.ch_history.get(node_id, 0) + 1

        # Ensure at least one CH if nodes are alive
        if len(cluster_heads) == 0:
            alive_nodes = [nid for nid, n in controller.network.nodes.items()
                           if nid != 'SINK' and n.is_alive()]
            if alive_nodes:
                # Select node with highest energy
                best_node = max(alive_nodes,
                                key=lambda nid: controller.network.nodes[nid].energy)
                cluster_heads.append(best_node)

        return cluster_heads

    def _form_clusters(self, controller, cluster_heads: List[str]) -> Dict[str, List[str]]:
        """
        Assign nodes to nearest cluster head.

        Args:
            controller: SDN controller
            cluster_heads: List of CH node IDs

        Returns:
            Dictionary mapping CH to list of member nodes
        """
        clusters = {ch: [ch] for ch in cluster_heads}

        for node_id, node in controller.network.nodes.items():
            if node_id == 'SINK' or not node.is_alive():
                continue

            if node_id in cluster_heads:
                continue  # CH already in its own cluster

            # Find nearest CH
            min_distance = float('inf')
            nearest_ch = None

            for ch_id in cluster_heads:
                ch_node = controller.network.nodes[ch_id]
                distance = np.sqrt((node.x - ch_node.x) ** 2 +
                                   (node.y - ch_node.y) ** 2)

                if distance < min_distance:
                    min_distance = distance
                    nearest_ch = ch_id

            if nearest_ch:
                clusters[nearest_ch].append(node_id)

        return clusters

    def compute_routing_table(self, controller) -> Dict[str, str]:
        """
        Compute LEACH routing table.

        Setup phase:
        1. Select cluster heads
        2. Form clusters (nodes join nearest CH)

        Steady-state phase:
        3. Member nodes → CH
        4. CH → SINK

        Args:
            controller: SDN controller

        Returns:
            Routing table
        """
        routing_table = {}

        # Setup phase
        self.cluster_heads = self._select_cluster_heads(controller)
        self.clusters = self._form_clusters(controller, self.cluster_heads)

        # Build routing table
        for ch_id, members in self.clusters.items():
            # CH routes directly to SINK
            routing_table[ch_id] = 'SINK'

            # Members route to their CH
            for member_id in members:
                if member_id != ch_id:
                    routing_table[member_id] = ch_id

        # Increment round
        self.round_num += 1

        return routing_table
