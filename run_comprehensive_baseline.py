import os
import json
import time
import numpy as np
from datetime import datetime
from pathlib import Path

from src.config import SimulationConfig
from src.models.network import SDNController
from src.models.node import SensorNode, Position
from src.routing.spr import ShortestPathRouting
from src.routing.ear import EnergyAwareRouting
from src.routing.alb import AdaptiveLoadBalancing
from src.simulation.simulator import NetworkSimulator
from src.visualization.plotter import ResultsPlotter
from src.visualization.advanced_plotter import AdvancedPlotter
from src.statistical_analysis import StatisticalAnalyzer
from src.topology_generator import TopologyGenerator
from src.traffic_patterns import create_traffic_pattern

# Try to import DRL-SDN, but continue without it if PyTorch is not available
try:
    from src.routing.drl_sdn import DRLSDNRouting
    DRL_AVAILABLE = True
except ImportError:
    print("⚠️  PyTorch not available - DRL-SDN algorithm will be skipped")
    print("    Running with baseline algorithms: SPR, EAR, ALB\n")
    DRL_AVAILABLE = False


def run_scenario(
    scenario_name: str,
    config: SimulationConfig,
    topology_type: str,
    traffic_pattern: str,
    num_runs: int = 5
):
    print(f"\n{'='*80}")
    print(f" SCENARIO: {scenario_name} ".center(80))
    print(f"{'='*80}")
    print(f"Topology: {topology_type}")
    print(f"Traffic: {traffic_pattern}")
    print(f"Number of runs: {num_runs}")
    print(f"{'='*80}\n")

    results_dir = Path(config.output_dir) / scenario_name
    results_dir.mkdir(parents=True, exist_ok=True)

    algorithms = {
        'SPR': ShortestPathRouting(),
        'EAR': EnergyAwareRouting(),
        'ALB': AdaptiveLoadBalancing(),
    }

    if DRL_AVAILABLE:
        algorithms['DRL-SDN'] = DRLSDNRouting(config)

    all_runs_results = {algo_name: [] for algo_name in algorithms.keys()}

    for run_idx in range(num_runs):
        print(f"\n--- Run {run_idx + 1}/{num_runs} ---")

        run_config = SimulationConfig(
            num_nodes=config.num_nodes,
            area_size=config.area_size,
            comm_range=config.comm_range,
            initial_energy=config.initial_energy,
            max_rounds=config.max_rounds,
            packets_per_round=config.packets_per_round,
            seed=config.seed + run_idx * 1000,
            output_dir=str(results_dir)
        )

        controller = SDNController(run_config)

        if topology_type == 'random':
            positions = TopologyGenerator.generate_random_topology(
                run_config.num_nodes, run_config.area_size, run_config.seed
            )
        elif topology_type == 'grid':
            positions = TopologyGenerator.generate_grid_topology(
                run_config.num_nodes, run_config.area_size
            )
        elif topology_type == 'cluster':
            positions = TopologyGenerator.generate_cluster_topology(
                run_config.num_nodes, run_config.area_size, num_clusters=4
            )
        elif topology_type == 'concentric':
            positions = TopologyGenerator.generate_concentric_topology(
                run_config.num_nodes, run_config.area_size, num_rings=3
            )
        elif topology_type == 'hotspot':
            positions = TopologyGenerator.generate_hotspot_topology(
                run_config.num_nodes, run_config.area_size
            )
        else:
            positions = TopologyGenerator.generate_random_topology(
                run_config.num_nodes, run_config.area_size, run_config.seed
            )

        sink_position = TopologyGenerator.optimize_sink_placement(
            positions, run_config.area_size, method='centroid'
        )

        for idx, pos in enumerate(positions):
            node = SensorNode(
                node_id=f"N{idx}",
                position=pos,
                energy=run_config.initial_energy,
                is_sink=False,
                config=run_config
            )
            controller.register_node(node)

        sink_node = SensorNode(
            node_id="SINK",
            position=sink_position,
            energy=float('inf'),
            is_sink=True,
            config=run_config
        )
        controller.register_node(sink_node)

        for node_id, node in controller.nodes.items():
            for other_id, other_node in controller.nodes.items():
                if node_id != other_id:
                    distance = node.position.distance_to(other_node.position)
                    if distance <= run_config.comm_range:
                        controller.establish_link(node_id, other_id, distance)

        traffic = create_traffic_pattern(traffic_pattern)

        for algo_name, algorithm in algorithms.items():
            print(f"\nEvaluating {algo_name}...")

            controller.reset_network()

            if algo_name == 'DRL-SDN' and DRL_AVAILABLE:
                print(f"Training {algo_name}...")
                algorithm.train(controller, verbose=False)

            simulator = NetworkSimulator(controller, run_config)

            start_time = time.time()
            metrics = simulator.run_simulation(
                algorithm,
                traffic_pattern=traffic,
                verbose=False
            )
            execution_time = time.time() - start_time

            metrics['execution_time'] = execution_time
            metrics['run_index'] = run_idx
            all_runs_results[algo_name].append(metrics)

            print(f"{algo_name}: FND={metrics['first_node_death']}, "
                  f"PDR={metrics['avg_pdr']:.4f}, "
                  f"Lifetime={metrics['network_lifetime']}")

    aggregated_results = {}
    for algo_name in algorithms.keys():
        runs = all_runs_results[algo_name]

        aggregated_results[algo_name] = {
            'fnd_mean': np.mean([r['first_node_death'] for r in runs]),
            'fnd_std': np.std([r['first_node_death'] for r in runs]),
            'fnd_values': [r['first_node_death'] for r in runs],

            'pdr_mean': np.mean([r['avg_pdr'] for r in runs]),
            'pdr_std': np.std([r['avg_pdr'] for r in runs]),
            'pdr_values': [r['avg_pdr'] for r in runs],

            'efficiency_mean': np.mean([r['energy_efficiency'] for r in runs]),
            'efficiency_std': np.std([r['energy_efficiency'] for r in runs]),
            'efficiency_values': [r['energy_efficiency'] for r in runs],

            'fairness_mean': np.mean([r['avg_fairness'] for r in runs]),
            'fairness_std': np.std([r['fairness_std'] for r in runs]),
            'fairness_values': [r['avg_fairness'] for r in runs],

            'lifetime_mean': np.mean([r['network_lifetime'] for r in runs]),
            'lifetime_std': np.std([r['network_lifetime'] for r in runs]),
            'lifetime_values': [r['network_lifetime'] for r in runs],

            'execution_time_mean': np.mean([r['execution_time'] for r in runs]),
            'all_runs': runs
        }

    results_file = results_dir / 'aggregated_results.json'
    with open(results_file, 'w') as f:
        json.dump(aggregated_results, f, indent=2)

    print(f"\n{'='*80}")
    print(f" STATISTICAL ANALYSIS ".center(80))
    print(f"{'='*80}\n")

    analyzer = StatisticalAnalyzer()

    metrics_to_analyze = {
        'FND': ('fnd_values', True),
        'PDR': ('pdr_values', True),
        'Energy Efficiency': ('efficiency_values', True),
        'Fairness': ('fairness_values', True),
        'Network Lifetime': ('lifetime_values', True)
    }

    statistical_results = {}

    for metric_name, (value_key, higher_is_better) in metrics_to_analyze.items():
        metric_data = {
            algo_name: aggregated_results[algo_name][value_key]
            for algo_name in algorithms.keys()
        }

        comparison = analyzer.compare_algorithms(
            metric_data, metric_name, higher_is_better
        )

        statistical_results[metric_name] = comparison

        print(f"\n{metric_name}:")
        print(f"  ANOVA p-value: {comparison['anova']['p_value']:.6f}")
        if comparison['anova']['significant_at_0.05']:
            print(f"  *** Significant difference detected (p < 0.05) ***")
        print(f"  Best algorithm: {comparison['best_algorithm']} "
              f"(mean={comparison['best_value']:.4f})")

    stats_file = results_dir / 'statistical_analysis.json'
    with open(stats_file, 'w') as f:
        json.dump(statistical_results, f, indent=2, default=str)

    print(f"\n{'='*80}")
    print(f" GENERATING VISUALIZATIONS ".center(80))
    print(f"{'='*80}\n")

    plotter = AdvancedPlotter(dpi=300)

    fnd_stats = {
        algo_name: {
            'mean': aggregated_results[algo_name]['fnd_mean'],
            'std': aggregated_results[algo_name]['fnd_std'],
            'ci': StatisticalAnalyzer.compute_confidence_interval(
                aggregated_results[algo_name]['fnd_values']
            ),
            'values': aggregated_results[algo_name]['fnd_values']
        }
        for algo_name in algorithms.keys()
    }

    plotter.plot_statistical_comparison(
        fnd_stats,
        'First Node Death (FND)',
        str(results_dir / 'fnd_comparison.png'),
        higher_is_better=True
    )

    performance_3d = {
        algo_name: {
            'FND': aggregated_results[algo_name]['fnd_mean'],
            'PDR': aggregated_results[algo_name]['pdr_mean'],
            'Efficiency': aggregated_results[algo_name]['efficiency_mean']
        }
        for algo_name in algorithms.keys()
    }

    plotter.plot_3d_performance_space(
        performance_3d,
        ('FND', 'PDR', 'Efficiency'),
        str(results_dir / 'performance_3d.png')
    )

    radar_data = {
        algo_name: {
            'FND': aggregated_results[algo_name]['fnd_mean'],
            'PDR': aggregated_results[algo_name]['pdr_mean'] * 100,
            'Efficiency': aggregated_results[algo_name]['efficiency_mean'],
            'Fairness': aggregated_results[algo_name]['fairness_mean'],
            'Lifetime': aggregated_results[algo_name]['lifetime_mean']
        }
        for algo_name in algorithms.keys()
    }

    plotter.plot_radar_chart(
        radar_data,
        ['FND', 'PDR', 'Efficiency', 'Fairness', 'Lifetime'],
        str(results_dir / 'radar_comparison.png'),
        normalize=True
    )

    print(f"\nResults saved to: {results_dir}")
    print(f"Scenario {scenario_name} completed successfully!")

    return aggregated_results, statistical_results


