"""
Visualization module for simulation results.

This module provides comprehensive plotting capabilities for analyzing
and presenting WSN routing algorithm performance.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from typing import Dict, List, Optional
from pathlib import Path


class ResultsPlotter:
    """
    Comprehensive visualization for simulation results.

    Provides methods to generate:
    - Network topology visualization
    - Performance comparison charts
    - Temporal evolution plots
    - Statistical analysis plots
    """

    def __init__(self, output_dir: str = "results", dpi: int = 300):
        """
        Initialize results plotter.

        Args:
            output_dir: Directory to save plots
            dpi: DPI for saved figures
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi

        # Set default style
        plt.style.use('seaborn-v0_8-darkgrid')
        self.colors = {
            'SPR': '#FF6B6B',      # Red
            'EAR': '#4ECDC4',      # Teal
            'ALB': '#95E1D3',      # Light teal
            'DRL-SDN': '#2E86AB'   # Blue
        }

    def plot_network_topology(
        self,
        controller,
        filename: str = "network_topology.png",
        show_labels: bool = False
    ):
        """
        Plot network topology showing nodes and links.

        Args:
            controller: SDN controller with network state
            filename: Output filename
            show_labels: Whether to show node labels
        """
        fig, ax = plt.subplots(figsize=(12, 12))

        # Plot links
        for u, v in controller.network_graph.edges():
            node_u = controller.nodes[u]
            node_v = controller.nodes[v]

            x = [node_u.position.x, node_v.position.x]
            y = [node_u.position.y, node_v.position.y]

            ax.plot(x, y, 'gray', alpha=0.3, linewidth=0.5, zorder=1)

        # Plot nodes
        for node_id, node in controller.nodes.items():
            if node.is_sink:
                # Sink node
                ax.scatter(
                    node.position.x, node.position.y,
                    c='red', s=500, marker='s',
                    edgecolors='black', linewidths=2,
                    zorder=3, label='Sink'
                )
            elif node.is_alive:
                # Active sensor
                energy_ratio = node.get_residual_energy_ratio()
                color = plt.cm.RdYlGn(energy_ratio)  # Color by energy

                ax.scatter(
                    node.position.x, node.position.y,
                    c=[color], s=100, marker='o',
                    edgecolors='black', linewidths=0.5,
                    zorder=2
                )
            else:
                # Dead sensor
                ax.scatter(
                    node.position.x, node.position.y,
                    c='gray', s=50, marker='x',
                    alpha=0.5, zorder=2
                )

            # Node labels
            if show_labels and not node.is_sink:
                ax.text(
                    node.position.x, node.position.y + 2,
                    node_id, fontsize=6,
                    ha='center', va='bottom'
                )

        # Colorbar for energy
        sm = plt.cm.ScalarMappable(
            cmap=plt.cm.RdYlGn,
            norm=plt.Normalize(vmin=0, vmax=1)
        )
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Residual Energy Ratio', rotation=270, labelpad=20)

        ax.set_xlabel('X Position (m)', fontsize=12)
        ax.set_ylabel('Y Position (m)', fontsize=12)
        ax.set_title('Wireless Sensor Network Topology', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=self.dpi, bbox_inches='tight')
        plt.close()

    def plot_comparative_metrics(
        self,
        results: Dict[str, Dict],
        filename: str = "comparative_metrics.png"
    ):
        """
        Plot comprehensive comparison of all algorithms.

        Args:
            results: Dictionary mapping algorithm names to their results
            filename: Output filename
        """
        fig, axes = plt.subplots(2, 4, figsize=(20, 10))
        axes = axes.flatten()

        algorithms = list(results.keys())
        colors = [self.colors.get(alg, '#333333') for alg in algorithms]

        # 1. Network Lifetime
        ax = axes[0]
        lifetimes = [results[alg]['network_lifetime'] for alg in algorithms]
        bars = ax.bar(algorithms, lifetimes, color=colors, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('Rounds', fontsize=10)
        ax.set_title('Network Lifetime', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom', fontsize=9)

        # 2. First Node Death (FND)
        ax = axes[1]
        fnds = [results[alg]['first_node_death'] for alg in algorithms]
        bars = ax.bar(algorithms, fnds, color=colors, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('Rounds', fontsize=10)
        ax.set_title('First Node Death (FND)', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom', fontsize=9)

        # 3. Half Node Death (HND)
        ax = axes[2]
        hnds = [results[alg]['half_node_death'] for alg in algorithms]
        bars = ax.bar(algorithms, hnds, color=colors, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('Rounds', fontsize=10)
        ax.set_title('Half Nodes Death (HND)', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom', fontsize=9)

        # 4. Packet Delivery Ratio
        ax = axes[3]
        pdrs = [results[alg]['final_pdr'] for alg in algorithms]
        bars = ax.bar(algorithms, pdrs, color=colors, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('PDR (%)', fontsize=10)
        ax.set_title('Packet Delivery Ratio', fontsize=11, fontweight='bold')
        ax.set_ylim([0, 105])
        ax.grid(True, alpha=0.3, axis='y')
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%', ha='center', va='bottom', fontsize=9)

        # 5. Average Hop Count
        ax = axes[4]
        hops = [results[alg]['average_hop_count'] for alg in algorithms]
        bars = ax.bar(algorithms, hops, color=colors, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('Hops', fontsize=10)
        ax.set_title('Average Hop Count', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}', ha='center', va='bottom', fontsize=9)

        # 6. Energy Efficiency
        ax = axes[5]
        efficiencies = [results[alg]['energy_efficiency'] for alg in algorithms]
        bars = ax.bar(algorithms, efficiencies, color=colors, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('Packets/Joule', fontsize=10)
        ax.set_title('Energy Efficiency', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}', ha='center', va='bottom', fontsize=9)

        # 7. Average Latency
        ax = axes[6]
        latencies = [results[alg]['average_latency'] for alg in algorithms]
        bars = ax.bar(algorithms, latencies, color=colors, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('Hops', fontsize=10)
        ax.set_title('Average Latency', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}', ha='center', va='bottom', fontsize=9)

        # 8. Fairness Index
        ax = axes[7]
        fairness = [results[alg]['average_fairness'] for alg in algorithms]
        bars = ax.bar(algorithms, fairness, color=colors, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('Jain\'s Index', fontsize=10)
        ax.set_title('Fairness Index', fontsize=11, fontweight='bold')
        ax.set_ylim([0, 1.05])
        ax.grid(True, alpha=0.3, axis='y')
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}', ha='center', va='bottom', fontsize=9)

        plt.suptitle('Routing Algorithm Performance Comparison',
                    fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=self.dpi, bbox_inches='tight')
        plt.close()

    def plot_temporal_evolution(
        self,
        results: Dict[str, Dict],
        filename: str = "temporal_evolution.png"
    ):
        """
        Plot temporal evolution of key metrics.

        Args:
            results: Dictionary mapping algorithm names to their results
            filename: Output filename
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        algorithms = list(results.keys())

        # 1. Active Nodes Over Time
        ax = axes[0, 0]
        for alg in algorithms:
            data = results[alg]['alive_nodes']
            color = self.colors.get(alg, '#333333')
            ax.plot(data, label=alg, color=color, linewidth=2, alpha=0.8)

        ax.set_xlabel('Round', fontsize=11)
        ax.set_ylabel('Active Nodes', fontsize=11)
        ax.set_title('Network Lifetime Evolution', fontsize=12, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)

        # 2. Average Energy Over Time
        ax = axes[0, 1]
        for alg in algorithms:
            data = results[alg]['average_energy']
            color = self.colors.get(alg, '#333333')
            ax.plot(data, label=alg, color=color, linewidth=2, alpha=0.8)

        ax.set_xlabel('Round', fontsize=11)
        ax.set_ylabel('Average Energy (J)', fontsize=11)
        ax.set_title('Average Energy Depletion', fontsize=12, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)

        # 3. PDR Over Time (smoothed)
        ax = axes[1, 0]
        window = 50  # Moving average window
        for alg in algorithms:
            data = results[alg]['pdr_per_round']
            if len(data) > window:
                # Compute moving average
                smoothed = np.convolve(data, np.ones(window)/window, mode='valid')
                x = range(window-1, len(data))
                color = self.colors.get(alg, '#333333')
                ax.plot(x, smoothed, label=alg, color=color, linewidth=2, alpha=0.8)

        ax.set_xlabel('Round', fontsize=11)
        ax.set_ylabel('PDR (ratio)', fontsize=11)
        ax.set_title(f'Packet Delivery Ratio (Moving Avg, window={window})',
                    fontsize=12, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 1.05])

        # 4. Fairness Index Over Time (smoothed)
        ax = axes[1, 1]
        for alg in algorithms:
            data = results[alg]['fairness_index']
            if len(data) > window:
                smoothed = np.convolve(data, np.ones(window)/window, mode='valid')
                x = range(window-1, len(data))
                color = self.colors.get(alg, '#333333')
                ax.plot(x, smoothed, label=alg, color=color, linewidth=2, alpha=0.8)

        ax.set_xlabel('Round', fontsize=11)
        ax.set_ylabel('Fairness Index', fontsize=11)
        ax.set_title(f'Fairness Evolution (Moving Avg, window={window})',
                    fontsize=12, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 1.05])

        plt.suptitle('Temporal Evolution of Performance Metrics',
                    fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=self.dpi, bbox_inches='tight')
        plt.close()

    def plot_improvement_analysis(
        self,
        results: Dict[str, Dict],
        baseline: str = "SPR",
        filename: str = "improvement_analysis.png"
    ):
        """
        Plot improvement percentages relative to baseline.

        Args:
            results: Dictionary mapping algorithm names to their results
            baseline: Baseline algorithm name
            filename: Output filename
        """
        if baseline not in results:
            print(f"Warning: Baseline '{baseline}' not found in results")
            return

        metrics = [
            ('network_lifetime', 'Network Lifetime', True),
            ('first_node_death', 'First Node Death', True),
            ('final_pdr', 'Packet Delivery Ratio', True),
            ('energy_efficiency', 'Energy Efficiency', True),
            ('average_fairness', 'Fairness Index', True),
            ('average_hop_count', 'Average Hop Count', False),
        ]

        fig, ax = plt.subplots(figsize=(14, 8))

        algorithms = [alg for alg in results.keys() if alg != baseline]
        x = np.arange(len(metrics))
        width = 0.25

        for i, alg in enumerate(algorithms):
            improvements = []

            for metric_key, metric_name, higher_better in metrics:
                baseline_value = results[baseline][metric_key]
                alg_value = results[alg][metric_key]

                if baseline_value == 0:
                    improvement = 0
                else:
                    improvement = ((alg_value - baseline_value) / baseline_value) * 100

                if not higher_better:
                    improvement = -improvement

                improvements.append(improvement)

            color = self.colors.get(alg, '#333333')
            offset = width * (i - len(algorithms)/2 + 0.5)
            bars = ax.bar(x + offset, improvements, width,
                         label=alg, color=color, edgecolor='black', linewidth=1)

            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:+.1f}%',
                       ha='center', va='bottom' if height >= 0 else 'top',
                       fontsize=8, fontweight='bold')

        ax.set_ylabel('Improvement over Baseline (%)', fontsize=12)
        ax.set_title(f'Performance Improvement Relative to {baseline}',
                    fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([m[1] for m in metrics], rotation=15, ha='right')
        ax.legend(loc='best', fontsize=10)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=self.dpi, bbox_inches='tight')
        plt.close()

    def plot_energy_analysis(
        self,
        results: Dict[str, Dict],
        filename: str = "energy_analysis.png"
    ):
        """
        Plot detailed energy consumption analysis.

        Args:
            results: Dictionary mapping algorithm names to their results
            filename: Output filename
        """
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))

        algorithms = list(results.keys())

        # 1. Total Energy Consumed
        ax = axes[0]
        energies = [results[alg]['total_energy_consumed'] for alg in algorithms]
        colors = [self.colors.get(alg, '#333333') for alg in algorithms]
        bars = ax.bar(algorithms, energies, color=colors, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('Energy (J)', fontsize=11)
        ax.set_title('Total Energy Consumed', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.4f}', ha='center', va='bottom', fontsize=9)

        # 2. Energy per Packet
        ax = axes[1]
        energy_per_packet = [
            results[alg]['total_energy_consumed'] / max(1, results[alg]['packets_delivered'])
            for alg in algorithms
        ]
        bars = ax.bar(algorithms, energy_per_packet, color=colors, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('Energy/Packet (J)', fontsize=11)
        ax.set_title('Energy per Delivered Packet', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.6f}', ha='center', va='bottom', fontsize=9)

        # 3. Minimum Energy Over Time
        ax = axes[2]
        for alg in algorithms:
            data = results[alg]['minimum_energy']
            color = self.colors.get(alg, '#333333')
            ax.plot(data, label=alg, color=color, linewidth=2, alpha=0.8)

        ax.set_xlabel('Round', fontsize=11)
        ax.set_ylabel('Minimum Energy (J)', fontsize=11)
        ax.set_title('Minimum Node Energy Evolution', fontsize=12, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.suptitle('Energy Consumption Analysis',
                    fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=self.dpi, bbox_inches='tight')
        plt.close()

    def generate_all_plots(
        self,
        results: Dict[str, Dict],
        controller=None
    ):
        """
        Generate all visualization plots.

        Args:
            results: Dictionary mapping algorithm names to their results
            controller: Optional SDN controller for topology plot
        """
        print("\n" + "="*80)
        print(" GENERATING VISUALIZATIONS ".center(80))
        print("="*80)

        if controller is not None:
            print("Generating network topology plot...")
            self.plot_network_topology(controller)

        print("Generating comparative metrics plot...")
        self.plot_comparative_metrics(results)

        print("Generating temporal evolution plot...")
        self.plot_temporal_evolution(results)

        print("Generating improvement analysis plot...")
        self.plot_improvement_analysis(results)

        print("Generating energy analysis plot...")
        self.plot_energy_analysis(results)

        print(f"\nAll plots saved to: {self.output_dir}")
        print("="*80)
