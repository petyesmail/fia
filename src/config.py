"""
Configuration module for WSN-SDN simulation.

This module contains all configuration parameters for the simulation including
network topology, energy models, DRL hyperparameters, and output settings.
"""

import os
import random
import numpy as np
from dataclasses import dataclass, field
from typing import Tuple, Optional
from pathlib import Path

# Optional torch import
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    TORCH_AVAILABLE = False


@dataclass
class SimulationConfig:
    """
    Comprehensive configuration for WSN-SDN simulation.

    This class encapsulates all parameters needed for network deployment,
    energy modeling, routing algorithms, and deep reinforcement learning.

    Attributes:
        Network Topology:
            num_nodes: Number of sensor nodes in the network
            area_size: Size of the deployment area (square area)
            sink_position: (x, y) coordinates of the sink node
            comm_range: Communication range of sensor nodes (meters)

        Energy Model (First Order Radio):
            initial_energy: Initial energy of each sensor node (Joules)
            E_elec: Energy for electronics (J/bit)
            E_fs: Free space amplification energy (J/bit/m²)
            E_mp: Multipath amplification energy (J/bit/m⁴)
            d0: Threshold distance for energy model (meters)
            packet_size: Size of data packets (bits)

        DRL Parameters:
            state_dim: Dimension of state space
            action_dim: Dimension of action space
            hidden_dim: Hidden layer size in neural network
            learning_rate: Learning rate for optimizer
            gamma: Discount factor for future rewards
            epsilon_start: Initial exploration rate
            epsilon_min: Minimum exploration rate
            epsilon_decay: Decay rate for epsilon
            batch_size: Batch size for training
            buffer_size: Size of experience replay buffer
            training_episodes: Number of training episodes

        Simulation Control:
            max_rounds: Maximum simulation rounds
            packets_per_round: Number of packets transmitted per round
            seed: Random seed for reproducibility
            output_dir: Directory for saving results
            device: Computing device (CPU/GPU)
    """

    # Network Topology
    num_nodes: int = 100
    area_size: float = 100.0
    sink_position: Tuple[float, float] = (50.0, 50.0)
    comm_range: float = 35.0

    # Energy Model Parameters
    initial_energy: float = 0.5  # Joules
    E_elec: float = 50e-9  # J/bit
    E_fs: float = 10e-12  # J/bit/m²
    E_mp: float = 0.0013e-12  # J/bit/m⁴
    d0: float = 87.0  # meters
    packet_size: int = 4000  # bits

    # DRL Hyperparameters
    state_dim: int = 20
    action_dim: int = 6
    hidden_dim: int = 128  # Increased for better representation
    learning_rate: float = 0.0005  # Adjusted for stability
    gamma: float = 0.95
    epsilon_start: float = 1.0
    epsilon_min: float = 0.01
    epsilon_decay: float = 0.995
    batch_size: int = 64  # Increased for better gradient estimates
    buffer_size: int = 10000  # Increased capacity
    training_episodes: int = 500  # More training
    target_update_freq: int = 10  # How often to update target network

    # Simulation Parameters
    max_rounds: int = 1000  # Extended simulation
    packets_per_round: int = 20

    # System Configuration
    seed: int = 42
    output_dir: str = "results"
    use_gpu: bool = True
    verbose: bool = True

    # Derived attributes
    device: Optional[object] = field(init=False, default=None)

    def __post_init__(self):
        """Initialize derived attributes and set random seeds."""
        # Set device (if torch is available)
        if TORCH_AVAILABLE:
            if self.use_gpu and torch.cuda.is_available():
                self.device = torch.device('cuda')
            else:
                self.device = torch.device('cpu')
        else:
            self.device = 'cpu'  # String fallback if torch not available

        # Set random seeds for reproducibility
        random.seed(self.seed)
        np.random.seed(self.seed)

        if TORCH_AVAILABLE:
            torch.manual_seed(self.seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed(self.seed)
                torch.cuda.manual_seed_all(self.seed)

        # Create output directory
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

    def get_transmission_energy(self, distance: float) -> float:
        """
        Calculate transmission energy based on distance.

        Uses the First Order Radio Energy Model:
        - For d < d0: E_tx = E_elec * k + E_fs * k * d²
        - For d ≥ d0: E_tx = E_elec * k + E_mp * k * d⁴

        Args:
            distance: Transmission distance in meters

        Returns:
            Energy consumption in Joules
        """
        if distance < self.d0:
            return (self.E_elec * self.packet_size +
                   self.E_fs * self.packet_size * distance**2)
        return (self.E_elec * self.packet_size +
               self.E_mp * self.packet_size * distance**4)

    def get_reception_energy(self) -> float:
        """
        Calculate reception energy.

        Returns:
            Energy consumption for receiving a packet in Joules
        """
        return self.E_elec * self.packet_size

    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        return {
            'num_nodes': self.num_nodes,
            'area_size': self.area_size,
            'sink_position': self.sink_position,
            'comm_range': self.comm_range,
            'initial_energy': self.initial_energy,
            'E_elec': self.E_elec,
            'E_fs': self.E_fs,
            'E_mp': self.E_mp,
            'd0': self.d0,
            'packet_size': self.packet_size,
            'state_dim': self.state_dim,
            'action_dim': self.action_dim,
            'hidden_dim': self.hidden_dim,
            'learning_rate': self.learning_rate,
            'gamma': self.gamma,
            'epsilon_start': self.epsilon_start,
            'epsilon_min': self.epsilon_min,
            'epsilon_decay': self.epsilon_decay,
            'batch_size': self.batch_size,
            'buffer_size': self.buffer_size,
            'training_episodes': self.training_episodes,
            'max_rounds': self.max_rounds,
            'packets_per_round': self.packets_per_round,
            'seed': self.seed
        }

    def print_summary(self):
        """Print configuration summary."""
        print("=" * 80)
        print(" SIMULATION CONFIGURATION ".center(80))
        print("=" * 80)
        print(f"\nNetwork Topology:")
        print(f"  Nodes: {self.num_nodes}")
        print(f"  Area: {self.area_size}x{self.area_size} m²")
        print(f"  Sink Position: {self.sink_position}")
        print(f"  Communication Range: {self.comm_range} m")
        print(f"\nEnergy Model:")
        print(f"  Initial Energy: {self.initial_energy} J")
        print(f"  E_elec: {self.E_elec} J/bit")
        print(f"  E_fs: {self.E_fs} J/bit/m²")
        print(f"  E_mp: {self.E_mp} J/bit/m⁴")
        print(f"  d0: {self.d0} m")
        print(f"  Packet Size: {self.packet_size} bits")
        print(f"\nDRL Configuration:")
        print(f"  State Dimension: {self.state_dim}")
        print(f"  Action Dimension: {self.action_dim}")
        print(f"  Hidden Dimension: {self.hidden_dim}")
        print(f"  Learning Rate: {self.learning_rate}")
        print(f"  Training Episodes: {self.training_episodes}")
        print(f"\nSimulation Settings:")
        print(f"  Max Rounds: {self.max_rounds}")
        print(f"  Packets/Round: {self.packets_per_round}")
        print(f"  Device: {self.device}")
        print(f"  Output Directory: {self.output_dir}")
        print("=" * 80)


def get_default_config() -> SimulationConfig:
    """
    Get default simulation configuration.

    Returns:
        Default SimulationConfig instance
    """
    return SimulationConfig()


def get_small_network_config() -> SimulationConfig:
    """
    Get configuration for small network (testing).

    Returns:
        SimulationConfig for small network
    """
    return SimulationConfig(
        num_nodes=50,
        area_size=80.0,
        comm_range=30.0,
        max_rounds=300,
        training_episodes=200
    )


def get_large_network_config() -> SimulationConfig:
    """
    Get configuration for large network (extensive evaluation).

    Returns:
        SimulationConfig for large network
    """
    return SimulationConfig(
        num_nodes=200,
        area_size=150.0,
        comm_range=40.0,
        max_rounds=1500,
        training_episodes=800
    )
