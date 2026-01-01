"""
Base class for routing algorithms.

This module defines the abstract interface that all routing algorithms must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.network import SDNController


class RoutingAlgorithm(ABC):
    """
    Abstract base class for routing algorithms.

    All routing algorithms must implement:
    - algorithm_name: Property returning the algorithm's name
    - compute_routing_table: Method that computes next-hop routing decisions

    The routing algorithm receives the complete network state through the
    SDN controller and returns a routing table mapping source nodes to
    their next-hop destinations.
    """

    @property
    @abstractmethod
    def algorithm_name(self) -> str:
        """
        Get the name of the routing algorithm.

        Returns:
            String identifier for the algorithm
        """
        pass

    @abstractmethod
    def compute_routing_table(self, controller: 'SDNController') -> Dict[str, str]:
        """
        Compute routing table for the current network state.

        Args:
            controller: SDN controller with complete network state

        Returns:
            Dictionary mapping source node IDs to next-hop node IDs
            Format: {source_id: next_hop_id}

        Example:
            {'N1': 'N5', 'N2': 'N3', 'N3': 'SINK'}
        """
        pass

    def get_description(self) -> str:
        """
        Get a human-readable description of the algorithm.

        Returns:
            Algorithm description
        """
        return f"{self.algorithm_name} Routing Algorithm"

    def __str__(self) -> str:
        return self.algorithm_name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
