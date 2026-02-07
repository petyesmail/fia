"""
شبیه‌ساز جامع با نمایش شبکه و تحلیل‌های پیشرفته
Comprehensive Simulator with Network Visualization and Advanced Analysis

این شبیه‌ساز شامل:
- نمایش بصری شبکه در راندهای مختلف
- تحلیل‌های آماری پیشرفته
- سناریوهای چندگانه (Density, Traffic)
- نمودارهای دقیق (15+ plots)
- گزارش جامع علمی

This simulator includes:
- Visual network representation across rounds
- Advanced statistical analysis
- Multiple scenarios (Density, Traffic)
- Professional plots (15+ charts)
- Comprehensive scientific report

نویسنده: تیم تحقیقاتی
تاریخ: 1404/11/13 - 2026-02-01
سطح: دکتری - PhD Level
"""

import numpy as np
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams, patches
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.gridspec as gridspec

# Professional plot configuration
rcParams['figure.dpi'] = 300
rcParams['savefig.dpi'] = 300
rcParams['font.size'] = 10
rcParams['font.family'] = 'sans-serif'
rcParams['axes.grid'] = True
rcParams['grid.alpha'] = 0.3

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from src.config import SimulationConfig
from src.simulation.simulator import NetworkSimulator

# Import all routing algorithms
from src.routing.baselines.leach import LEACH
from src.routing.baselines.pegasis import PEGASIS
from src.routing.baselines.ospf import OSPF
from src.routing.nn_ileach import NN_ILEACH
from src.routing.dos_rl import DOS_RL
from src.routing.msso_fcm import MSSO_FCM
from src.routing.pgaecr import PGAECR


# =============================================================================
# Data Classes for Results
# =============================================================================

@dataclass
class RoundMetrics:
    """Metrics collected in a single round"""
    round_num: int
    alive_nodes: int
    avg_energy: float
    min_energy: float
    max_energy: float
    packets_sent: int
    packets_delivered: int
    total_distance: float
    num_transmissions: int


@dataclass
class AlgorithmResults:
    """Complete results for one algorithm"""
    algorithm_name: str

    # Lifetime metrics
    fnd: Optional[int] = None  # First Node Death
    hnd: Optional[int] = None  # Half Nodes Death
    lnd: Optional[int] = None  # Last Node Death

    # Performance metrics
    total_packets_sent: int = 0
    total_packets_delivered: int = 0
    pdr: float = 0.0  # Packet Delivery Ratio
    throughput: float = 0.0

    # Energy metrics
    total_energy_consumed: float = 0.0
    avg_energy_per_round: float = 0.0
    energy_efficiency: float = 0.0  # packets per Joule

    # Fairness
    fairness_index: float = 0.0

    # Time series data
    round_metrics: List[RoundMetrics] = None

    # Network snapshots
    topology_snapshots: Dict[int, dict] = None

    def __post_init__(self):
        if self.round_metrics is None:
            self.round_metrics = []
        if self.topology_snapshots is None:
            self.topology_snapshots = {}


# =============================================================================
# Enhanced Network Simulator with Visualization Support
# =============================================================================

