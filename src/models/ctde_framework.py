import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from collections import deque
from typing import List, Tuple, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from ..config import SimulationConfig
    from .network import SDNController


class CentralizedCritic(nn.Module):

    def __init__(self, global_state_dim: int, num_agents: int, action_dim: int, hidden_dim: int = 256):
        super(CentralizedCritic, self).__init__()

        total_input_dim = global_state_dim + num_agents * action_dim

        self.network = nn.Sequential(
            nn.Linear(total_input_dim, hidden_dim),
            nn.ReLU(),
            nn.LayerNorm(hidden_dim),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.LayerNorm(hidden_dim),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, 1)
        )

        self._initialize_weights()

    def _initialize_weights(self):
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.orthogonal_(module.weight, gain=np.sqrt(2))
                if module.bias is not None:
                    nn.init.constant_(module.bias, 0.0)

    def forward(self, global_state: torch.Tensor, all_actions: torch.Tensor) -> torch.Tensor:
        x = torch.cat([global_state, all_actions], dim=-1)
        return self.network(x)


class DecentralizedActor(nn.Module):

    def __init__(self, local_state_dim: int, action_dim: int, hidden_dim: int = 128):
        super(DecentralizedActor, self).__init__()

        self.network = nn.Sequential(
            nn.Linear(local_state_dim, hidden_dim),
            nn.ReLU(),
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, action_dim)
        )

        self._initialize_weights()

    def _initialize_weights(self):
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.constant_(module.bias, 0.0)

    def forward(self, local_state: torch.Tensor) -> torch.Tensor:
        return self.network(local_state)

    def get_action(self, local_state: torch.Tensor, epsilon: float = 0.0) -> int:
        if np.random.random() < epsilon:
            return np.random.randint(0, self.network[-1].out_features)

        with torch.no_grad():
            q_values = self.forward(local_state)
            return int(torch.argmax(q_values).item())


class MultiAgentReplayBuffer:

    def __init__(self, capacity: int, num_agents: int):
        self.buffer = deque(maxlen=capacity)
        self.num_agents = num_agents

    def store(
        self,
        global_state: np.ndarray,
        local_states: List[np.ndarray],
        actions: List[int],
        rewards: List[float],
        next_global_state: np.ndarray,
        next_local_states: List[np.ndarray],
        dones: List[float]
    ):
        self.buffer.append((
            global_state,
            local_states,
            actions,
            rewards,
            next_global_state,
            next_local_states,
            dones
        ))

    def sample_batch(self, batch_size: int) -> Tuple:
        import random
        batch = random.sample(self.buffer, batch_size)

        global_states = np.array([exp[0] for exp in batch], dtype=np.float32)
        local_states = [np.array([exp[1][i] for exp in batch], dtype=np.float32)
                       for i in range(self.num_agents)]
        actions = [np.array([exp[2][i] for exp in batch], dtype=np.int64)
                  for i in range(self.num_agents)]
        rewards = [np.array([exp[3][i] for exp in batch], dtype=np.float32)
                  for i in range(self.num_agents)]
        next_global_states = np.array([exp[4] for exp in batch], dtype=np.float32)
        next_local_states = [np.array([exp[5][i] for exp in batch], dtype=np.float32)
                            for i in range(self.num_agents)]
        dones = [np.array([exp[6][i] for exp in batch], dtype=np.float32)
                for i in range(self.num_agents)]

        return (global_states, local_states, actions, rewards,
                next_global_states, next_local_states, dones)

    def __len__(self) -> int:
        return len(self.buffer)


