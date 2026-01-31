"""
Demonstration of All Implemented Routing Algorithms.

This script demonstrates the usage of all baseline and advanced routing algorithms
implemented in this project, showing clear output of which algorithm is running.
"""

import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from models.network import Network, NetworkConfig
from models.node import SensorNode
from simulation.simulator import NetworkSimulator
from routing.baselines.leach import LEACH
from routing.baselines.pegasis import PEGASIS
from routing.baselines.ospf import OSPF
from routing.nn_ileach import NN_ILEACH
from routing.dos_rl import DOS_RL


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_algorithm_header(algo_name: str, description: str):
    """Print algorithm header."""
    print(f"\n{'─' * 80}")
    print(f"🔄 RUNNING: {algo_name}")
    print(f"📋 Description: {description}")
    print(f"{'─' * 80}")


def create_test_network(num_nodes=20):
    """Create a small test network."""
    config = NetworkConfig(
        num_sensors=num_nodes,
        area_width=100,
        area_height=100,
        communication_range=30,
        initial_energy=0.5
    )

    network = Network(config)
    return network


def run_algorithm_demo(algorithm, network, rounds=5):
    """Run an algorithm for a few rounds and display results."""
    algo_name = algorithm.algorithm_name
    print(f"\n📊 Simulating {algo_name} for {rounds} rounds...")

    for round_num in range(rounds):
        print(f"\n  Round {round_num + 1}/{rounds}:")

        # Compute routing table
        routing_table = algorithm.compute_routing_table(network.controller)

        # Show sample routes
        sample_nodes = list(routing_table.keys())[:3]
        for node_id in sample_nodes:
            next_hop = routing_table.get(node_id, "N/A")
            node = network.nodes[node_id]
            print(f"    Node {node_id} → {next_hop} "
                  f"(Energy: {node.energy:.3f}J)")

        # Calculate metrics
        alive_count = sum(1 for n in network.nodes.values()
                          if n.node_id != 'SINK' and n.is_alive())
        total_energy = sum(n.energy for n in network.nodes.values()
                           if n.node_id != 'SINK')

        print(f"    ✓ Alive nodes: {alive_count}/{network.config.num_sensors}")
        print(f"    ✓ Total energy: {total_energy:.2f}J")
        print(f"    ✓ Routes computed: {len(routing_table)}")

    print(f"\n✅ {algo_name} demonstration complete!")
    return routing_table


def main():
    """Main demonstration function."""
    print_section("WSN-SDN Adaptive Routing Algorithms - Comprehensive Demonstration")

    print("\n📝 This demo showcases:")
    print("   • 3 Baseline Algorithms (LEACH, PEGASIS, OSPF)")
    print("   • 2 Advanced Algorithms (NN_ILEACH, DOS-RL)")
    print("   • Clear indication of which algorithm is running")
    print("   • Performance metrics for each algorithm")

    # Set random seed for reproducibility
    np.random.seed(42)

    # ===== BASELINE ALGORITHMS =====
    print_section("PART 1: BASELINE ALGORITHMS")

    # 1. LEACH
    print_algorithm_header(
        "LEACH",
        "Low-Energy Adaptive Clustering Hierarchy - Probabilistic clustering"
    )
    network1 = create_test_network(20)
    leach = LEACH(optimal_ch_percentage=0.1)
    run_algorithm_demo(leach, network1, rounds=3)

    # 2. PEGASIS
    print_algorithm_header(
        "PEGASIS",
        "Power-Efficient Gathering - Chain-based routing with rotating leadership"
    )
    network2 = create_test_network(20)
    pegasis = PEGASIS()
    run_algorithm_demo(pegasis, network2, rounds=3)

    # 3. OSPF
    print_algorithm_header(
        "OSPF",
        "Open Shortest Path First - Link-state routing for SDN comparison"
    )
    network3 = create_test_network(20)
    ospf = OSPF()
    run_algorithm_demo(ospf, network3, rounds=3)

    # ===== ADVANCED ALGORITHMS =====
    print_section("PART 2: ADVANCED ALGORITHMS")

    # 4. NN_ILEACH
    print_algorithm_header(
        "NN_ILEACH",
        "Neural Network Improved LEACH - ML-based cluster head selection"
    )
    network4 = create_test_network(20)
    nn_ileach = NN_ILEACH()
    print("   🧠 Training neural network on optimal CH selections...")
    run_algorithm_demo(nn_ileach, network4, rounds=3)

    # 5. DOS-RL
    print_algorithm_header(
        "DOS-RL",
        "Dynamic Objective Selection with RL - Multi-objective Q-learning"
    )
    network5 = create_test_network(20)
    dos_rl = DOS_RL(epsilon=0.3)  # Lower epsilon for demo
    print("   🎯 Using 3 objectives: Energy, Load Balance, Link Quality")
    run_algorithm_demo(dos_rl, network5, rounds=3)

    # ===== SUMMARY =====
    print_section("SUMMARY")

    print("\n✅ Successfully demonstrated:")
    print("   1. ✓ LEACH - Baseline clustering algorithm")
    print("   2. ✓ PEGASIS - Chain-based routing")
    print("   3. ✓ OSPF - Shortest path routing")
    print("   4. ✓ NN_ILEACH - Neural network enhanced LEACH")
    print("   5. ✓ DOS-RL - Multi-objective reinforcement learning")

    print("\n📊 Implemented Utilities:")
    print("   ✓ SimpleFeedForward Neural Network")
    print("   ✓ Q-Learning Framework")
    print("   ✓ Fuzzy C-Means Clustering")
    print("   ✓ Snake Optimizer (MSSO)")
    print("   ✓ Whale Optimization Algorithm (WOA)")
    print("   ✓ Genetic Algorithm with NSGA-II")
    print("   ✓ Graph Attention Networks (GAT)")
    print("   ✓ Graph Convolution Networks (GCN)")
    print("   ✓ Minimum Spanning Tree (MST)")
    print("   ✓ TDMA Scheduler")
    print("   ✓ Performance Metrics (Jain's Index, PDR, Energy Efficiency)")

    print("\n🚧 Remaining Implementations:")
    print("   ⏳ MSSO-FCM - Snake Optimizer + Fuzzy Clustering")
    print("   ⏳ PGAECR - Pareto Genetic Algorithm")
    print("   ⏳ WOAD3QN-RP - Whale Opt + Dueling Double DQN")
    print("   ⏳ GN-DQN - Graph Neural Network + DQN")

    print("\n📈 Expected Performance (from literature):")
    print("   • LEACH: FND ~500-700 rounds, PDR 95-98%")
    print("   • PEGASIS: FND ~750-1050 rounds (+50% vs LEACH)")
    print("   • NN_ILEACH: FND ~11,361 rounds (20× LEACH!)")
    print("   • DOS-RL: PDR +10-20% vs OSPF, Jain's Index >0.85")

    print("\n" + "=" * 80)
    print("  Demo Complete! All algorithms clearly identified and demonstrated.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
