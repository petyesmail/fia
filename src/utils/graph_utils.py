"""
Graph neural network utilities.

This module provides graph-based operations for GN-DQN:
- Graph construction from network topology
- Graph Attention Layer (GAT)
- Graph Convolution Layer (GCN)
- Global pooling operations
"""

import numpy as np
from typing import Dict, List, Tuple, Optional


class GraphBuilder:
    """
    Build graph representation from WSN network.
    """

    @staticmethod
    def build_adjacency_matrix(node_positions: Dict[int, Tuple[float, float]],
                                communication_range: float) -> np.ndarray:
        """
        Build adjacency matrix based on communication range.

        Args:
            node_positions: Dictionary mapping node_id to (x, y)
            communication_range: Maximum communication distance

        Returns:
            Adjacency matrix (n_nodes, n_nodes)
        """
        node_ids = sorted(node_positions.keys())
        n_nodes = len(node_ids)
        adj_matrix = np.zeros((n_nodes, n_nodes))

        id_to_idx = {node_id: idx for idx, node_id in enumerate(node_ids)}

        for i, node_i in enumerate(node_ids):
            x_i, y_i = node_positions[node_i]

            for j, node_j in enumerate(node_ids):
                if i == j:
                    continue

                x_j, y_j = node_positions[node_j]
                distance = np.sqrt((x_i - x_j) ** 2 + (y_i - y_j) ** 2)

                if distance <= communication_range:
                    adj_matrix[i, j] = 1.0

        return adj_matrix

    @staticmethod
    def create_node_features(nodes_data: Dict[int, Dict]) -> np.ndarray:
        """
        Create node feature matrix.

        Features per node:
        - Residual energy (normalized)
        - Buffer occupancy (normalized)
        - Geographic location (x, y normalized)
        - Degree centrality
        - Historical traffic

        Args:
            nodes_data: Dictionary with node information

        Returns:
            Node feature matrix (n_nodes, n_features)
        """
        node_ids = sorted(nodes_data.keys())
        n_nodes = len(node_ids)
        n_features = 5  # energy, buffer, x, y, degree

        features = np.zeros((n_nodes, n_features))

        for idx, node_id in enumerate(node_ids):
            data = nodes_data[node_id]

            features[idx, 0] = data.get('energy', 0.0)  # Normalized energy
            features[idx, 1] = data.get('buffer', 0.0)  # Normalized buffer
            features[idx, 2] = data.get('x', 0.0)  # Normalized x
            features[idx, 3] = data.get('y', 0.0)  # Normalized y
            features[idx, 4] = data.get('degree', 0.0)  # Degree centrality

        return features

    @staticmethod
    def create_edge_features(adj_matrix: np.ndarray,
                              node_positions: Dict[int, Tuple[float, float]],
                              link_quality: Optional[Dict[Tuple[int, int], float]] = None) -> Dict:
        """
        Create edge feature dictionary.

        Args:
            adj_matrix: Adjacency matrix
            node_positions: Node positions
            link_quality: Optional link quality metrics

        Returns:
            Dictionary with edge features
        """
        node_ids = sorted(node_positions.keys())
        edge_features = {}

        for i, node_i in enumerate(node_ids):
            for j, node_j in enumerate(node_ids):
                if adj_matrix[i, j] > 0:
                    x_i, y_i = node_positions[node_i]
                    x_j, y_j = node_positions[node_j]

                    distance = np.sqrt((x_i - x_j) ** 2 + (y_i - y_j) ** 2)

                    quality = 1.0
                    if link_quality and (node_i, node_j) in link_quality:
                        quality = link_quality[(node_i, node_j)]

                    edge_features[(i, j)] = {
                        'distance': distance,
                        'quality': quality
                    }

        return edge_features


