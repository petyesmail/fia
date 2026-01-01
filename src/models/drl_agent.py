"""
Deep Reinforcement Learning Agent for Routing.

This module implements a DQN-based agent that learns optimal routing decisions
through interaction with the network environment.
"""

import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from collections import deque
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..config import SimulationConfig
    from .network import SDNController


class DeepQNetwork(nn.Module):
    """
    Deep Q-Network for approximating action-value function.

    Architecture:
    - Input layer: state_dim
    - Hidden layer 1: hidden_dim with ReLU
    - Hidden layer 2: hidden_dim with ReLU
    - Output layer: action_dim (Q-values)

    The network uses Xavier initialization for stable training.
    """

    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int):
        """
        Initialize DQN.

        Args:
            state_dim: Dimension of state space
            action_dim: Dimension of action space
            hidden_dim: Size of hidden layers
        """
        super(DeepQNetwork, self).__init__()

        self.network = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.BatchNorm1d(hidden_dim),  # Added batch normalization
            nn.Dropout(0.1),  # Added dropout for regularization
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.BatchNorm1d(hidden_dim),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, action_dim)
        )

        self._initialize_weights()

    def _initialize_weights(self):
        """Initialize network weights using Xavier initialization."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.constant_(module.bias, 0.0)

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the network.

        Args:
            state: Input state tensor [batch_size, state_dim]

        Returns:
            Q-values for each action [batch_size, action_dim]
        """
        return self.network(state)


class ExperienceReplayBuffer:
    """
    Experience replay buffer for storing and sampling transitions.

    The buffer stores (state, action, reward, next_state, done) tuples
    and supports random sampling for breaking temporal correlations.
    """

    def __init__(self, capacity: int):
        """
        Initialize replay buffer.

        Args:
            capacity: Maximum number of transitions to store
        """
        self.buffer = deque(maxlen=capacity)

    def store(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: float
    ):
        """
        Store a transition in the buffer.

        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode terminated (1.0 if done, 0.0 otherwise)
        """
        self.buffer.append((state, action, reward, next_state, done))

    def sample_batch(self, batch_size: int) -> Tuple:
        """
        Sample a random batch of transitions.

        Args:
            batch_size: Number of transitions to sample

        Returns:
            Tuple of (states, actions, rewards, next_states, dones)
        """
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        return (
            np.array(states, dtype=np.float32),
            np.array(actions, dtype=np.int64),
            np.array(rewards, dtype=np.float32),
            np.array(next_states, dtype=np.float32),
            np.array(dones, dtype=np.float32)
        )

    def __len__(self) -> int:
        """Get current buffer size."""
        return len(self.buffer)

    def clear(self):
        """Clear the buffer."""
        self.buffer.clear()


