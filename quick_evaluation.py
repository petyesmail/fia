"""
ارزیابی سریع الگوریتم‌ها با راندهای کمتر
Quick evaluation with fewer rounds for faster results
"""

import numpy as np
import sys
import json
import time
from pathlib import Path
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Configure
rcParams['figure.dpi'] = 300
rcParams['savefig.dpi'] = 300
rcParams['font.size'] = 10

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from src.config import SimulationConfig
from src.simulation.simulator import NetworkSimulator
from src.routing.baselines.leach import LEACH
from src.routing.baselines.pegasis import PEGASIS
from src.routing.baselines.ospf import OSPF
from src.routing.nn_ileach import NN_ILEACH


def run_quick_sim(algorithm, config, max_rounds=200):
    """Run quick simulation"""
    simulator = NetworkSimulator(config)
    simulator.deploy_network()

    packets_sent = 0
    packets_delivered = 0
    alive_history = []
    energy_history = []

    for round_num in range(1, max_rounds + 1):
        try:
            routing_table = algorithm.compute_routing_table(simulator.controller)
            alive_nodes = simulator.controller.get_active_sensors()

            if not alive_nodes:
                break

            alive_history.append(len(alive_nodes))
            energy_stats = simulator.controller.get_network_energy_statistics()
            energy_history.append(energy_stats['average_residual_energy'])

            # Transmit packets
            for node_id in alive_nodes[:3]:  # 3 packets per round
                next_hop = routing_table.get(node_id)
                if not next_hop or next_hop not in simulator.controller.nodes:
                    continue

                node = simulator.controller.nodes[node_id]
                next_node = simulator.controller.nodes[next_hop]

                distance = np.sqrt((node.x - next_node.x)**2 + (node.y - next_node.y)**2)
                tx_energy = config.get_transmission_energy(distance)
                rx_energy = config.get_reception_energy()

                if node.current_energy >= tx_energy:
                    node.consume_energy(tx_energy)
                    packets_sent += 1

                    if next_node.current_energy >= rx_energy:
                        next_node.consume_energy(rx_energy)
                        if next_hop == 'SINK':
                            packets_delivered += 1

        except Exception as e:
            print(f"Error in {algorithm.algorithm_name}: {e}")
            break

    pdr = (packets_delivered / packets_sent * 100) if packets_sent > 0 else 0
    throughput = packets_delivered / max_rounds
    energy_stats = simulator.controller.get_network_energy_statistics()
    total_energy = energy_stats['total_consumed_energy']
    efficiency = packets_delivered / total_energy if total_energy > 0 else 0
    fairness = simulator.controller.calculate_fairness_index()

    return {
        'name': algorithm.algorithm_name,
        'pdr': pdr,
        'throughput': throughput,
        'efficiency': efficiency,
        'total_energy': total_energy,
        'fairness': fairness,
        'packets_delivered': packets_delivered,
        'alive_history': alive_history,
        'energy_history': energy_history
    }


