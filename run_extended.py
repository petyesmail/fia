#!/usr/bin/env python3
"""
Extended simulation with increased rounds and traffic load.
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


def main():
    print("\n" + "="*90)
    print(" EXTENDED SIMULATION: 2000 Rounds, High Traffic ".center(90))
    print("="*90)

    # Extended configuration
    config = SimulationConfig(
        num_nodes=100,
        max_rounds=2000,           # Extended
        packets_per_round=30,      # Increased traffic
        initial_energy=0.5,
        comm_range=35.0,
        output_dir="results/extended"
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
        print(f"\n{'='*90}")
        print(f" Evaluating: {algorithm.algorithm_name} ".center(90))
        print(f"{'='*90}")

        simulator.reset_simulation()
        simulator.execute_simulation(algorithm, verbose=True)
        results[algorithm.algorithm_name] = simulator.get_results()

    # Print results
    print("\n" + "="*110)
    print(" EXTENDED SIMULATION RESULTS ".center(110))
    print("="*110)

    header = (
        f"{'Algorithm':<12} "
        f"{'Lifetime':>10} "
        f"{'FND':>8} "
        f"{'HND':>8} "
        f"{'PDR(%)':>10} "
        f"{'AvgHops':>10} "
        f"{'Efficiency':>12} "
        f"{'Fairness':>10}"
    )
    print(f"\n{header}")
    print("-"*110)

    for name, metrics in results.items():
        print(
            f"{name:<12} "
            f"{metrics.get('network_lifetime', 0):>10} "
            f"{metrics.get('first_node_death', 0):>8} "
            f"{metrics.get('half_node_death', 0):>8} "
            f"{metrics.get('final_pdr', 0):>10.2f} "
            f"{metrics.get('average_hop_count', 0):>10.2f} "
            f"{metrics.get('energy_efficiency', 0):>12.2f} "
            f"{metrics.get('average_fairness', 0):>10.4f}"
        )

    print("="*110)

    # Save results
    output = {
        'simulation_time': datetime.now().isoformat(),
        'configuration': config.to_dict(),
        'results': results
    }

    filepath = Path(config.output_dir) / "results_extended.json"
    with open(filepath, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {filepath}")

    # Visualization
    plotter = ResultsPlotter(output_dir=config.output_dir, dpi=300)
    plotter.generate_all_plots(results, controller=simulator.controller)

    print("\n" + "="*90)
    print(" EXTENDED SIMULATION COMPLETED ".center(90))
    print("="*90 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
