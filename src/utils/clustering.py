"""
Clustering algorithms and utilities.

This module provides:
- Fuzzy C-Means (FCM) clustering
- Minimum Spanning Tree (MST) construction
- TDMA scheduling
- Cluster head selection utilities
"""

import numpy as np
from typing import List, Tuple, Dict
import heapq


class FuzzyCMeans:
    """
    Fuzzy C-Means clustering algorithm.
    Used in MSSO-FCM for cluster formation.
    """

    def __init__(self, n_clusters: int, m: float = 2.0, max_iter: int = 100,
                 epsilon: float = 0.001):
        """
        Initialize FCM.

        Args:
            n_clusters: Number of clusters
            m: Fuzziness coefficient (typically 2.0)
            max_iter: Maximum iterations
            epsilon: Convergence threshold
        """
        self.n_clusters = n_clusters
        self.m = m
        self.max_iter = max_iter
        self.epsilon = epsilon
        self.centers = None
        self.membership = None

    def _calculate_membership(self, data: np.ndarray, centers: np.ndarray) -> np.ndarray:
        """
        Calculate fuzzy membership matrix.

        Formula: u_ij = 1 / Σ[(d_ij/d_ik)^(2/(m-1))]

        Args:
            data: Data points (n_samples, n_features)
            centers: Cluster centers (n_clusters, n_features)

        Returns:
            Membership matrix (n_samples, n_clusters)
        """
        n_samples = data.shape[0]
        membership = np.zeros((n_samples, self.n_clusters))

        for i in range(n_samples):
            for j in range(self.n_clusters):
                distances = []
                for k in range(self.n_clusters):
                    d_ij = np.linalg.norm(data[i] - centers[j])
                    d_ik = np.linalg.norm(data[i] - centers[k])

                    if d_ik < 1e-10:
                        d_ik = 1e-10

                    distances.append((d_ij / d_ik) ** (2.0 / (self.m - 1)))

                membership[i, j] = 1.0 / sum(distances)

        return membership

    def _update_centers(self, data: np.ndarray, membership: np.ndarray) -> np.ndarray:
        """
        Update cluster centers.

        Args:
            data: Data points
            membership: Membership matrix

        Returns:
            Updated centers
        """
        centers = np.zeros((self.n_clusters, data.shape[1]))

        for j in range(self.n_clusters):
            numerator = np.sum((membership[:, j] ** self.m)[:, np.newaxis] * data, axis=0)
            denominator = np.sum(membership[:, j] ** self.m)

            if denominator > 0:
                centers[j] = numerator / denominator
            else:
                centers[j] = data[np.random.randint(0, data.shape[0])]

        return centers

    def fit(self, data: np.ndarray, initial_centers: np.ndarray = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fit FCM to data.

        Args:
            data: Data points (n_samples, n_features)
            initial_centers: Initial cluster centers (optional)

        Returns:
            Tuple of (centers, membership_matrix)
        """
        n_samples = data.shape[0]

        # Initialize centers
        if initial_centers is not None:
            self.centers = initial_centers
        else:
            indices = np.random.choice(n_samples, self.n_clusters, replace=False)
            self.centers = data[indices].copy()

        # Initialize membership
        self.membership = self._calculate_membership(data, self.centers)

        # Iterate until convergence
        for iteration in range(self.max_iter):
            old_centers = self.centers.copy()

            # Update membership
            self.membership = self._calculate_membership(data, self.centers)

            # Update centers
            self.centers = self._update_centers(data, self.membership)

            # Check convergence
            center_shift = np.linalg.norm(self.centers - old_centers)
            if center_shift < self.epsilon:
                break

        return self.centers, self.membership

    def predict(self, data: np.ndarray) -> np.ndarray:
        """
        Predict cluster assignments.

        Args:
            data: Data points

        Returns:
            Cluster labels (hard assignment)
        """
        membership = self._calculate_membership(data, self.centers)
        return np.argmax(membership, axis=1)


class MinimumSpanningTree:
    """
    Minimum Spanning Tree construction using Kruskal's algorithm.
    Used for inter-cluster routing in MSSO-FCM.
    """

    def __init__(self):
        """Initialize MST constructor."""
        self.parent = {}
        self.rank = {}

    def make_set(self, node):
        """Create a set for a node."""
        self.parent[node] = node
        self.rank[node] = 0

    def find(self, node):
        """Find set representative with path compression."""
        if self.parent[node] != node:
            self.parent[node] = self.find(self.parent[node])
        return self.parent[node]

    def union(self, node1, node2):
        """Union two sets by rank."""
        root1 = self.find(node1)
        root2 = self.find(node2)

        if root1 == root2:
            return False

        if self.rank[root1] < self.rank[root2]:
            self.parent[root1] = root2
        elif self.rank[root1] > self.rank[root2]:
            self.parent[root2] = root1
        else:
            self.parent[root2] = root1
            self.rank[root1] += 1

        return True

    def kruskal(self, nodes: List, edges: List[Tuple[int, int, float]]) -> List[Tuple[int, int, float]]:
        """
        Construct MST using Kruskal's algorithm.

        Args:
            nodes: List of node IDs
            edges: List of (node1, node2, weight) tuples

        Returns:
            List of MST edges
        """
        # Initialize sets
        for node in nodes:
            self.make_set(node)

        # Sort edges by weight
        sorted_edges = sorted(edges, key=lambda x: x[2])

        mst_edges = []

        for edge in sorted_edges:
            node1, node2, weight = edge

            # Try to add edge
            if self.union(node1, node2):
                mst_edges.append(edge)

                # MST complete when we have n-1 edges
                if len(mst_edges) == len(nodes) - 1:
                    break

        return mst_edges

    def build_from_positions(self, positions: Dict[int, Tuple[float, float]]) -> List[Tuple[int, int, float]]:
        """
        Build MST from node positions.

        Args:
            positions: Dictionary mapping node_id to (x, y) position

        Returns:
            List of MST edges
        """
        nodes = list(positions.keys())
        edges = []

        # Create complete graph
        for i, node1 in enumerate(nodes):
            for node2 in nodes[i + 1:]:
                x1, y1 = positions[node1]
                x2, y2 = positions[node2]
                distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                edges.append((node1, node2, distance))

        return self.kruskal(nodes, edges)


class TDMAScheduler:
    """
    TDMA (Time Division Multiple Access) scheduler for cluster communication.
    Used in NN_ILEACH for intra-cluster scheduling.
    """

    def __init__(self, slot_duration: float = 0.01):
        """
        Initialize TDMA scheduler.

        Args:
            slot_duration: Duration of each time slot in seconds
        """
        self.slot_duration = slot_duration
        self.schedules = {}

    def create_schedule(self, cluster_id: int, member_nodes: List[int]) -> Dict[int, int]:
        """
        Create TDMA schedule for a cluster.

        Args:
            cluster_id: Cluster identifier
            member_nodes: List of node IDs in the cluster

        Returns:
            Dictionary mapping node_id to time_slot
        """
        schedule = {}

        for slot, node_id in enumerate(member_nodes):
            schedule[node_id] = slot

        self.schedules[cluster_id] = schedule

        return schedule

    def get_slot(self, cluster_id: int, node_id: int) -> int:
        """
        Get time slot for a node.

        Args:
            cluster_id: Cluster identifier
            node_id: Node identifier

        Returns:
            Time slot number
        """
        if cluster_id in self.schedules:
            return self.schedules[cluster_id].get(node_id, -1)
        return -1

    def get_transmission_time(self, cluster_id: int, node_id: int) -> float:
        """
        Get transmission start time for a node.

        Args:
            cluster_id: Cluster identifier
            node_id: Node identifier

        Returns:
            Transmission start time in seconds
        """
        slot = self.get_slot(cluster_id, node_id)
        if slot >= 0:
            return slot * self.slot_duration
        return -1.0


class ClusterHeadSelector:
    """
    Utilities for cluster head selection.
    """

    @staticmethod
    def leach_threshold(round_num: int, node_id: int, times_ch: int,
                        optimal_ch_prob: float, total_nodes: int) -> bool:
        """
        LEACH probabilistic cluster head selection.

        Args:
            round_num: Current round number
            node_id: Node identifier
            times_ch: Number of times node has been CH
            optimal_ch_prob: Optimal CH probability (typically sqrt(N)/N)
            total_nodes: Total number of nodes

        Returns:
            True if node should become CH
        """
        if times_ch >= total_nodes:
            return False

        # Reset period
        period = int(1.0 / optimal_ch_prob)
        r = round_num % period

        # Threshold calculation
        if r < total_nodes:
            threshold = optimal_ch_prob / (1 - optimal_ch_prob * (r % period))
        else:
            threshold = 0.0

        random_value = np.random.random()

        return random_value < threshold

    @staticmethod
    def select_by_energy(nodes_energy: Dict[int, float], n_clusters: int) -> List[int]:
        """
        Select cluster heads based on highest energy.

        Args:
            nodes_energy: Dictionary mapping node_id to residual_energy
            n_clusters: Number of cluster heads to select

        Returns:
            List of selected CH node IDs
        """
        sorted_nodes = sorted(nodes_energy.items(), key=lambda x: x[1], reverse=True)
        return [node_id for node_id, _ in sorted_nodes[:n_clusters]]

    @staticmethod
    def assign_to_nearest_ch(node_positions: Dict[int, Tuple[float, float]],
                              ch_positions: Dict[int, Tuple[float, float]]) -> Dict[int, int]:
        """
        Assign nodes to nearest cluster head.

        Args:
            node_positions: Dictionary mapping node_id to (x, y)
            ch_positions: Dictionary mapping ch_id to (x, y)

        Returns:
            Dictionary mapping node_id to ch_id
        """
        assignments = {}

        for node_id, (x, y) in node_positions.items():
            if node_id in ch_positions:
                # Node is itself a CH
                assignments[node_id] = node_id
                continue

            min_distance = float('inf')
            nearest_ch = None

            for ch_id, (ch_x, ch_y) in ch_positions.items():
                distance = np.sqrt((x - ch_x) ** 2 + (y - ch_y) ** 2)

                if distance < min_distance:
                    min_distance = distance
                    nearest_ch = ch_id

            if nearest_ch is not None:
                assignments[node_id] = nearest_ch

        return assignments
