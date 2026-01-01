"""Routing algorithms module."""
from .base import RoutingAlgorithm
from .spr import ShortestPathRouting
from .ear import EnergyAwareRouting
from .alb import AdaptiveLoadBalancing

# Optional DRL routing (requires torch)
try:
    from .drl_sdn import DRLSDNRouting
    __all__ = [
        'RoutingAlgorithm',
        'ShortestPathRouting',
        'EnergyAwareRouting',
        'AdaptiveLoadBalancing',
        'DRLSDNRouting'
    ]
except ImportError:
    DRLSDNRouting = None
    __all__ = [
        'RoutingAlgorithm',
        'ShortestPathRouting',
        'EnergyAwareRouting',
        'AdaptiveLoadBalancing'
    ]