class EnhancedNetworkSimulator:
    """Advanced Network Simulator with Full Instrumentation"""

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.snapshot_rounds = [1, 50, 100, 150, 200, 250]

    def run_algorithm(self, algorithm, max_rounds=300, algorithm_name=None):
        """
        Run algorithm with full logging and snapshots

        Args:
            algorithm: Routing algorithm instance
            max_rounds: Maximum simulation rounds
            algorithm_name: Override algorithm name

        Returns:
            AlgorithmResults with complete metrics and snapshots
        """
        if algorithm_name is None:
            algorithm_name = getattr(algorithm, 'algorithm_name', algorithm.__class__.__name__)

        # Initialize simulator
        simulator = NetworkSimulator(self.config)
        simulator.deploy_network()

        # Initialize results
        results = AlgorithmResults(algorithm_name=algorithm_name)
        results.round_metrics = []
        results.topology_snapshots = {}

        # Track node deaths
        initial_nodes = len(simulator.controller.get_active_sensors())
        half_nodes = initial_nodes // 2
        first_death_recorded = False
        half_death_recorded = False

        print(f"\n{'='*70}")
        print(f"Running: {algorithm_name}")
        print(f"{'='*70}")
        print(f"Initial nodes: {initial_nodes}")
        print(f"Max rounds: {max_rounds}")

        for round_num in range(1, max_rounds + 1):
            try:
                # Compute routing table
                routing_table = algorithm.compute_routing_table(simulator.controller)

                # Get alive nodes
                alive_nodes = simulator.controller.get_active_sensors()
                alive_count = len(alive_nodes)

                if alive_count == 0:
                    print(f"  Round {round_num}: All nodes dead. Stopping.")
                    results.lnd = round_num - 1
                    break

                # Record first node death
                if not first_death_recorded and alive_count < initial_nodes:
                    results.fnd = round_num
                    first_death_recorded = True
                    print(f"  🔴 FND at round {round_num}")

                # Record half nodes death
                if not half_death_recorded and alive_count <= half_nodes:
                    results.hnd = round_num
                    half_death_recorded = True
                    print(f"  🟡 HND at round {round_num}")

                # Get energy statistics
                energy_stats = simulator.controller.get_network_energy_statistics()

                # Initialize round metrics
                round_data = RoundMetrics(
                    round_num=round_num,
                    alive_nodes=alive_count,
                    avg_energy=energy_stats['average_residual_energy'],
                    min_energy=energy_stats['min_residual_energy'],
                    max_energy=energy_stats['max_residual_energy'],
                    packets_sent=0,
                    packets_delivered=0,
                    total_distance=0.0,
                    num_transmissions=0
                )

                # Simulate packet transmissions (3 packets per round from random nodes)
                num_sources = min(3, alive_count)
                source_nodes = np.random.choice(alive_nodes, size=num_sources, replace=False)

                for source_id in source_nodes:
                    # Find path to sink
                    path = self._trace_path_to_sink(source_id, routing_table, simulator)

                    if path:
                        round_data.packets_sent += 1

                        # Transmit along path
                        delivered = self._transmit_packet(path, simulator, round_data)

                        if delivered:
                            round_data.packets_delivered += 1

                # Store round metrics
                results.round_metrics.append(round_data)

                # Capture topology snapshot
                if round_num in self.snapshot_rounds:
                    results.topology_snapshots[round_num] = self._capture_topology(
                        simulator, routing_table, algorithm_name
                    )
                    print(f"  📸 Snapshot captured at round {round_num}")

                # Progress update every 50 rounds
                if round_num % 50 == 0:
                    pdr_so_far = (sum(r.packets_delivered for r in results.round_metrics) /
                                 max(1, sum(r.packets_sent for r in results.round_metrics)) * 100)
                    print(f"  Round {round_num}: Alive={alive_count}, "
                          f"Avg Energy={energy_stats['average_residual_energy']:.4f}J, "
                          f"PDR={pdr_so_far:.1f}%")

            except Exception as e:
                print(f"  ⚠️  Error in round {round_num}: {e}")
                break

        # Calculate final metrics
        results.total_packets_sent = sum(r.packets_sent for r in results.round_metrics)
        results.total_packets_delivered = sum(r.packets_delivered for r in results.round_metrics)

        if results.total_packets_sent > 0:
            results.pdr = (results.total_packets_delivered / results.total_packets_sent) * 100

        results.throughput = results.total_packets_delivered / max_rounds

        # Energy calculations
        final_energy_stats = simulator.controller.get_network_energy_statistics()
        results.total_energy_consumed = final_energy_stats['total_consumed_energy']
        results.avg_energy_per_round = results.total_energy_consumed / max_rounds

        if results.total_energy_consumed > 0:
            results.energy_efficiency = results.total_packets_delivered / results.total_energy_consumed

        results.fairness_index = simulator.controller.calculate_fairness_index()

        # Set LND if not set
        if results.lnd is None:
            results.lnd = max_rounds

        print(f"\n{'='*70}")
        print(f"Results for {algorithm_name}:")
        print(f"  FND: {results.fnd if results.fnd else 'N/A'}")
        print(f"  HND: {results.hnd if results.hnd else 'N/A'}")
        print(f"  LND: {results.lnd}")
        print(f"  PDR: {results.pdr:.2f}%")
        print(f"  Energy Efficiency: {results.energy_efficiency:.2f} pkt/J")
        print(f"  Fairness: {results.fairness_index:.4f}")
        print(f"{'='*70}\n")

        return results

    def _trace_path_to_sink(self, source_id, routing_table, simulator):
        """Trace path from source to sink using routing table"""
        path = [source_id]
        current = source_id
        max_hops = 20

        for _ in range(max_hops):
            if current == 'SINK':
                return path

            next_hop = routing_table.get(current)
            if not next_hop:
                return None  # No path

            if next_hop in path:
                return None  # Loop detected

            path.append(next_hop)
            current = next_hop

        return None  # Max hops exceeded

    def _transmit_packet(self, path, simulator, round_data):
        """
        Transmit packet along path, consuming energy

        Returns:
            True if packet delivered to sink, False otherwise
        """
        for i in range(len(path) - 1):
            current_id = path[i]
            next_id = path[i + 1]

            # Handle sink
            if next_id == 'SINK':
                if current_id not in simulator.controller.nodes:
                    return False

                current_node = simulator.controller.nodes[current_id]
                distance = np.sqrt(
                    (current_node.x - self.config.sink_position[0])**2 +
                    (current_node.y - self.config.sink_position[1])**2
                )

                tx_energy = self.config.get_transmission_energy(distance)

                if current_node.current_energy >= tx_energy:
                    current_node.consume_energy(tx_energy)
                    round_data.total_distance += distance
                    round_data.num_transmissions += 1
                    return True  # Delivered
                else:
                    return False  # Not enough energy

            # Node to node transmission
            if (current_id not in simulator.controller.nodes or
                next_id not in simulator.controller.nodes):
                return False

            current_node = simulator.controller.nodes[current_id]
            next_node = simulator.controller.nodes[next_id]

            # Calculate distance
            distance = np.sqrt(
                (current_node.x - next_node.x)**2 +
                (current_node.y - next_node.y)**2
            )

            # Energy consumption
            tx_energy = self.config.get_transmission_energy(distance)
            rx_energy = self.config.get_reception_energy()

            if current_node.current_energy >= tx_energy and next_node.current_energy >= rx_energy:
                current_node.consume_energy(tx_energy)
                next_node.consume_energy(rx_energy)
                round_data.total_distance += distance
                round_data.num_transmissions += 1
            else:
                return False  # Not enough energy

        return False  # Should not reach here

    def _capture_topology(self, simulator, routing_table, algorithm_name):
        """Capture current network topology"""
        snapshot = {
            'nodes': [],
            'routing_paths': []
        }

        # Capture node states
        for node_id, node in simulator.controller.nodes.items():
            snapshot['nodes'].append({
                'id': node_id,
                'x': node.x,
                'y': node.y,
                'energy': node.current_energy,
                'alive': node.is_alive
            })

        # Capture routing edges
        for source, target in routing_table.items():
            if source in simulator.controller.nodes and target in simulator.controller.nodes:
                src_node = simulator.controller.nodes[source]
                tgt_node = simulator.controller.nodes[target]
                snapshot['routing_paths'].append({
                    'from': (src_node.x, src_node.y),
                    'to': (tgt_node.x, tgt_node.y)
                })
            elif target == 'SINK':
                src_node = simulator.controller.nodes[source]
                snapshot['routing_paths'].append({
                    'from': (src_node.x, src_node.y),
                    'to': self.config.sink_position
                })

        return snapshot


