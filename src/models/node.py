"""
Sensor node models for WSN simulation.

This module defines the Position class for 2D coordinates and the SensorNode
class representing wireless sensor nodes with energy management.
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..config import SimulationConfig


@dataclass
class Position:
    """
    2D position in the network deployment area.

    Attributes:
        x: X-coordinate
        y: Y-coordinate
    """
    x: float
    y: float

    def distance_to(self, other: 'Position') -> float:
        """
        Calculate Euclidean distance to another position.

        Args:
            other: Target position

        Returns:
            Euclidean distance in meters
        """
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def __str__(self) -> str:
        return f"({self.x:.2f}, {self.y:.2f})"

    def to_tuple(self) -> tuple:
        """Convert to tuple representation."""
        return (self.x, self.y)


class SensorNode:
    """
    Wireless sensor node with comprehensive energy management.

    This class models a wireless sensor node including:
    - Energy consumption for transmission and reception
    - Packet statistics
    - Neighbor discovery and routing
    - Node lifecycle management

    Attributes:
        id: Unique node identifier
        position: 2D position in the network
        initial_energy: Initial energy capacity (J)
        current_energy: Current remaining energy (J)
        is_sink: Whether this node is the sink node
        is_alive: Whether the node has remaining energy
        neighbors: List of neighbor node IDs
        next_hop: Next hop node ID for routing
        transmitted_packets: Count of transmitted packets
        received_packets: Count of received packets
        total_energy_consumed: Total energy consumed (J)
        config: Simulation configuration
    """

    def __init__(
        self,
        node_id: str,
        position: Position,
        energy: float,
        is_sink: bool,
        config: 'SimulationConfig'
    ):
        """
        Initialize a sensor node.

        Args:
            node_id: Unique identifier for the node
            position: 2D position in the network
            energy: Initial energy in Joules
            is_sink: Whether this is the sink node
            config: Simulation configuration
        """
        self.id = node_id
        self.position = position
        self.initial_energy = energy
        self.current_energy = energy
        self.is_sink = is_sink
        self.config = config

        # State
        self.is_alive = True
        self.neighbors: List[str] = []
        self.next_hop: Optional[str] = None

        # Statistics
        self.transmitted_packets = 0
        self.received_packets = 0
        self.total_energy_consumed = 0.0
        self.forwarded_packets = 0  # Added for load balancing metrics
        self.dropped_packets = 0  # Added for reliability metrics

        # Temporal metrics
        self.lifetime_rounds = 0
        self.death_round = None

    def get_residual_energy_ratio(self) -> float:
        """
        Get residual energy as a ratio of initial energy.

        Returns:
            Ratio of current energy to initial energy [0, 1]
        """
        if self.initial_energy <= 0:
            return 0.0
        return max(0.0, min(1.0, self.current_energy / self.initial_energy))

    def get_residual_energy(self) -> float:
        """
        Get absolute residual energy.

        Returns:
            Current remaining energy in Joules
        """
        return max(0.0, self.current_energy)

    def calculate_transmission_cost(self, distance: float) -> float:
        """
        Calculate energy cost for transmitting a packet.

        Uses First Order Radio Energy Model:
        - Short distance (d < d0): E = E_elec * k + E_fs * k * d²
        - Long distance (d ≥ d0): E = E_elec * k + E_mp * k * d⁴

        Args:
            distance: Transmission distance in meters

        Returns:
            Energy consumption in Joules
        """
        return self.config.get_transmission_energy(distance)

    def calculate_reception_cost(self) -> float:
        """
        Calculate energy cost for receiving a packet.

        Returns:
            Energy consumption in Joules
        """
        return self.config.get_reception_energy()

    def consume_energy(self, amount: float) -> bool:
        """
        Consume energy and update node state.

        Args:
            amount: Amount of energy to consume in Joules

        Returns:
            True if energy was successfully consumed, False if node died
        """
        if not self.is_alive:
            return False

        if amount > self.current_energy:
            self.current_energy = 0.0
            self.is_alive = False
            return False

        self.current_energy -= amount
        self.total_energy_consumed += amount

        # Check if energy is critically low
        if self.current_energy < 1e-6:  # Numerical threshold
            self.is_alive = False
            return False

        return True

    def transmit_packet(self, distance: float) -> bool:
        """
        Transmit a packet to a neighbor.

        Args:
            distance: Distance to the receiver in meters

        Returns:
            True if transmission successful, False otherwise
        """
        if not self.is_alive or self.is_sink:
            return False

        cost = self.calculate_transmission_cost(distance)

        if self.consume_energy(cost):
            self.transmitted_packets += 1
            return True

        return False

    def receive_packet(self) -> bool:
        """
        Receive a packet from a neighbor.

        Returns:
            True if reception successful, False otherwise
        """
        if not self.is_alive:
            return False

        cost = self.calculate_reception_cost()

        if self.consume_energy(cost):
            self.received_packets += 1
            return True

        return False

    def forward_packet(self) -> bool:
        """
        Forward a received packet (combines reception + transmission statistics).

        Returns:
            True if forwarding successful, False otherwise
        """
        if not self.is_alive:
            return False

        self.forwarded_packets += 1
        return True

    def drop_packet(self):
        """Record a dropped packet."""
        self.dropped_packets += 1

    def get_load_factor(self) -> float:
        """
        Calculate node load factor based on transmitted packets.

        Returns:
            Normalized load factor
        """
        # Normalize by a reasonable maximum (configurable)
        max_expected_load = 1000
        return min(1.0, self.transmitted_packets / max_expected_load)

    def get_forwarding_load(self) -> float:
        """
        Calculate forwarding load (packets forwarded through this node).

        Returns:
            Forwarding load metric
        """
        max_expected_forwarding = 500
        return min(1.0, self.forwarded_packets / max_expected_forwarding)

    def reset(self):
        """Reset node to initial state."""
        self.current_energy = self.initial_energy
        self.is_alive = True
        self.transmitted_packets = 0
        self.received_packets = 0
        self.forwarded_packets = 0
        self.dropped_packets = 0
        self.total_energy_consumed = 0.0
        self.next_hop = None
        self.lifetime_rounds = 0
        self.death_round = None

    def update_lifetime(self, current_round: int):
        """
        Update lifetime statistics.

        Args:
            current_round: Current simulation round
        """
        if self.is_alive:
            self.lifetime_rounds = current_round
        elif self.death_round is None:
            self.death_round = current_round

    def get_statistics(self) -> dict:
        """
        Get comprehensive node statistics.

        Returns:
            Dictionary of node statistics
        """
        return {
            'id': self.id,
            'position': self.position.to_tuple(),
            'is_alive': self.is_alive,
            'is_sink': self.is_sink,
            'initial_energy': self.initial_energy,
            'current_energy': self.current_energy,
            'residual_energy_ratio': self.get_residual_energy_ratio(),
            'total_energy_consumed': self.total_energy_consumed,
            'transmitted_packets': self.transmitted_packets,
            'received_packets': self.received_packets,
            'forwarded_packets': self.forwarded_packets,
            'dropped_packets': self.dropped_packets,
            'neighbors_count': len(self.neighbors),
            'lifetime_rounds': self.lifetime_rounds,
            'death_round': self.death_round
        }

    def __str__(self) -> str:
        status = "ALIVE" if self.is_alive else "DEAD"
        energy_pct = self.get_residual_energy_ratio() * 100
        return (f"Node {self.id} [{status}]: "
                f"Energy={energy_pct:.1f}%, "
                f"TX={self.transmitted_packets}, "
                f"RX={self.received_packets}")

    def __repr__(self) -> str:
        return f"SensorNode(id={self.id}, alive={self.is_alive}, energy={self.current_energy:.6f})"
