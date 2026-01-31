"""
DOS-RL: Dynamic Objective Selection with Reinforcement Learning.

Multi-objective Q-learning with dynamic weight adjustment based on network state.
Three objectives: Energy Conservation, Load Balancing, Link Quality.

Reference:
Godfrey, K., et al. (2023). An energy-efficient routing protocol with 
reinforcement learning in software-defined wireless sensor networks.
Sensors, 23(20), 8435. DOI: 10.3390/s23208435

Expected Performance:
- PDR improvement: 10-20% vs OSPF
- End-to-end delay: Significant reduction vs SDN-Q
- Energy balance: Jain's index > 0.85
"""

import numpy as np
from typing import Dict, List, Tuple
from .base import RoutingAlgorithm


class DOS_RL(RoutingAlgorithm):
    """
    Dynamic Objective Selection with Reinforcement Learning.
    
    Maintains 3 Q-tables for different objectives.
    Dynamically adjusts weights based on network conditions.
    """
    
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=1.0, epsilon_min=0.05, epsilon_decay=0.99):
        """
        Initialize DOS-RL.
        
        Args:
            alpha: Learning rate
            gamma: Discount factor
            epsilon: Initial exploration rate
            epsilon_min: Minimum exploration rate
            epsilon_decay: Epsilon decay rate
        """
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        
        # Three Q-tables for three objectives
        self.q_energy = {}  # Energy conservation
        self.q_load = {}    # Load balancing
        self.q_link = {}    # Link quality
        
        # Dynamic weights
        self.w_energy = 0.33
        self.w_load = 0.33
        self.w_link = 0.34
        
        # State tracking
        self.queue_lengths = {}
        self.packet_counts = {}
        
    @property
    def algorithm_name(self) -> str:
        return "DOS-RL"
    
    def get_description(self) -> str:
        return ("DOS-RL: Dynamic Objective Selection with Reinforcement Learning. "
                "Multi-objective Q-learning with adaptive weights.")
    
    def _get_state(self, node_id: str, controller) -> Tuple:
        """Extract state representation."""
        node = controller.nodes[node_id]
        
        # Energy level (discretized)
        energy_level = int(node.energy / node.initial_energy * 10) if node.initial_energy > 0 else 0
        
        # Queue level
        queue_level = self.queue_lengths.get(node_id, 0)
        
        # Neighbor count
        alive_neighbors = self._get_alive_neighbors(node_id, controller)
        neighbor_count = len(alive_neighbors)
        
        return (energy_level, queue_level, neighbor_count)
    
    def _get_alive_neighbors(self, node_id: str, controller) -> List[str]:
        """Get list of alive neighbor nodes."""
        neighbors = []
        node = controller.nodes[node_id]
        comm_range = controller.config.comm_range
        
        for other_id, other in controller.nodes.items():
            if other_id == node_id or other_id == 'SINK':
                continue
            if not other.is_alive:
                continue
            
            dist = np.sqrt((node.x - other.x) ** 2 + (node.y - other.y) ** 2)
            if dist <= comm_range:
                neighbors.append(other_id)
        
        # Always include SINK as potential next hop
        if node_id != 'SINK':
            sink = controller.nodes['SINK']
            dist_to_sink = np.sqrt((node.x - sink.x) ** 2 + (node.y - sink.y) ** 2)
            if dist_to_sink <= comm_range:
                neighbors.append('SINK')
        
        return neighbors
    
    def _update_weights(self, controller):
        """Dynamically adjust objective weights based on network state."""
        # Calculate average energy
        total_nodes = 0
        total_energy = 0
        for nid, node in controller.nodes.items():
            if nid != 'SINK' and node.is_alive:
                total_nodes += 1
                total_energy += node.energy / node.initial_energy if node.initial_energy > 0 else 0
        
        avg_energy = total_energy / total_nodes if total_nodes > 0 else 1.0
        
        # Calculate congestion
        avg_queue = np.mean(list(self.queue_lengths.values())) if self.queue_lengths else 0
        max_queue = 10  # Assumed max queue size
        congestion_ratio = avg_queue / max_queue if max_queue > 0 else 0
        
        # Adjust weights
        if avg_energy < 0.3:
            # Low energy: prioritize energy
            self.w_energy = 0.6
            self.w_load = 0.2
            self.w_link = 0.2
        elif congestion_ratio > 0.7:
            # High congestion: prioritize load balancing
            self.w_energy = 0.2
            self.w_load = 0.6
            self.w_link = 0.2
        else:
            # Normal: balanced
            self.w_energy = 0.33
            self.w_load = 0.33
            self.w_link = 0.34
    
    def _select_action(self, state: Tuple, neighbors: List[str]) -> str:
        """Select action using epsilon-greedy policy."""
        if len(neighbors) == 0:
            return None
        
        if np.random.random() < self.epsilon:
            # Exploration
            return np.random.choice(neighbors)
        
        # Exploitation: choose based on combined Q-values
        best_action = None
        best_value = float('-inf')
        
        for action in neighbors:
            q_e = self.q_energy.get((state, action), 0.0)
            q_l = self.q_load.get((state, action), 0.0)
            q_k = self.q_link.get((state, action), 0.0)
            
            combined_q = self.w_energy * q_e + self.w_load * q_l + self.w_link * q_k
            
            if combined_q > best_value:
                best_value = combined_q
                best_action = action
        
        return best_action if best_action else neighbors[0]
    
    def compute_routing_table(self, controller) -> Dict[str, str]:
        """Compute routing table using multi-objective Q-learning."""
        routing_table = {}
        
        # Update dynamic weights
        self._update_weights(controller)
        
        # For each alive node, select next hop
        for node_id, node in controller.nodes.items():
            if node_id == 'SINK' or not node.is_alive:
                continue
            
            state = self._get_state(node_id, controller)
            neighbors = self._get_alive_neighbors(node_id, controller)
            
            if neighbors:
                next_hop = self._select_action(state, neighbors)
                if next_hop:
                    routing_table[node_id] = next_hop
                    
                    # Update Q-values (simplified - would normally happen after receiving rewards)
                    # For now, use heuristic rewards
                    r_energy = controller.nodes[next_hop].energy / controller.nodes[next_hop].initial_energy if next_hop != 'SINK' else 1.0
                    r_load = 1.0 - self.queue_lengths.get(next_hop, 0) / 10.0
                    r_link = 0.9  # Assume good link quality
                    
                    # Update Q-tables
                    old_q_e = self.q_energy.get((state, next_hop), 0.0)
                    old_q_l = self.q_load.get((state, next_hop), 0.0)
                    old_q_k = self.q_link.get((state, next_hop), 0.0)
                    
                    self.q_energy[(state, next_hop)] = old_q_e + self.alpha * (r_energy - old_q_e)
                    self.q_load[(state, next_hop)] = old_q_l + self.alpha * (r_load - old_q_l)
                    self.q_link[(state, next_hop)] = old_q_k + self.alpha * (r_link - old_q_k)
        
        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        return routing_table
