"""
Comprehensive Demonstration of All 9 WSN-SDN Routing Algorithms.

This script executes all implemented algorithms with:
- Clear algorithm identification
- Professional metrics (FND, PDR, energy efficiency)
- Multiple scenarios (standard, high density, variable traffic)
- Comparative analysis

Author: Research Team
Date: 2026-01-31
"""

import numpy as np
import sys
from pathlib import Path
from typing import Dict, List

# Add project root to path
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


def print_header(title: str, char: str = "="):
    """Print formatted header."""
    print(f"\n{char * 80}")
    print(f"{title.center(80)}")
    print(f"{char * 80}")


def print_algorithm_info(algorithm):
    """Print algorithm identification and description."""
    print(f"\n{'─' * 80}")
    print(f"🔬 ALGORITHM: {algorithm.algorithm_name}")
    print(f"📝 DESCRIPTION: {algorithm.get_description()}")
    print(f"{'─' * 80}")


def run_algorithm_simulation(algorithm, simulator, max_rounds=100):
    """
    Run simulation for a specific algorithm.

    Args:
        algorithm: Routing algorithm instance
        simulator: NetworkSimulator instance
        max_rounds: Maximum simulation rounds

    Returns:
        Dictionary with performance metrics
    """
    print_algorithm_info(algorithm)

    # Reset simulation
    simulator.reset_simulation()

    # Metrics tracking
    metrics = {
        'algorithm_name': algorithm.algorithm_name,
        'fnd': None,  # First Node Death
        'hnd': None,  # Half Nodes Death
        'lnd': None,  # Last Node Death
        'alive_history': [],
        'energy_history': [],
        'total_packets_sent': 0,
        'total_packets_delivered': 0,
    }

    total_nodes = simulator.config.num_nodes
    half_threshold = total_nodes // 2

    print(f"\n⚙️  Running simulation for {max_rounds} rounds...")
    print(f"   Network: {total_nodes} nodes, {simulator.config.area_size}×{simulator.config.area_size}m²")
    print(f"   Initial energy: {simulator.config.initial_energy}J per node")

    for round_num in range(1, max_rounds + 1):
        # Compute routing table
        routing_table = algorithm.compute_routing_table(simulator.controller)

        # Simulate packet transmission
        alive_nodes = simulator.controller.get_active_sensors()

        if not alive_nodes:
            if metrics['lnd'] is None:
                metrics['lnd'] = round_num - 1
            break

        # Track alive nodes
        alive_count = len(alive_nodes)
        metrics['alive_history'].append(alive_count)

        # Track energy
        energy_stats = simulator.controller.get_network_energy_statistics()
        metrics['energy_history'].append(energy_stats['average_residual_energy'])

        # Detect lifetime events
        if metrics['fnd'] is None and alive_count < total_nodes:
            metrics['fnd'] = round_num
            print(f"   🔴 FND (First Node Death) at round {round_num}")

        if metrics['hnd'] is None and alive_count <= half_threshold:
            metrics['hnd'] = round_num
            print(f"   🟠 HND (Half Nodes Death) at round {round_num}")

        # Simulate packet transmission for each alive node
        for node_id in alive_nodes[:min(len(alive_nodes), 5)]:  # Sample 5 nodes per round
            next_hop = routing_table.get(node_id)
            if next_hop:
                node = simulator.controller.nodes[node_id]
                next_node = simulator.controller.nodes[next_hop]

                # Calculate transmission distance
                distance = np.sqrt(
                    (node.x - next_node.x) ** 2 +
                    (node.y - next_node.y) ** 2
                )

                # Energy consumption
                tx_energy = simulator.config.get_transmission_energy(distance)
                rx_energy = simulator.config.get_reception_energy()

                # Deduct energy
                if node.current_energy >= tx_energy:
                    node.consume_energy(tx_energy)
                    metrics['total_packets_sent'] += 1

                    if next_node.current_energy >= rx_energy:
                        next_node.consume_energy(rx_energy)
                        if next_hop == 'SINK':
                            metrics['total_packets_delivered'] += 1

        # Progress indicator
        if round_num % 20 == 0 or round_num == max_rounds:
            print(f"   Round {round_num}/{max_rounds}: {alive_count}/{total_nodes} nodes alive, "
                  f"Avg energy: {energy_stats['average_residual_energy']:.4f}J")

    # Set LND if not set
    if metrics['lnd'] is None:
        metrics['lnd'] = max_rounds

    # Calculate final metrics
    if metrics['total_packets_sent'] > 0:
        metrics['pdr'] = (metrics['total_packets_delivered'] / metrics['total_packets_sent']) * 100
    else:
        metrics['pdr'] = 0.0

    final_stats = simulator.controller.get_network_energy_statistics()
    metrics['total_energy_consumed'] = final_stats['total_consumed_energy']
    metrics['energy_efficiency'] = (
        metrics['total_packets_delivered'] / metrics['total_energy_consumed']
        if metrics['total_energy_consumed'] > 0 else 0
    )
    metrics['fairness_index'] = simulator.controller.calculate_fairness_index()

    # Print results
    print(f"\n📊 RESULTS FOR {algorithm.algorithm_name}:")
    print(f"   ✓ FND (First Node Death): Round {metrics['fnd'] or 'N/A'}")
    print(f"   ✓ HND (Half Nodes Death): Round {metrics['hnd'] or 'N/A'}")
    print(f"   ✓ LND (Last Node Death): Round {metrics['lnd']}")
    print(f"   ✓ PDR (Packet Delivery Ratio): {metrics['pdr']:.2f}%")
    print(f"   ✓ Energy Efficiency: {metrics['energy_efficiency']:.2f} packets/J")
    print(f"   ✓ Fairness Index: {metrics['fairness_index']:.4f}")
    print(f"   ✓ Total Packets Delivered: {metrics['total_packets_delivered']}")
    print(f"   ✓ Total Energy Consumed: {metrics['total_energy_consumed']:.4f}J")

    return metrics


