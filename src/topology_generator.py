import numpy as np
import random
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class Position:
    x: float
    y: float

    def distance_to(self, other: 'Position') -> float:
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


class TopologyGenerator:

    @staticmethod
    def generate_random_topology(
        num_nodes: int,
        area_size: float,
        seed: int = None
    ) -> List[Position]:
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        positions = []
        for _ in range(num_nodes):
            x = random.uniform(0, area_size)
            y = random.uniform(0, area_size)
            positions.append(Position(x, y))

        return positions

    @staticmethod
    def generate_grid_topology(
        num_nodes: int,
        area_size: float,
        jitter: float = 0.1
    ) -> List[Position]:
        grid_size = int(np.ceil(np.sqrt(num_nodes)))

        cell_size = area_size / grid_size

        positions = []
        for i in range(grid_size):
            for j in range(grid_size):
                if len(positions) >= num_nodes:
                    break

                base_x = (i + 0.5) * cell_size
                base_y = (j + 0.5) * cell_size

                jitter_x = random.uniform(-jitter, jitter) * cell_size
                jitter_y = random.uniform(-jitter, jitter) * cell_size

                x = max(0, min(area_size, base_x + jitter_x))
                y = max(0, min(area_size, base_y + jitter_y))

                positions.append(Position(x, y))

            if len(positions) >= num_nodes:
                break

        return positions[:num_nodes]

    @staticmethod
    def generate_cluster_topology(
        num_nodes: int,
        area_size: float,
        num_clusters: int = 4,
        cluster_std: float = None
    ) -> List[Position]:
        if cluster_std is None:
            cluster_std = area_size / (num_clusters * 3)

        cluster_centers = []
        grid_size = int(np.ceil(np.sqrt(num_clusters)))
        cell_size = area_size / grid_size

        for i in range(grid_size):
            for j in range(grid_size):
                if len(cluster_centers) >= num_clusters:
                    break
                center_x = (i + 0.5) * cell_size
                center_y = (j + 0.5) * cell_size
                cluster_centers.append((center_x, center_y))

        cluster_centers = cluster_centers[:num_clusters]

        nodes_per_cluster = num_nodes // num_clusters
        remaining_nodes = num_nodes % num_clusters

        positions = []

        for cluster_idx, (center_x, center_y) in enumerate(cluster_centers):
            nodes_in_this_cluster = nodes_per_cluster
            if cluster_idx < remaining_nodes:
                nodes_in_this_cluster += 1

            for _ in range(nodes_in_this_cluster):
                while True:
                    x = np.random.normal(center_x, cluster_std)
                    y = np.random.normal(center_y, cluster_std)

                    if 0 <= x <= area_size and 0 <= y <= area_size:
                        positions.append(Position(x, y))
                        break

        return positions

    @staticmethod
    def generate_concentric_topology(
        num_nodes: int,
        area_size: float,
        num_rings: int = 3
    ) -> List[Position]:
        center_x = area_size / 2
        center_y = area_size / 2

        max_radius = area_size / 2 * 0.9

        nodes_per_ring = num_nodes // num_rings
        remaining_nodes = num_nodes % num_rings

        positions = []

        for ring_idx in range(num_rings):
            radius = (ring_idx + 1) * max_radius / num_rings

            nodes_in_ring = nodes_per_ring
            if ring_idx < remaining_nodes:
                nodes_in_ring += 1

            angle_step = 2 * np.pi / nodes_in_ring

            for node_idx in range(nodes_in_ring):
                angle = node_idx * angle_step

                angle_jitter = random.uniform(-0.1, 0.1) * angle_step
                radius_jitter = random.uniform(-0.1, 0.1) * (max_radius / num_rings)

                actual_angle = angle + angle_jitter
                actual_radius = radius + radius_jitter

                x = center_x + actual_radius * np.cos(actual_angle)
                y = center_y + actual_radius * np.sin(actual_angle)

                x = max(0, min(area_size, x))
                y = max(0, min(area_size, y))

                positions.append(Position(x, y))

        return positions[:num_nodes]

    @staticmethod
    def generate_hotspot_topology(
        num_nodes: int,
        area_size: float,
        hotspot_ratio: float = 0.3
    ) -> List[Position]:
        num_hotspot_nodes = int(num_nodes * hotspot_ratio)
        num_regular_nodes = num_nodes - num_hotspot_nodes

        hotspot_center = Position(area_size / 2, area_size / 2)
        hotspot_radius = area_size / 4

        hotspot_positions = []
        for _ in range(num_hotspot_nodes):
            while True:
                angle = random.uniform(0, 2 * np.pi)
                radius = random.uniform(0, hotspot_radius)

                x = hotspot_center.x + radius * np.cos(angle)
                y = hotspot_center.y + radius * np.sin(angle)

                if 0 <= x <= area_size and 0 <= y <= area_size:
                    hotspot_positions.append(Position(x, y))
                    break

        regular_positions = []
        for _ in range(num_regular_nodes):
            while True:
                x = random.uniform(0, area_size)
                y = random.uniform(0, area_size)

                pos = Position(x, y)
                if pos.distance_to(hotspot_center) > hotspot_radius:
                    regular_positions.append(pos)
                    break

        return hotspot_positions + regular_positions

    @staticmethod
    def optimize_sink_placement(
        node_positions: List[Position],
        area_size: float,
        method: str = 'centroid'
    ) -> Position:
        if method == 'centroid':
            avg_x = np.mean([pos.x for pos in node_positions])
            avg_y = np.mean([pos.y for pos in node_positions])
            return Position(avg_x, avg_y)

        elif method == 'center':
            return Position(area_size / 2, area_size / 2)

        elif method == 'min_max_distance':
            best_pos = Position(area_size / 2, area_size / 2)
            min_max_distance = float('inf')

            test_positions = [
                Position(area_size / 2, area_size / 2),
                Position(area_size / 4, area_size / 2),
                Position(3 * area_size / 4, area_size / 2),
                Position(area_size / 2, area_size / 4),
                Position(area_size / 2, 3 * area_size / 4),
            ]

            for test_pos in test_positions:
                max_distance = max(test_pos.distance_to(pos) for pos in node_positions)

                if max_distance < min_max_distance:
                    min_max_distance = max_distance
                    best_pos = test_pos

            return best_pos

        else:
            return Position(area_size / 2, area_size / 2)