class GraphAttentionLayer:
    """
    Graph Attention Layer (GAT).
    Implements attention mechanism for graph neural networks.
    """

    def __init__(self, in_features: int, out_features: int, alpha: float = 0.2):
        """
        Initialize GAT layer.

        Args:
            in_features: Input feature dimension
            out_features: Output feature dimension
            alpha: LeakyReLU negative slope
        """
        self.in_features = in_features
        self.out_features = out_features
        self.alpha = alpha

        # Initialize weights
        self.W = np.random.randn(in_features, out_features) * 0.01
        self.a = np.random.randn(2 * out_features, 1) * 0.01

    def leaky_relu(self, x):
        """LeakyReLU activation."""
        return np.where(x > 0, x, x * self.alpha)

    def compute_attention(self, h_i: np.ndarray, h_j: np.ndarray) -> float:
        """
        Compute attention coefficient between nodes i and j.

        Args:
            h_i: Features of node i
            h_j: Features of node j

        Returns:
            Attention coefficient
        """
        concat = np.concatenate([h_i, h_j])
        e = self.leaky_relu(np.dot(concat, self.a))
        return float(e)

    def forward(self, node_features: np.ndarray, adj_matrix: np.ndarray) -> np.ndarray:
        """
        Forward pass through GAT layer.

        Args:
            node_features: Input node features (n_nodes, in_features)
            adj_matrix: Adjacency matrix (n_nodes, n_nodes)

        Returns:
            Output node features (n_nodes, out_features)
        """
        n_nodes = node_features.shape[0]

        # Linear transformation
        h = np.dot(node_features, self.W)  # (n_nodes, out_features)

        # Compute attention coefficients
        attention = np.zeros((n_nodes, n_nodes))

        for i in range(n_nodes):
            neighbors = np.where(adj_matrix[i] > 0)[0]

            if len(neighbors) == 0:
                continue

            # Compute attention for all neighbors
            e_values = []
            for j in neighbors:
                e = self.compute_attention(h[i], h[j])
                e_values.append(e)

            # Softmax normalization
            e_values = np.array(e_values)
            e_exp = np.exp(e_values - np.max(e_values))
            alpha_values = e_exp / np.sum(e_exp)

            # Store normalized attention
            for idx, j in enumerate(neighbors):
                attention[i, j] = alpha_values[idx]

        # Aggregate neighbor features
        output = np.zeros((n_nodes, self.out_features))

        for i in range(n_nodes):
            for j in range(n_nodes):
                if attention[i, j] > 0:
                    output[i] += attention[i, j] * h[j]

        return output


class GraphConvolutionLayer:
    """
    Graph Convolution Layer (GCN).
    Implements standard graph convolution with normalization.
    """

    def __init__(self, in_features: int, out_features: int):
        """
        Initialize GCN layer.

        Args:
            in_features: Input feature dimension
            out_features: Output feature dimension
        """
        self.in_features = in_features
        self.out_features = out_features

        # Initialize weight matrix
        self.W = np.random.randn(in_features, out_features) * np.sqrt(2.0 / in_features)

    def normalize_adjacency(self, adj_matrix: np.ndarray) -> np.ndarray:
        """
        Normalize adjacency matrix: D^(-1/2) * A * D^(-1/2)

        Args:
            adj_matrix: Adjacency matrix

        Returns:
            Normalized adjacency matrix
        """
        # Add self-loops
        adj_with_self_loops = adj_matrix + np.eye(adj_matrix.shape[0])

        # Compute degree matrix
        degree = np.sum(adj_with_self_loops, axis=1)
        degree[degree == 0] = 1  # Avoid division by zero

        # D^(-1/2)
        d_inv_sqrt = np.diag(1.0 / np.sqrt(degree))

        # Normalized adjacency
        norm_adj = d_inv_sqrt @ adj_with_self_loops @ d_inv_sqrt

        return norm_adj

    def forward(self, node_features: np.ndarray, adj_matrix: np.ndarray) -> np.ndarray:
        """
        Forward pass through GCN layer.

        Formula: H' = σ(D^(-1/2) * A * D^(-1/2) * H * W)

        Args:
            node_features: Input node features (n_nodes, in_features)
            adj_matrix: Adjacency matrix (n_nodes, n_nodes)

        Returns:
            Output node features (n_nodes, out_features)
        """
        # Normalize adjacency
        norm_adj = self.normalize_adjacency(adj_matrix)

        # Graph convolution
        support = np.dot(node_features, self.W)
        output = np.dot(norm_adj, support)

        return output


