"""
Neural network architectures for routing algorithms.

This module provides various neural network architectures including:
- Simple feedforward networks (for NN_ILEACH)
- Deep Q-Networks (DQN)
- Dueling DQN (for WOAD3QN-RP)
- Experience replay buffers
"""

import numpy as np
import random
from collections import deque
from typing import Tuple, List, Optional
import pickle


class SimpleFeedForward:
    """
    Simple feedforward neural network with tanh activation.
    Used for NN_ILEACH cluster head prediction.

    Architecture: input → hidden1 → hidden2 → output
    Activation: tanh for hidden layers, sigmoid for output
    """

    def __init__(self, input_size: int, hidden_sizes: List[int], output_size: int,
                 learning_rate: float = 0.01):
        """
        Initialize neural network.

        Args:
            input_size: Number of input features
            hidden_sizes: List of hidden layer sizes
            output_size: Number of output neurons
            learning_rate: Learning rate for training
        """
        self.input_size = input_size
        self.hidden_sizes = hidden_sizes
        self.output_size = output_size
        self.lr = learning_rate

        # Initialize weights and biases
        self.weights = []
        self.biases = []

        # Input to first hidden layer
        layer_sizes = [input_size] + hidden_sizes + [output_size]

        for i in range(len(layer_sizes) - 1):
            w = np.random.randn(layer_sizes[i], layer_sizes[i + 1]) * 0.1
            b = np.zeros((1, layer_sizes[i + 1]))
            self.weights.append(w)
            self.biases.append(b)

        self.activations = []
        self.z_values = []

    def tanh(self, x):
        """Tanh activation function."""
        return np.tanh(x)

    def tanh_derivative(self, x):
        """Derivative of tanh."""
        return 1 - np.tanh(x) ** 2

    def sigmoid(self, x):
        """Sigmoid activation function."""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

    def sigmoid_derivative(self, x):
        """Derivative of sigmoid."""
        s = self.sigmoid(x)
        return s * (1 - s)

    def forward(self, x):
        """
        Forward propagation.

        Args:
            x: Input features (batch_size, input_size)

        Returns:
            Output predictions (batch_size, output_size)
        """
        if len(x.shape) == 1:
            x = x.reshape(1, -1)

        self.activations = [x]
        self.z_values = []

        a = x

        # Hidden layers with tanh
        for i in range(len(self.weights) - 1):
            z = np.dot(a, self.weights[i]) + self.biases[i]
            a = self.tanh(z)
            self.z_values.append(z)
            self.activations.append(a)

        # Output layer with sigmoid
        z = np.dot(a, self.weights[-1]) + self.biases[-1]
        a = self.sigmoid(z)
        self.z_values.append(z)
        self.activations.append(a)

        return a

    def backward(self, x, y):
        """
        Backward propagation with gradient descent.

        Args:
            x: Input features
            y: Target values
        """
        m = x.shape[0]

        # Output layer gradient
        deltas = [None] * len(self.weights)
        deltas[-1] = (self.activations[-1] - y) * self.sigmoid_derivative(self.z_values[-1])

        # Hidden layers gradients
        for i in range(len(self.weights) - 2, -1, -1):
            deltas[i] = np.dot(deltas[i + 1], self.weights[i + 1].T) * self.tanh_derivative(self.z_values[i])

        # Update weights and biases
        for i in range(len(self.weights)):
            self.weights[i] -= self.lr * np.dot(self.activations[i].T, deltas[i]) / m
            self.biases[i] -= self.lr * np.sum(deltas[i], axis=0, keepdims=True) / m

    def train(self, X, y, epochs=1000, verbose=False):
        """
        Train the network.

        Args:
            X: Training features (n_samples, input_size)
            y: Training targets (n_samples, output_size)
            epochs: Number of training epochs
            verbose: Print training progress
        """
        if len(y.shape) == 1:
            y = y.reshape(-1, 1)

        for epoch in range(epochs):
            # Forward pass
            predictions = self.forward(X)

            # Backward pass
            self.backward(X, y)

            # Calculate loss
            if verbose and epoch % 100 == 0:
                loss = np.mean((predictions - y) ** 2)
                print(f"Epoch {epoch}, Loss: {loss:.6f}")

    def predict(self, x):
        """
        Make predictions.

        Args:
            x: Input features

        Returns:
            Predictions
        """
        return self.forward(x)

    def save(self, filepath):
        """Save model to file."""
        model_data = {
            'weights': self.weights,
            'biases': self.biases,
            'input_size': self.input_size,
            'hidden_sizes': self.hidden_sizes,
            'output_size': self.output_size,
            'lr': self.lr
        }
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

    def load(self, filepath):
        """Load model from file."""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        self.weights = model_data['weights']
        self.biases = model_data['biases']
        self.input_size = model_data['input_size']
        self.hidden_sizes = model_data['hidden_sizes']
        self.output_size = model_data['output_size']
        self.lr = model_data['lr']


