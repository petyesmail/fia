#!/usr/bin/env python3
"""
Main simulation runner for WSN-SDN Routing Algorithm Comparative Study.

This script orchestrates the complete simulation including:
1. Network deployment
2. Routing algorithm evaluation
3. Performance metric collection
4. Results visualization
5. Statistical analysis
"""

import warnings
import json
import sys
from pathlib import Path
from datetime import datetime

warnings.filterwarnings('ignore')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import SimulationConfig, get_default_config
from src.simulation.simulator import NetworkSimulator
from src.visualization.plotter import ResultsPlotter
from src.routing.spr import ShortestPathRouting
from src.routing.ear import EnergyAwareRouting
from src.routing.alb import AdaptiveLoadBalancing
from src.routing.drl_sdn import DRLSDNRouting


def print_header():
    """Print simulation header."""
    print("\n" + "="*90)
    print(" WSN-SDN ROUTING ALGORITHM COMPARATIVE STUDY ".center(90))
    print(" Deep Reinforcement Learning for Energy-Efficient Routing ".center(90))
    print("="*90)
    print(f"\nSimulation Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*90)


def print_comparative_summary(results: dict):
    """Print comprehensive comparative summary."""
    print("\n" + "="*110)
    print(" COMPREHENSIVE SIMULATION RESULTS ".center(110))
    print("="*110)

    # Header
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

    # Data rows
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

    print("-"*110)

    # Best algorithm per metric
    print("\n" + "="*110)
    print(" BEST ALGORITHM PER METRIC ".center(110))
    print("="*110)

    metrics_comparison = {
        'network_lifetime': ('Network Lifetime', 'rounds', True),
        'first_node_death': ('First Node Death (FND)', 'rounds', True),
        'half_node_death': ('Half Nodes Death (HND)', 'rounds', True),
        'stability_period': ('Stability Period', 'rounds', True),
        'final_pdr': ('Packet Delivery Ratio', '%', True),
        'average_hop_count': ('Average Hop Count', 'hops', False),
        'energy_efficiency': ('Energy Efficiency', 'pkts/J', True),
        'average_fairness': ('Fairness Index', '', True),
        'average_latency': ('Average Latency', 'hops', False)
    }

    for metric_key, (metric_name, unit, higher_is_better) in metrics_comparison.items():
        values = {name: results[name].get(metric_key, 0) for name in results}
        best_algorithm = max(values, key=values.get) if higher_is_better else min(values, key=values.get)

        # Calculate improvement over SPR
        improvement = ""
        if 'SPR' in values and best_algorithm != 'SPR' and values['SPR'] != 0:
            pct_change = ((values[best_algorithm] - values['SPR']) / values['SPR']) * 100
            improvement = f" ({pct_change:+.1f}% vs SPR)"

        unit_str = f" {unit}" if unit else ""
        print(f"  {metric_name:<35}: {best_algorithm:<10} = {values[best_algorithm]:.4f}{unit_str}{improvement}")

    print("="*110)


def print_detailed_comparison(results: dict):
    """Print detailed comparison with DRL-SDN improvements."""
    print("\n" + "="*90)
    print(" DRL-SDN IMPROVEMENTS OVER BASELINE ALGORITHMS ".center(90))
    print("="*90)

    if 'DRL-SDN' not in results:
        print("DRL-SDN results not available")
        return

    drl_sdn = results['DRL-SDN']
    baseline_algorithms = ['SPR', 'EAR', 'ALB']

    metrics = [
        ('network_lifetime', 'Network Lifetime', True, 'rounds'),
        ('first_node_death', 'First Node Death', True, 'rounds'),
        ('final_pdr', 'Packet Delivery Ratio', True, '%'),
        ('energy_efficiency', 'Energy Efficiency', True, 'pkts/J'),
        ('average_fairness', 'Fairness Index', True, ''),
        ('average_hop_count', 'Average Hop Count', False, 'hops')
    ]

    for baseline in baseline_algorithms:
        if baseline not in results:
            continue

        print(f"\nComparison with {baseline}:")
        print("-" * 90)

        for metric_key, metric_name, higher_better, unit in metrics:
            baseline_val = results[baseline].get(metric_key, 0)
            drl_val = drl_sdn.get(metric_key, 0)

            if baseline_val == 0:
                continue

            improvement = ((drl_val - baseline_val) / baseline_val) * 100

            # Invert improvement for metrics where lower is better
            if not higher_better:
                improvement = -improvement

            symbol = "↑" if improvement > 0 else "↓"
            unit_str = f" {unit}" if unit else ""

            print(f"  {metric_name:<30}: {baseline_val:>10.2f} → {drl_val:>10.2f}{unit_str}  "
                  f"{symbol} {abs(improvement):>6.2f}%")

    print("="*90)


def save_results_to_json(results: dict, config: SimulationConfig, filename: str = "results.json"):
    """Save results to JSON file."""
    output = {
        'simulation_time': datetime.now().isoformat(),
        'configuration': config.to_dict(),
        'results': results
    }

    filepath = Path(config.output_dir) / filename
    with open(filepath, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {filepath}")


def main():
    """Main simulation entry point."""
    print_header()

    # =========================================================================
    # CONFIGURATION
    # =========================================================================
    config = get_default_config()
    config.print_summary()

    # =========================================================================
    # NETWORK DEPLOYMENT
    # =========================================================================
    simulator = NetworkSimulator(config)
    simulator.deploy_network()

    # =========================================================================
    # ROUTING ALGORITHMS
    # =========================================================================
    algorithms = [
        ShortestPathRouting(),
        EnergyAwareRouting(energy_weight=0.6),
        AdaptiveLoadBalancing(weight_energy=0.4, weight_distance=0.3, weight_load=0.3),
        DRLSDNRouting(config)
    ]

    print("\n" + "="*90)
    print(" ALGORITHMS TO EVALUATE ".center(90))
    print("="*90)
    for i, alg in enumerate(algorithms, 1):
        print(f"{i}. {alg.algorithm_name}: {alg.get_description()}")
    print("="*90)

    # =========================================================================
    # SIMULATION EXECUTION
    # =========================================================================
    results = {}

    for algorithm in algorithms:
        print(f"\n{'='*90}")
        print(f" Evaluating: {algorithm.algorithm_name} ".center(90))
        print(f"{'='*90}")

        # Reset network for fair comparison
        simulator.reset_simulation()

        # Run simulation
        simulator.execute_simulation(algorithm, verbose=True)

        # Store results
        results[algorithm.algorithm_name] = simulator.get_results()

    # =========================================================================
    # RESULTS ANALYSIS
    # =========================================================================
    print_comparative_summary(results)
    print_detailed_comparison(results)

    # =========================================================================
    # SAVE RESULTS
    # =========================================================================
    save_results_to_json(results, config)

    # Export CSVs for each algorithm
    for alg_name in results.keys():
        csv_filename = f"{config.output_dir}/{alg_name}_results.csv"
        # Results already saved, just print confirmation
        print(f"Results for {alg_name} available in JSON")

    # =========================================================================
    # VISUALIZATION
    # =========================================================================
    plotter = ResultsPlotter(output_dir=config.output_dir, dpi=300)
    plotter.generate_all_plots(results, controller=simulator.controller)

    # =========================================================================
    # COMPLETION
    # =========================================================================
    print("\n" + "="*90)
    print(" SIMULATION COMPLETED SUCCESSFULLY ".center(90))
    print("="*90)
    print(f"Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Results Directory: {config.output_dir}")
    print("="*90 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during simulation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