class GlobalPooling:
    """
    Global pooling operations for graph-level representations.
    """

    @staticmethod
    def mean_pool(node_features: np.ndarray) -> np.ndarray:
        """
        Mean pooling over all nodes.

        Args:
            node_features: Node features (n_nodes, n_features)

        Returns:
            Graph-level features (n_features,)
        """
        return np.mean(node_features, axis=0)

    @staticmethod
    def max_pool(node_features: np.ndarray) -> np.ndarray:
        """
        Max pooling over all nodes.

        Args:
            node_features: Node features (n_nodes, n_features)

        Returns:
            Graph-level features (n_features,)
        """
        return np.max(node_features, axis=0)

    @staticmethod
    def sum_pool(node_features: np.ndarray) -> np.ndarray:
        """
        Sum pooling over all nodes.

        Args:
            node_features: Node features (n_nodes, n_features)

        Returns:
            Graph-level features (n_features,)
        """
        return np.sum(node_features, axis=0)

    @staticmethod
    def attention_pool(node_features: np.ndarray, attention_weights: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Attention-based pooling.

        Args:
            node_features: Node features (n_nodes, n_features)
            attention_weights: Optional attention weights (n_nodes,)

        Returns:
            Graph-level features (n_features,)
        """
        if attention_weights is None:
            # Uniform attention
            attention_weights = np.ones(node_features.shape[0]) / node_features.shape[0]

        # Normalize
        attention_weights = attention_weights / np.sum(attention_weights)

        # Weighted sum
        pooled = np.sum(node_features * attention_weights[:, np.newaxis], axis=0)

        return pooled


class GraphNeuralNetwork:
    """
    Complete Graph Neural Network combining GAT, GCN, and pooling.
    Used in GN-DQN algorithm.
    """

    def __init__(self, input_dim: int, hidden_dim: int = 64, output_dim: int = 128):
        """
        Initialize GNN.

        Args:
            input_dim: Input feature dimension
            hidden_dim: Hidden layer dimension
            output_dim: Output graph embedding dimension
        """
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim

        # Layer 1: GAT
        self.gat_layer = GraphAttentionLayer(input_dim, hidden_dim)

        # Layer 2: GCN
        self.gcn_layer = GraphConvolutionLayer(hidden_dim, output_dim)

        # Pooling
        self.pooling = GlobalPooling()

    def relu(self, x):
        """ReLU activation."""
        return np.maximum(0, x)

    def forward(self, node_features: np.ndarray, adj_matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Forward pass through GNN.

        Args:
            node_features: Input node features (n_nodes, input_dim)
            adj_matrix: Adjacency matrix (n_nodes, n_nodes)

        Returns:
            Tuple of (graph_embedding, node_embeddings)
        """
        # Layer 1: GAT with ReLU
        h1 = self.gat_layer.forward(node_features, adj_matrix)
        h1 = self.relu(h1)

        # Layer 2: GCN with ReLU
        h2 = self.gcn_layer.forward(h1, adj_matrix)
        h2 = self.relu(h2)

        # Global pooling
        graph_embedding = self.pooling.mean_pool(h2)

        return graph_embedding, h2

    def save_weights(self, filepath: str):
        """Save GNN weights."""
        import pickle
        weights = {
            'gat_W': self.gat_layer.W,
            'gat_a': self.gat_layer.a,
            'gcn_W': self.gcn_layer.W
        }
        with open(filepath, 'wb') as f:
            pickle.dump(weights, f)

    def load_weights(self, filepath: str):
        """Load GNN weights."""
        import pickle
        with open(filepath, 'rb') as f:
            weights = pickle.load(f)
        self.gat_layer.W = weights['gat_W']
        self.gat_layer.a = weights['gat_a']
        self.gcn_layer.W = weights['gcn_W']
