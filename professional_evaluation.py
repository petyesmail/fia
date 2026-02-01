"""
ارزیابی جامع و حرفه‌ای الگوریتم‌های مسیریابی WSN-SDN
Professional Comprehensive Evaluation of WSN-SDN Routing Algorithms

این اسکریپت اجرای واقعی و کامل همه الگوریتم‌ها با خروجی‌های گرافیکی حرفه‌ای
This script performs real execution of all algorithms with professional graphical outputs

نویسنده: تیم تحقیقاتی
تاریخ: 1404/11/12 - 2026-01-31
"""

import numpy as np
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

# Matplotlib configuration
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.patches as mpatches

# Configure matplotlib for better quality
rcParams['figure.dpi'] = 300
rcParams['savefig.dpi'] = 300
rcParams['font.size'] = 10
rcParams['axes.labelsize'] = 12
rcParams['axes.titlesize'] = 14
rcParams['legend.fontsize'] = 9
rcParams['xtick.labelsize'] = 9
rcParams['ytick.labelsize'] = 9

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from src.config import SimulationConfig
from src.simulation.simulator import NetworkSimulator

# Import all 9 algorithms
from src.routing.baselines.leach import LEACH
from src.routing.baselines.pegasis import PEGASIS
from src.routing.baselines.ospf import OSPF
from src.routing.nn_ileach import NN_ILEACH
from src.routing.dos_rl import DOS_RL
from src.routing.msso_fcm import MSSO_FCM
from src.routing.pgaecr import PGAECR
from src.routing.woad3qn_rp import WOAD3QN_RP
from src.routing.gn_dqn import GN_DQN


@dataclass
class AlgorithmResult:
    """نتایج ارزیابی یک الگوریتم"""
    algorithm_name: str
    fnd: int  # First Node Death
    hnd: int  # Half Nodes Death
    lnd: int  # Last Node Death
    pdr: float  # Packet Delivery Ratio (%)
    throughput: float  # packets/second
    energy_efficiency: float  # packets/Joule
    total_energy: float  # Total energy consumed (J)
    fairness_index: float  # Jain's Fairness Index
    avg_delay: float  # Average delay (ms)
    packets_sent: int
    packets_delivered: int
    alive_nodes_history: List[int]
    energy_history: List[float]