class DRLRoutingAgent:
    """
    Deep Reinforcement Learning agent for routing decisions.

    This agent uses Double DQN with experience replay to learn
    optimal routing policies that maximize network performance
    while minimizing energy consumption.

    Key Features:
    - Double DQN for reducing overestimation bias
    - Experience replay for sample efficiency
    - Epsilon-greedy exploration
    - Target network for stable training
    - State feature extraction from network
    """

    def __init__(self, config: 'SimulationConfig'):
        """
        Initialize DRL agent.

        Args:
            config: Simulation configuration
        """
        self.config = config
        self.epsilon = config.epsilon_start

        # Create policy and target networks
        self.policy_network = DeepQNetwork(
            config.state_dim,
            config.action_dim,
            config.hidden_dim
        ).to(config.device)

        self.target_network = DeepQNetwork(
            config.state_dim,
            config.action_dim,
            config.hidden_dim
        ).to(config.device)

        # Initialize target network with policy network weights
        self.target_network.load_state_dict(self.policy_network.state_dict())
        self.target_network.eval()  # Target network is always in eval mode

        # Optimizer
        self.optimizer = optim.Adam(
            self.policy_network.parameters(),
            lr=config.learning_rate
        )

        # Experience replay
        self.replay_buffer = ExperienceReplayBuffer(config.buffer_size)

        # Training statistics
        self.training_steps = 0
        self.total_loss = 0.0

    def extract_state_features(
        self,
        controller: 'SDNController',
        current_node_id: str
    ) -> np.ndarray:
        """
        Extract state features for the current node.

        State representation includes:
        1. Current node features (4 features):
           - Residual energy ratio
           - Normalized x position
           - Normalized y position
           - Distance to sink (normalized)

        2. Neighbor features (4 neighbors × 4 features = 16 features):
           For each of top-4 closest neighbors to sink:
           - Residual energy ratio
           - Distance to sink (normalized)
           - Distance to current node (normalized)
           - Transmitted packets (normalized)

        Total: 20 features

        Args:
            controller: SDN controller with network state
            current_node_id: ID of current node

        Returns:
            State feature vector [state_dim]
        """
        node = controller.nodes[current_node_id]
        sink = controller.get_sink_node()

        if sink is None:
            # Fallback if no sink
            return np.zeros(self.config.state_dim, dtype=np.float32)

        # Current node features
        features = [
            node.get_residual_energy_ratio(),
            node.position.x / controller.config.area_size,
            node.position.y / controller.config.area_size,
            node.position.distance_to(sink.position) / (controller.config.area_size * np.sqrt(2)),
        ]

        # Get valid neighbors (alive, not sink)
        valid_neighbors = [
            n_id for n_id in node.neighbors
            if controller.nodes[n_id].is_alive and n_id != "SINK"
        ]

        # Sort by distance to sink (greedy baseline)
        valid_neighbors = sorted(
            valid_neighbors,
            key=lambda n: controller.nodes[n].position.distance_to(sink.position)
        )[:4]  # Top 4 neighbors

        # Extract neighbor features
        for i in range(4):
            if i < len(valid_neighbors):
                neighbor = controller.nodes[valid_neighbors[i]]

                features.extend([
                    neighbor.get_residual_energy_ratio(),
                    neighbor.position.distance_to(sink.position) / (controller.config.area_size * np.sqrt(2)),
                    node.position.distance_to(neighbor.position) / controller.config.comm_range,
                    min(neighbor.transmitted_packets / 100.0, 1.0)
                ])
            else:
                # Padding for missing neighbors
                features.extend([0.0, 1.0, 1.0, 0.0])

        # Ensure correct dimensionality
        state = np.array(features[:self.config.state_dim], dtype=np.float32)

        # Pad if necessary
        if len(state) < self.config.state_dim:
            state = np.pad(state, (0, self.config.state_dim - len(state)))

        return state

    def select_action(
        self,
        state: np.ndarray,
        num_valid_actions: int,
        training: bool = True
    ) -> int:
        """
        Select action using epsilon-greedy policy.

        Args:
            state: Current state features
            num_valid_actions: Number of valid actions
            training: Whether in training mode (enables exploration)

        Returns:
            Selected action index
        """
        # Exploration: random action
        if training and random.random() < self.epsilon:
            return random.randrange(min(num_valid_actions, self.config.action_dim))

        # Exploitation: best action according to Q-network
        self.policy_network.eval()
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.config.device)
            q_values = self.policy_network(state_tensor).cpu().numpy()[0]

            # Select best action from valid actions
            valid_q = q_values[:min(num_valid_actions, self.config.action_dim)]
            action = int(np.argmax(valid_q))

        self.policy_network.train()
        return action

    def train_step(self) -> float:
        """
        Perform one training step using experience replay.

        Returns:
            Training loss value
        """
        if len(self.replay_buffer) < self.config.batch_size:
            return 0.0

        # Sample batch
        states, actions, rewards, next_states, dones = \
            self.replay_buffer.sample_batch(self.config.batch_size)

        # Convert to tensors
        states_t = torch.FloatTensor(states).to(self.config.device)
        actions_t = torch.LongTensor(actions).to(self.config.device)
        rewards_t = torch.FloatTensor(rewards).to(self.config.device)
        next_states_t = torch.FloatTensor(next_states).to(self.config.device)
        dones_t = torch.FloatTensor(dones).to(self.config.device)

        # Current Q-values
        current_q_values = self.policy_network(states_t).gather(1, actions_t.unsqueeze(1)).squeeze()

        # Target Q-values (Double DQN)
        with torch.no_grad():
            # Use policy network to select actions
            next_actions = self.policy_network(next_states_t).argmax(1)
            # Use target network to evaluate actions
            next_q_values = self.target_network(next_states_t).gather(1, next_actions.unsqueeze(1)).squeeze()
            target_q_values = rewards_t + self.config.gamma * next_q_values * (1 - dones_t)

        # Compute loss
        loss = F.mse_loss(current_q_values, target_q_values)

        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_network.parameters(), 1.0)  # Gradient clipping
        self.optimizer.step()

        # Update statistics
        self.training_steps += 1
        self.total_loss += loss.item()

        # Decay epsilon
        if self.epsilon > self.config.epsilon_min:
            self.epsilon *= self.config.epsilon_decay

        return loss.item()

    def synchronize_networks(self):
        """Synchronize target network with policy network."""
        self.target_network.load_state_dict(self.policy_network.state_dict())

    def get_average_loss(self) -> float:
        """Get average training loss."""
        if self.training_steps == 0:
            return 0.0
        return self.total_loss / self.training_steps

    def save_model(self, filepath: str):
        """Save model weights."""
        torch.save({
            'policy_network': self.policy_network.state_dict(),
            'target_network': self.target_network.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'training_steps': self.training_steps
        }, filepath)

    def load_model(self, filepath: str):
        """Load model weights."""
        checkpoint = torch.load(filepath, map_location=self.config.device)
        self.policy_network.load_state_dict(checkpoint['policy_network'])
        self.target_network.load_state_dict(checkpoint['target_network'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])
        self.epsilon = checkpoint['epsilon']
        self.training_steps = checkpoint['training_steps']
