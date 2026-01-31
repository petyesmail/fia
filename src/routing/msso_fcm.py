"""
MSSO-FCM: Multi-Strategy Snake Optimizer with Fuzzy C-Means Clustering.

Combines metaheuristic optimization with fuzzy clustering for optimal
cluster head selection and inter-cluster routing via MST.

Reference:
Yang, G., et al. (2024). Energy efficient cluster-based routing protocol 
for WSN using multi-strategy fusion snake optimizer and minimum spanning tree.
Scientific Reports, 14, 16786. DOI: 10.1038/s41598-024-66703-9

Expected Performance (100 nodes, 0.5J):
- Energy reduction: 26.64% minimum
- Network lifetime: +25.84%
- Stability period: +52.43%
- Throughput: +40.99%
"""

import numpy as np
from typing import Dict, List, Tuple
from .base import RoutingAlgorithm
from ..utils.optimization import SnakeOptimizer
from ..utils.clustering import FuzzyCMeans, MinimumSpanningTree


class MSSO_FCM(RoutingAlgorithm):
    """
    Multi-Strategy Snake Optimizer + Fuzzy C-Means.
    
    Uses MSSO for CH selection optimization and FCM for cluster formation.
    Inter-cluster routing via MST.
    """
    
    def __init__(self, n_clusters=None, pop_size=30, max_iter=50):
        """
        Initialize MSSO-FCM.
        
        Args:
            n_clusters: Number of clusters (auto if None)
            pop_size: Snake optimizer population size
            max_iter: Maximum optimization iterations
        """
        self.n_clusters = n_clusters
        self.pop_size = pop_size
        self.max_iter = max_iter
        self.cluster_heads = []
        self.clusters = {}
        
    @property
    def algorithm_name(self) -> str:
        return "MSSO-FCM"
    
    def get_description(self) -> str:
        return ("MSSO-FCM: Multi-Strategy Snake Optimizer with Fuzzy C-Means. "
                "Metaheuristic optimization for energy-efficient clustering.")
    
    def _fitness_function(self, solution: np.ndarray, controller) -> float:
        """
        Fitness function for MSSO.
        
        F = w1×E_residual + w2×(1/d_BS) + w3×(1/d_intra) + w4×N_neighbors
        
        Weights: [0.4, 0.2, 0.2, 0.2]
        """
        alive_nodes = [nid for nid, n in controller.network.nodes.items()
                       if nid != 'SINK' and n.is_alive()]
        
        if len(alive_nodes) == 0:
            return float('inf')
        
        # Decode solution to CH indices
        n_ch = int(np.sqrt(len(alive_nodes)))
        ch_indices = np.argsort(solution)[:n_ch]
        ch_nodes = [alive_nodes[i] for i in ch_indices if i < len(alive_nodes)]
        
        if len(ch_nodes) == 0:
            return float('inf')
        
        total_fitness = 0.0
        sink = controller.network.nodes['SINK']
        
        for ch_id in ch_nodes:
            node = controller.network.nodes[ch_id]
            
            # Energy (normalized)
            energy_score = node.energy / node.initial_energy if node.initial_energy > 0 else 0
            
            # Distance to BS (inverted and normalized)
            dist_bs = np.sqrt((node.x - sink.x)**2 + (node.y - sink.y)**2)
            max_dist = np.sqrt(controller.network.config.area_width**2 + 
                               controller.network.config.area_height**2)
            dist_bs_score = 1.0 / (dist_bs + 1e-6) * max_dist
            
            # Average intra-cluster distance (smaller is better)
            intra_dist = 0.0
            count = 0
            for other_id in alive_nodes:
                if other_id != ch_id:
                    other = controller.network.nodes[other_id]
                    d = np.sqrt((node.x - other.x)**2 + (node.y - other.y)**2)
                    intra_dist += d
                    count += 1
            avg_intra = intra_dist / count if count > 0 else 0
            intra_score = 1.0 / (avg_intra + 1e-6) * controller.network.config.communication_range
            
            # Number of neighbors
            neighbors = sum(1 for other_id in alive_nodes 
                            if other_id != ch_id and
                            np.sqrt((node.x - controller.network.nodes[other_id].x)**2 + 
                                    (node.y - controller.network.nodes[other_id].y)**2) 
                            <= controller.network.config.communication_range)
            neighbor_score = neighbors / len(alive_nodes)
            
            # Combined fitness
            fitness = (0.4 * energy_score + 
                       0.2 * dist_bs_score + 
                       0.2 * intra_score + 
                       0.2 * neighbor_score)
            
            total_fitness += fitness
        
        return -total_fitness  # Minimize (MSSO minimizes)
    
    def compute_routing_table(self, controller) -> Dict[str, str]:
        """Compute MSSO-FCM routing table."""
        routing_table = {}
        
        alive_nodes = [nid for nid, n in controller.network.nodes.items()
                       if nid != 'SINK' and n.is_alive()]
        
        if len(alive_nodes) == 0:
            return routing_table
        
        # Determine number of clusters
        if self.n_clusters is None:
            self.n_clusters = max(1, int(np.sqrt(len(alive_nodes))))
        
        # MSSO optimization for CH selection
        optimizer = SnakeOptimizer(
            pop_size=self.pop_size,
            max_iter=min(self.max_iter, 20),  # Limit iterations
            dim=len(alive_nodes),
            lb=0.0,
            ub=1.0
        )
        
        best_solution, _ = optimizer.optimize(
            lambda sol: self._fitness_function(sol, controller)
        )
        
        # Select CHs from solution
        ch_indices = np.argsort(best_solution)[:self.n_clusters]
        self.cluster_heads = [alive_nodes[i] for i in ch_indices if i < len(alive_nodes)]
        
        if len(self.cluster_heads) == 0:
            return routing_table
        
        # FCM for cluster formation
        node_positions = np.array([[controller.network.nodes[nid].x,
                                     controller.network.nodes[nid].y]
                                    for nid in alive_nodes])
        
        ch_positions = np.array([[controller.network.nodes[ch].x,
                                   controller.network.nodes[ch].y]
                                  for ch in self.cluster_heads])
        
        fcm = FuzzyCMeans(n_clusters=len(self.cluster_heads), m=2.0)
        _, membership = fcm.fit(node_positions, initial_centers=ch_positions)
        
        # Assign nodes to clusters
        self.clusters = {ch: [] for ch in self.cluster_heads}
        for idx, node_id in enumerate(alive_nodes):
            cluster_idx = np.argmax(membership[idx])
            if cluster_idx < len(self.cluster_heads):
                self.clusters[self.cluster_heads[cluster_idx]].append(node_id)
        
        # Build MST for inter-cluster routing
        mst = MinimumSpanningTree()
        ch_pos_dict = {ch: (controller.network.nodes[ch].x, 
                            controller.network.nodes[ch].y)
                       for ch in self.cluster_heads}
        ch_pos_dict['SINK'] = (controller.network.nodes['SINK'].x,
                                controller.network.nodes['SINK'].y)
        
        mst_edges = mst.build_from_positions(ch_pos_dict)
        
        # Build routing table
        # Members → CH
        for ch, members in self.clusters.items():
            for member in members:
                if member != ch:
                    routing_table[member] = ch
        
        # CH → next hop via MST
        for ch in self.cluster_heads:
            # Find path to SINK in MST
            for edge in mst_edges:
                if ch in edge[:2]:
                    other = edge[1] if edge[0] == ch else edge[0]
                    if other == 'SINK' or other in self.cluster_heads:
                        routing_table[ch] = other
                        break
        
        return routing_table