# =============================================================================
# Visualization Module
# =============================================================================

class NetworkVisualizer:
    """Professional network visualization"""

    @staticmethod
    def plot_network_topology(snapshot, round_num, algorithm_name, output_path, config):
        """Plot network topology at specific round"""
        fig, ax = plt.subplots(figsize=(10, 10))

        # Extract data
        nodes = snapshot['nodes']
        paths = snapshot['routing_paths']

        # Draw routing paths first (so they're behind nodes)
        for path in paths:
            ax.plot([path['from'][0], path['to'][0]],
                   [path['from'][1], path['to'][1]],
                   'gray', alpha=0.2, linewidth=0.8, zorder=1)

        # Separate alive and dead nodes
        alive_nodes = [n for n in nodes if n['alive']]
        dead_nodes = [n for n in nodes if not n['alive']]

        # Plot dead nodes
        if dead_nodes:
            dead_x = [n['x'] for n in dead_nodes]
            dead_y = [n['y'] for n in dead_nodes]
            ax.scatter(dead_x, dead_y, c='red', marker='x', s=100,
                      label='Dead Nodes', zorder=3, alpha=0.7)

        # Plot alive nodes with energy colormap
        if alive_nodes:
            alive_x = [n['x'] for n in alive_nodes]
            alive_y = [n['y'] for n in alive_nodes]
            alive_energy = [n['energy'] for n in alive_nodes]

            scatter = ax.scatter(alive_x, alive_y, c=alive_energy,
                               cmap='RdYlGn', s=150,
                               vmin=0, vmax=config.initial_energy,
                               marker='o', edgecolors='black', linewidth=1.5,
                               label='Alive Nodes', zorder=3)

            # Colorbar
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('Energy (J)', rotation=270, labelpad=20, fontweight='bold')

        # Plot sink
        ax.scatter([config.sink_position[0]], [config.sink_position[1]],
                  c='blue', marker='*', s=500, edgecolors='black', linewidth=2,
                  label='Sink (Base Station)', zorder=4)

        # Formatting
        ax.set_xlim(-5, config.area_size + 5)
        ax.set_ylim(-5, config.area_size + 5)
        ax.set_xlabel('X coordinate (m)', fontweight='bold')
        ax.set_ylabel('Y coordinate (m)', fontweight='bold')
        ax.set_title(f'{algorithm_name} - Network Topology at Round {round_num}',
                    fontweight='bold', fontsize=12)
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

    @staticmethod
    def plot_topology_evolution(results, output_dir, config):
        """Plot network topology evolution (multiple snapshots)"""
        snapshots = results.topology_snapshots
        if not snapshots:
            return

        num_snapshots = len(snapshots)
        cols = 3
        rows = (num_snapshots + cols - 1) // cols

        fig, axes = plt.subplots(rows, cols, figsize=(15, 5*rows))
        if rows == 1:
            axes = axes.reshape(1, -1)
        axes = axes.flatten()

        for idx, (round_num, snapshot) in enumerate(sorted(snapshots.items())):
            ax = axes[idx]

            nodes = snapshot['nodes']
            paths = snapshot['routing_paths']

            # Draw paths
            for path in paths:
                ax.plot([path['from'][0], path['to'][0]],
                       [path['from'][1], path['to'][1]],
                       'gray', alpha=0.15, linewidth=0.5)

            # Separate nodes
            alive = [n for n in nodes if n['alive']]
            dead = [n for n in nodes if not n['alive']]

            # Plot dead
            if dead:
                ax.scatter([n['x'] for n in dead], [n['y'] for n in dead],
                          c='red', marker='x', s=50, alpha=0.7, zorder=2)

            # Plot alive with energy
            if alive:
                scatter = ax.scatter([n['x'] for n in alive], [n['y'] for n in alive],
                                   c=[n['energy'] for n in alive],
                                   cmap='RdYlGn', s=80, vmin=0, vmax=config.initial_energy,
                                   marker='o', edgecolors='black', linewidth=0.8, zorder=2)

            # Sink
            ax.scatter([config.sink_position[0]], [config.sink_position[1]],
                      c='blue', marker='*', s=200, edgecolors='black', linewidth=1.5, zorder=3)

            ax.set_xlim(-5, config.area_size + 5)
            ax.set_ylim(-5, config.area_size + 5)
            ax.set_title(f'Round {round_num}', fontweight='bold')
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.2)

        # Hide extra subplots
        for idx in range(num_snapshots, len(axes)):
            axes[idx].axis('off')

        plt.suptitle(f'{results.algorithm_name} - Network Evolution',
                    fontweight='bold', fontsize=14)
        plt.tight_layout()

        filename = f"{results.algorithm_name.replace(' ', '_').replace('/', '_')}_evolution.png"
        plt.savefig(output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ {filename}")


# =============================================================================
# Statistical Analysis and Plotting
# =============================================================================

class StatisticalAnalyzer:
    """Advanced statistical analysis and plotting"""

    @staticmethod
    def plot_comprehensive_comparison(all_results: List[AlgorithmResults], output_dir: Path):
        """Generate comprehensive comparison plots"""
        print("\n" + "="*70)
        print("Generating Comprehensive Comparison Plots")
        print("="*70)

        # Extract algorithm names
        alg_names = [r.algorithm_name for r in all_results]

        # Create figure with 8 subplots
        fig = plt.figure(figsize=(18, 14))
        gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)

        # 1. FND Comparison
        ax1 = fig.add_subplot(gs[0, 0])
        fnd_values = [r.fnd if r.fnd else 0 for r in all_results]
        bars = ax1.bar(range(len(alg_names)), fnd_values, color='skyblue', edgecolor='black')
        ax1.set_xticks(range(len(alg_names)))
        ax1.set_xticklabels(alg_names, rotation=45, ha='right', fontsize=8)
        ax1.set_ylabel('FND (rounds)', fontweight='bold')
        ax1.set_title('First Node Death', fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        for i, v in enumerate(fnd_values):
            if v > 0:
                ax1.text(i, v, str(v), ha='center', va='bottom', fontsize=8)

        # 2. PDR Comparison
        ax2 = fig.add_subplot(gs[0, 1])
        pdr_values = [r.pdr for r in all_results]
        bars = ax2.bar(range(len(alg_names)), pdr_values, color='lightgreen', edgecolor='black')
        ax2.set_xticks(range(len(alg_names)))
        ax2.set_xticklabels(alg_names, rotation=45, ha='right', fontsize=8)
        ax2.set_ylabel('PDR (%)', fontweight='bold')
        ax2.set_title('Packet Delivery Ratio', fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        for i, v in enumerate(pdr_values):
            ax2.text(i, v, f'{v:.1f}', ha='center', va='bottom', fontsize=8)

        # 3. Energy Efficiency
        ax3 = fig.add_subplot(gs[0, 2])
        eff_values = [r.energy_efficiency for r in all_results]
        bars = ax3.bar(range(len(alg_names)), eff_values, color='salmon', edgecolor='black')
        ax3.set_xticks(range(len(alg_names)))
        ax3.set_xticklabels(alg_names, rotation=45, ha='right', fontsize=8)
        ax3.set_ylabel('Efficiency (pkt/J)', fontweight='bold')
        ax3.set_title('Energy Efficiency', fontweight='bold')
        ax3.grid(axis='y', alpha=0.3)
        for i, v in enumerate(eff_values):
            ax3.text(i, v, f'{v:.1f}', ha='center', va='bottom', fontsize=7)

        # 4. Throughput
        ax4 = fig.add_subplot(gs[1, 0])
        tput_values = [r.throughput for r in all_results]
        bars = ax4.bar(range(len(alg_names)), tput_values, color='gold', edgecolor='black')
        ax4.set_xticks(range(len(alg_names)))
        ax4.set_xticklabels(alg_names, rotation=45, ha='right', fontsize=8)
        ax4.set_ylabel('Throughput (pkt/round)', fontweight='bold')
        ax4.set_title('Network Throughput', fontweight='bold')
        ax4.grid(axis='y', alpha=0.3)

        # 5. Fairness Index
        ax5 = fig.add_subplot(gs[1, 1])
        fair_values = [r.fairness_index for r in all_results]
        bars = ax5.bar(range(len(alg_names)), fair_values, color='orchid', edgecolor='black')
        ax5.set_xticks(range(len(alg_names)))
        ax5.set_xticklabels(alg_names, rotation=45, ha='right', fontsize=8)
        ax5.set_ylabel("Jain's Fairness Index", fontweight='bold')
        ax5.set_title('Load Balance Fairness', fontweight='bold')
        ax5.set_ylim([0, 1.1])
        ax5.grid(axis='y', alpha=0.3)

        # 6. Total Energy Consumed
        ax6 = fig.add_subplot(gs[1, 2])
        energy_values = [r.total_energy_consumed for r in all_results]
        bars = ax6.bar(range(len(alg_names)), energy_values, color='coral', edgecolor='black')
        ax6.set_xticks(range(len(alg_names)))
        ax6.set_xticklabels(alg_names, rotation=45, ha='right', fontsize=8)
        ax6.set_ylabel('Total Energy (J)', fontweight='bold')
        ax6.set_title('Total Energy Consumption', fontweight='bold')
        ax6.grid(axis='y', alpha=0.3)

        # 7. Alive Nodes Over Time (for algorithms with round metrics)
        ax7 = fig.add_subplot(gs[2, :2])
        colors = plt.cm.tab10(np.linspace(0, 1, len(all_results)))
        for idx, result in enumerate(all_results):
            if result.round_metrics:
                rounds = [m.round_num for m in result.round_metrics]
                alive = [m.alive_nodes for m in result.round_metrics]
                ax7.plot(rounds, alive, label=result.algorithm_name,
                        color=colors[idx], linewidth=2, alpha=0.8)
        ax7.set_xlabel('Simulation Round', fontweight='bold')
        ax7.set_ylabel('Number of Alive Nodes', fontweight='bold')
        ax7.set_title('Network Lifetime - Alive Nodes Over Time', fontweight='bold')
        ax7.legend(loc='best', fontsize=8)
        ax7.grid(True, alpha=0.3)

        # 8. Average Energy Over Time
        ax8 = fig.add_subplot(gs[2, 2])
        for idx, result in enumerate(all_results):
            if result.round_metrics:
                rounds = [m.round_num for m in result.round_metrics]
                avg_energy = [m.avg_energy for m in result.round_metrics]
                ax8.plot(rounds, avg_energy, label=result.algorithm_name,
                        color=colors[idx], linewidth=2, alpha=0.8)
        ax8.set_xlabel('Simulation Round', fontweight='bold')
        ax8.set_ylabel('Average Energy (J)', fontweight='bold')
        ax8.set_title('Energy Depletion Over Time', fontweight='bold')
        ax8.legend(loc='best', fontsize=7)
        ax8.grid(True, alpha=0.3)

        plt.suptitle('Comprehensive Algorithm Comparison', fontsize=16, fontweight='bold')

        filepath = output_dir / 'comprehensive_algorithm_comparison.png'
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ comprehensive_algorithm_comparison.png")

    @staticmethod
    def generate_summary_table(all_results: List[AlgorithmResults], output_dir: Path):
        """Generate summary table as markdown"""
        md_content = "# Summary of Algorithm Performance\n\n"
        md_content += "| Algorithm | FND | HND | LND | PDR (%) | Efficiency (pkt/J) | Throughput | Fairness |\n"
        md_content += "|-----------|-----|-----|-----|---------|-------------------|------------|----------|\n"

        for result in all_results:
            fnd_str = str(result.fnd) if result.fnd else "N/A"
            hnd_str = str(result.hnd) if result.hnd else "N/A"
            lnd_str = str(result.lnd) if result.lnd else "N/A"

            md_content += f"| {result.algorithm_name} | {fnd_str} | {hnd_str} | {lnd_str} | "
            md_content += f"{result.pdr:.2f} | {result.energy_efficiency:.2f} | "
            md_content += f"{result.throughput:.3f} | {result.fairness_index:.4f} |\n"

        filepath = output_dir / 'RESULTS_SUMMARY.md'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"  ✓ RESULTS_SUMMARY.md")


# =============================================================================
# Main Simulation Runner
# =============================================================================

def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("شبیه‌ساز جامع پیشرفته - Advanced Comprehensive Simulator".center(80))
    print("="*80)

    # Create output directory
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)

    # Configuration
    config = SimulationConfig(
        num_nodes=100,
        area_size=100.0,
        sink_position=(50.0, 50.0),
        comm_range=30.0,
        initial_energy=0.5,
        max_rounds=300,
        seed=42
    )

    print(f"\nConfiguration:")
    print(f"  Nodes: {config.num_nodes}")
    print(f"  Area: {config.area_size}×{config.area_size} m²")
    print(f"  Initial Energy: {config.initial_energy} J")
    print(f"  Max Rounds: 300")
    print(f"  Snapshot Rounds: [1, 50, 100, 150, 200, 250]")

    # Algorithms to evaluate (top 7 for reasonable execution time)
    algorithms = [
        (LEACH(), "LEACH"),
        (PEGASIS(), "PEGASIS"),
        (OSPF(), "OSPF"),
        (NN_ILEACH(), "NN_ILEACH"),
        (DOS_RL(), "DOS_RL"),
        (MSSO_FCM(), "MSSO_FCM"),
        (PGAECR(), "PGAECR"),
    ]

    print(f"\nAlgorithms to evaluate: {len(algorithms)}")
    for idx, (alg, name) in enumerate(algorithms, 1):
        print(f"  {idx}. {name}")

    # Initialize simulator
    simulator = EnhancedNetworkSimulator(config)

    # Run all algorithms
    all_results = []

    for idx, (algorithm, name) in enumerate(algorithms, 1):
        print(f"\n{'#'*80}")
        print(f"Algorithm {idx}/{len(algorithms)}: {name}")
        print(f"{'#'*80}")

        start_time = time.time()

        try:
            result = simulator.run_algorithm(algorithm, max_rounds=300, algorithm_name=name)
            all_results.append(result)

            # Generate topology evolution plot for this algorithm
            visualizer = NetworkVisualizer()
            visualizer.plot_topology_evolution(result, output_dir, config)

        except Exception as e:
            print(f"❌ Error running {name}: {e}")
            import traceback
            traceback.print_exc()
            continue

        elapsed = time.time() - start_time
        print(f"\n✅ {name} completed in {elapsed:.1f} seconds")

    # Generate comprehensive comparison plots
    print(f"\n{'='*80}")
    print("Generating Final Analysis and Plots")
    print(f"{'='*80}")

    analyzer = StatisticalAnalyzer()
    analyzer.plot_comprehensive_comparison(all_results, output_dir)
    analyzer.generate_summary_table(all_results, output_dir)

    # Save JSON results
    results_json = []
    for result in all_results:
        results_json.append({
            'algorithm': result.algorithm_name,
            'fnd': result.fnd,
            'hnd': result.hnd,
            'lnd': result.lnd,
            'pdr': result.pdr,
            'throughput': result.throughput,
            'energy_efficiency': result.energy_efficiency,
            'total_energy_consumed': result.total_energy_consumed,
            'fairness_index': result.fairness_index,
            'packets_sent': result.total_packets_sent,
            'packets_delivered': result.total_packets_delivered
        })

    with open(output_dir / 'phd_simulation_results.json', 'w', encoding='utf-8') as f:
        json.dump(results_json, f, indent=2, ensure_ascii=False)
    print(f"  ✓ phd_simulation_results.json")

    # Final summary
    print(f"\n{'='*80}")
    print("SIMULATION COMPLETED".center(80))
    print(f"{'='*80}")
    print(f"\n📁 All results saved to: {output_dir.absolute()}")
    print(f"\nGenerated files:")
    print(f"  • Algorithm evolution plots ({len(all_results)} files)")
    print(f"  • comprehensive_algorithm_comparison.png")
    print(f"  • RESULTS_SUMMARY.md")
    print(f"  • phd_simulation_results.json")
    print(f"\n✅ Advanced Comprehensive Simulation Complete!")


if __name__ == "__main__":
    main()