def create_plots(results, output_dir):
    """Create plots"""
    output_dir = Path(output_dir)

    # 1. PDR Comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    names = [r['name'] for r in results]
    pdrs = [r['pdr'] for r in results]
    colors = ['#E74C3C', '#3498DB', '#2ECC71', '#F39C12']

    bars = ax.bar(names, pdrs, color=colors, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('PDR (%)', fontweight='bold')
    ax.set_title('Packet Delivery Ratio Comparison', fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_dir / 'pdr_comparison.png', dpi=300)
    plt.close()
    print("✓ pdr_comparison.png")

    # 2. Energy Efficiency
    fig, ax = plt.subplots(figsize=(10, 6))
    effs = [r['efficiency'] for r in results]

    bars = ax.bar(names, effs, color=colors, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('Energy Efficiency (packets/Joule)', fontweight='bold')
    ax.set_title('Energy Efficiency Comparison', fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{height:.1f}', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_dir / 'energy_efficiency.png', dpi=300)
    plt.close()
    print("✓ energy_efficiency.png")

    # 3. Alive Nodes Over Time
    fig, ax = plt.subplots(figsize=(12, 6))

    for i, result in enumerate(results):
        if result['alive_history']:
            rounds = range(1, len(result['alive_history']) + 1)
            ax.plot(rounds, result['alive_history'],
                   label=result['name'], color=colors[i],
                   marker='o', markevery=max(1, len(rounds)//10),
                   linewidth=2, markersize=5)

    ax.set_xlabel('Simulation Round', fontweight='bold')
    ax.set_ylabel('Number of Alive Nodes', fontweight='bold')
    ax.set_title('Alive Nodes Over Time', fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'alive_nodes_temporal.png', dpi=300)
    plt.close()
    print("✓ alive_nodes_temporal.png")

    # 4. Comprehensive Comparison
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # PDR
    axes[0,0].bar(names, pdrs, color=colors, edgecolor='black')
    axes[0,0].set_title('PDR (%)', fontweight='bold')
    axes[0,0].grid(True, alpha=0.3, axis='y')
    axes[0,0].tick_params(axis='x', rotation=45)

    # Efficiency
    axes[0,1].bar(names, effs, color=colors, edgecolor='black')
    axes[0,1].set_title('Energy Efficiency (pkt/J)', fontweight='bold')
    axes[0,1].grid(True, alpha=0.3, axis='y')
    axes[0,1].tick_params(axis='x', rotation=45)

    # Throughput
    tputs = [r['throughput'] for r in results]
    axes[1,0].bar(names, tputs, color=colors, edgecolor='black')
    axes[1,0].set_title('Throughput (pkt/s)', fontweight='bold')
    axes[1,0].grid(True, alpha=0.3, axis='y')
    axes[1,0].tick_params(axis='x', rotation=45)

    # Fairness
    fairs = [r['fairness'] for r in results]
    axes[1,1].bar(names, fairs, color=colors, edgecolor='black')
    axes[1,1].set_title("Jain's Fairness Index", fontweight='bold')
    axes[1,1].set_ylim([0, 1.1])
    axes[1,1].grid(True, alpha=0.3, axis='y')
    axes[1,1].tick_params(axis='x', rotation=45)

    plt.suptitle('Comprehensive Algorithm Comparison', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / 'comprehensive_comparison.png', dpi=300)
    plt.close()
    print("✓ comprehensive_comparison.png")


def main():
    print("="*80)
    print("Quick Evaluation - Top 4 Algorithms".center(80))
    print("="*80)

    config = SimulationConfig(
        num_nodes=100,
        area_size=100.0,
        sink_position=(50.0, 50.0),
        comm_range=30.0,
        initial_energy=0.5,
        max_rounds=200,
        seed=42
    )

    print(f"\nConfiguration:")
    print(f"  Nodes: {config.num_nodes}")
    print(f"  Rounds: 200 (quick mode)")
    print(f"  Energy: {config.initial_energy}J\n")

    algorithms = [
        LEACH(),
        PEGASIS(),
        OSPF(),
        NN_ILEACH(),
    ]

    results = []
    for i, alg in enumerate(algorithms, 1):
        print(f"{i}/4: Running {alg.algorithm_name}...", end=' ')
        result = run_quick_sim(alg, config, max_rounds=200)
        results.append(result)
        print(f"PDR={result['pdr']:.1f}%, Eff={result['efficiency']:.1f} pkt/J")

    # Create plots
    print(f"\nGenerating plots...")
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    create_plots(results, output_dir)

    # Save results
    with open(output_dir / 'quick_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("✓ quick_results.json")

    # Summary
    print(f"\n{'='*80}")
    print("Summary".center(80))
    print(f"{'='*80}")
    print(f"{'Algorithm':<15} {'PDR%':<8} {'Efficiency':<12} {'Fairness':<10}")
    print("-"*80)
    for r in results:
        print(f"{r['name']:<15} {r['pdr']:<8.2f} {r['efficiency']:<12.2f} {r['fairness']:<10.4f}")

    best_pdr = max(results, key=lambda x: x['pdr'])
    best_eff = max(results, key=lambda x: x['efficiency'])

    print(f"\nBest Performers:")
    print(f"  • Highest PDR: {best_pdr['name']} ({best_pdr['pdr']:.2f}%)")
    print(f"  • Best Efficiency: {best_eff['name']} ({best_eff['efficiency']:.2f} pkt/J)")

    print(f"\n✅ Quick evaluation completed!")
    print(f"📁 Results saved to: results/")


if __name__ == "__main__":
    main()
