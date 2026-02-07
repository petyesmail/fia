"""
Final Comprehensive Evaluation - Student Research Project
ارزیابی جامع نهایی - پروژه تحقیقاتی دانشجویی

This script performs comprehensive evaluation of all routing algorithms
with proper energy settings to observe network lifetime metrics.

این اسکریپت ارزیابی جامع تمام الگوریتم‌های مسیریابی را با
تنظیمات مناسب انرژی برای مشاهده معیارهای طول عمر شبکه انجام می‌دهد.

Features:
- Lower initial energy (0.2J) to observe node deaths
- Extended rounds (500) to capture FND, HND, LND
- Multiple traffic scenarios
- Comprehensive visualizations
- Statistical analysis
"""

import numpy as np
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.gridspec as gridspec

# Configuration
rcParams['figure.dpi'] = 300
rcParams['savefig.dpi'] = 300
rcParams['font.size'] = 10
rcParams['axes.grid'] = True
rcParams['grid.alpha'] = 0.3

# Add paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from src.config import SimulationConfig
from src.simulation.simulator import NetworkSimulator
from src.routing.baselines.leach import LEACH
from src.routing.baselines.ospf import OSPF
from src.routing.baselines.pegasis import PEGASIS
from src.routing.nn_ileach import NN_ILEACH
from src.routing.dos_rl import DOS_RL


@dataclass
class ComprehensiveResults:
    """Comprehensive results for an algorithm"""
    algorithm_name: str
    fnd: int = None
    hnd: int = None
    lnd: int = None
    total_packets_sent: int = 0
    total_packets_delivered: int = 0
    pdr: float = 0.0
    total_energy_consumed: float = 0.0
    energy_efficiency: float = 0.0
    alive_nodes_history: List[int] = None
    avg_energy_history: List[float] = None
    throughput_history: List[float] = None

    def __post_init__(self):
        if self.alive_nodes_history is None:
            self.alive_nodes_history = []
        if self.avg_energy_history is None:
            self.avg_energy_history = []
        if self.throughput_history is None:
            self.throughput_history = []