def main():
    print("\n" + "="*80)
    print(" COMPREHENSIVE DISSERTATION-LEVEL SIMULATION FRAMEWORK ".center(80))
    print("="*80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if not DRL_AVAILABLE:
        print("⚠️  Running with BASELINE algorithms only (PyTorch not available)")
    print("="*80 + "\n")

    base_output_dir = "results/dissertation_comprehensive"
    Path(base_output_dir).mkdir(parents=True, exist_ok=True)

    scenarios = [
        {
            'name': 'scenario_1_baseline',
            'config': SimulationConfig(
                num_nodes=100,
                area_size=100.0,
                comm_range=35.0,
                initial_energy=0.5,
                max_rounds=1000,
                packets_per_round=20,
                training_episodes=300,
                output_dir=f"{base_output_dir}/scenario_1"
            ),
            'topology': 'random',
            'traffic': 'constant',
            'runs': 5
        },

        {
            'name': 'scenario_2_grid_topology',
            'config': SimulationConfig(
                num_nodes=100,
                area_size=100.0,
                comm_range=35.0,
                initial_energy=0.5,
                max_rounds=1000,
                packets_per_round=20,
                training_episodes=300,
                output_dir=f"{base_output_dir}/scenario_2"
            ),
            'topology': 'grid',
            'traffic': 'constant',
            'runs': 5
        },

        {
            'name': 'scenario_3_cluster_topology',
            'config': SimulationConfig(
                num_nodes=100,
                area_size=100.0,
                comm_range=35.0,
                initial_energy=0.5,
                max_rounds=1000,
                packets_per_round=20,
                training_episodes=300,
                output_dir=f"{base_output_dir}/scenario_3"
            ),
            'topology': 'cluster',
            'traffic': 'constant',
            'runs': 5
        },

        {
            'name': 'scenario_4_bursty_traffic',
            'config': SimulationConfig(
                num_nodes=100,
                area_size=100.0,
                comm_range=35.0,
                initial_energy=0.5,
                max_rounds=1000,
                packets_per_round=20,
                training_episodes=300,
                output_dir=f"{base_output_dir}/scenario_4"
            ),
            'topology': 'random',
            'traffic': 'bursty',
            'runs': 5
        },

        {
            'name': 'scenario_5_periodic_traffic',
            'config': SimulationConfig(
                num_nodes=100,
                area_size=100.0,
                comm_range=35.0,
                initial_energy=0.5,
                max_rounds=1000,
                packets_per_round=20,
                training_episodes=300,
                output_dir=f"{base_output_dir}/scenario_5"
            ),
            'topology': 'random',
            'traffic': 'periodic',
            'runs': 5
        },

        {
            'name': 'scenario_6_low_energy',
            'config': SimulationConfig(
                num_nodes=100,
                area_size=100.0,
                comm_range=35.0,
                initial_energy=0.25,
                max_rounds=500,
                packets_per_round=20,
                training_episodes=200,
                output_dir=f"{base_output_dir}/scenario_6"
            ),
            'topology': 'random',
            'traffic': 'constant',
            'runs': 5
        },

        {
            'name': 'scenario_7_high_energy',
            'config': SimulationConfig(
                num_nodes=100,
                area_size=100.0,
                comm_range=35.0,
                initial_energy=1.0,
                max_rounds=2000,
                packets_per_round=20,
                training_episodes=400,
                output_dir=f"{base_output_dir}/scenario_7"
            ),
            'topology': 'random',
            'traffic': 'constant',
            'runs': 5
        },

        {
            'name': 'scenario_8_large_network',
            'config': SimulationConfig(
                num_nodes=200,
                area_size=150.0,
                comm_range=40.0,
                initial_energy=0.5,
                max_rounds=1500,
                packets_per_round=25,
                training_episodes=500,
                output_dir=f"{base_output_dir}/scenario_8"
            ),
            'topology': 'random',
            'traffic': 'constant',
            'runs': 3
        }
    ]

    all_scenario_results = {}

    total_scenarios = len(scenarios)
    for idx, scenario in enumerate(scenarios, 1):
        print(f"\n{'#'*80}")
        print(f" EXECUTING SCENARIO {idx}/{total_scenarios} ".center(80))
        print(f"{'#'*80}")

        start_time = time.time()

        try:
            results, stats = run_scenario(
                scenario['name'],
                scenario['config'],
                scenario['topology'],
                scenario['traffic'],
                scenario['runs']
            )

            all_scenario_results[scenario['name']] = {
                'results': results,
                'statistics': stats,
                'execution_time': time.time() - start_time
            }

            print(f"\n✓ Scenario {scenario['name']} completed in "
                  f"{time.time() - start_time:.2f} seconds")

        except Exception as e:
            print(f"\n✗ Error in scenario {scenario['name']}: {str(e)}")
            import traceback
            traceback.print_exc()

    summary_file = Path(base_output_dir) / 'comprehensive_summary.json'
    with open(summary_file, 'w') as f:
        json.dump(all_scenario_results, f, indent=2, default=str)

    print("\n" + "="*80)
    print(" COMPREHENSIVE SIMULATION COMPLETED ".center(80))
    print("="*80)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Results directory: {base_output_dir}")
    print(f"Total scenarios executed: {len(all_scenario_results)}")
    print("="*80 + "\n")

    print("\n" + "="*80)
    print(" FINAL SUMMARY ".center(80))
    print("="*80 + "\n")

    for scenario_name, scenario_data in all_scenario_results.items():
        print(f"\n{scenario_name}:")
        print(f"  Execution time: {scenario_data['execution_time']:.2f}s")

        if 'results' in scenario_data:
            results = scenario_data['results']
            print(f"\n  Algorithm Performance:")
            for algo_name, algo_results in results.items():
                print(f"    {algo_name}:")
                print(f"      FND: {algo_results['fnd_mean']:.2f} ± {algo_results['fnd_std']:.2f}")
                print(f"      PDR: {algo_results['pdr_mean']:.4f} ± {algo_results['pdr_std']:.4f}")
                print(f"      Efficiency: {algo_results['efficiency_mean']:.2f} ± "
                      f"{algo_results['efficiency_std']:.2f}")

    print("\n" + "="*80)
    print(" ALL SIMULATIONS COMPLETED SUCCESSFULLY ".center(80))
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
