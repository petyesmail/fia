#!/usr/bin/env python3
"""
Scalability test with different network sizes.
"""

import warnings
import json
import sys
from pathlib import Path
from datetime import datetime

warnings.filterwarnings('ignore')
sys.path.insert(0, str(Path(__file__).parent))

from src.config import SimulationConfig
from src.simulation.simulator import NetworkSimulator
from src.visualization.plotter import ResultsPlotter
from src.routing.spr import ShortestPathRouting
from src.routing.ear import EnergyAwareRouting
from src.routing.alb import AdaptiveLoadBalancing


def run_network_size(num_nodes, area_size, output_suffix):
    """Run simulation for specific network size."""
    print("\n" + "="*90)
    print(f" SCALABILITY TEST: {num_nodes} Nodes ".center(90))
    print("="*90)

    config = SimulationConfig(
        num_nodes=num_nodes,
        area_size=area_size,
        max_rounds=1000,
        packets_per_round=20,
        initial_energy=0.5,
        comm_range=35.0,
        output_dir=f"results/scale_{output_suffix}"
    )

    config.print_summary()

    simulator = NetworkSimulator(config)
    simulator.deploy_network()

    algorithms = [
        ShortestPathRouting(),
        EnergyAwareRouting(energy_weight=0.6),
        AdaptiveLoadBalancing(weight_energy=0.4, weight_distance=0.3, weight_load=0.3),
    ]

    results = {}

    for algorithm in algorithms:
        print(f"\nEvaluating {algorithm.algorithm_name}...")
        simulator.reset_simulation()
        simulator.execute_simulation(algorithm, verbose=False)
        results[algorithm.algorithm_name] = simulator.get_results()

    # Save results
    output = {
        'simulation_time': datetime.now().isoformat(),
        'network_size': num_nodes,
        'configuration': config.to_dict(),
        'results': results
    }

    filepath = Path(config.output_dir) / f"results_{output_suffix}.json"
    with open(filepath, 'w') as f:
        json.dump(output, f, indent=2)

    # Visualization
    plotter = ResultsPlotter(output_dir=config.output_dir, dpi=300)
    plotter.generate_all_plots(results, controller=simulator.controller)

    return results


def main():
    print("\n" + "="*90)
    print(" SCALABILITY ANALYSIS: Multiple Network Sizes ".center(90))
    print("="*90)

    # Test configurations
    configurations = [
        (50, 80.0, "small"),      # Small network
        (100, 100.0, "medium"),   # Medium network
        (150, 120.0, "large"),    # Large network
    ]

    all_results = {}

    for num_nodes, area_size, size_label in configurations:
        results = run_network_size(num_nodes, area_size, size_label)
        all_results[size_label] = results

    # Comprehensive comparison
    print("\n" + "="*110)
    print(" SCALABILITY ANALYSIS RESULTS ".center(110))
    print("="*110)

    for size_label in ["small", "medium", "large"]:
        num_nodes = {"small": 50, "medium": 100, "large": 150}[size_label]
        print(f"\n{size_label.upper()} Network ({num_nodes} nodes):")
        print("-" * 110)

        header = (
            f"{'Algorithm':<12} "
            f"{'Lifetime':>10} "
            f"{'FND':>8} "
            f"{'PDR(%)':>10} "
            f"{'Efficiency':>12} "
            f"{'Fairness':>10}"
        )
        print(header)
        print("-" * 110)

        for alg_name, metrics in all_results[size_label].items():
            print(
                f"{alg_name:<12} "
                f"{metrics.get('network_lifetime', 0):>10} "
                f"{metrics.get('first_node_death', 0):>8} "
                f"{metrics.get('final_pdr', 0):>10.2f} "
                f"{metrics.get('energy_efficiency', 0):>12.2f} "
                f"{metrics.get('average_fairness', 0):>10.4f}"
            )

    # Save consolidated results
    consolidated = {
        'simulation_time': datetime.now().isoformat(),
        'scalability_results': all_results
    }

    Path("results/scalability").mkdir(parents=True, exist_ok=True)
    with open("results/scalability/consolidated_results.json", 'w') as f:
        json.dump(consolidated, f, indent=2)

    print("\n" + "="*90)
    print(" SCALABILITY ANALYSIS COMPLETED ".center(90))
    print("="*90 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
