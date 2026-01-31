"""
Metrics calculation utilities for WSN performance evaluation.

This module provides functions to calculate various performance metrics
including Jain's fairness index, PDR, energy efficiency, and network lifetime metrics.
"""

import numpy as np
from typing import List, Dict, Tuple


def calculate_jains_fairness_index(values: List[float]) -> float:
    """
    Calculate Jain's Fairness Index.

    Formula: f(x1,...,xn) = (Σxi)² / (n × Σxi²)
    Range: [0, 1] where 1 is perfectly fair

    Args:
        values: List of values (e.g., energy consumption, traffic load)

    Returns:
        Fairness index between 0 and 1
    """
    if not values or len(values) == 0:
        return 0.0

    values = np.array(values, dtype=float)
    n = len(values)

    sum_x = np.sum(values)
    sum_x_squared = np.sum(values ** 2)

    if sum_x_squared == 0:
        return 1.0  # All values are zero, perfectly fair

    fairness = (sum_x ** 2) / (n * sum_x_squared)
    return float(fairness)


def calculate_pdr(packets_sent: int, packets_received: int) -> float:
    """
    Calculate Packet Delivery Ratio (PDR).

    Args:
        packets_sent: Total packets sent
        packets_received: Total packets successfully received

    Returns:
        PDR as percentage (0-100)
    """
    if packets_sent == 0:
        return 0.0

    pdr = (packets_received / packets_sent) * 100
    return float(pdr)


def calculate_energy_efficiency(packets_delivered: int, energy_consumed: float) -> float:
    """
    Calculate energy efficiency (packets per Joule).

    Args:
        packets_delivered: Number of packets successfully delivered
        energy_consumed: Total energy consumed in Joules

    Returns:
        Energy efficiency (packets/J)
    """
    if energy_consumed == 0:
        return 0.0

    efficiency = packets_delivered / energy_consumed
    return float(efficiency)


def calculate_stability_period(alive_nodes_history: List[int]) -> int:
    """
    Calculate stability period (rounds until first node death).

    Args:
        alive_nodes_history: List of alive nodes count per round

    Returns:
        FND (First Node Death) round number
    """
    if not alive_nodes_history:
        return 0

    total_nodes = alive_nodes_history[0]

    for round_num, alive in enumerate(alive_nodes_history):
        if alive < total_nodes:
            return round_num

    return len(alive_nodes_history)


def calculate_network_lifetime_metrics(alive_nodes_history: List[int]) -> Dict[str, int]:
    """
    Calculate network lifetime metrics: FND, HND, LND.

    Args:
        alive_nodes_history: List of alive nodes count per round

    Returns:
        Dictionary with FND, HND, LND values
    """
    if not alive_nodes_history:
        return {'FND': 0, 'HND': 0, 'LND': 0}

    total_nodes = alive_nodes_history[0]
    half_nodes = total_nodes // 2

    fnd = 0  # First Node Death
    hnd = 0  # Half Nodes Death
    lnd = 0  # Last Node Death

    for round_num, alive in enumerate(alive_nodes_history):
        if fnd == 0 and alive < total_nodes:
            fnd = round_num

        if hnd == 0 and alive <= half_nodes:
            hnd = round_num

        if alive == 0:
            lnd = round_num
            break

    if lnd == 0:
        lnd = len(alive_nodes_history)

    return {
        'FND': fnd,
        'HND': hnd,
        'LND': lnd,
        'stability_period': fnd,
        'instability_period': lnd - fnd
    }


def calculate_energy_variance(residual_energies: List[float]) -> float:
    """
    Calculate variance of residual energies across nodes.

    Args:
        residual_energies: List of residual energy values

    Returns:
        Variance of energies
    """
    if not residual_energies:
        return 0.0

    return float(np.var(residual_energies))


def calculate_throughput(packets_to_sink: int, total_rounds: int, round_time: float = 1.0) -> float:
    """
    Calculate network throughput.

    Args:
        packets_to_sink: Total packets delivered to sink
        total_rounds: Total simulation rounds
        round_time: Time per round in seconds

    Returns:
        Throughput in packets per second
    """
    if total_rounds == 0:
        return 0.0

    total_time = total_rounds * round_time
    throughput = packets_to_sink / total_time
    return float(throughput)


def calculate_average_delay(delays: List[float]) -> Tuple[float, float, float]:
    """
    Calculate delay statistics.

    Args:
        delays: List of packet delays

    Returns:
        Tuple of (average, max, 95th_percentile) delays
    """
    if not delays:
        return (0.0, 0.0, 0.0)

    delays_array = np.array(delays)
    avg_delay = float(np.mean(delays_array))
    max_delay = float(np.max(delays_array))
    p95_delay = float(np.percentile(delays_array, 95))

    return (avg_delay, max_delay, p95_delay)


def calculate_hop_count_distribution(hop_counts: List[int]) -> Dict[str, float]:
    """
    Calculate hop count statistics.

    Args:
        hop_counts: List of hop counts for packets

    Returns:
        Dictionary with mean, median, max hop counts
    """
    if not hop_counts:
        return {'mean': 0.0, 'median': 0.0, 'max': 0.0}

    hop_array = np.array(hop_counts)

    return {
        'mean': float(np.mean(hop_array)),
        'median': float(np.median(hop_array)),
        'max': float(np.max(hop_array)),
        'min': float(np.min(hop_array))
    }
