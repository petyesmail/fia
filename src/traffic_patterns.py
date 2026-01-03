import numpy as np
import random
from typing import List, Dict
from abc import ABC, abstractmethod


class TrafficPattern(ABC):

    @abstractmethod
    def get_traffic_load(self, round_num: int, node_id: str) -> int:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass


class ConstantTrafficPattern(TrafficPattern):

    def __init__(self, packets_per_round: int = 20):
        self.packets_per_round = packets_per_round

    def get_traffic_load(self, round_num: int, node_id: str) -> int:
        return self.packets_per_round

    def get_description(self) -> str:
        return f"Constant: {self.packets_per_round} packets/round"


class BurstyTrafficPattern(TrafficPattern):

    def __init__(
        self,
        base_load: int = 10,
        burst_load: int = 50,
        burst_probability: float = 0.2
    ):
        self.base_load = base_load
        self.burst_load = burst_load
        self.burst_probability = burst_probability

    def get_traffic_load(self, round_num: int, node_id: str) -> int:
        if random.random() < self.burst_probability:
            return self.burst_load
        return self.base_load

    def get_description(self) -> str:
        return f"Bursty: {self.base_load}-{self.burst_load} packets (p={self.burst_probability})"


class PeriodicTrafficPattern(TrafficPattern):

    def __init__(
        self,
        base_load: int = 15,
        peak_load: int = 40,
        period: int = 100,
        duty_cycle: float = 0.3
    ):
        self.base_load = base_load
        self.peak_load = peak_load
        self.period = period
        self.duty_cycle = duty_cycle

    def get_traffic_load(self, round_num: int, node_id: str) -> int:
        phase = (round_num % self.period) / self.period

        if phase < self.duty_cycle:
            return self.peak_load
        else:
            return self.base_load

    def get_description(self) -> str:
        return f"Periodic: {self.base_load}-{self.peak_load} packets (T={self.period})"


class ExponentialTrafficPattern(TrafficPattern):

    def __init__(
        self,
        mean_load: int = 20,
        min_load: int = 5,
        max_load: int = 50
    ):
        self.mean_load = mean_load
        self.min_load = min_load
        self.max_load = max_load

    def get_traffic_load(self, round_num: int, node_id: str) -> int:
        load = int(np.random.exponential(self.mean_load))
        return max(self.min_load, min(self.max_load, load))

    def get_description(self) -> str:
        return f"Exponential: mean={self.mean_load}, range=[{self.min_load}, {self.max_load}]"


class SinusoidalTrafficPattern(TrafficPattern):

    def __init__(
        self,
        base_load: int = 20,
        amplitude: int = 15,
        period: int = 200,
        phase_shift: float = 0.0
    ):
        self.base_load = base_load
        self.amplitude = amplitude
        self.period = period
        self.phase_shift = phase_shift

    def get_traffic_load(self, round_num: int, node_id: str) -> int:
        phase = 2 * np.pi * (round_num / self.period) + self.phase_shift
        load = self.base_load + self.amplitude * np.sin(phase)
        return max(1, int(load))

    def get_description(self) -> str:
        return f"Sinusoidal: {self.base_load}±{self.amplitude} packets (T={self.period})"


class EventDrivenTrafficPattern(TrafficPattern):

    def __init__(
        self,
        base_load: int = 10,
        event_load: int = 60,
        event_duration: int = 50,
        events: List[int] = None
    ):
        self.base_load = base_load
        self.event_load = event_load
        self.event_duration = event_duration
        self.events = events if events else [200, 500, 800, 1200]

        self.active_events = {}

    def get_traffic_load(self, round_num: int, node_id: str) -> int:
        if round_num in self.events:
            self.active_events[round_num] = self.event_duration

        for event_start in list(self.active_events.keys()):
            self.active_events[event_start] -= 1
            if self.active_events[event_start] <= 0:
                del self.active_events[event_start]

        if self.active_events:
            return self.event_load
        return self.base_load

    def get_description(self) -> str:
        return f"Event-driven: {self.base_load} base, {self.event_load} during events"


class HotspotTrafficPattern(TrafficPattern):

    def __init__(
        self,
        base_load: int = 15,
        hotspot_load: int = 45,
        hotspot_nodes: List[str] = None,
        hotspot_probability: float = 0.3
    ):
        self.base_load = base_load
        self.hotspot_load = hotspot_load
        self.hotspot_nodes = set(hotspot_nodes) if hotspot_nodes else set()
        self.hotspot_probability = hotspot_probability

    def set_hotspot_nodes(self, nodes: List[str]):
        self.hotspot_nodes = set(nodes)

    def get_traffic_load(self, round_num: int, node_id: str) -> int:
        if node_id in self.hotspot_nodes:
            if random.random() < self.hotspot_probability:
                return self.hotspot_load
            return int(self.base_load * 1.5)
        return self.base_load

    def get_description(self) -> str:
        return f"Hotspot: {self.base_load} base, {self.hotspot_load} at hotspots"


class AdaptiveTrafficPattern(TrafficPattern):

    def __init__(
        self,
        initial_load: int = 20,
        growth_rate: float = 0.001,
        max_load: int = 50,
        variance: float = 0.2
    ):
        self.initial_load = initial_load
        self.growth_rate = growth_rate
        self.max_load = max_load
        self.variance = variance

    def get_traffic_load(self, round_num: int, node_id: str) -> int:
        base = min(
            self.max_load,
            self.initial_load * (1 + self.growth_rate * round_num)
        )

        noise = random.uniform(-self.variance, self.variance) * base

        return max(1, int(base + noise))

    def get_description(self) -> str:
        return f"Adaptive: grows from {self.initial_load} to {self.max_load}"


class CompositeTrafficPattern(TrafficPattern):

    def __init__(self, patterns: List[TrafficPattern], weights: List[float] = None):
        self.patterns = patterns

        if weights is None:
            self.weights = [1.0 / len(patterns)] * len(patterns)
        else:
            total = sum(weights)
            self.weights = [w / total for w in weights]

    def get_traffic_load(self, round_num: int, node_id: str) -> int:
        total_load = 0.0

        for pattern, weight in zip(self.patterns, self.weights):
            load = pattern.get_traffic_load(round_num, node_id)
            total_load += load * weight

        return max(1, int(total_load))

    def get_description(self) -> str:
        return "Composite: " + ", ".join(
            f"{p.get_description()} (w={w:.2f})"
            for p, w in zip(self.patterns, self.weights)
        )


def create_traffic_pattern(pattern_type: str, **kwargs) -> TrafficPattern:
    patterns = {
        'constant': ConstantTrafficPattern,
        'bursty': BurstyTrafficPattern,
        'periodic': PeriodicTrafficPattern,
        'exponential': ExponentialTrafficPattern,
        'sinusoidal': SinusoidalTrafficPattern,
        'event': EventDrivenTrafficPattern,
        'hotspot': HotspotTrafficPattern,
        'adaptive': AdaptiveTrafficPattern
    }

    pattern_class = patterns.get(pattern_type.lower())
    if pattern_class is None:
        raise ValueError(f"Unknown traffic pattern: {pattern_type}")

    return pattern_class(**kwargs)
