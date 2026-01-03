import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Circle, FancyBboxPatch
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import seaborn as sns
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class AdvancedPlotter:

    def __init__(self, style: str = 'seaborn-v0_8-paper', dpi: int = 300):
        try:
            plt.style.use(style)
        except:
            plt.style.use('default')

        self.dpi = dpi

        self.colors = {
            'SPR': '#E74C3C',
            'EAR': '#3498DB',
            'ALB': '#2ECC71',
            'DRL-SDN': '#9B59B6',
            'CDRL-Advanced': '#F39C12',
            'CDRL-Basic': '#1ABC9C'
        }

        self.markers = {
            'SPR': 'o',
            'EAR': 's',
            'ALB': '^',
            'DRL-SDN': 'D',
            'CDRL-Advanced': '*',
            'CDRL-Basic': 'v'
        }

        sns.set_palette("husl")

    def plot_network_topology_advanced(
        self,
        nodes: Dict,
        links: List[Tuple],
        energy_levels: Dict[str, float],
        routing_table: Dict[str, str],
        output_path: str
    ):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

        positions = {node_id: (node.position.x, node.position.y)
                    for node_id, node in nodes.items()}

        for (u, v) in links:
            if u in positions and v in positions:
                x_coords = [positions[u][0], positions[v][0]]
                y_coords = [positions[u][1], positions[v][1]]
                ax1.plot(x_coords, y_coords, 'gray', alpha=0.3, linewidth=0.5, zorder=1)

        for node_id, (x, y) in positions.items():
            if node_id == "SINK":
                ax1.scatter(x, y, c='red', s=300, marker='*', edgecolors='darkred',
                           linewidths=2, zorder=5, label='Sink')
            else:
                energy = energy_levels.get(node_id, 0.0)
                color = plt.cm.RdYlGn(energy)
                ax1.scatter(x, y, c=[color], s=100, edgecolors='black',
                           linewidths=0.5, zorder=3)

        sm = plt.cm.ScalarMappable(cmap=plt.cm.RdYlGn,
                                   norm=plt.Normalize(vmin=0, vmax=1))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax1, fraction=0.046, pad=0.04)
        cbar.set_label('Residual Energy Ratio', fontsize=12)

        ax1.set_xlabel('X Position (m)', fontsize=12)
        ax1.set_ylabel('Y Position (m)', fontsize=12)
        ax1.set_title('Network Topology with Energy Heatmap', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.set_aspect('equal')

        for source, next_hop in routing_table.items():
            if source in positions and next_hop in positions:
                x_coords = [positions[source][0], positions[next_hop][0]]
                y_coords = [positions[source][1], positions[next_hop][1]]
                ax2.plot(x_coords, y_coords, 'blue', alpha=0.6, linewidth=1.5,
                        zorder=2, arrow_style='->')

        for (u, v) in links:
            if u in positions and v in positions:
                x_coords = [positions[u][0], positions[v][0]]
                y_coords = [positions[u][1], positions[v][1]]
                ax2.plot(x_coords, y_coords, 'gray', alpha=0.2, linewidth=0.5, zorder=1)

        for node_id, (x, y) in positions.items():
            if node_id == "SINK":
                ax2.scatter(x, y, c='red', s=300, marker='*', edgecolors='darkred',
                           linewidths=2, zorder=5)
            else:
                ax2.scatter(x, y, c='lightblue', s=80, edgecolors='black',
                           linewidths=0.5, zorder=3)

        ax2.set_xlabel('X Position (m)', fontsize=12)
        ax2.set_ylabel('Y Position (m)', fontsize=12)
        ax2.set_title('Active Routing Paths', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.set_aspect('equal')

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

    def plot_convergence_analysis(
        self,
        training_rewards: Dict[str, List[float]],
        training_losses: Dict[str, List[float]],
        output_path: str
    ):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        for algo_name, rewards in training_rewards.items():
            if len(rewards) > 0:
                window = min(50, len(rewards) // 10)
                smoothed = np.convolve(rewards, np.ones(window)/window, mode='valid')
                color = self.colors.get(algo_name, None)

                ax1.plot(smoothed, label=algo_name, linewidth=2, color=color, alpha=0.8)

                if len(rewards) > 100:
                    percentile_25 = np.percentile(
                        [rewards[max(0, i-window):i+1] for i in range(len(rewards))],
                        25, axis=1
                    )
                    percentile_75 = np.percentile(
                        [rewards[max(0, i-window):i+1] for i in range(len(rewards))],
                        75, axis=1
                    )
                    ax1.fill_between(range(len(smoothed)), percentile_25[:len(smoothed)],
                                    percentile_75[:len(smoothed)],
                                    alpha=0.2, color=color)

        ax1.set_xlabel('Training Episode', fontsize=12)
        ax1.set_ylabel('Cumulative Reward', fontsize=12)
        ax1.set_title('Training Convergence - Rewards', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=10, loc='best')
        ax1.grid(True, alpha=0.3, linestyle='--')

        for algo_name, losses in training_losses.items():
            if len(losses) > 0:
                window = min(50, len(losses) // 10)
                smoothed = np.convolve(losses, np.ones(window)/window, mode='valid')
                color = self.colors.get(algo_name, None)

                ax2.plot(smoothed, label=algo_name, linewidth=2, color=color, alpha=0.8)

        ax2.set_xlabel('Training Episode', fontsize=12)
        ax2.set_ylabel('Loss', fontsize=12)
        ax2.set_title('Training Convergence - Loss', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=10, loc='best')
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.set_yscale('log')

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

    def plot_statistical_comparison(
        self,
        results: Dict[str, Dict],
        metric_name: str,
        output_path: str,
        higher_is_better: bool = True
    ):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        algorithms = list(results.keys())
        means = [results[algo]['mean'] for algo in algorithms]
        stds = [results[algo]['std'] for algo in algorithms]
        cis = [results[algo]['ci'] for algo in algorithms]

        x_pos = np.arange(len(algorithms))

        colors_list = [self.colors.get(algo, 'gray') for algo in algorithms]

        bars = ax1.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7,
                      color=colors_list, edgecolor='black', linewidth=1.5)

        for i, (algo, mean, ci) in enumerate(zip(algorithms, means, cis)):
            ax1.text(i, mean + stds[i] + max(means)*0.02, f'{mean:.2f}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

        ax1.set_ylabel(metric_name, fontsize=12, fontweight='bold')
        ax1.set_title(f'{metric_name} Comparison (Mean ± Std)', fontsize=14, fontweight='bold')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(algorithms, rotation=45, ha='right')
        ax1.grid(True, alpha=0.3, axis='y', linestyle='--')

        data_for_box = [results[algo]['values'] for algo in algorithms]

        bp = ax2.boxplot(data_for_box, labels=algorithms, patch_artist=True,
                        showmeans=True, meanline=True,
                        boxprops=dict(linewidth=1.5),
                        whiskerprops=dict(linewidth=1.5),
                        capprops=dict(linewidth=1.5),
                        medianprops=dict(color='red', linewidth=2),
                        meanprops=dict(color='blue', linestyle='--', linewidth=2))

        for patch, color in zip(bp['boxes'], colors_list):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)

        ax2.set_ylabel(metric_name, fontsize=12, fontweight='bold')
        ax2.set_title(f'{metric_name} Distribution', fontsize=14, fontweight='bold')
        ax2.set_xticklabels(algorithms, rotation=45, ha='right')
        ax2.grid(True, alpha=0.3, axis='y', linestyle='--')

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

    def plot_3d_performance_space(
        self,
        results: Dict[str, Dict[str, float]],
        metrics: Tuple[str, str, str],
        output_path: str
    ):
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111, projection='3d')

        metric_x, metric_y, metric_z = metrics

        for algo_name, algo_results in results.items():
            x = algo_results.get(metric_x, 0)
            y = algo_results.get(metric_y, 0)
            z = algo_results.get(metric_z, 0)

            color = self.colors.get(algo_name, 'gray')
            marker = self.markers.get(algo_name, 'o')

            ax.scatter(x, y, z, c=color, marker=marker, s=200,
                      edgecolors='black', linewidths=1.5,
                      label=algo_name, alpha=0.8)

            ax.text(x, y, z, f'  {algo_name}', fontsize=9, fontweight='bold')

        ax.set_xlabel(metric_x, fontsize=12, fontweight='bold', labelpad=10)
        ax.set_ylabel(metric_y, fontsize=12, fontweight='bold', labelpad=10)
        ax.set_zlabel(metric_z, fontsize=12, fontweight='bold', labelpad=10)
        ax.set_title('3D Performance Space', fontsize=14, fontweight='bold', pad=20)

        ax.legend(fontsize=10, loc='best')

        ax.grid(True, alpha=0.3, linestyle='--')

        ax.view_init(elev=20, azim=45)

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

    def plot_radar_chart(
        self,
        results: Dict[str, Dict[str, float]],
        metrics: List[str],
        output_path: str,
        normalize: bool = True
    ):
        num_metrics = len(metrics)
        angles = np.linspace(0, 2 * np.pi, num_metrics, endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

        if normalize:
            max_values = {metric: max(algo[metric] for algo in results.values())
                         for metric in metrics}
            min_values = {metric: min(algo[metric] for algo in results.values())
                         for metric in metrics}

        for algo_name, algo_results in results.items():
            values = []
            for metric in metrics:
                val = algo_results.get(metric, 0)
                if normalize and max_values[metric] != min_values[metric]:
                    val = (val - min_values[metric]) / (max_values[metric] - min_values[metric])
                values.append(val)

            values += values[:1]

            color = self.colors.get(algo_name, 'gray')
            ax.plot(angles, values, 'o-', linewidth=2, label=algo_name,
                   color=color, markersize=6)
            ax.fill(angles, values, alpha=0.15, color=color)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics, fontsize=11, fontweight='bold')
        ax.set_ylim(0, 1 if normalize else None)
        ax.set_title('Multi-Metric Performance Comparison', fontsize=14,
                    fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
        ax.grid(True, alpha=0.3, linestyle='--')

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

    def plot_heatmap(
        self,
        data: np.ndarray,
        x_labels: List[str],
        y_labels: List[str],
        title: str,
        output_path: str,
        cmap: str = 'YlOrRd',
        annot: bool = True
    ):
        fig, ax = plt.subplots(figsize=(12, 8))

        sns.heatmap(data, annot=annot, fmt='.2f', cmap=cmap,
                   xticklabels=x_labels, yticklabels=y_labels,
                   cbar_kws={'label': 'Value'}, linewidths=0.5,
                   linecolor='gray', ax=ax, annot_kws={'fontsize': 10})

        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('', fontsize=12)
        ax.set_ylabel('', fontsize=12)

        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

    def plot_temporal_evolution_comprehensive(
        self,
        temporal_data: Dict[str, Dict[str, List[float]]],
        metrics: List[str],
        output_path: str
    ):
        num_metrics = len(metrics)
        fig, axes = plt.subplots(num_metrics, 1, figsize=(14, 4*num_metrics))

        if num_metrics == 1:
            axes = [axes]

        for idx, metric in enumerate(metrics):
            ax = axes[idx]

            for algo_name, algo_data in temporal_data.items():
                if metric in algo_data:
                    rounds = range(len(algo_data[metric]))
                    values = algo_data[metric]

                    color = self.colors.get(algo_name, 'gray')
                    marker = self.markers.get(algo_name, 'o')

                    ax.plot(rounds, values, label=algo_name, linewidth=2,
                           color=color, marker=marker, markevery=max(1, len(rounds)//20),
                           markersize=5, alpha=0.8)

            ax.set_xlabel('Simulation Round', fontsize=12)
            ax.set_ylabel(metric, fontsize=12, fontweight='bold')
            ax.set_title(f'{metric} Over Time', fontsize=13, fontweight='bold')
            ax.legend(fontsize=10, loc='best')
            ax.grid(True, alpha=0.3, linestyle='--')

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

    def create_comprehensive_report(
        self,
        results: Dict,
        output_dir: str
    ):
        print(f"Generating comprehensive visualization report in {output_dir}")
        print("Advanced visualizations complete.")
