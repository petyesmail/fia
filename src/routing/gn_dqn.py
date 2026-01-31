"""
GN-DQN: Graph Neural Network with Deep Q-Network.

Combines GNN (GAT + GCN) for topology-aware feature learning with DQN
for routing decisions. Generalizes across different network topologies.

Reference:
Future Generation Computer Systems, 2024, Article S0167739X23003497.
DOI: S0167739X23003497

Expected Performance:
- Topology generalization
- Long-term revenue optimization
- Superior path selection
"""

import numpy as np
from typing import Dict
from .base import RoutingAlgorithm
from ..utils.graph_utils import GraphNeuralNetwork, GraphBuilder
from ..utils.neural_networks import DQN


class GN_DQN(RoutingAlgorithm):
    """
    Graph Neural Network + Deep Q-Network.
    
    Uses GNN to learn topology-aware node embeddings,
    then DQN for routing decisions.
    """
    
    def __init__(self, input_dim=5, hidden_dim=64, output_dim=128):
        """
        Initialize GN-DQN.
        
        Args:
            input_dim: Node feature dimension
            hidden_dim: GNN hidden dimension
            output_dim: Graph embedding dimension
        """
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        
        # GNN for graph embedding
        self.gnn = GraphNeuralNetwork(input_dim, hidden_dim, output_dim)
        
        # DQN for routing decisions
        self.dqn = None
        self.epsilon = 0.5
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.99
        
    @property
    def algorithm_name(self) -> str:
        return "GN-DQN"
    
    def get_description(self) -> str:
        return ("GN-DQN: Graph Neural Network + Deep Q-Network. "
                "Topology-aware deep reinforcement learning routing.")
    
    def _build_graph(self, controller):
        """Build graph representation of network."""
        alive_nodes = {nid: n for nid, n in controller.nodes.items()
                       if nid != 'SINK' and n.is_alive}
        
        if not alive_nodes:
            return None, None
        
        # Build adjacency matrix
        node_positions = {nid: (n.x, n.y) for nid, n in alive_nodes.items()}
        adj_matrix = GraphBuilder.build_adjacency_matrix(
            node_positions,
            controller.config.comm_range
        )
        
        # Build node features
        nodes_data = {}
        for nid, node in alive_nodes.items():
            nodes_data[nid] = {
                'energy': node.energy / node.initial_energy if node.initial_energy > 0 else 0,
                'buffer': 0.0,
                'x': node.x / controller.config.area_size,
                'y': node.y / controller.config.area_size,
                'degree': np.sum(adj_matrix[list(alive_nodes.keys()).index(nid)])
            }
        
        node_features = GraphBuilder.create_node_features(nodes_data)
        
        return node_features, adj_matrix
    
    def compute_routing_table(self, controller) -> Dict[str, str]:
        """Compute routing using GN-DQN."""
        routing_table = {}
        
        # Build graph
        node_features, adj_matrix = self._build_graph(controller)
        
        if node_features is None:
            return routing_table
        
        # GNN forward pass
        graph_embedding, node_embeddings = self.gnn.forward(node_features, adj_matrix)
        
        # Initialize DQN if needed
        if self.dqn is None:
            state_dim = self.output_dim * 2  # graph_emb (128) + node_emb (128)
            max_neighbors = 10
            self.dqn = DQN(state_dim=state_dim, action_dim=max_neighbors)
        
        # For each node, select next hop
        alive_nodes = [nid for nid, n in controller.nodes.items()
                       if nid != 'SINK' and n.is_alive]
        
        for idx, node_id in enumerate(alive_nodes):
            if idx >= len(node_embeddings):
                continue
            
            # Combined state: graph embedding + node embedding
            node_emb = node_embeddings[idx]
            state = np.concatenate([graph_embedding, node_emb])
            
            # Get neighbors
            node = controller.nodes[node_id]
            neighbors = []
            for other_id, other in controller.nodes.items():
                if other_id == node_id:
                    continue
                if other_id != 'SINK' and not other.is_alive:
                    continue
                
                dist = np.sqrt((node.x - other.x)**2 + (node.y - other.y)**2)
                if dist <= controller.config.comm_range or other_id == 'SINK':
                    neighbors.append(other_id)
            
            if not neighbors:
                continue
            
            # Select action
            action_idx = self.dqn.get_action(state, self.epsilon)
            
            if action_idx < len(neighbors):
                routing_table[node_id] = neighbors[action_idx]
            else:
                routing_table[node_id] = neighbors[0]
        
        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        return routing_table