class CTDEFramework:

    def __init__(
        self,
        config: 'SimulationConfig',
        num_agents: int,
        local_state_dim: int,
        global_state_dim: int,
        action_dim: int
    ):
        self.config = config
        self.num_agents = num_agents
        self.local_state_dim = local_state_dim
        self.global_state_dim = global_state_dim
        self.action_dim = action_dim

        self.actors = [
            DecentralizedActor(local_state_dim, action_dim, config.hidden_dim).to(config.device)
            for _ in range(num_agents)
        ]

        self.centralized_critic = CentralizedCritic(
            global_state_dim, num_agents, action_dim, config.hidden_dim * 2
        ).to(config.device)

        self.target_critic = CentralizedCritic(
            global_state_dim, num_agents, action_dim, config.hidden_dim * 2
        ).to(config.device)
        self.target_critic.load_state_dict(self.centralized_critic.state_dict())
        self.target_critic.eval()

        self.actor_optimizers = [
            optim.Adam(actor.parameters(), lr=config.learning_rate)
            for actor in self.actors
        ]

        self.critic_optimizer = optim.Adam(
            self.centralized_critic.parameters(),
            lr=config.learning_rate * 2
        )

        self.replay_buffer = MultiAgentReplayBuffer(config.buffer_size, num_agents)

        self.epsilon = config.epsilon_start
        self.training_steps = 0

    def select_actions(
        self,
        local_states: List[np.ndarray],
        training: bool = True
    ) -> List[int]:
        actions = []
        epsilon = self.epsilon if training else 0.0

        for i, (actor, local_state) in enumerate(zip(self.actors, local_states)):
            state_tensor = torch.FloatTensor(local_state).unsqueeze(0).to(self.config.device)
            action = actor.get_action(state_tensor, epsilon)
            actions.append(action)

        return actions

    def train_step(self) -> Tuple[float, float]:
        if len(self.replay_buffer) < self.config.batch_size:
            return 0.0, 0.0

        (global_states, local_states, actions, rewards,
         next_global_states, next_local_states, dones) = \
            self.replay_buffer.sample_batch(self.config.batch_size)

        global_states_t = torch.FloatTensor(global_states).to(self.config.device)
        next_global_states_t = torch.FloatTensor(next_global_states).to(self.config.device)

        current_actions_t = []
        for i in range(self.num_agents):
            actions_t = torch.LongTensor(actions[i]).to(self.config.device)
            actions_one_hot = F.one_hot(actions_t, num_classes=self.action_dim).float()
            current_actions_t.append(actions_one_hot)
        current_actions_concat = torch.cat(current_actions_t, dim=1)

        current_q = self.centralized_critic(global_states_t, current_actions_concat)

        with torch.no_grad():
            next_actions_t = []
            for i in range(self.num_agents):
                local_state_t = torch.FloatTensor(next_local_states[i]).to(self.config.device)
                next_q = self.actors[i](local_state_t)
                next_action = torch.argmax(next_q, dim=1)
                next_action_one_hot = F.one_hot(next_action, num_classes=self.action_dim).float()
                next_actions_t.append(next_action_one_hot)
            next_actions_concat = torch.cat(next_actions_t, dim=1)

            next_q = self.target_critic(next_global_states_t, next_actions_concat)

            team_reward = torch.FloatTensor([
                sum(rewards[i][j] for i in range(self.num_agents))
                for j in range(self.config.batch_size)
            ]).unsqueeze(1).to(self.config.device)

            team_done = torch.FloatTensor([
                max(dones[i][j] for i in range(self.num_agents))
                for j in range(self.config.batch_size)
            ]).unsqueeze(1).to(self.config.device)

            target_q = team_reward + self.config.gamma * next_q * (1 - team_done)

        critic_loss = F.mse_loss(current_q, target_q)

        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.centralized_critic.parameters(), 1.0)
        self.critic_optimizer.step()

        total_actor_loss = 0.0

        for i in range(self.num_agents):
            local_state_t = torch.FloatTensor(local_states[i]).to(self.config.device)

            predicted_q = self.actors[i](local_state_t)
            predicted_actions = F.gumbel_softmax(predicted_q, tau=1.0, hard=False)

            all_actions_list = []
            for j in range(self.num_agents):
                if j == i:
                    all_actions_list.append(predicted_actions)
                else:
                    actions_t = torch.LongTensor(actions[j]).to(self.config.device)
                    actions_one_hot = F.one_hot(actions_t, num_classes=self.action_dim).float()
                    all_actions_list.append(actions_one_hot)

            all_actions_concat = torch.cat(all_actions_list, dim=1)

            actor_q = self.centralized_critic(global_states_t, all_actions_concat)

            actor_loss = -actor_q.mean()

            self.actor_optimizers[i].zero_grad()
            actor_loss.backward()
            torch.nn.utils.clip_grad_norm_(self.actors[i].parameters(), 1.0)
            self.actor_optimizers[i].step()

            total_actor_loss += actor_loss.item()

        self.training_steps += 1

        if self.epsilon > self.config.epsilon_min:
            self.epsilon *= self.config.epsilon_decay

        if self.training_steps % self.config.target_update_freq == 0:
            self.target_critic.load_state_dict(self.centralized_critic.state_dict())

        return critic_loss.item(), total_actor_loss / self.num_agents

    def save_models(self, filepath_prefix: str):
        for i, actor in enumerate(self.actors):
            torch.save(actor.state_dict(), f"{filepath_prefix}_actor_{i}.pth")

        torch.save(self.centralized_critic.state_dict(), f"{filepath_prefix}_critic.pth")

        torch.save({
            'epsilon': self.epsilon,
            'training_steps': self.training_steps
        }, f"{filepath_prefix}_training_state.pth")

    def load_models(self, filepath_prefix: str):
        for i, actor in enumerate(self.actors):
            actor.load_state_dict(
                torch.load(f"{filepath_prefix}_actor_{i}.pth", map_location=self.config.device)
            )

        self.centralized_critic.load_state_dict(
            torch.load(f"{filepath_prefix}_critic.pth", map_location=self.config.device)
        )

        training_state = torch.load(
            f"{filepath_prefix}_training_state.pth",
            map_location=self.config.device
        )
        self.epsilon = training_state['epsilon']
        self.training_steps = training_state['training_steps']

        self.target_critic.load_state_dict(self.centralized_critic.state_dict())
