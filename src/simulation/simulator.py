"""
Network simulator for WSN-SDN routing evaluation.

This module implements the complete network simulation including deployment,
routing execution, and performance metric collection.
"""

import random
import numpy as np
import copy
from typing import Dict, List, Tuple, Optional, TYPE_CHECKING

from ..models.node import SensorNode, Position
from ..models.network import SDNController

if TYPE_CHECKING:
    from ..config import SimulationConfig
    from ..routing.base import RoutingAlgorithm


class NetworkSimulator:
    """
    Comprehensive simulator for wireless sensor network operations.

    The simulator handles:
    1. Network deployment (random node placement)
    2. Topology construction (neighbor discovery)
    3. Routing protocol execution
    4. Packet transmission simulation
    5. Performance metric collection

    Metrics collected:
    - Network lifetime (rounds until network partition)
    - First Node Death (FND)
    - Half Nodes Death (HND)
    - Last Node Death (LND)
    - Packet Delivery Ratio (PDR)
    - Average hop count
    - Energy consumption
    - Energy efficiency (packets/joule)
    - Fairness index
    - Throughput
    """

    def __init__(self, config: 'SimulationConfig'):
        """
        Initialize network simulator.

        Args:
            config: Simulation configuration
        """
        self.config = config
        self.controller = SDNController(config)
        self.performance_metrics = {}

        # Simulation state
        self.is_deployed = False
        self.current_algorithm = None

    def deploy_network(self, seed: Optional[int] = None):
        """
        Deploy sensor network with random node placement.

        Nodes are placed uniformly at random in the deployment area.
        The sink is placed at the configured position.
        Links are established between nodes within communication range.

        Args:
            seed: Random seed for deployment (None uses config seed)
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        print("\n" + "="*80)
        print(" NETWORK DEPLOYMENT ".center(80))
        print("="*80)

        # Deploy sensor nodes
        for i in range(self.config.num_nodes):
            # Random position with margin from edges
            x = random.uniform(5, self.config.area_size - 5)
            y = random.uniform(5, self.config.area_size - 5)

            node = SensorNode(
                node_id=f"N{i}",
                position=Position(x, y),
                energy=self.config.initial_energy,
                is_sink=False,
                config=self.config
            )

            self.controller.register_node(node)

        # Deploy sink node
        sink_x, sink_y = self.config.sink_position
        sink = SensorNode(
            node_id="SINK",
            position=Position(sink_x, sink_y),
            energy=float('inf'),  # Unlimited energy
            is_sink=True,
            config=self.config
        )
        self.controller.register_node(sink)

        # Establish communication links
        nodes = list(self.controller.nodes.values())
        links_created = 0

        for i, node1 in enumerate(nodes):
            for node2 in nodes[i+1:]:
                distance = node1.position.distance_to(node2.position)

                if distance <= self.config.comm_range:
                    self.controller.establish_link(node1.id, node2.id, distance)
                    links_created += 1

        self.is_deployed = True

        # Print deployment summary
        print(f"\nDeployment Summary:")
        print(f"  Sensor Nodes: {self.config.num_nodes}")
        print(f"  Sink Position: {self.config.sink_position}")
        print(f"  Area: {self.config.area_size} x {self.config.area_size} m²")
        print(f"  Communication Range: {self.config.comm_range} m")
        print(f"  Links Established: {links_created}")

        # Check connectivity
        topology_stats = self.controller.get_topology_statistics()
        print(f"  Network Connected: {topology_stats['is_connected']}")
        print(f"  Average Degree: {topology_stats['average_degree']:.2f}")
        print(f"  Network Density: {topology_stats['network_density']:.4f}")
        print("="*80)

    def reset_simulation(self):
        """Reset simulation state for a new run."""
        self.controller.reset_network()
        self.current_algorithm = None

        self.performance_metrics = {
            # Temporal metrics
            'alive_nodes': [],
            'average_energy': [],
            'minimum_energy': [],
            'energy_std_dev': [],

            # Traffic metrics
            'packets_sent': 0,
            'packets_delivered': 0,
            'total_hops': 0,
            'pdr_per_round': [],
            'throughput_per_round': [],
            'latency_per_round': [],

            # Energy metrics
            'cumulative_energy': [],

            # Fairness metrics
            'fairness_index': [],

            # Final metrics (computed at end)
            'network_lifetime': 0,
            'first_node_death': 0,
            'half_node_death': 0,
            'last_node_death': 0,
            'final_pdr': 0.0,
            'average_hop_count': 0.0,
            'total_energy_consumed': 0.0,
            'energy_efficiency': 0.0,
            'average_latency': 0.0,
            'average_fairness': 0.0,
            'stability_period': 0,
            'instability_period': 0
        }

    def execute_simulation(
        self,
        algorithm: 'RoutingAlgorithm',
        verbose: bool = True
    ):
        """
        Execute complete simulation for a routing algorithm.

        Args:
            algorithm: Routing algorithm to evaluate
            verbose: Whether to print progress
        """
        if not self.is_deployed:
            raise RuntimeError("Network must be deployed before simulation")

        self.current_algorithm = algorithm

        if verbose:
            print("\n" + "="*80)
            print(f" SIMULATING: {algorithm.algorithm_name} ".center(80))
            print("="*80)
            print(f"Algorithm: {algorithm.get_description()}")
            print(f"Max Rounds: {self.config.max_rounds}")
            print(f"Packets/Round: {self.config.packets_per_round}")
            print("-"*80)

        # Train DRL agent if needed
        try:
            from ..routing.drl_sdn import DRLSDNRouting
            if isinstance(algorithm, DRLSDNRouting) and not algorithm.is_trained:
                algorithm.train(self.controller, verbose=verbose)
        except ImportError:
            # DRL not available (torch not installed)
            pass

        # Main simulation loop
        for round_num in range(self.config.max_rounds):
            # Check if network is still operational
            active_count = self.controller.get_active_node_count()

            if active_count == 0:
                if verbose:
                    print(f"\nNetwork terminated at round {round_num} (no active nodes)")
                break

            # Compute routing table
            routing_table = algorithm.compute_routing_table(self.controller)

            # Apply routing table
            for node_id, next_hop in routing_table.items():
                self.controller.nodes[node_id].next_hop = next_hop

            # Execute packet transmission round
            delivered, total_hops = self._execute_transmission_round()

            # Update node lifetimes
            self.controller.update_all_lifetimes(round_num)

            # Record metrics
            self._record_round_metrics(round_num, active_count, delivered, total_hops)

            # Print progress
            if verbose and round_num % 200 == 0:
                pdr = (self.performance_metrics['packets_delivered'] /
                      max(1, self.performance_metrics['packets_sent']) * 100)
                avg_energy = self.performance_metrics['average_energy'][-1]
                print(f"Round {round_num:4d}: "
                      f"Active={active_count:3d}/{self.config.num_nodes}, "
                      f"PDR={pdr:6.2f}%, "
                      f"Avg Energy={avg_energy:.6f} J")

        # Calculate final metrics
        self._calculate_final_metrics()

        if verbose:
            print("-"*80)
            self._print_results_summary()
            print("="*80)

    def _execute_transmission_round(self) -> Tuple[int, int]:
        """
        Execute one round of packet transmission.

        Returns:
            Tuple of (packets_delivered, total_hops)
        """
        active_sensors = self.controller.get_active_sensors()

        if not active_sensors:
            return 0, 0

        packets_delivered = 0
        total_hops = 0

        # Generate and transmit packets
        for _ in range(self.config.packets_per_round):
            # Random source
            source = random.choice(active_sensors)
            self.performance_metrics['packets_sent'] += 1

            # Route packet to sink
            current = source
            visited = {current}
            hop_count = 0
            max_hops = 20  # Prevent infinite loops

            for _ in range(max_hops):
                # Check if reached sink
                if current == "SINK":
                    packets_delivered += 1
                    self.performance_metrics['packets_delivered'] += 1
                    self.performance_metrics['total_hops'] += hop_count
                    total_hops += hop_count
                    break

                # Get current node
                node = self.controller.nodes.get(current)
                if not node or not node.is_alive:
                    break  # Node died

                # Get next hop
                next_hop = node.next_hop
                if not next_hop or next_hop not in self.controller.nodes:
                    break  # No route

                next_node = self.controller.nodes[next_hop]
                if not next_node.is_alive:
                    break  # Next hop dead

                # Prevent loops (except to sink)
                if next_hop in visited and next_hop != "SINK":
                    break

                # Calculate transmission distance
                distance = node.position.distance_to(next_node.position)

                # Transmit packet
                if not node.transmit_packet(distance):
                    break  # Transmission failed (energy depleted)

                # Receive packet (if not sink)
                if next_hop != "SINK":
                    if not next_node.receive_packet():
                        break  # Reception failed
                    next_node.forward_packet()

                # Move to next hop
                hop_count += 1
                visited.add(next_hop)
                current = next_hop

        return packets_delivered, total_hops

    def _record_round_metrics(
        self,
        round_num: int,
        active_count: int,
        delivered: int,
        total_hops: int
    ):
        """
        Record performance metrics for current round.

        Args:
            round_num: Current round number
            active_count: Number of active nodes
            delivered: Packets delivered this round
            total_hops: Total hops for delivered packets
        """
        metrics = self.performance_metrics

        # Node count
        metrics['alive_nodes'].append(active_count)

        # Energy metrics
        active_nodes = [
            self.controller.nodes[n]
            for n in self.controller.get_active_sensors()
        ]

        if active_nodes:
            energy_ratios = [n.get_residual_energy_ratio() for n in active_nodes]
            energies = [n.current_energy for n in active_nodes]

            metrics['average_energy'].append(np.mean(energies))
            metrics['minimum_energy'].append(np.min(energies))
            metrics['energy_std_dev'].append(np.std(energy_ratios))
        else:
            metrics['average_energy'].append(0.0)
            metrics['minimum_energy'].append(0.0)
            metrics['energy_std_dev'].append(0.0)

        # Traffic metrics
        pdr = delivered / max(1, self.config.packets_per_round)
        metrics['pdr_per_round'].append(pdr)
        metrics['throughput_per_round'].append(delivered)

        # Latency (average hops per delivered packet)
        if delivered > 0:
            metrics['latency_per_round'].append(total_hops / delivered)
        else:
            metrics['latency_per_round'].append(0)

        # Cumulative energy
        total_consumed = sum(
            n.total_energy_consumed
            for n in self.controller.nodes.values()
            if not n.is_sink
        )
        metrics['cumulative_energy'].append(total_consumed)

        # Fairness index
        fairness = self.controller.calculate_fairness_index()
        metrics['fairness_index'].append(fairness)

    def _calculate_final_metrics(self):
        """Calculate final aggregate metrics."""
        metrics = self.performance_metrics

        # Network lifetime
        metrics['network_lifetime'] = len(metrics['alive_nodes'])

        # Packet delivery ratio
        metrics['final_pdr'] = (
            metrics['packets_delivered'] /
            max(1, metrics['packets_sent']) * 100
        )

        # Average hop count
        metrics['average_hop_count'] = (
            metrics['total_hops'] /
            max(1, metrics['packets_delivered'])
        )

        # Energy metrics
        metrics['total_energy_consumed'] = sum(
            n.total_energy_consumed
            for n in self.controller.nodes.values()
            if not n.is_sink
        )

        # Energy efficiency (packets per joule)
        metrics['energy_efficiency'] = (
            metrics['packets_delivered'] /
            max(0.001, metrics['total_energy_consumed'])
        )

        # Average latency
        if metrics['latency_per_round']:
            metrics['average_latency'] = np.mean(metrics['latency_per_round'])

        # Average fairness
        if metrics['fairness_index']:
            metrics['average_fairness'] = np.mean(metrics['fairness_index'])

        # Stability metrics (FND, HND, LND)
        num_nodes = self.config.num_nodes
        alive_nodes = metrics['alive_nodes']

        metrics['first_node_death'] = metrics['network_lifetime']
        metrics['half_node_death'] = metrics['network_lifetime']
        metrics['last_node_death'] = metrics['network_lifetime']

        for i, alive in enumerate(alive_nodes):
            # First node death
            if alive < num_nodes and metrics['first_node_death'] == metrics['network_lifetime']:
                metrics['first_node_death'] = i

            # Half nodes death
            if alive <= num_nodes // 2 and metrics['half_node_death'] == metrics['network_lifetime']:
                metrics['half_node_death'] = i

            # Last node death
            if alive == 0 and metrics['last_node_death'] == metrics['network_lifetime']:
                metrics['last_node_death'] = i
                break

        # Stability and instability periods
        metrics['stability_period'] = metrics['first_node_death']
        metrics['instability_period'] = metrics['network_lifetime'] - metrics['first_node_death']

    def _print_results_summary(self):
        """Print comprehensive results summary."""
        m = self.performance_metrics

        print(f"\nResults Summary for {self.current_algorithm.algorithm_name}:")
        print(f"\nLifetime Metrics:")
        print(f"  Network Lifetime: {m['network_lifetime']} rounds")
        print(f"  First Node Death (FND): {m['first_node_death']} rounds")
        print(f"  Half Nodes Death (HND): {m['half_node_death']} rounds")
        print(f"  Stability Period: {m['stability_period']} rounds")
        print(f"  Instability Period: {m['instability_period']} rounds")

        print(f"\nTraffic Metrics:")
        print(f"  Packets Sent: {m['packets_sent']}")
        print(f"  Packets Delivered: {m['packets_delivered']}")
        print(f"  Packet Delivery Ratio: {m['final_pdr']:.2f}%")
        print(f"  Average Hop Count: {m['average_hop_count']:.2f}")
        print(f"  Average Latency: {m['average_latency']:.2f} hops")

        print(f"\nEnergy Metrics:")
        print(f"  Total Energy Consumed: {m['total_energy_consumed']:.6f} J")
        print(f"  Energy Efficiency: {m['energy_efficiency']:.2f} packets/J")

        print(f"\nFairness Metrics:")
        print(f"  Average Fairness Index: {m['average_fairness']:.4f}")

    def get_results(self) -> Dict:
        """
        Get complete simulation results.

        Returns:
            Dictionary with all performance metrics
        """
        return copy.deepcopy(self.performance_metrics)

    def export_results_to_csv(self, filename: str):
        """
        Export results to CSV file.

        Args:
            filename: Output CSV filename
        """
        import csv

        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(['Metric', 'Value'])

            # Write metrics
            m = self.performance_metrics
            writer.writerow(['Algorithm', self.current_algorithm.algorithm_name])
            writer.writerow(['Network Lifetime', m['network_lifetime']])
            writer.writerow(['First Node Death', m['first_node_death']])
            writer.writerow(['Half Node Death', m['half_node_death']])
            writer.writerow(['Packet Delivery Ratio (%)', f"{m['final_pdr']:.2f}"])
            writer.writerow(['Average Hop Count', f"{m['average_hop_count']:.2f}"])
            writer.writerow(['Total Energy Consumed (J)', f"{m['total_energy_consumed']:.6f}"])
            writer.writerow(['Energy Efficiency (pkts/J)', f"{m['energy_efficiency']:.2f}"])
            writer.writerow(['Average Fairness', f"{m['average_fairness']:.4f}"])
