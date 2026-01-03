import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..config import SimulationConfig
    from .network import SDNController


class CNNFeatureExtractor(nn.Module):

    def __init__(self, grid_size: int = 10, num_channels: int = 4, feature_dim: int = 128):
        super(CNNFeatureExtractor, self).__init__()

        self.grid_size = grid_size
        self.num_channels = num_channels
        self.feature_dim = feature_dim

        self.conv1 = nn.Conv2d(num_channels, 32, kernel_size=3, stride=1, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)

        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)

        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1)
        self.bn3 = nn.BatchNorm2d(128)

        conv_output_size = grid_size // 4
        self.fc_input_dim = 128 * conv_output_size * conv_output_size

        self.fc1 = nn.Linear(self.fc_input_dim, 256)
        self.dropout = nn.Dropout(0.3)
        self.fc2 = nn.Linear(256, feature_dim)

        self._initialize_weights()

    def _initialize_weights(self):
        for module in self.modules():
            if isinstance(module, nn.Conv2d):
                nn.init.kaiming_normal_(module.weight, mode='fan_out', nonlinearity='relu')
                if module.bias is not None:
                    nn.init.constant_(module.bias, 0)
            elif isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.constant_(module.bias, 0)
            elif isinstance(module, nn.BatchNorm2d):
                nn.init.constant_(module.weight, 1)
                nn.init.constant_(module.bias, 0)

    def forward(self, grid_state: torch.Tensor) -> torch.Tensor:
        x = self.pool1(F.relu(self.bn1(self.conv1(grid_state))))
        x = self.pool2(F.relu(self.bn2(self.conv2(x))))
        x = F.relu(self.bn3(self.conv3(x)))

        x = x.view(x.size(0), -1)

        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        features = self.fc2(x)

        return features

    def extract_grid_representation(
        self,
        controller: 'SDNController',
        current_node_id: str,
        config: 'SimulationConfig'
    ) -> torch.Tensor:
        grid = np.zeros((self.num_channels, self.grid_size, self.grid_size), dtype=np.float32)

        cell_size = config.area_size / self.grid_size

        for node_id, node in controller.nodes.items():
            if not node.is_alive:
                continue

            grid_x = min(int(node.position.x / cell_size), self.grid_size - 1)
            grid_y = min(int(node.position.y / cell_size), self.grid_size - 1)

            grid[0, grid_y, grid_x] = node.get_residual_energy_ratio()

            if node_id != "SINK":
                grid[1, grid_y, grid_x] = min(node.transmitted_packets / 100.0, 1.0)

            grid[2, grid_y, grid_x] = 1.0 if node.is_alive else 0.0

            if node_id == current_node_id:
                grid[3, grid_y, grid_x] = 1.0
            elif node_id == "SINK":
                grid[3, grid_y, grid_x] = 0.5

        return torch.FloatTensor(grid).unsqueeze(0)


class SpatialAttention(nn.Module):

    def __init__(self, in_channels: int):
        super(SpatialAttention, self).__init__()

        self.conv1 = nn.Conv2d(in_channels, in_channels // 4, kernel_size=1)
        self.conv2 = nn.Conv2d(in_channels // 4, 1, kernel_size=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, channels, height, width = x.size()

        attention = F.relu(self.conv1(x))
        attention = torch.sigmoid(self.conv2(attention))

        return x * attention


class EnhancedCNNExtractor(nn.Module):

    def __init__(self, grid_size: int = 10, num_channels: int = 4, feature_dim: int = 128):
        super(EnhancedCNNExtractor, self).__init__()

        self.grid_size = grid_size
        self.num_channels = num_channels
        self.feature_dim = feature_dim

        self.conv1 = nn.Conv2d(num_channels, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.attention1 = SpatialAttention(32)

        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.attention2 = SpatialAttention(64)

        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.attention3 = SpatialAttention(128)

        self.global_avg_pool = nn.AdaptiveAvgPool2d(1)
        self.global_max_pool = nn.AdaptiveMaxPool2d(1)

        self.fc = nn.Sequential(
            nn.Linear(128 * 2, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, feature_dim)
        )

        self._initialize_weights()

    def _initialize_weights(self):
        for module in self.modules():
            if isinstance(module, nn.Conv2d):
                nn.init.kaiming_normal_(module.weight, mode='fan_out', nonlinearity='relu')
                if module.bias is not None:
                    nn.init.constant_(module.bias, 0)
            elif isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.constant_(module.bias, 0)
            elif isinstance(module, nn.BatchNorm2d):
                nn.init.constant_(module.weight, 1)
                nn.init.constant_(module.bias, 0)

    def forward(self, grid_state: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.bn1(self.conv1(grid_state)))
        x = self.attention1(x)
        x = F.max_pool2d(x, 2)

        x = F.relu(self.bn2(self.conv2(x)))
        x = self.attention2(x)
        x = F.max_pool2d(x, 2)

        x = F.relu(self.bn3(self.conv3(x)))
        x = self.attention3(x)

        avg_pool = self.global_avg_pool(x).view(x.size(0), -1)
        max_pool = self.global_max_pool(x).view(x.size(0), -1)

        combined = torch.cat([avg_pool, max_pool], dim=1)

        features = self.fc(combined)

        return features

    def extract_grid_representation(
        self,
        controller: 'SDNController',
        current_node_id: str,
        config: 'SimulationConfig'
    ) -> torch.Tensor:
        grid = np.zeros((self.num_channels, self.grid_size, self.grid_size), dtype=np.float32)

        cell_size = config.area_size / self.grid_size

        for node_id, node in controller.nodes.items():
            if not node.is_alive:
                continue

            grid_x = min(int(node.position.x / cell_size), self.grid_size - 1)
            grid_y = min(int(node.position.y / cell_size), self.grid_size - 1)

            grid[0, grid_y, grid_x] = max(grid[0, grid_y, grid_x], node.get_residual_energy_ratio())

            if node_id != "SINK":
                load_value = min(node.transmitted_packets / 100.0, 1.0)
                grid[1, grid_y, grid_x] = max(grid[1, grid_y, grid_x], load_value)

            grid[2, grid_y, grid_x] = 1.0

            if node_id == current_node_id:
                grid[3, grid_y, grid_x] = 1.0
            elif node_id == "SINK":
                sink = controller.get_sink_node()
                if sink:
                    sink_x = min(int(sink.position.x / cell_size), self.grid_size - 1)
                    sink_y = min(int(sink.position.y / cell_size), self.grid_size - 1)
                    grid[3, sink_y, sink_x] = 0.8

        return torch.FloatTensor(grid).unsqueeze(0)