class ProfessionalEvaluator:
    """ارزیاب حرفه‌ای الگوریتم‌ها"""

    def __init__(self, output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # رنگ‌ها برای هر الگوریتم
        self.colors = {
            'LEACH': '#E74C3C',
            'PEGASIS': '#3498DB',
            'OSPF': '#2ECC71',
            'NN_ILEACH': '#F39C12',
            'DOS-RL': '#9B59B6',
            'MSSO-FCM': '#1ABC9C',
            'PGAECR': '#E67E22',
            'WOAD3QN-RP': '#34495E',
            'GN-DQN': '#95A5A6'
        }

        self.markers = ['o', 's', '^', 'D', 'v', 'p', '*', 'h', 'X']

    def run_simulation(self, algorithm, config: SimulationConfig, max_rounds: int = 500) -> AlgorithmResult:
        """
        اجرای شبیه‌سازی برای یک الگوریتم
        Run simulation for one algorithm
        """
        print(f"\n{'='*80}")
        print(f"🔬 الگوریتم: {algorithm.algorithm_name}".center(80))
        print(f"   Algorithm: {algorithm.algorithm_name}".center(80))
        print(f"{'='*80}")

        # Create simulator
        simulator = NetworkSimulator(config)
        simulator.deploy_network()

        # Initialize metrics
        total_nodes = config.num_nodes
        half_threshold = total_nodes // 2

        fnd = None
        hnd = None
        lnd = max_rounds

        packets_sent = 0
        packets_delivered = 0
        total_delay = 0.0

        alive_history = []
        energy_history = []

        # Run simulation
        for round_num in range(1, max_rounds + 1):
            try:
                # Compute routing
                routing_table = algorithm.compute_routing_table(simulator.controller)

                # Get alive nodes
                alive_nodes = simulator.controller.get_active_sensors()
                if not alive_nodes:
                    lnd = round_num - 1
                    break

                alive_count = len(alive_nodes)
                alive_history.append(alive_count)

                # Track energy
                energy_stats = simulator.controller.get_network_energy_statistics()
                energy_history.append(energy_stats['average_residual_energy'])

                # Detect lifetime events
                if fnd is None and alive_count < total_nodes:
                    fnd = round_num
                    print(f"   🔴 FND at round {round_num}")

                if hnd is None and alive_count <= half_threshold:
                    hnd = round_num
                    print(f"   🟠 HND at round {round_num}")

                # Simulate packet transmission
                for node_id in alive_nodes[:5]:  # 5 packets per round
                    next_hop = routing_table.get(node_id)
                    if not next_hop:
                        continue

                    node = simulator.controller.nodes[node_id]
                    if next_hop not in simulator.controller.nodes:
                        continue

                    next_node = simulator.controller.nodes[next_hop]

                    # Calculate distance
                    distance = np.sqrt((node.x - next_node.x)**2 + (node.y - next_node.y)**2)

                    # Energy consumption
                    tx_energy = config.get_transmission_energy(distance)
                    rx_energy = config.get_reception_energy()

                    if node.current_energy >= tx_energy:
                        node.consume_energy(tx_energy)
                        packets_sent += 1

                        if next_node.current_energy >= rx_energy:
                            next_node.consume_energy(rx_energy)
                            if next_hop == 'SINK':
                                packets_delivered += 1
                                total_delay += 1.0 + np.random.normal(0, 0.1)

                # Progress
                if round_num % 100 == 0:
                    print(f"   Round {round_num}/{max_rounds}: {alive_count}/{total_nodes} alive, "
                          f"Energy: {energy_stats['average_residual_energy']:.4f}J")

            except Exception as e:
                print(f"   ⚠️ Error at round {round_num}: {str(e)}")
                break

        # Calculate metrics
        pdr = (packets_delivered / packets_sent * 100) if packets_sent > 0 else 0
        throughput = packets_delivered / max_rounds

        energy_stats = simulator.controller.get_network_energy_statistics()
        total_energy = energy_stats['total_consumed_energy']
        energy_efficiency = packets_delivered / total_energy if total_energy > 0 else 0
        fairness = simulator.controller.calculate_fairness_index()
        avg_delay = total_delay / packets_delivered if packets_delivered > 0 else 0

        # Print results
        print(f"\n📊 نتایج / Results:")
        print(f"   FND: {fnd or 'N/A'} rounds")
        print(f"   HND: {hnd or 'N/A'} rounds")
        print(f"   LND: {lnd} rounds")
        print(f"   PDR: {pdr:.2f}%")
        print(f"   Throughput: {throughput:.2f} pkt/s")
        print(f"   Energy Efficiency: {energy_efficiency:.2f} pkt/J")
        print(f"   Fairness Index: {fairness:.4f}")

        return AlgorithmResult(
            algorithm_name=algorithm.algorithm_name,
            fnd=fnd or max_rounds,
            hnd=hnd or max_rounds,
            lnd=lnd,
            pdr=pdr,
            throughput=throughput,
            energy_efficiency=energy_efficiency,
            total_energy=total_energy,
            fairness_index=fairness,
            avg_delay=avg_delay,
            packets_sent=packets_sent,
            packets_delivered=packets_delivered,
            alive_nodes_history=alive_history,
            energy_history=energy_history
        )

    def generate_plots(self, results: List[AlgorithmResult]):
        """
        تولید نمودارهای حرفه‌ای
        Generate professional plots
        """
        print(f"\n{'='*80}")
        print("📈 تولید نمودارها / Generating Plots".center(80))
        print(f"{'='*80}\n")

        # 1. Network Lifetime Comparison
        self._plot_lifetime_comparison(results)

        # 2. PDR Comparison
        self._plot_pdr_comparison(results)

        # 3. Energy Efficiency Comparison
        self._plot_energy_efficiency(results)

        # 4. Throughput Comparison
        self._plot_throughput(results)

        # 5. Fairness Index Comparison
        self._plot_fairness(results)

        # 6. Alive Nodes Over Time
        self._plot_alive_nodes_temporal(results)

        # 7. Energy Consumption Over Time
        self._plot_energy_temporal(results)

        # 8. Comprehensive Comparison
        self._plot_comprehensive_comparison(results)

        print(f"\n✅ همه نمودارها در '{self.output_dir}' ذخیره شدند")
        print(f"✅ All plots saved to '{self.output_dir}'")

    def _plot_lifetime_comparison(self, results: List[AlgorithmResult]):
        """نمودار مقایسه طول عمر شبکه"""
        fig, ax = plt.subplots(figsize=(12, 6))

        algorithms = [r.algorithm_name for r in results]
        fnd_values = [r.fnd for r in results]
        hnd_values = [r.hnd for r in results]
        lnd_values = [r.lnd for r in results]

        x = np.arange(len(algorithms))
        width = 0.25

        ax.bar(x - width, fnd_values, width, label='FND', color='#E74C3C', edgecolor='black')
        ax.bar(x, hnd_values, width, label='HND', color='#F39C12', edgecolor='black')
        ax.bar(x + width, lnd_values, width, label='LND', color='#2ECC71', edgecolor='black')

        ax.set_xlabel('الگوریتم‌ها / Algorithms', fontweight='bold')
        ax.set_ylabel('تعداد راندها / Number of Rounds', fontweight='bold')
        ax.set_title('مقایسه طول عمر شبکه\nNetwork Lifetime Comparison', fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(algorithms, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(self.output_dir / 'network_lifetime.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✓ network_lifetime.png")

    def _plot_pdr_comparison(self, results: List[AlgorithmResult]):
        """نمودار مقایسه PDR"""
        fig, ax = plt.subplots(figsize=(12, 6))

        algorithms = [r.algorithm_name for r in results]
        pdr_values = [r.pdr for r in results]
        colors = [self.colors.get(alg, '#95A5A6') for alg in algorithms]

        bars = ax.bar(algorithms, pdr_values, color=colors, edgecolor='black', linewidth=1.5)

        ax.set_xlabel('الگوریتم‌ها / Algorithms', fontweight='bold')
        ax.set_ylabel('PDR (%)', fontweight='bold')
        ax.set_title('نسبت تحویل بسته\nPacket Delivery Ratio Comparison', fontweight='bold', pad=20)
        ax.set_xticklabels(algorithms, rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontweight='bold', fontsize=9)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'pdr_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✓ pdr_comparison.png")

    def _plot_energy_efficiency(self, results: List[AlgorithmResult]):
        """نمودار کارایی انرژی"""
        fig, ax = plt.subplots(figsize=(12, 6))

        algorithms = [r.algorithm_name for r in results]
        efficiency = [r.energy_efficiency for r in results]
        colors = [self.colors.get(alg, '#95A5A6') for alg in algorithms]

        bars = ax.bar(algorithms, efficiency, color=colors, edgecolor='black', linewidth=1.5)

        ax.set_xlabel('الگوریتم‌ها / Algorithms', fontweight='bold')
        ax.set_ylabel('کارایی انرژی / Energy Efficiency (packets/Joule)', fontweight='bold')
        ax.set_title('کارایی انرژی الگوریتم‌ها\nEnergy Efficiency Comparison', fontweight='bold', pad=20)
        ax.set_xticklabels(algorithms, rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontweight='bold', fontsize=9)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'energy_efficiency.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✓ energy_efficiency.png")

    def _plot_throughput(self, results: List[AlgorithmResult]):
        """نمودار توان عبور"""
        fig, ax = plt.subplots(figsize=(12, 6))

        algorithms = [r.algorithm_name for r in results]
        throughput = [r.throughput for r in results]
        colors = [self.colors.get(alg, '#95A5A6') for alg in algorithms]

        bars = ax.bar(algorithms, throughput, color=colors, edgecolor='black', linewidth=1.5)

        ax.set_xlabel('الگوریتم‌ها / Algorithms', fontweight='bold')
        ax.set_ylabel('توان عبور / Throughput (packets/second)', fontweight='bold')
        ax.set_title('مقایسه توان عبور\nThroughput Comparison', fontweight='bold', pad=20)
        ax.set_xticklabels(algorithms, rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom', fontweight='bold', fontsize=9)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'throughput_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✓ throughput_comparison.png")

    def _plot_fairness(self, results: List[AlgorithmResult]):
        """نمودار شاخص عدالت"""
        fig, ax = plt.subplots(figsize=(12, 6))

        algorithms = [r.algorithm_name for r in results]
        fairness = [r.fairness_index for r in results]
        colors = [self.colors.get(alg, '#95A5A6') for alg in algorithms]

        bars = ax.bar(algorithms, fairness, color=colors, edgecolor='black', linewidth=1.5)

        ax.set_xlabel('الگوریتم‌ها / Algorithms', fontweight='bold')
        ax.set_ylabel("شاخص عدالت Jain / Jain's Fairness Index", fontweight='bold')
        ax.set_title("مقایسه شاخص عدالت\nFairness Index Comparison", fontweight='bold', pad=20)
        ax.set_xticklabels(algorithms, rotation=45, ha='right')
        ax.set_ylim([0, 1.1])
        ax.grid(True, alpha=0.3, axis='y')

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}',
                   ha='center', va='bottom', fontweight='bold', fontsize=9)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'fairness_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✓ fairness_comparison.png")

    def _plot_alive_nodes_temporal(self, results: List[AlgorithmResult]):
        """نمودار نودهای زنده در طول زمان"""
        fig, ax = plt.subplots(figsize=(14, 7))

        for i, result in enumerate(results):
            if result.alive_nodes_history:
                rounds = range(1, len(result.alive_nodes_history) + 1)
                ax.plot(rounds, result.alive_nodes_history,
                       label=result.algorithm_name,
                       color=self.colors.get(result.algorithm_name, '#95A5A6'),
                       marker=self.markers[i % len(self.markers)],
                       markevery=max(1, len(rounds)//10),
                       linewidth=2, markersize=6)

        ax.set_xlabel('راند شبیه‌سازی / Simulation Round', fontweight='bold')
        ax.set_ylabel('تعداد نودهای زنده / Number of Alive Nodes', fontweight='bold')
        ax.set_title('تغییرات تعداد نودهای زنده در طول زمان\nAlive Nodes Over Time', fontweight='bold', pad=20)
        ax.legend(loc='best', ncol=2)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'alive_nodes_temporal.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✓ alive_nodes_temporal.png")

    def _plot_energy_temporal(self, results: List[AlgorithmResult]):
        """نمودار انرژی در طول زمان"""
        fig, ax = plt.subplots(figsize=(14, 7))

        for i, result in enumerate(results):
            if result.energy_history:
                rounds = range(1, len(result.energy_history) + 1)
                ax.plot(rounds, result.energy_history,
                       label=result.algorithm_name,
                       color=self.colors.get(result.algorithm_name, '#95A5A6'),
                       marker=self.markers[i % len(self.markers)],
                       markevery=max(1, len(rounds)//10),
                       linewidth=2, markersize=6)

        ax.set_xlabel('راند شبیه‌سازی / Simulation Round', fontweight='bold')
        ax.set_ylabel('انرژی متوسط باقیمانده / Average Residual Energy (J)', fontweight='bold')
        ax.set_title('تغییرات انرژی در طول زمان\nEnergy Consumption Over Time', fontweight='bold', pad=20)
        ax.legend(loc='best', ncol=2)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / 'energy_temporal.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✓ energy_temporal.png")

    def _plot_comprehensive_comparison(self, results: List[AlgorithmResult]):
        """نمودار مقایسه جامع"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.ravel()

        algorithms = [r.algorithm_name for r in results]

        # Subplot 1: FND
        fnd_values = [r.fnd for r in results]
        colors = [self.colors.get(alg, '#95A5A6') for alg in algorithms]
        axes[0].bar(algorithms, fnd_values, color=colors, edgecolor='black')
        axes[0].set_title('FND - First Node Death', fontweight='bold')
        axes[0].set_ylabel('Rounds')
        axes[0].tick_params(axis='x', rotation=45)
        axes[0].grid(True, alpha=0.3, axis='y')

        # Subplot 2: PDR
        pdr_values = [r.pdr for r in results]
        axes[1].bar(algorithms, pdr_values, color=colors, edgecolor='black')
        axes[1].set_title('PDR - Packet Delivery Ratio', fontweight='bold')
        axes[1].set_ylabel('PDR (%)')
        axes[1].tick_params(axis='x', rotation=45)
        axes[1].grid(True, alpha=0.3, axis='y')

        # Subplot 3: Energy Efficiency
        eff_values = [r.energy_efficiency for r in results]
        axes[2].bar(algorithms, eff_values, color=colors, edgecolor='black')
        axes[2].set_title('Energy Efficiency', fontweight='bold')
        axes[2].set_ylabel('packets/Joule')
        axes[2].tick_params(axis='x', rotation=45)
        axes[2].grid(True, alpha=0.3, axis='y')

        # Subplot 4: Throughput
        thr_values = [r.throughput for r in results]
        axes[3].bar(algorithms, thr_values, color=colors, edgecolor='black')
        axes[3].set_title('Throughput', fontweight='bold')
        axes[3].set_ylabel('packets/second')
        axes[3].tick_params(axis='x', rotation=45)
        axes[3].grid(True, alpha=0.3, axis='y')

        # Subplot 5: Fairness
        fair_values = [r.fairness_index for r in results]
        axes[4].bar(algorithms, fair_values, color=colors, edgecolor='black')
        axes[4].set_title("Jain's Fairness Index", fontweight='bold')
        axes[4].set_ylabel('Fairness Index')
        axes[4].tick_params(axis='x', rotation=45)
        axes[4].set_ylim([0, 1.1])
        axes[4].grid(True, alpha=0.3, axis='y')

        # Subplot 6: Total Energy
        energy_values = [r.total_energy for r in results]
        axes[5].bar(algorithms, energy_values, color=colors, edgecolor='black')
        axes[5].set_title('Total Energy Consumed', fontweight='bold')
        axes[5].set_ylabel('Energy (J)')
        axes[5].tick_params(axis='x', rotation=45)
        axes[5].grid(True, alpha=0.3, axis='y')

        plt.suptitle('مقایسه جامع الگوریتم‌ها\nComprehensive Algorithm Comparison',
                     fontsize=16, fontweight='bold', y=1.00)
        plt.tight_layout()
        plt.savefig(self.output_dir / 'comprehensive_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✓ comprehensive_comparison.png")

    def save_results(self, results: List[AlgorithmResult]):
        """ذخیره نتایج در JSON"""
        output = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'algorithms': {}
        }

        for result in results:
            output['algorithms'][result.algorithm_name] = {
                'fnd': result.fnd,
                'hnd': result.hnd,
                'lnd': result.lnd,
                'pdr': result.pdr,
                'throughput': result.throughput,
                'energy_efficiency': result.energy_efficiency,
                'total_energy': result.total_energy,
                'fairness_index': result.fairness_index,
                'avg_delay': result.avg_delay,
                'packets_sent': result.packets_sent,
                'packets_delivered': result.packets_delivered
            }

        with open(self.output_dir / 'evaluation_results.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\n   ✓ evaluation_results.json")


def main():
    """
    اجرای اصلی ارزیابی
    Main evaluation execution
    """
    print("="*100)
    print("ارزیابی جامع و حرفه‌ای الگوریتم‌های مسیریابی WSN-SDN".center(100))
    print("Professional Comprehensive Evaluation of WSN-SDN Routing Algorithms".center(100))
    print("="*100)
    print("\nتاریخ: 1404/11/12 - 2026-01-31")
    print("سطح: دکتری / پروفسوری - PhD / Professorial Level\n")

    # Configuration
    config = SimulationConfig(
        num_nodes=100,
        area_size=100.0,
        sink_position=(50.0, 50.0),
        comm_range=30.0,
        initial_energy=0.5,
        max_rounds=500,
        seed=42
    )

    print(f"⚙️  تنظیمات شبیه‌سازی / Simulation Configuration:")
    print(f"   • تعداد نودها / Nodes: {config.num_nodes}")
    print(f"   • ناحیه / Area: {config.area_size}×{config.area_size} m²")
    print(f"   • انرژی اولیه / Initial Energy: {config.initial_energy} J")
    print(f"   • حداکثر راندها / Max Rounds: 500")
    print(f"   • مدل انرژی / Energy Model: First-Order Radio Model")
    print(f"     - E_elec: {config.E_elec * 1e9:.1f} nJ/bit")
    print(f"     - ε_fs: {config.E_fs * 1e12:.1f} pJ/bit/m²")
    print(f"     - ε_mp: {config.E_mp * 1e12:.4f} pJ/bit/m⁴")

    # Initialize evaluator
    evaluator = ProfessionalEvaluator(output_dir="results")

    # Define algorithms
    algorithms = [
        LEACH(),
        PEGASIS(),
        OSPF(),
        NN_ILEACH(),
        DOS_RL(),
        MSSO_FCM(),
        PGAECR(),
        WOAD3QN_RP(),
        GN_DQN(),
    ]

    # Run evaluations
    results = []
    for i, algorithm in enumerate(algorithms, 1):
        print(f"\n{'#'*100}")
        print(f"الگوریتم {i}/{len(algorithms)} - Algorithm {i}/{len(algorithms)}".center(100))
        print(f"{'#'*100}")

        result = evaluator.run_simulation(algorithm, config, max_rounds=500)
        results.append(result)

        time.sleep(0.5)  # Small delay for readability

    # Generate plots
    evaluator.generate_plots(results)

    # Save results
    evaluator.save_results(results)

    # Print summary
    print(f"\n{'='*100}")
    print("خلاصه نتایج / Results Summary".center(100))
    print(f"{'='*100}\n")

    print(f"{'الگوریتم':<15} {'FND':<8} {'PDR%':<8} {'کارایی':<12} {'Throughput':<12} {'Fairness':<10}")
    print("-"*100)
    for r in results:
        print(f"{r.algorithm_name:<15} {r.fnd:<8} {r.pdr:<8.2f} {r.energy_efficiency:<12.2f} "
              f"{r.throughput:<12.2f} {r.fairness_index:<10.4f}")

    # Best performers
    best_pdr = max(results, key=lambda x: x.pdr)
    best_efficiency = max(results, key=lambda x: x.energy_efficiency)
    best_fairness = max(results, key=lambda x: x.fairness_index)

    print(f"\n🏆 بهترین عملکردها / Best Performers:")
    print(f"   • بالاترین PDR / Highest PDR: {best_pdr.algorithm_name} ({best_pdr.pdr:.2f}%)")
    print(f"   • بهترین کارایی / Best Efficiency: {best_efficiency.algorithm_name} ({best_efficiency.energy_efficiency:.2f} pkt/J)")
    print(f"   • بهترین عدالت / Best Fairness: {best_fairness.algorithm_name} ({best_fairness.fairness_index:.4f})")

    print(f"\n{'='*100}")
    print("✅ ارزیابی کامل شد! / Evaluation Completed!".center(100))
    print(f"{'='*100}")
    print(f"\n📁 خروجی‌ها / Outputs:")
    print(f"   • نمودارها / Plots: results/*.png")
    print(f"   • نتایج / Results: results/evaluation_results.json")
    print()


if __name__ == "__main__":
    main()