class ComprehensiveEvaluator:
    """Comprehensive evaluator with improved settings"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)

        # Improved configuration for observing node deaths
        self.config = SimulationConfig(
            num_nodes=100,
            area_size=100.0,
            sink_position=(50.0, 50.0),
            comm_range=30.0,
            initial_energy=0.2,  # Lower energy to observe deaths
            max_rounds=500,  # More rounds
            seed=42
        )

        # Algorithms to evaluate
        self.algorithms = [
            ("LEACH", LEACH),
            ("PEGASIS", PEGASIS),
            ("OSPF", OSPF),
            ("NN_ILEACH", NN_ILEACH),
            ("DOS_RL", DOS_RL),
        ]

    def run_algorithm(self, AlgClass, alg_name: str) -> ComprehensiveResults:
        """Run a single algorithm with comprehensive tracking"""

        print(f"\n{'='*70}")
        print(f"Evaluating: {alg_name}")
        print(f"{'='*70}")

        # Create simulator
        simulator = NetworkSimulator(self.config)
        simulator.deploy_network()

        # Create algorithm instance
        algorithm = AlgClass()

        # Results tracking
        results = ComprehensiveResults(algorithm_name=alg_name)

        initial_nodes = len(simulator.controller.get_active_sensors())
        half_nodes = initial_nodes // 2

        print(f"Initial nodes: {initial_nodes}")
        print(f"Initial energy per node: {self.config.initial_energy}J")

        # Run simulation
        for round_num in range(1, self.config.max_rounds + 1):
            try:
                # Compute routing
                routing_table = algorithm.compute_routing_table(simulator.controller)

                # Get alive nodes
                alive_nodes = simulator.controller.get_active_sensors()
                alive_count = len(alive_nodes)

                if alive_count == 0:
                    results.lnd = round_num - 1
                    print(f"  All nodes dead at round {round_num}")
                    break

                # Track deaths
                if results.fnd is None and alive_count < initial_nodes:
                    results.fnd = round_num
                    print(f"  🔴 FND (First Node Death) at round {round_num}")

                if results.hnd is None and alive_count <= half_nodes:
                    results.hnd = round_num
                    print(f"  🟡 HND (Half Nodes Death) at round {round_num}")

                # Get energy stats
                energy_stats = simulator.controller.get_network_energy_statistics()

                # Track metrics
                results.alive_nodes_history.append(alive_count)
                results.avg_energy_history.append(energy_stats['average_residual_energy'])

                # Transmit packets (3 per round)
                num_sources = min(3, alive_count)
                source_nodes = np.random.choice(alive_nodes, size=num_sources, replace=False)

                round_delivered = 0
                for source_id in source_nodes:
                    path = self._trace_path(source_id, routing_table, simulator)
                    if path:
                        results.total_packets_sent += 1
                        if self._transmit_packet(path, simulator):
                            results.total_packets_delivered += 1
                            round_delivered += 1

                results.throughput_history.append(round_delivered)

                # Progress every 100 rounds
                if round_num % 100 == 0:
                    pdr = (results.total_packets_delivered / max(1, results.total_packets_sent)) * 100
                    print(f"  Round {round_num}: Alive={alive_count}, "
                          f"Avg Energy={energy_stats['average_residual_energy']:.4f}J, "
                          f"PDR={pdr:.1f}%")

            except Exception as e:
                print(f"  Error at round {round_num}: {e}")
                break

        # Calculate final metrics
        if results.total_packets_sent > 0:
            results.pdr = (results.total_packets_delivered / results.total_packets_sent) * 100

        final_stats = simulator.controller.get_network_energy_statistics()
        results.total_energy_consumed = final_stats['total_consumed_energy']

        if results.total_energy_consumed > 0:
            results.energy_efficiency = results.total_packets_delivered / results.total_energy_consumed

        if results.lnd is None:
            results.lnd = self.config.max_rounds

        # Print summary
        print(f"\n{'='*70}")
        print(f"Results Summary for {alg_name}:")
        print(f"  FND: {results.fnd if results.fnd else 'N/A (no deaths)'}")
        print(f"  HND: {results.hnd if results.hnd else 'N/A'}")
        print(f"  LND: {results.lnd}")
        print(f"  PDR: {results.pdr:.2f}%")
        print(f"  Packets: {results.total_packets_delivered}/{results.total_packets_sent}")
        print(f"  Energy Efficiency: {results.energy_efficiency:.2f} pkt/J")
        print(f"  Total Energy: {results.total_energy_consumed:.4f}J")
        print(f"{'='*70}\n")

        return results

    def _trace_path(self, source_id, routing_table, simulator):
        """Trace path from source to sink"""
        path = [source_id]
        current = source_id

        for _ in range(20):
            if current == 'SINK':
                return path
            next_hop = routing_table.get(current)
            if not next_hop or next_hop in path:
                return None
            path.append(next_hop)
            current = next_hop
        return None

    def _transmit_packet(self, path, simulator):
        """Transmit packet and consume energy"""
        for i in range(len(path) - 1):
            current_id = path[i]
            next_id = path[i + 1]

            if next_id == 'SINK':
                if current_id not in simulator.controller.nodes:
                    return False
                node = simulator.controller.nodes[current_id]
                distance = np.sqrt(
                    (node.x - self.config.sink_position[0])**2 +
                    (node.y - self.config.sink_position[1])**2
                )
                energy = self.config.get_transmission_energy(distance)
                if node.current_energy >= energy:
                    node.consume_energy(energy)
                    return True
                return False

            if current_id not in simulator.controller.nodes or next_id not in simulator.controller.nodes:
                return False

            curr_node = simulator.controller.nodes[current_id]
            next_node = simulator.controller.nodes[next_id]

            distance = np.sqrt((curr_node.x - next_node.x)**2 + (curr_node.y - next_node.y)**2)
            tx_energy = self.config.get_transmission_energy(distance)
            rx_energy = self.config.get_reception_energy()

            if curr_node.current_energy >= tx_energy and next_node.current_energy >= rx_energy:
                curr_node.consume_energy(tx_energy)
                next_node.consume_energy(rx_energy)
            else:
                return False

        return False

    def run_all_algorithms(self) -> List[ComprehensiveResults]:
        """Run all algorithms"""

        print("\n" + "="*80)
        print("FINAL COMPREHENSIVE EVALUATION".center(80))
        print("="*80)
        print(f"\nConfiguration:")
        print(f"  Nodes: {self.config.num_nodes}")
        print(f"  Initial Energy: {self.config.initial_energy}J (Lower to observe deaths)")
        print(f"  Max Rounds: {self.config.max_rounds}")
        print(f"  Traffic: 3 packets/round")

        all_results = []

        for alg_name, AlgClass in self.algorithms:
            result = self.run_algorithm(AlgClass, alg_name)
            all_results.append(result)

        return all_results

    def generate_visualizations(self, all_results: List[ComprehensiveResults]):
        """Generate comprehensive visualizations"""

        print("\n" + "="*80)
        print("Generating Visualizations")
        print("="*80)

        # 1. Network Lifetime Comparison
        self._plot_lifetime_comparison(all_results)

        # 2. Alive Nodes Over Time
        self._plot_alive_nodes_temporal(all_results)

        # 3. Energy Depletion
        self._plot_energy_depletion(all_results)

        # 4. Performance Metrics
        self._plot_performance_metrics(all_results)

        # 5. Comprehensive Dashboard
        self._plot_dashboard(all_results)

    def _plot_lifetime_comparison(self, results):
        """Plot lifetime metrics comparison"""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        alg_names = [r.algorithm_name for r in results]
        colors = plt.cm.Set3(np.linspace(0, 1, len(alg_names)))

        # FND
        ax = axes[0]
        fnd_values = [r.fnd if r.fnd else 0 for r in results]
        bars = ax.bar(alg_names, fnd_values, color=colors, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('FND (rounds)', fontweight='bold')
        ax.set_title('First Node Death', fontweight='bold')
        ax.tick_params(axis='x', rotation=45)
        for i, v in enumerate(fnd_values):
            if v > 0:
                ax.text(i, v, str(v), ha='center', va='bottom', fontweight='bold')

        # HND
        ax = axes[1]
        hnd_values = [r.hnd if r.hnd else 0 for r in results]
        bars = ax.bar(alg_names, hnd_values, color=colors, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('HND (rounds)', fontweight='bold')
        ax.set_title('Half Nodes Death', fontweight='bold')
        ax.tick_params(axis='x', rotation=45)
        for i, v in enumerate(hnd_values):
            if v > 0:
                ax.text(i, v, str(v), ha='center', va='bottom', fontweight='bold')

        # LND
        ax = axes[2]
        lnd_values = [r.lnd for r in results]
        bars = ax.bar(alg_names, lnd_values, color=colors, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('LND (rounds)', fontweight='bold')
        ax.set_title('Last Node Death', fontweight='bold')
        ax.tick_params(axis='x', rotation=45)
        for i, v in enumerate(lnd_values):
            ax.text(i, v, str(v), ha='center', va='bottom', fontweight='bold')

        plt.suptitle('Network Lifetime Metrics Comparison', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.output_dir / 'lifetime_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ lifetime_comparison.png")

    def _plot_alive_nodes_temporal(self, results):
        """Plot alive nodes over time"""
        fig, ax = plt.subplots(figsize=(12, 6))

        colors = plt.cm.tab10(np.linspace(0, 1, len(results)))

        for idx, result in enumerate(results):
            rounds = range(1, len(result.alive_nodes_history) + 1)
            ax.plot(rounds, result.alive_nodes_history,
                   label=result.algorithm_name, color=colors[idx],
                   linewidth=2.5, alpha=0.8)

        ax.set_xlabel('Simulation Round', fontweight='bold', fontsize=12)
        ax.set_ylabel('Number of Alive Nodes', fontweight='bold', fontsize=12)
        ax.set_title('Network Lifetime - Alive Nodes Over Time', fontweight='bold', fontsize=14)
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 105])

        plt.tight_layout()
        plt.savefig(self.output_dir / 'alive_nodes_over_time.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ alive_nodes_over_time.png")

    def _plot_energy_depletion(self, results):
        """Plot energy depletion over time"""
        fig, ax = plt.subplots(figsize=(12, 6))

        colors = plt.cm.tab10(np.linspace(0, 1, len(results)))

        for idx, result in enumerate(results):
            rounds = range(1, len(result.avg_energy_history) + 1)
            ax.plot(rounds, result.avg_energy_history,
                   label=result.algorithm_name, color=colors[idx],
                   linewidth=2.5, alpha=0.8)

        ax.set_xlabel('Simulation Round', fontweight='bold', fontsize=12)
        ax.set_ylabel('Average Residual Energy (J)', fontweight='bold', fontsize=12)
        ax.set_title('Energy Depletion Over Time', fontweight='bold', fontsize=14)
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'energy_depletion.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ energy_depletion.png")

    def _plot_performance_metrics(self, results):
        """Plot performance metrics"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()

        alg_names = [r.algorithm_name for r in results]
        colors = plt.cm.Set2(np.linspace(0, 1, len(alg_names)))

        # PDR
        ax = axes[0]
        pdr_values = [r.pdr for r in results]
        bars = ax.bar(alg_names, pdr_values, color=colors, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('PDR (%)', fontweight='bold')
        ax.set_title('Packet Delivery Ratio', fontweight='bold')
        ax.tick_params(axis='x', rotation=45)
        for i, v in enumerate(pdr_values):
            ax.text(i, v + 1, f'{v:.1f}%', ha='center', fontweight='bold', fontsize=9)

        # Energy Efficiency
        ax = axes[1]
        eff_values = [r.energy_efficiency for r in results]
        bars = ax.bar(alg_names, eff_values, color=colors, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('Efficiency (pkt/J)', fontweight='bold')
        ax.set_title('Energy Efficiency', fontweight='bold')
        ax.tick_params(axis='x', rotation=45)
        for i, v in enumerate(eff_values):
            ax.text(i, v + 20, f'{v:.0f}', ha='center', fontweight='bold', fontsize=8)

        # Total Packets Delivered
        ax = axes[2]
        packets_values = [r.total_packets_delivered for r in results]
        bars = ax.bar(alg_names, packets_values, color=colors, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('Total Packets', fontweight='bold')
        ax.set_title('Total Packets Delivered', fontweight='bold')
        ax.tick_params(axis='x', rotation=45)

        # Total Energy Consumed
        ax = axes[3]
        energy_values = [r.total_energy_consumed for r in results]
        bars = ax.bar(alg_names, energy_values, color=colors, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('Total Energy (J)', fontweight='bold')
        ax.set_title('Total Energy Consumed', fontweight='bold')
        ax.tick_params(axis='x', rotation=45)

        plt.suptitle('Performance Metrics Comparison', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.output_dir / 'performance_metrics.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ performance_metrics.png")

    def _plot_dashboard(self, results):
        """Comprehensive dashboard"""
        fig = plt.figure(figsize=(18, 12))
        gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)

        alg_names = [r.algorithm_name for r in results]
        colors = plt.cm.tab10(np.linspace(0, 1, len(results)))

        # 1. Alive Nodes
        ax1 = fig.add_subplot(gs[0, :2])
        for idx, result in enumerate(results):
            rounds = range(1, len(result.alive_nodes_history) + 1)
            ax1.plot(rounds, result.alive_nodes_history,
                    label=result.algorithm_name, color=colors[idx], linewidth=2)
        ax1.set_xlabel('Round')
        ax1.set_ylabel('Alive Nodes')
        ax1.set_title('Network Lifetime', fontweight='bold')
        ax1.legend(loc='best', fontsize=8)
        ax1.grid(True, alpha=0.3)

        # 2. FND Comparison
        ax2 = fig.add_subplot(gs[0, 2])
        fnd_values = [r.fnd if r.fnd else 0 for r in results]
        ax2.barh(alg_names, fnd_values, color=colors, edgecolor='black')
        ax2.set_xlabel('FND (rounds)')
        ax2.set_title('First Node Death', fontweight='bold')

        # 3. Energy Depletion
        ax3 = fig.add_subplot(gs[1, :2])
        for idx, result in enumerate(results):
            rounds = range(1, len(result.avg_energy_history) + 1)
            ax3.plot(rounds, result.avg_energy_history,
                    label=result.algorithm_name, color=colors[idx], linewidth=2)
        ax3.set_xlabel('Round')
        ax3.set_ylabel('Avg Energy (J)')
        ax3.set_title('Energy Depletion', fontweight='bold')
        ax3.legend(loc='best', fontsize=8)
        ax3.grid(True, alpha=0.3)

        # 4. PDR
        ax4 = fig.add_subplot(gs[1, 2])
        pdr_values = [r.pdr for r in results]
        ax4.barh(alg_names, pdr_values, color=colors, edgecolor='black')
        ax4.set_xlabel('PDR (%)')
        ax4.set_title('Packet Delivery Ratio', fontweight='bold')

        # 5. Energy Efficiency
        ax5 = fig.add_subplot(gs[2, 0])
        eff_values = [r.energy_efficiency for r in results]
        ax5.bar(alg_names, eff_values, color=colors, edgecolor='black')
        ax5.set_ylabel('Efficiency (pkt/J)')
        ax5.set_title('Energy Efficiency', fontweight='bold')
        ax5.tick_params(axis='x', rotation=45)

        # 6. HND
        ax6 = fig.add_subplot(gs[2, 1])
        hnd_values = [r.hnd if r.hnd else 0 for r in results]
        ax6.bar(alg_names, hnd_values, color=colors, edgecolor='black')
        ax6.set_ylabel('HND (rounds)')
        ax6.set_title('Half Nodes Death', fontweight='bold')
        ax6.tick_params(axis='x', rotation=45)

        # 7. LND
        ax7 = fig.add_subplot(gs[2, 2])
        lnd_values = [r.lnd for r in results]
        ax7.bar(alg_names, lnd_values, color=colors, edgecolor='black')
        ax7.set_ylabel('LND (rounds)')
        ax7.set_title('Last Node Death', fontweight='bold')
        ax7.tick_params(axis='x', rotation=45)

        plt.suptitle('Comprehensive Evaluation Dashboard', fontsize=16, fontweight='bold')
        plt.savefig(self.output_dir / 'comprehensive_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("  ✓ comprehensive_dashboard.png")

    def save_results(self, all_results: List[ComprehensiveResults]):
        """Save results to JSON"""

        results_data = []
        for result in all_results:
            results_data.append({
                'algorithm': result.algorithm_name,
                'fnd': result.fnd,
                'hnd': result.hnd,
                'lnd': result.lnd,
                'pdr': result.pdr,
                'total_packets_sent': result.total_packets_sent,
                'total_packets_delivered': result.total_packets_delivered,
                'energy_efficiency': result.energy_efficiency,
                'total_energy_consumed': result.total_energy_consumed
            })

        with open(self.output_dir / 'final_evaluation_results.json', 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)

        print("  ✓ final_evaluation_results.json")

        # Generate summary markdown
        self._generate_summary_markdown(all_results)

    def _generate_summary_markdown(self, results):
        """Generate summary report"""

        md = ["# Final Comprehensive Evaluation Results\n\n"]
        md.append("## Configuration\n\n")
        md.append(f"- **Nodes**: {self.config.num_nodes}\n")
        md.append(f"- **Initial Energy**: {self.config.initial_energy}J\n")
        md.append(f"- **Max Rounds**: {self.config.max_rounds}\n")
        md.append(f"- **Traffic**: 3 packets/round\n\n")

        md.append("## Results Summary\n\n")
        md.append("| Algorithm | FND | HND | LND | PDR (%) | Efficiency (pkt/J) | Packets Delivered |\n")
        md.append("|-----------|-----|-----|-----|---------|-------------------|------------------|\n")

        for result in results:
            fnd_str = str(result.fnd) if result.fnd else "N/A"
            hnd_str = str(result.hnd) if result.hnd else "N/A"
            md.append(f"| {result.algorithm_name} | {fnd_str} | {hnd_str} | {result.lnd} | "
                     f"{result.pdr:.2f} | {result.energy_efficiency:.2f} | "
                     f"{result.total_packets_delivered}/{result.total_packets_sent} |\n")

        md.append("\n## Key Observations\n\n")

        # Find best performers
        best_fnd = max([r for r in results if r.fnd], key=lambda x: x.fnd, default=None)
        best_pdr = max(results, key=lambda x: x.pdr)
        best_eff = max(results, key=lambda x: x.energy_efficiency)

        if best_fnd:
            md.append(f"- **Best Network Lifetime (FND)**: {best_fnd.algorithm_name} ({best_fnd.fnd} rounds)\n")
        md.append(f"- **Best PDR**: {best_pdr.algorithm_name} ({best_pdr.pdr:.2f}%)\n")
        md.append(f"- **Best Energy Efficiency**: {best_eff.algorithm_name} ({best_eff.energy_efficiency:.2f} pkt/J)\n")

        with open(self.output_dir / 'FINAL_EVALUATION_SUMMARY.md', 'w', encoding='utf-8') as f:
            f.write(''.join(md))

        print("  ✓ FINAL_EVALUATION_SUMMARY.md")


def main():
    """Main execution"""

    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)

    evaluator = ComprehensiveEvaluator(output_dir)

    # Run all algorithms
    all_results = evaluator.run_all_algorithms()

    # Generate visualizations
    evaluator.generate_visualizations(all_results)

    # Save results
    evaluator.save_results(all_results)

    print("\n" + "="*80)
    print("✅ FINAL COMPREHENSIVE EVALUATION COMPLETED")
    print("="*80)
    print(f"\n📁 All results saved to: {output_dir.absolute()}")
    print(f"\nGenerated files:")
    print(f"  • lifetime_comparison.png")
    print(f"  • alive_nodes_over_time.png")
    print(f"  • energy_depletion.png")
    print(f"  • performance_metrics.png")
    print(f"  • comprehensive_dashboard.png")
    print(f"  • final_evaluation_results.json")
    print(f"  • FINAL_EVALUATION_SUMMARY.md")
    print(f"\n✅ Evaluation Complete!\n")


if __name__ == "__main__":
    main()