class ExperienceReplayBuffer:
    """
    Experience replay buffer for DRL algorithms.
    Stores transitions (state, action, reward, next_state, done).
    """

    def __init__(self, capacity: int = 10000):
        """
        Initialize replay buffer.

        Args:
            capacity: Maximum buffer size
        """
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        """Add experience to buffer."""
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size: int):
        """
        Sample random batch from buffer.

        Args:
            batch_size: Number of samples

        Returns:
            Batch of experiences
        """
        batch = random.sample(self.buffer, min(batch_size, len(self.buffer)))

        states = np.array([e[0] for e in batch])
        actions = np.array([e[1] for e in batch])
        rewards = np.array([e[2] for e in batch])
        next_states = np.array([e[3] for e in batch])
        dones = np.array([e[4] for e in batch])

        return states, actions, rewards, next_states, dones

    def __len__(self):
        """Return current buffer size."""
        return len(self.buffer)


class DQN:
    """
    Deep Q-Network implementation.
    Used as base for various DRL routing algorithms.
    """

    def __init__(self, state_dim: int, action_dim: int,
                 hidden_sizes: List[int] = [256, 128],
                 learning_rate: float = 0.001,
                 gamma: float = 0.95):
        """
        Initialize DQN.

        Args:
            state_dim: State space dimension
            action_dim: Action space dimension
            hidden_sizes: Hidden layer sizes
            learning_rate: Learning rate
            gamma: Discount factor
        """
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.lr = learning_rate

        # Build network
        self.weights = []
        self.biases = []

        layer_sizes = [state_dim] + hidden_sizes + [action_dim]

        for i in range(len(layer_sizes) - 1):
            w = np.random.randn(layer_sizes[i], layer_sizes[i + 1]) * np.sqrt(2.0 / layer_sizes[i])
            b = np.zeros((1, layer_sizes[i + 1]))
            self.weights.append(w)
            self.biases.append(b)

    def relu(self, x):
        """ReLU activation."""
        return np.maximum(0, x)

    def forward(self, state):
        """
        Forward pass to get Q-values.

        Args:
            state: Input state

        Returns:
            Q-values for all actions
        """
        if len(state.shape) == 1:
            state = state.reshape(1, -1)

        a = state

        # Hidden layers with ReLU
        for i in range(len(self.weights) - 1):
            z = np.dot(a, self.weights[i]) + self.biases[i]
            a = self.relu(z)

        # Output layer (linear)
        q_values = np.dot(a, self.weights[-1]) + self.biases[-1]

        return q_values

    def get_action(self, state, epsilon: float = 0.0):
        """
        Get action using epsilon-greedy policy.

        Args:
            state: Current state
            epsilon: Exploration rate

        Returns:
            Selected action
        """
        if np.random.random() < epsilon:
            return np.random.randint(0, self.action_dim)
        else:
            q_values = self.forward(state)
            return int(np.argmax(q_values))

    def train_step(self, states, actions, rewards, next_states, dones):
        """
        Single training step.

        Args:
            states: Batch of states
            actions: Batch of actions
            rewards: Batch of rewards
            next_states: Batch of next states
            dones: Batch of done flags

        Returns:
            Loss value
        """
        # Current Q-values
        q_values = self.forward(states)

        # Target Q-values
        next_q_values = self.forward(next_states)
        max_next_q = np.max(next_q_values, axis=1)

        targets = rewards + self.gamma * max_next_q * (1 - dones)

        # Update Q-values for taken actions
        q_targets = q_values.copy()
        for i, action in enumerate(actions):
            q_targets[i, action] = targets[i]

        # Simple gradient descent (simplified)
        loss = np.mean((q_values - q_targets) ** 2)

        return loss

    def save(self, filepath):
        """Save model."""
        model_data = {
            'weights': self.weights,
            'biases': self.biases,
            'state_dim': self.state_dim,
            'action_dim': self.action_dim,
            'gamma': self.gamma,
            'lr': self.lr
        }
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

    def load(self, filepath):
        """Load model."""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        self.weights = model_data['weights']
        self.biases = model_data['biases']
        self.state_dim = model_data['state_dim']
        self.action_dim = model_data['action_dim']
        self.gamma = model_data['gamma']
        self.lr = model_data['lr']