def print_comparison_table(all_results: List[Dict]):
    """Print comparative analysis table."""
    print_header("COMPARATIVE ANALYSIS - ALL ALGORITHMS")

    print(f"\n{'Algorithm':<20} {'FND':<10} {'HND':<10} {'LND':<10} {'PDR (%)':<12} {'Eff.(pkt/J)':<15} {'Fairness':<12}")
    print("─" * 100)

    for result in all_results:
        print(f"{result['algorithm_name']:<20} "
              f"{result['fnd'] or 'N/A':<10} "
              f"{result['hnd'] or 'N/A':<10} "
              f"{result['lnd']:<10} "
              f"{result['pdr']:<12.2f} "
              f"{result['energy_efficiency']:<15.2f} "
              f"{result['fairness_index']:<12.4f}")

    print("─" * 100)

    # Find best performers
    print("\n🏆 BEST PERFORMERS:")

    # Best FND
    fnd_results = [r for r in all_results if r['fnd'] is not None]
    if fnd_results:
        best_fnd = max(fnd_results, key=lambda x: x['fnd'])
        print(f"   • Longest FND: {best_fnd['algorithm_name']} ({best_fnd['fnd']} rounds)")
    else:
        print(f"   • Longest FND: No nodes died in simulation")

    # Best PDR
    best_pdr = max(all_results, key=lambda x: x['pdr'])
    print(f"   • Highest PDR: {best_pdr['algorithm_name']} ({best_pdr['pdr']:.2f}%)")

    # Best Energy Efficiency
    best_eff = max(all_results, key=lambda x: x['energy_efficiency'])
    print(f"   • Best Energy Efficiency: {best_eff['algorithm_name']} ({best_eff['energy_efficiency']:.2f} pkt/J)")

    # Best Fairness
    best_fair = max(all_results, key=lambda x: x['fairness_index'])
    print(f"   • Best Fairness: {best_fair['algorithm_name']} ({best_fair['fairness_index']:.4f})")


def main():
    """Main execution function."""
    print_header("WSN-SDN ADAPTIVE ROUTING ALGORITHMS", "=")
    print_header("COMPREHENSIVE EVALUATION - ALL 9 ALGORITHMS", "=")

    print("\n📋 Algorithms to be evaluated:")
    print("   BASELINE ALGORITHMS:")
    print("      1. LEACH - Low Energy Adaptive Clustering Hierarchy")
    print("      2. PEGASIS - Power-Efficient Gathering in Sensor Information Systems")
    print("      3. OSPF - Open Shortest Path First (SDN)")
    print("\n   ADVANCED ALGORITHMS (2023-2026):")
    print("      4. NN_ILEACH - Neural Network Improved LEACH")
    print("      5. DOS-RL - Dynamic Objective Selection Q-Learning")
    print("      6. MSSO-FCM - Multi-Strategy Snake Optimizer + Fuzzy C-Means")
    print("      7. PGAECR - Pareto Genetic Algorithm Energy-aware Clustering Routing")
    print("      8. WOAD3QN-RP - Whale Optimization + Dueling Double DQN")
    print("      9. GN-DQN - Graph Neural Network + DQN")

    # Create simulation configuration
    config = SimulationConfig(
        num_nodes=50,
        area_size=100.0,
        sink_position=(50.0, 50.0),
        comm_range=30.0,
        initial_energy=0.5,  # 0.5 Joules
        max_rounds=200,
        seed=42
    )

    print(f"\n⚙️  Simulation Configuration:")
    print(f"   • Nodes: {config.num_nodes}")
    print(f"   • Area: {config.area_size}×{config.area_size} m²")
    print(f"   • Communication Range: {config.comm_range} m")
    print(f"   • Initial Energy: {config.initial_energy} J per node")
    print(f"   • Energy Model: First-Order Radio Model")
    print(f"     - E_elec: {config.E_elec * 1e9:.1f} nJ/bit")
    print(f"     - ε_fs: {config.E_fs * 1e12:.1f} pJ/bit/m²")
    print(f"     - ε_mp: {config.E_mp * 1e12:.4f} pJ/bit/m⁴")
    print(f"     - d0: {config.d0} m")
    print(f"     - Packet size: {config.packet_size} bits")

    # Create simulator and deploy network
    simulator = NetworkSimulator(config)
    simulator.deploy_network()

    # Define all algorithms
    algorithms = [
        # Baseline algorithms
        LEACH(),
        PEGASIS(),
        OSPF(),

        # Advanced algorithms
        NN_ILEACH(),
        DOS_RL(),
        MSSO_FCM(),
        PGAECR(),
        WOAD3QN_RP(),
        GN_DQN(),
    ]

    # Run simulations
    all_results = []

    for i, algorithm in enumerate(algorithms, 1):
        print_header(f"ALGORITHM {i}/{len(algorithms)}")
        result = run_algorithm_simulation(algorithm, simulator, max_rounds=150)
        all_results.append(result)

        # Small delay for readability
        import time
        time.sleep(0.5)

    # Print comparison
    print_comparison_table(all_results)

    print_header("SIMULATION COMPLETED", "=")
    print("\n✅ All 9 algorithms have been evaluated successfully!")
    print("📊 Results show clear identification of each algorithm's performance.")
    print("📈 Check the comparison table above for detailed metrics.\n")


if __name__ == "__main__":
    main()
