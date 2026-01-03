import random
import numpy as np
import networkx as nx
import torch
from typing import Dict, List, TYPE_CHECKING

from .base import RoutingAlgorithm
from ..models.drl_agent import DRLRoutingAgent
from ..models.cnn_feature_extractor import EnhancedCNNExtractor

if TYPE_CHECKING:
    from ..config import SimulationConfig
    from ..models.network import SDNController


class CDRLAdvancedRouting(RoutingAlgorithm):

    def __init__(self, config: 'SimulationConfig', use_cnn: bool = True):
        self.config = config
        self.use_cnn = use_cnn
        self.agent = DRLRoutingAgent(config)

        if use_cnn:
            self.cnn_extractor = EnhancedCNNExtractor(
                grid_size=10,
                num_channels=4,
                feature_dim=config.state_dim
            ).to(config.device)

            self.cnn_optimizer = torch.optim.Adam(
                self.cnn_extractor.parameters(),
                lr=config.learning_rate
            )

        self.is_trained = False
        self.training_episodes_completed = 0
        self.training_rewards = []
        self.training_losses = []

        self.cooperation_weights = np.ones(config.num_nodes) / config.num_nodes

    @property
    def algorithm_name(self) -> str:
        return "CDRL-Advanced" if self.use_cnn else "CDRL-Basic"

    def get_description(self) -> str:
        if self.use_cnn:
            return "CDRL with CNN feature extraction and multi-layer cooperation"
        return "CDRL with standard feature extraction"

    def extract_features(
        self,
        controller: 'SDNController',
        current_node_id: str
    ) -> np.ndarray:
        if self.use_cnn:
            grid_repr = self.cnn_extractor.extract_grid_representation(
                controller, current_node_id, self.config
            ).to(self.config.device)

            self.cnn_extractor.eval()
            with torch.no_grad():
                features = self.cnn_extractor(grid_repr)
            features_np = features.cpu().numpy().flatten()

            if len(features_np) < self.config.state_dim:
                features_np = np.pad(features_np, (0, self.config.state_dim - len(features_np)))
            elif len(features_np) > self.config.state_dim:
                features_np = features_np[:self.config.state_dim]

            return features_np.astype(np.float32)
        else:
            return self.agent.extract_state_features(controller, current_node_id)

    def compute_cooperation_reward(
        self,
        controller: 'SDNController',
        node_id: str,
        neighbor_id: str
    ) -> float:
        node = controller.nodes[node_id]
        neighbor = controller.nodes[neighbor_id]

        energy_similarity = 1.0 - abs(
            node.get_residual_energy_ratio() - neighbor.get_residual_energy_ratio()
        )

        load_similarity = 1.0 - abs(
            min(node.transmitted_packets / 100.0, 1.0) -
            min(neighbor.transmitted_packets / 100.0, 1.0)
        )

        cooperation_score = 0.6 * energy_similarity + 0.4 * load_similarity

        return cooperation_score * 5.0

    def train(self, controller: 'SDNController', verbose: bool = True):
        if verbose:
            print("\n" + "="*80)
            print(" CDRL-ADVANCED TRAINING ".center(80))
            print("="*80)
            print(f"Training episodes: {self.config.training_episodes}")
            print(f"Feature extraction: {'CNN-based' if self.use_cnn else 'Standard'}")
            print(f"State dimension: {self.config.state_dim}")
            print(f"Device: {self.config.device}")
            print("-"*80)

        for episode in range(self.config.training_episodes):
            episode_reward = 0.0
            episode_loss = 0.0
            steps_taken = 0

            active_sensors = controller.get_active_sensors()
            if len(active_sensors) < 2:
                continue

            source = random.choice(active_sensors)
            current = source
            visited = {current}

            for step in range(20):
                state = self.extract_features(controller, current)
                node = controller.nodes[current]
                sink = controller.get_sink_node()

                if sink is None:
                    break

                if "SINK" in node.neighbors:
                    reward = 150.0
                    self.agent.replay_buffer.store(state, 0, reward, state, 1.0)
                    episode_reward += reward
                    break

                valid_neighbors = [
                    n for n in node.neighbors
                    if controller.nodes[n].is_alive and n not in visited
                ]

                valid_neighbors = sorted(
                    valid_neighbors,
                    key=lambda n: controller.nodes[n].position.distance_to(sink.position)
                )[:6]

                if not valid_neighbors:
                    reward = -80.0
                    self.agent.replay_buffer.store(state, 0, reward, state, 1.0)
                    episode_reward += reward
                    break

                action = self.agent.select_action(state, len(valid_neighbors), training=True)
                action = min(action, len(valid_neighbors) - 1)
                next_node_id = valid_neighbors[action]
                next_node = controller.nodes[next_node_id]

                current_distance = node.position.distance_to(sink.position)
                next_distance = next_node.position.distance_to(sink.position)

                distance_reward = (current_distance - next_distance) * 8.0

                energy_reward = next_node.get_residual_energy_ratio() * 15.0

                if next_node.get_residual_energy_ratio() < 0.2:
                    energy_reward -= 20.0

                load_penalty = -next_node.get_load_factor() * 8.0

                cooperation_reward = self.compute_cooperation_reward(
                    controller, current, next_node_id
                )

                hop_penalty = -1.0

                reward = (distance_reward + energy_reward + load_penalty +
                         cooperation_reward + hop_penalty)
                episode_reward += reward

                next_state = self.extract_features(controller, next_node_id)

                self.agent.replay_buffer.store(state, action, reward, next_state, 0.0)

                loss = self.agent.train_step()
                episode_loss += loss
                steps_taken += 1

                visited.add(next_node_id)
                current = next_node_id

            if episode % self.config.target_update_freq == 0:
                self.agent.synchronize_networks()

            self.training_rewards.append(episode_reward)
            avg_loss = episode_loss / max(steps_taken, 1)
            self.training_losses.append(avg_loss)
            self.training_episodes_completed = episode + 1

            if verbose and episode % 50 == 0:
                recent_rewards = self.training_rewards[-50:] if self.training_rewards else [0]
                recent_losses = self.training_losses[-50:] if self.training_losses else [0]
                avg_reward = np.mean(recent_rewards)
                avg_loss_display = np.mean(recent_losses)

                print(f"Episode {episode:4d}/{self.config.training_episodes}: "
                      f"Epsilon={self.agent.epsilon:.4f}, "
                      f"Avg Reward={avg_reward:8.2f}, "
                      f"Avg Loss={avg_loss_display:.6f}, "
                      f"Buffer={len(self.agent.replay_buffer)}")

        self.is_trained = True

        if verbose:
            print("-"*80)
            print(f"Training completed!")
            print(f"Final epsilon: {self.agent.epsilon:.4f}")
            print(f"Total training steps: {self.agent.training_steps}")
            print(f"Average reward: {np.mean(self.training_rewards):.2f}")
            print(f"Average loss: {np.mean(self.training_losses):.6f}")
            print("="*80 + "\n")

    def compute_routing_table(self, controller: 'SDNController') -> Dict[str, str]:
        routes = {}
        active_sensors = controller.get_active_sensors()
        sink = controller.get_sink_node()

        if not active_sensors or sink is None:
            return routes

        energy_levels = [
            controller.nodes[n].get_residual_energy_ratio()
            for n in active_sensors
        ]
        average_energy = np.mean(energy_levels)
        minimum_energy = np.min(energy_levels)

        load_distribution = {
            n: controller.nodes[n].transmitted_packets
            for n in active_sensors
        }
        maximum_load = max(load_distribution.values()) if load_distribution else 1

        if minimum_energy < 0.15:
            w_energy, w_distance, w_load, w_coop = 0.60, 0.20, 0.10, 0.10
            network_state = "CRITICAL"
        elif minimum_energy < 0.30:
            w_energy, w_distance, w_load, w_coop = 0.50, 0.25, 0.15, 0.10
            network_state = "WARNING"
        elif average_energy < 0.50:
            w_energy, w_distance, w_load, w_coop = 0.40, 0.30, 0.20, 0.10
            network_state = "MODERATE"
        else:
            w_energy, w_distance, w_load, w_coop = 0.30, 0.40, 0.20, 0.10
            network_state = "HEALTHY"

        routing_graph = nx.Graph()

        for node_id in [n for n in controller.network_graph.nodes()
                       if controller.nodes[n].is_alive]:
            routing_graph.add_node(node_id)

        for u, v in controller.network_graph.edges():
            if u not in routing_graph.nodes() or v not in routing_graph.nodes():
                continue

            distance = controller.network_graph[u][v]['weight']
            energy_u = controller.nodes[u].get_residual_energy_ratio()
            energy_v = controller.nodes[v].get_residual_energy_ratio()
            min_edge_energy = min(energy_u, energy_v)

            energy_cost = 1.0 - min_edge_energy

            if min_edge_energy < 0.10:
                energy_cost += 1.5
            elif min_edge_energy < 0.20:
                energy_cost += 0.8

            distance_cost = distance / controller.config.comm_range

            load_u = load_distribution.get(u, 0) / max(maximum_load, 1)
            load_v = load_distribution.get(v, 0) / max(maximum_load, 1)
            load_cost = (load_u + load_v) / 2.0

            cooperation_score = self.compute_cooperation_reward(controller, u, v)
            cooperation_cost = 1.0 - (cooperation_score / 10.0)

            health_bonus = 0.0
            if min_edge_energy > average_energy:
                health_bonus = -0.20
            elif min_edge_energy > average_energy * 1.2:
                health_bonus = -0.35

            total_cost = (
                w_energy * energy_cost +
                w_distance * distance_cost +
                w_load * load_cost +
                w_coop * cooperation_cost +
                health_bonus
            )

            routing_graph.add_edge(u, v, weight=max(0.001, total_cost))

        for source in active_sensors:
            if source == "SINK":
                continue

            try:
                path = nx.shortest_path(
                    routing_graph,
                    source=source,
                    target="SINK",
                    weight='weight'
                )

                if len(path) > 1:
                    routes[source] = path[1]

            except nx.NetworkXNoPath:
                node = controller.nodes[source]
                valid_neighbors = [
                    n for n in node.neighbors
                    if controller.nodes[n].is_alive
                ]

                if "SINK" in valid_neighbors:
                    routes[source] = "SINK"
                elif valid_neighbors:
                    routes[source] = min(
                        valid_neighbors,
                        key=lambda n: controller.nodes[n].position.distance_to(sink.position)
                    )

        return routes

    def get_training_statistics(self) -> dict:
        return {
            'is_trained': self.is_trained,
            'episodes_completed': self.training_episodes_completed,
            'final_epsilon': self.agent.epsilon,
            'training_steps': self.agent.training_steps,
            'average_loss': self.agent.get_average_loss(),
            'buffer_size': len(self.agent.replay_buffer),
            'average_reward': np.mean(self.training_rewards) if self.training_rewards else 0.0,
            'total_reward': sum(self.training_rewards),
            'feature_extraction': 'CNN-based' if self.use_cnn else 'Standard',
            'cooperation_enabled': True
        }
